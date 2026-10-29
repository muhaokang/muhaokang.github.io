---
layout: post
title: "SQL 没有报错，金额为什么多算了？从数据粒度到 JOIN 放大"
date: 2023-11-12 08:00:00 +0800
last_modified_at: 2026-10-29
author: Haokang Mu
permalink: /sql-join-grain/
description: "用三张模拟表复现关联导致的金额重复计算，说明数据粒度、预聚合和 EXISTS 各自解决什么问题。"
tags: [SQL, 数据建模, 数据质量]
---

一条 SQL 跑完了，行数也没有大得离谱，但汇总金额就是对不上。遇到这种情况，可以先把 `SUM` 放到一边，回答一个问题：**执行到这一步时，一行数据究竟代表什么？**

订单表的一行是一笔订单，明细表的一行是一项商品，附件表的一行是一个文件。把三张表关联起来以后，结果中的一行可能已经变成“某笔订单的一项商品与一个附件的组合”。此时继续累加订单金额，就会把同一个金额算多次。

下面用一个可以直接运行的小例子，把这个过程拆开看。数据全部为模拟数据，不涉及实际业务系统。

## 1. 先把要统计的对象说清楚

需求是：**按区域统计至少有一个附件的订单数量、订单金额，以及这些订单的商品明细金额。**

这里有三个边界：

- 统计对象是订单，每笔订单只计一次。
- “有附件”是筛选条件，不要求把每个附件展开到结果里。
- 商品明细金额要先按订单汇总，才能和订单金额放到同一行。

先看输入数据。`orders` 每笔订单一行，主键是 `order_id`：

| order_id | region | order_amount |
|---|---|---:|
| 101 | north | 100.00 |
| 102 | north | 100.00 |
| 103 | south | 80.00 |

`order_items` 每个明细一行，主键是 `item_id`。这里的 `item_amount` 已经是该明细的金额，不是单价：

| item_id | order_id | item_amount |
|---|---|---:|
| 11 | 101 | 60.00 |
| 12 | 101 | 40.00 |
| 21 | 102 | 100.00 |
| 31 | 103 | 80.00 |

`attachments` 每个附件一行，主键是 `attachment_id`：

| attachment_id | order_id |
|---|---|
| 1 | 101 |
| 2 | 101 |
| 3 | 102 |

全部订单金额是 280 元，但订单 103 没有附件，不在本次统计范围内。因此，正确结果应当是：north 区域有 2 笔订单，订单金额 200 元，明细金额也是 200 元。

**280 和 200 的差异来自筛选范围，不能直接当成数据丢失。** 对账前必须先对齐统计对象。

## 2. 直接关联，金额在哪一步变多了

下面这条 SQL 很容易写出来：

```sql
SELECT o.region,
       COUNT(*) AS joined_rows,
       COUNT(DISTINCT o.order_id) AS order_count,
       SUM(o.order_amount) AS order_amount,
       SUM(i.item_amount) AS item_amount
FROM orders o
JOIN order_items i ON o.order_id = i.order_id
JOIN attachments a ON o.order_id = a.order_id
GROUP BY o.region
ORDER BY o.region;
```

执行结果：

| region | joined_rows | order_count | order_amount | item_amount |
|---|---:|---:|---:|---:|
| north | 5 | 2 | 500.00 | 300.00 |

订单数看起来是对的，两个金额却都错了。把聚合之前的数据展开，就能看到原因：

| order_id | item_id | attachment_id | order_amount | item_amount |
|---|---|---|---:|---:|
| 101 | 11 | 1 | 100.00 | 60.00 |
| 101 | 11 | 2 | 100.00 | 60.00 |
| 101 | 12 | 1 | 100.00 | 40.00 |
| 101 | 12 | 2 | 100.00 | 40.00 |
| 102 | 21 | 3 | 100.00 | 100.00 |

订单 101 有 2 个明细和 2 个附件。两个关联都只按订单号匹配，所以它产生了 `2 × 2 = 4` 行。

订单金额被重复 4 次，变成 400 元；两个明细也分别被重复 2 次，合计变成 200 元。再加上订单 102，就得到了 500 和 300。

对于这种两个子表独立按同一订单键进行的内连接，一笔订单有 `m` 个明细和 `n` 个附件，就会形成 `m × n` 个组合。这不是子表本身一定有脏数据，而是关联后的粒度变了。如果关联条件还包含明细号，或者增加了其他过滤条件，则要按实际匹配关系重新分析，不能机械地套乘法。

`COUNT(DISTINCT order_id)` 只修正了订单数量，无法同时修正 `SUM`。这也是为什么只核对订单数不够。

## 3. 为什么补一个 DISTINCT 还不够

一种尝试是把金额改成：

```sql
SUM(DISTINCT o.order_amount)
```

结果会变成 100 元。因为订单 101 和 102 的金额恰好都为 100，`DISTINCT` 消除的是相同的**金额值**，并不知道它们来自两笔不同订单。

另一种写法是在聚合结果外加 `SELECT DISTINCT`。但 `GROUP BY region` 已经得到一行 north，金额在聚合时就算成了 500，外层去重不能把错误的总额还原。

当然，先选出唯一的 `(order_id, order_amount)` 再汇总，在订单号确实唯一决定金额的前提下，也可以恢复订单粒度。关键在于选出的列是否都属于同一笔订单；一旦继续携带 `item_id` 或 `attachment_id`，结果仍然会展开。

所以要先明确需要保留的记录，再决定如何去重。

## 4. 只判断是否存在，就使用 EXISTS

如果只要订单数和订单金额，根本不需要关联商品明细。附件只负责判断这笔订单是否进入统计范围：

```sql
SELECT o.region,
       COUNT(*) AS order_count,
       SUM(o.order_amount) AS order_amount
FROM orders o
WHERE EXISTS (
    SELECT 1 FROM attachments a
    WHERE a.order_id = o.order_id
)
GROUP BY o.region
ORDER BY o.region;
```

结果为 `north / 2 / 200.00`。同一订单有几个匹配附件，都只决定 `EXISTS` 是否成立，不会把左侧订单展开。

DuckDB 的 [JOIN 文档](https://duckdb.org/docs/1.4/sql/query_syntax/from)说明了半连接的语义：保留左侧存在匹配的行。Spark SQL 也提供 [LEFT SEMI JOIN](https://spark.apache.org/docs/latest/sql-ref-syntax-qry-select-join.html)。这里选择 `EXISTS` 表达筛选目的；本文实际执行环境是 DuckDB，没有据此推断其他引擎的性能。

需要注意，`EXISTS` 也不会替左表去重。如果订单表本身有同一订单的多个版本，必须先确定要使用哪个版本。

## 5. 需要右表指标，就先对齐粒度

完整需求还包含商品明细金额，可以先把商品明细聚合到订单粒度，再关联订单表：

```sql
WITH item_total AS (
    SELECT order_id, SUM(item_amount) AS item_amount
    FROM order_items
    GROUP BY order_id
)
SELECT o.region,
       COUNT(*) AS order_count,
       SUM(o.order_amount) AS order_amount,
       SUM(i.item_amount) AS item_amount,
       SUM(CASE WHEN i.order_id IS NULL THEN 1 ELSE 0 END) AS missing_item_orders
FROM orders o
LEFT JOIN item_total i ON o.order_id = i.order_id
WHERE EXISTS (
    SELECT 1 FROM attachments a
    WHERE a.order_id = o.order_id
)
GROUP BY o.region
ORDER BY o.region;
```

结果：

| region | order_count | order_amount | item_amount | missing_item_orders |
|---|---:|---:|---:|---:|
| north | 2 | 200.00 | 200.00 | 0 |

这次的处理顺序是：商品明细按订单聚合，每个订单最多一行；再和订单表关联；用附件筛选订单；最后按区域汇总。

`missing_item_orders` 是特意保留的检查项。假设再加入一笔金额为 50 元、有附件但没有商品明细的订单 104，查询会得到：

| region | order_count | order_amount | item_amount | missing_item_orders |
|---|---:|---:|---:|---:|
| north | 3 | 250.00 | 200.00 | 1 |

这个结果没有把缺明细的订单悄悄过滤掉，但也不能直接认定两个金额都完整。是否允许缺明细，需要由统计口径决定。

在完整性尚未确认时，直接把缺失明细金额填成 0，会掩盖“没有取到数据”和“金额确实为零”的区别。另外，`SUM` 会忽略 NULL；没有任何匹配订单时，这条带 `GROUP BY` 的查询返回空结果，并不自动生成一行零值。这些情况都要单独处理。

## 6. 换成真实数仓时，还要检查什么

这个例子省略了租户、来源系统、业务日期和币种。实际使用时，至少要补齐以下判断：

1. **关联键是不是完整业务键。** 订单号可能只在某个来源或租户内唯一，不能默认全局唯一。
2. **两侧是否使用同一个统计范围。** 明细取最新快照、主表取历史快照，会带来另一类不一致。
3. **聚合后是否真的唯一。** 如果要按 `(租户, 订单号)` 关联，预聚合也必须保留这组键。
4. **过滤条件是否改变保留范围。** `LEFT JOIN` 后在 `WHERE` 中要求右侧字段等于某值，会排除右侧缺失的记录。
5. **金额是否具有可加性。** 本例使用相同币种，并约定明细金额可直接相加。折扣、税额、退款和币种换算需要另行定义。

排查时可以在每次关联后同时记录行数、唯一业务键数量、未匹配数量和关键金额。先定位是哪一步改变了粒度，再判断这个变化是否符合需求。只看最终总数，通常不容易找到问题出在哪里。

## 7. 运行本文示例

下载 [完整 Python 示例](/assets/examples/sql_join_grain.py)，其中包含建表、插入数据、错误写法、修复写法和结果断言。金额使用 `DECIMAL(12, 2)`。

在下载目录中执行：

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install duckdb==1.4.5
python3 sql_join_grain.py
```

本次验证使用 Python 3.9.6、DuckDB 1.4.5。脚本会检查金额 500/300 的错误结果、`SUM(DISTINCT)` 得到 100 的反例、修复后的 200/200，以及缺明细和无符合条件订单的情况。全部断言通过后输出 `PASS`。这些小数据验证用于说明计算语义，不是分布式引擎的性能测试。

继续阅读：[去重与最新状态](/dedup-and-latest-state/)、[调度与数据就绪](/data-readiness/)。

> 本文为历史专题补记，按 2023-11-12 归档，于 2026-10-29 整理并验证示例。文中的运行环境版本对应本次验证时间。
