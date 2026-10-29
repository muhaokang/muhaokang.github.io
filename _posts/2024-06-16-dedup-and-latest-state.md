---
layout: post
title: "去重不是 DISTINCT：业务主键、历史事件与最新状态"
date: 2024-06-16 08:00:00 +0800
last_modified_at: 2026-10-29
author: Haokang Mu
permalink: /dedup-and-latest-state/
description: "用事件重放、取消后重建、晚到数据和状态反复的可运行案例，区分事件去重与最新状态计算。"
tags: [SQL, 数据建模]
---

处理一张不断追加的事件表时，“按订单去重”听起来很明确，真正写 SQL 才会发现：重复到达的消息、同一订单的不同版本、取消后新建的订单，可能全挤在一张表里。

这些记录都能让订单号重复，但处理方式不同。把它们统一压成一行，行数可能变少，结果却未必正确。

下面用一组模拟订单说明三个问题：**什么算同一件事，什么算同一个对象，以及哪条记录代表最新状态。** 本文的指标是“当前有效订单数与金额”，不涉及收入确认、回款或结算。

## 1. 先写清楚三种粒度

假设订单状态变化时，上游会产生一条带完整状态的事件。这个案例约定：

| 要回答的问题 | 使用的键 | 说明 |
| --- | --- | --- |
| 这是不是同一个订单？ | `tenant_id + order_id` | 订单号只在租户内部唯一 |
| 这是不是同一次事件的重放？ | `tenant_id + event_id` | 同一事件可能投递多次，事件编号保持不变 |
| 哪个状态更新？ | 订单内的 `source_version` | 来源系统提供递增版本，每个版本对应一个完整状态 |

另有一个 `request_id`，表示订单来自哪个业务申请。旧订单取消后，可以在同一申请下新建订单，所以它不能直接代替订单主键。

这个区分决定了处理顺序：先识别重复投递，再保留不同状态版本，最后根据查询目的生成当前状态表。事件明细与当前状态表可以同时存在，各自服务不同的问题。

## 2. 准备一组会暴露问题的数据

模拟数据包含 10 条到达记录，分别覆盖下面的情况。`ACTIVE` 表示有效，`CANCELLED` 表示取消。

| 订单 | 金额 | 状态变化 | 特殊情况 |
| --- | ---: | --- | --- |
| T1 / O100 | 100 | v1 有效 → v2 取消 | v2 事件重复投递一次 |
| T1 / O101 | 100 | v1 有效 | 和 O100 来自同一申请 R100，是取消后新建的另一笔订单 |
| T1 / O200 | 80 | v1 有效 → v2 取消 | v1 在 11:30 才到达，晚于 11:10 到达的 v2 |
| T1 / O300 | 50 | v1 有效 → v2 取消 → v3 有效 | v2、v3 的业务时间都记为 12:05:00 |
| T2 / O100 | 200 | v1 有效 | 与 T1 的订单号相同，租户不同 |

全量到达后，预期有效订单是 T1/O101、T1/O300、T2/O100，共 **3 笔，金额 350**。取消的 O100 和 O200 仍然保留在状态表中，只是不参与这个指标。

完整建表、数据与断言放在[可运行示例]({{ '/assets/examples/dedup_and_latest_state.py' | relative_url }})里。下载文件后可以在独立环境运行：

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install "duckdb==1.4.5"
python3 dedup_and_latest_state.py
```

本次使用 Python 3.9.6、DuckDB 1.4.5 验证。这是本次补记的验证环境，不代表 2024 年使用过这些版本。数据和查询都在内存中运行，不连接外部数据库。

## 3. 先处理事件重放

O100 的取消事件 E02 到达了两次，业务字段相同，`ingested_at` 不同。直接执行 `SELECT DISTINCT *`，仍然得到 10 行，因为到达时间也是参与比较的字段。

如果按事件幂等键处理，则应该留下 9 个逻辑事件。但在保留某一条之前，要先确认同一个事件编号没有对应不同内容：

```sql
SELECT tenant_id, event_id
FROM (
    SELECT DISTINCT tenant_id, event_id, order_id, request_id,
           source_version, status, amount, event_time
    FROM raw_events
) AS payloads
GROUP BY tenant_id, event_id
HAVING COUNT(*) > 1;
```

这条检查应返回空集。它刻意不比较 `ingested_at`，因为重复投递允许有不同的到达时间。这里列出的字段构成了示例的完整业务载荷；真实事件还有其他业务字段时，也必须纳入一致性检查。

检查通过后，再按事件编号保留第一次到达：

```sql
CREATE VIEW events AS
SELECT tenant_id, event_id, order_id, request_id,
       source_version, status, amount, event_time, ingested_at
FROM (
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY tenant_id, event_id
        ORDER BY ingested_at ASC
    ) AS replay_rank
    FROM raw_events
) AS ranked
WHERE replay_rank = 1;
```

这里选择第一次到达，只是为了保留一个代表记录。同一事件的业务载荷已经检查为一致，即使两次到达时间也相同，选中哪份副本都不影响业务状态。

如果一个事件编号出现两种金额或状态，应先隔离冲突并核对来源。任取一条会隐藏问题。上游没有稳定事件编号时，也不能把包含到达时间的整行哈希直接当成幂等键，否则同一事件重放后仍会变成“新事件”。

## 4. 再为每个订单选最新状态

事件去重后，一笔订单仍然可以有多个版本。这是应该保留的历史。

本例中，来源系统承诺每个订单的版本递增，且一个版本只代表一个逻辑事件。先检查这个约定：

```sql
SELECT tenant_id, order_id, source_version
FROM events
GROUP BY tenant_id, order_id, source_version
HAVING COUNT(*) > 1;
```

检查通过后，按完整订单主键分组、来源版本倒序，就能得到唯一的最新状态：

```sql
CREATE VIEW latest_state AS
SELECT tenant_id, order_id, request_id, source_version, status, amount
FROM (
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY tenant_id, order_id
        ORDER BY source_version DESC
    ) AS state_rank
    FROM events
) AS ranked
WHERE state_rank = 1;
```

这里的排序能够确定结果，是因为前置检查和来源约定保证了订单内的版本唯一。`ROW_NUMBER()` 本身不会替我们判断两个冲突版本谁更可信。它按窗口中的分组和排序规则编号，具体语义可以查阅 [DuckDB 窗口函数文档](https://duckdb.org/docs/1.4/sql/functions/window_functions)。

如果同一版本对应两个不同状态，补一个 `event_id DESC` 虽然能让结果看起来稳定，却不能证明选中的状态正确。应先解决版本冲突；如果来源只有秒级时间，没有可靠版本或顺序，需要明确额外的排序依据，或者把这批记录标记为顺序不确定。

## 5. 先取最新，再过滤有效状态

得到 `latest_state` 后，指标计算很直接：

```sql
SELECT COUNT(*) AS active_orders, SUM(amount) AS active_amount
FROM latest_state
WHERE status = 'ACTIVE';
```

结果是 `3 / 350.00`。如果把状态条件提前放进窗口计算内部，含义就变了：

```sql
-- 错误示例：计算的是“最近一次有效”，不是“最新状态有效”。
SELECT tenant_id, order_id, source_version, amount
FROM (
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY tenant_id, order_id
        ORDER BY source_version DESC
    ) AS state_rank
    FROM events
    WHERE status = 'ACTIVE'
) AS ranked
WHERE state_rank = 1;
```

取消记录在排名之前就被删掉了，O100 和 O200 以前的有效版本重新排到第一名，最后错误地得到 **5 笔、530.00**。

两个问题都可以有业务意义：“最近一次有效时是什么状态”和“当前是否有效”。但需要先确定正在回答哪一个，不能只看 SQL 是否去重成功。

`DISTINCT` 的作用同样取决于投影字段。`SELECT DISTINCT tenant_id, order_id, status` 可以列出不同状态组合，却没有表达哪种状态更晚。关于 `DISTINCT` 如何比较结果行，可参考 [DuckDB SELECT 文档](https://duckdb.org/docs/1.4/sql/query_syntax/select)。

## 6. 三个容易被样例掩盖的边界

**到达晚，不等于状态新。** O200 的 v1 比 v2 晚到 20 分钟。如果按 `ingested_at DESC` 取最新，订单会从取消退回有效，结果变成 4 笔、430.00。`event_time` 表达事件发生时间，`ingested_at` 表达到达时间，`source_version` 表达本例来源系统的状态顺序，三者不能随意互换。

**取消后重建，可能是新的业务对象。** O100 与 O101 共享申请号 R100，但订单号不同。是否需要在申请层再合并，是另一个统计口径，不能在订单明细层顺手按 `request_id` 删除一笔。本例也保留了两个租户的 O100，避免因为省略租户键而合并不同对象。

**状态可以反复，不能默认取消就是最终状态。** O300 的 v2 取消后，v3 又变为有效。这里模拟的业务规则允许恢复，因此应保留 v3；其他系统可能禁止这种转移，需要按它自己的状态机检查。仅按 12:05:00 排序，无法区分本例的 v2 和 v3，可信版本才提供了先后关系。

对于增量处理，还要把新事件与已有状态比较。来源版本较旧的晚到数据不能覆盖更高版本；事件明细可以追加，当前状态也可以保持不变。跨来源合并时，如果版本只在各自来源内有效，就需要把来源范围纳入键或明确冲突规则，不能直接比较两个系统的数字大小。

## 7. 把结果和反例一起验证

示例脚本实际运行得到：

| 计算方法 | 结果 |
| --- | --- |
| 原始记录 / 整行 DISTINCT / 事件幂等去重 | 10 / 10 / 9 行 |
| 先取最新状态，再筛有效订单 | 3 笔 / 350.00 |
| 先筛有效，再取最新 | 5 笔 / 530.00 |
| 把最近到达当成最新状态 | 4 笔 / 430.00 |

脚本还验证了四个变化：再次重放同一事件不会改变指标；同一事件编号出现不同载荷会被检测出来；同一订单版本出现冲突事件会被检测出来；晚到的旧版本不会把正确状态回退。

这套方法依赖完整、可信的版本信息。本例的事件携带完整状态；如果输入是只包含变化字段的增量补丁，还需要按顺序还原状态，不能直接选最后一行。这里说的“当前”，也只是本次已收齐数据范围内的最新状态；上游尚有缺数时，应说明观测截止时间，不能把未到达当成不存在。

写去重逻辑时，先写下实体键、事件键和版本规则，再分别检查输入、历史和输出。这样行数变化才有明确含义，也更容易定位究竟是重复投递、状态变化，还是来源数据出了问题。

---

本文为历史专题补记，按 2024-06-16 归档，于 2026-10-29 整理并验证示例。
