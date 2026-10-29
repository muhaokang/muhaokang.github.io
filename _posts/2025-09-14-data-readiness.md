---
layout: post
title: "任务成功，数据为什么还是旧的？从调度依赖到数据就绪"
date: 2025-09-14 08:00:00 +0800
last_modified_at: 2026-10-29
permalink: /data-readiness/
author: Haokang Mu
description: "通过一条模拟日汇总链路，区分任务成功、分区存在与数据就绪，并实现一个可以复现的三态检查。"
tags: [数据质量, 数据工程]
---

日汇总任务显示成功，结果里的状态却还是昨天的；上游随后补齐数据，下游也没有自动变化。排查这种问题时，如果只看任务有没有报错，很容易错过真正的原因。

任务成功说明这次执行满足了程序和调度系统定义的成功条件。它是否读到了正确日期、正确版本且完整的数据，还要另外检查。

下面用订单与结算汇总构造一个例子。表名、时间和数量均为模拟数据，重点是看清链路中的判断条件。

## 1. 先把时间线画出来

假设每天生成前一天的订单日汇总，需要订单明细和结算明细两份输入。9 月 14 日这次运行应处理业务日期 `2025-09-13`。

| 时间 | 发生了什么 | 当时可以读取的数据 |
| --- | --- | --- |
| 08:50 | 订单明细发布完成 | 9 月 13 日订单数据 |
| 09:00 | 日汇总启动 | 订单已齐，9 月 13 日结算数据还没发布 |
| 09:03 | 日汇总执行成功 | 输出中的部分结算状态为空 |
| 10:00 | 结算明细发布完成 | 9 月 13 日结算数据就绪 |

如果日汇总使用左关联，暂时没有匹配结算记录的订单仍然可以输出。SQL 不一定报错，行数甚至可能与昨天接近。

10 点以后，源表变了，已经落盘的日汇总通常不会随之重算。此时会同时看到“所有任务都是成功的”和“下游结果仍然不对”。

这里至少有三个不同的时间概念：业务数据属于哪一天、任务实际在什么时候执行、某个输入版本什么时候发布。排查时应分别记录，不能用任务启动时间代替业务日期。Airflow 的数据区间与逻辑日期也明确区分了这些概念：逻辑日期表示数据区间的起点，并非实际执行时间。[官方说明](https://airflow.apache.org/docs/apache-airflow/2.10.5/core-concepts/dag-run.html#data-interval)

## 2. 把下游需要什么写成明确条件

“等上游好了再跑”不够具体。对这个日汇总，可以先约定四件事：

| 条件 | 需要回答的问题 |
| --- | --- |
| 业务范围正确 | 两个来源是否都覆盖目标业务日期？时区与业务日边界是否一致？ |
| 输入版本确定 | 下游读的是哪个已经发布的快照或批次？ |
| 来源齐备 | 订单、结算这两个必需来源是否都有就绪记录？ |
| 约定校验通过 | 记录数、业务主键、关键字段与对账结果是否满足约定？ |

有了这些条件，调度依赖才有了清楚的目标。跨工作流等待也要对应到需要的数据区间，不能只挑“最近一个成功实例”。Airflow 的 `ExternalTaskSensor` 可以等待另一个工作流在指定逻辑日期的任务状态，但仍需要把逻辑日期映射到本业务真正需要的输入。[跨工作流依赖说明](https://airflow.apache.org/docs/apache-airflow/2.10.5/howto/operator/external_task_sensor.html)

这个例子把“订单、结算都必须就绪”作为发布要求。实际链路也可以允许部分来源晚到，但必须明确输出是否为暂定结果、如何标记缺失、什么时候修正。不能让使用者从一个普通的空值猜测是哪种情况。

## 3. 三个看似合理、实际不够的检查

**分区存在，不代表装载完成。**

任务可能先创建分区，再分批写入。下游一看到分区就读取，有机会读到空表或中间状态。更明确的方式是由上游发布完成标记，标记指向已经完成校验、可稳定读取的版本；下游读取那个版本，而不是一个还在变化的位置。

**最新更新时间正常，不代表数据齐套。**

假设本批应有 80 条记录，目前只有 50 条写入成功，其中一条更新时间是 09:59。`MAX(updated_at)` 看起来很新，却不能说明另外 30 条已经到达。时间指标适合检查新鲜度，覆盖度还需要来源清单、批次记录数或业务对账来验证。

**结果为零，不一定是合法空批次。**

没有权限、请求超时、日期条件写错、上游没有数据，都可能让调用方拿不到有效明细。先记录查询是否成功，再解释返回内容。只有来源明确声明该批次已经完成、预期记录数就是零，实际读取也为零，才符合本文的合法空批次约定。

## 4. 一个可运行的三态检查

检查结果分成三种：

- `PASS`：约定的检查都有证据支持，可以继续使用这批输入。
- `BLOCK`：已经发现不满足约定的事实，例如业务日期错误或装载未完成。
- `UNKNOWN`：证据不足，例如查询失败，或者没有独立的预期记录数。

只有 `PASS` 才允许继续。`BLOCK` 与 `UNKNOWN` 都暂停消费，但后续动作不同：前者需要处理已知问题，后者需要补齐证据。如果两种情况同时存在，示例返回 `BLOCK`，同时保留所有原因。

示例为每个来源保存以下字段：

| 字段 | 含义 |
| --- | --- |
| `business_date` | 该快照对应的业务日期 |
| `publish_state` | 上游是否已经发布完成 |
| `manifest_snapshot` | 就绪清单声明的版本 |
| `observed_snapshot` | 本次实际读取的版本 |
| `expected_rows` | 来源清单独立提供的预期记录数 |
| `observed_rows` | 在指定版本中实际读到的记录数 |
| `query_ok` | 读取这个版本是否成功 |

这里的“独立”很重要。如果 `expected_rows` 也是对同一个不完整目标表执行 `COUNT(*)` 得到的，那么两者相等只是重复检查了同一份结果。

已经成功读取的清单和随后对数据的查询是两份证据。即使后者失败，清单中已知的日期错误或未发布状态也不能被丢掉。对每个来源，核心判断可以用下面的伪代码表示；遍历来源与汇总原因的实现见[完整示例脚本](/assets/examples/data_readiness.py)：

```python
# 先检查已经成功获得的清单证据，各项独立记录。
if snapshot.business_date != target_date:
    blocked.append("错误业务日期")
if snapshot.publish_state != "COMPLETE":
    blocked.append("批次还没有发布完成")
if not snapshot.manifest_snapshot:
    unknown.append("缺少清单版本号")
expected_valid = (
    snapshot.expected_rows is not None and snapshot.expected_rows >= 0
)
if not expected_valid:
    unknown.append("预期记录数不可用")

# 再检查数据；查询失败时保留前面已发现的问题。
if not snapshot.query_ok:
    unknown.append("数据查询失败")
else:
    if not snapshot.observed_snapshot:
        unknown.append("缺少读取版本号")
    elif (snapshot.manifest_snapshot
          and snapshot.manifest_snapshot != snapshot.observed_snapshot):
        blocked.append("清单与读取版本不一致")
    observed_valid = (
        snapshot.observed_rows is not None and snapshot.observed_rows >= 0
    )
    if not observed_valid:
        unknown.append("实际记录数不可用")
    elif expected_valid and snapshot.expected_rows != snapshot.observed_rows:
        blocked.append("记录数不符合约定")

status = "BLOCK" if blocked else "UNKNOWN" if unknown else "PASS"
```

下载脚本后直接运行，无需安装数据库或连接任何外部服务：

```sh
python3 data_readiness.py
```

本次使用 Python 3.9.6 验证，脚本只依赖标准库。输出如下，每个场景都包含结果断言：

```text
ready: PASS
stale_partition: BLOCK
partition_created: BLOCK
partial_load: BLOCK
wrong_snapshot: BLOCK
missing_source: BLOCK
query_failed: UNKNOWN
empty_without_evidence: UNKNOWN
valid_empty_batch: PASS
mixed_evidence: BLOCK (both reasons retained)
same_source_mixed_evidence: BLOCK (all known reasons retained)
All 11 scenarios passed.
```

`missing_source` 的前提是完整查询了就绪清单，确认必需来源没有记录。如果查询清单本身失败，应直接得到 `UNKNOWN`，不能把失败包装成空清单。`valid_empty_batch` 通过的原因则是清单明确声明了零条，且对应版本已经发布完成。

最后一个场景中，同一来源的清单已经显示业务日期错误、批次未发布，随后读取数据又失败。因此结果为 `BLOCK`，同时保留查询失败的 `UNKNOWN` 原因；不会因为读数据失败就覆盖掉已经确认的问题。

这只是一个最小示例。行数一致也不能证明内容正确：少一条、多一条可能恰好抵消，还可能存在金额错误、错误主键或来源间截止时点不一致。根据业务继续增加唯一性、范围覆盖、关键字段和金额对账，并保证校验和消费使用同一版本，才不会在“检查通过”之后又读到另一批数据。

## 5. 修复时先恢复条件，再决定补跑范围

回到最初的时间线，把日汇总固定推迟到 10:30 可能暂时有效，但如果上游某天延迟到 11 点，同样的问题还会出现。固定时间可以作为等待上限或运行窗口，数据依赖和就绪条件仍然需要表达清楚。

更稳妥的处理顺序是：

1. 确认日汇总实际消费的业务日期、版本和来源，圈定受影响的输出。
2. 修正依赖关系或就绪检查，确保后续运行不会再次提前消费。
3. 等上游目标版本发布并校验通过，判断日汇总及其下游哪些结果需要重算。
4. 明确重算是覆盖分区、按业务键合并还是追加写入，避免一次修复造成新的重复。
5. 验证最终消费层，包括已生成的导出文件或缓存；只看重跑实例成功还不够。

能否重复执行而不改变正确结果，是补跑前需要回答的问题。如果一个任务采用直接追加写入，就不能默认重跑一次只是“刷新一下”。

数据链路的检查最终要落到一个具体问题：**下游这次需要的那份数据，现在是否可以被稳定、完整地读取？** 任务状态、分区、时间戳和记录数都是证据的一部分，把它们放在同一个业务日期和版本下核对，判断才有意义。

---

本文为历史专题补记，按 2025-09-14 归档，于 2026-10-29 整理并验证示例。
