---
layout: post
title: "ClickHouse高级"
author: Haokang Mu
excerpt: ClickHouse高级.md
tags:
- ClickHouse

---

# 1.**Explain 查看执行计划 **
在 clickhouse 20.6 版本之前要查看 SQL 语句的执行计划需要设置日志级别为 trace 才能可以看到，并且只能真正执行 sql，在执行日志里面查看。在 20.6 版本引入了原生的执行计划的语法。在 20.6.3 版本成为正式版本的功能。 
**本文档基于目前较新稳定版 21.7.3.14。**
## 1.1 基本语法 
```sql
EXPLAIN [AST | SYNTAX | PLAN | PIPELINE] [setting = value, ...] 
SELECT ... [FORMAT ...] 
```

- PLAN：用于查看执行计划，默认值。 

◼ header 打印计划中各个步骤的 head 说明，默认关闭，默认值 0; 
◼ description 打印计划中各个步骤的描述，默认开启，默认值 1； 
◼ actions 打印计划中各个步骤的详细信息，默认关闭，默认值 0。 

- AST ：用于查看语法树; 
- SYNTAX：用于优化语法; 
- PIPELINE：用于查看 PIPELINE 计划。 

◼ header 打印计划中各个步骤的 head 说明，默认关闭; 
◼ graph 用 DOT 图形语言描述管道图，默认关闭，需要查看相关的图形需要配合 graphviz 查看； 
◼ actions 如果开启了 graph，紧凑打印打，默认开启。 
_注：PLAN 和 PIPELINE 还可以进行额外的显示设置，如上参数所示。_

## 1.2 案例实操 
**1.2.1 新版本使用 EXPLAIN **
可以再安装一个 20.6 以上版本，或者直接在官网的在线 demo，选择高版本进行测试。 
官网在线测试链接：https://play.clickhouse.tech/?file=welcome 

1）查看 PLAIN 
简单查询
```sql
EXPLAIN
SELECT arrayJoin([1, 2, 3, NULL, NULL])

Query id: 8c3ab78b-7147-439e-814e-72c583ba1c2f

Connecting to localhost:9000 as user default.
Connected to ClickHouse server version 21.7.3 revision 54449.

┌─explain───────────────────────────────────────────────────────────────────┐
│ Expression ((Projection + Before ORDER BY))                               │
│   SettingQuotaAndLimits (Set limits and quota after reading from storage) │
│     ReadFromStorage (SystemOne)                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

复杂 SQL 的执行计划
```sql
EXPLAIN
SELECT
    database,
    table,
    count(1) AS cnt
FROM system.parts
WHERE database IN ('datasets', 'system')
GROUP BY
    database,
    table
ORDER BY
    database ASC,
    cnt DESC
LIMIT 2 BY database

Query id: bd17ac72-99e6-4675-9c50-f5a5d7b2d76e

┌─explain─────────────────────────────────────────────────────────────────────────────────────┐
│ Expression (Projection)                                                                     │
│   LimitBy                                                                                   │
│     Expression (Before LIMIT BY)                                                            │
│       MergingSorted (Merge sorted streams for ORDER BY)                                     │
│         MergeSorting (Merge sorted blocks for ORDER BY)                                     │
│           PartialSorting (Sort each block for ORDER BY)                                     │
│             Expression (Before ORDER BY)                                                    │
│               Aggregating                                                                   │
│                 Expression (Before GROUP BY)                                                │
│                   Filter (WHERE)                                                            │
│                     SettingQuotaAndLimits (Set limits and quota after reading from storage) │
│                       ReadFromStorage (SystemParts)                                         │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

打开全部的参数的执行计划
```sql
EXPLAIN header = 1, actions = 1, description = 1
SELECT number
FROM system.numbers
LIMIT 10

Query id: 633e53c2-573c-450c-8137-554b79b9110b

Connecting to localhost:9000 as user default.
Connected to ClickHouse server version 21.7.3 revision 54449.

┌─explain───────────────────────────────────────────────────────────────────┐
│ Expression ((Projection + Before ORDER BY))                               │
│ Header: number UInt64                                                     │
│ Actions: INPUT :: 0 -> number UInt64 : 0                                  │
│ Positions: 0                                                              │
│   SettingQuotaAndLimits (Set limits and quota after reading from storage) │
│   Header: number UInt64                                                   │
│     Limit (preliminary LIMIT)                                             │
│     Header: number UInt64                                                 │
│     Limit 10                                                              │
│     Offset 0                                                              │
│       ReadFromStorage (SystemNumbers)                                     │
│       Header: number UInt64                                               │
└───────────────────────────────────────────────────────────────────────────┘
```

2）AST 语法树 
```sql
EXPLAIN AST
SELECT number
FROM system.numbers
LIMIT 10

Query id: af4f359b-c72e-41e7-b1f4-477d87597458

┌─explain─────────────────────────────────────┐
│ SelectWithUnionQuery (children 1)           │
│  ExpressionList (children 1)                │
│   SelectQuery (children 3)                  │
│    ExpressionList (children 1)              │
│     Identifier number                       │
│    TablesInSelectQuery (children 1)         │
│     TablesInSelectQueryElement (children 1) │
│      TableExpression (children 1)           │
│       TableIdentifier system.numbers        │
│    Literal UInt64_10                        │
└─────────────────────────────────────────────┘
```

3）SYNTAX 语法优化
先做一次查询 
```sql
SELECT if(number = 1, 'hello', if(number = 2, 'world', 'mhk'))
FROM numbers(10)

Query id: f17854b0-61ca-4d25-961a-567db0fba1e7

┌─if(equals(number, 1), 'hello', if(equals(number, 2), 'world', 'mhk'))─┐
│ mhk                                                                   │
│ hello                                                                 │
│ world                                                                 │
│ mhk                                                                   │
│ mhk                                                                   │
│ mhk                                                                   │
│ mhk                                                                   │
│ mhk                                                                   │
│ mhk                                                                   │
│ mhk                                                                   │
└───────────────────────────────────────────────────────────────────────┘
```
查看语法优化 
```sql
EXPLAIN SYNTAX
SELECT if(number = 1, 'hello', if(number = 2, 'world', 'mhk'))
FROM numbers(10)

Query id: a706af9e-986c-48e2-8446-1ce411e5ef96

┌─explain────────────────────────────────────────────────────────┐
│ SELECT if(number = 1, 'hello', if(number = 2, 'world', 'mhk')) │
│ FROM numbers(10)                                               │
└────────────────────────────────────────────────────────────────┘
```
开启三元运算符优化 
```sql
SET optimize_if_chain_to_multiif = 1

Query id: b9439d72-9de7-45b0-83c7-954034c897a7

Ok.
```
再次查看语法优化
```sql
EXPLAIN SYNTAX
SELECT if(number = 1, 'hello', if(number = 2, 'world', 'mhk'))
FROM numbers(10)

Query id: 7202a628-c87e-403a-ab67-ac0a3e6c31e3

┌─explain─────────────────────────────────────────────────────────┐
│ SELECT multiIf(number = 1, 'hello', number = 2, 'world', 'mhk') │
│ FROM numbers(10)                                                │
└─────────────────────────────────────────────────────────────────┘再次查看语法优化
```

4）查看 PIPELINE
```sql
EXPLAIN PIPELINE
SELECT sum(number)
FROM numbers_mt(100000)
GROUP BY number % 20

Query id: b02792e0-0555-4dce-84a8-353ededfc4cf

┌─explain─────────────────────────┐
│ (Expression)                    │
│ ExpressionTransform             │
│   (Aggregating)                 │
│   Resize 2 → 1                  │
│     AggregatingTransform × 2    │
│       (Expression)              │
│       ExpressionTransform × 2   │
│         (SettingQuotaAndLimits) │
│           (ReadFromStorage)     │
│           NumbersMt × 2 0 → 1   │
└─────────────────────────────────┘
```
  打开其他参数
```sql
EXPLAIN PIPELINE header = 1, graph = 1
SELECT sum(number)
FROM numbers_mt(10000)
GROUP BY number % 20

Query id: b2051401-c27e-4f8c-bacf-90061e4c6539

┌─explain─────────────────────────────────────┐
│ digraph                                     │
│ {                                           │
│   rankdir="LR";                             │
│   { node [shape = box]                      │
│         n2 [label="Limit"];                 │
│         n1 [label="Numbers"];               │
│     subgraph cluster_0 {                    │
│       label ="Aggregating";                 │
│       style=filled;                         │
│       color=lightgrey;                      │
│       node [style=filled,color=white];      │
│       { rank = same;                        │
│         n4 [label="AggregatingTransform"];  │
│       }                                     │
│     }                                       │
│     subgraph cluster_1 {                    │
│       label ="Expression";                  │
│       style=filled;                         │
│       color=lightgrey;                      │
│       node [style=filled,color=white];      │
│       { rank = same;                        │
│         n5 [label="ExpressionTransform"];   │
│       }                                     │
│     }                                       │
│     subgraph cluster_2 {                    │
│       label ="Expression";                  │
│       style=filled;                         │
│       color=lightgrey;                      │
│       node [style=filled,color=white];      │
│       { rank = same;                        │
│         n3 [label="ExpressionTransform"];   │
│       }                                     │
│     }                                       │
│   }                                         │
│   n2 -> n3 [label="                         │
│ number UInt64 UInt64(size = 0)"];           │
│   n1 -> n2 [label="                         │
│ number UInt64 UInt64(size = 0)"];           │
│   n4 -> n5 [label="                         │
│ modulo(number, 20) UInt8 UInt8(size = 0)    │
│ sum(number) UInt64 UInt64(size = 0)"];      │
│   n3 -> n4 [label="                         │
│ number UInt64 UInt64(size = 0)              │
│ modulo(number, 20) UInt8 UInt8(size = 0)"]; │
│ }                                           │
└─────────────────────────────────────────────┘
```

# 2. 建表优化 
## 2.1 数据类型 
### 2.1.1 时间字段的类型 
建表时能用数值型或日期时间型表示的字段就不要用字符串，全 String 类型在以 Hive 为中心的数仓建设中常见，但 ClickHouse 环境不应受此影响。 
虽然 ClickHouse 底层将 DateTime 存储为时间戳 Long 类型，但不建议存储 Long 类型， 因为 DateTime 不需要经过函数转换处理，执行效率高、可读性好。
```sql
create table t_type2(
  id UInt32,
  sku_id String,
  total_amount Decimal(16,2) ,
  create_time Int32 
) engine =ReplacingMergeTree(create_time)
  partition by toYYYYMMDD(toDate(create_time)) –-需要转换一次，否则报错
  primary key (id)
  order by (id, sku_id);
```
  
### 2.1.2 空值存储类型 
官方已经指出 **Nullable 类型几乎总是会拖累性能**，因为存储 Nullable 列时需要创建一个额外的文件来存储 NULL 的标记，并且 Nullable 列无法被索引。因此除非极特殊情况，应直接使用字段默认值表示空，或者自行指定一个在业务中无意义的值（例如用-1 表示没有商品 ID）。
```sql
hadoop102 :) CREATE TABLE t_null(x Int8, y Nullable(Int8)) ENGINE TinyLog;

CREATE TABLE t_null
(
    `x` Int8,
    `y` Nullable(Int8)
)
ENGINE = TinyLog

Query id: ad870b41-0650-4fe6-8313-aabdc2693946

Ok.

0 rows in set. Elapsed: 0.045 sec. 

hadoop102 :) INSERT INTO t_null VALUES (1, NULL), (2, 3);

INSERT INTO t_null VALUES

Query id: 33e450f9-0c21-483e-99fd-a35d793f77f4

Ok.

2 rows in set. Elapsed: 0.104 sec. 

hadoop102 :) SELECT x + y FROM t_null;

SELECT x + y
FROM t_null

Query id: 99828183-9860-4c6b-bb45-065729d6df38

┌─plus(x, y)─┐
│       ᴺᵁᴸᴸ │
│          5 │
└────────────┘

2 rows in set. Elapsed: 0.014 sec. 
```
查看存储的文件：（没有权限就用 root 用户）
```sql
[root@hadoop102 t_null]# pwd
/var/lib/clickhouse/data/default/t_null
[root@hadoop102 t_null]# ll
总用量 16
-rw-r----- 1 clickhouse clickhouse 91 4月  22 21:03 sizes.json
-rw-r----- 1 clickhouse clickhouse 28 4月  22 21:03 x.bin
-rw-r----- 1 clickhouse clickhouse 28 4月  22 21:03 y.bin
-rw-r----- 1 clickhouse clickhouse 28 4月  22 21:03 y.null.bin
```

## 2.2 分区和索引 
分区粒度根据业务特点决定，不宜过粗或过细。一般选择**按天分区**，也可以指定为 Tuple()， 以单表一亿数据为例，分区大小控制在 10-30 个为最佳。
 
必须指定索引列，ClickHouse 中的索引列即排序列，通过 order by 指定，一般在查询条件中经常被用来充当筛选条件的属性被纳入进来；可以是单一维度，也可以是组合维度的索引；通常需要满足高级列在前、查询频率大的在前原则；还有基数特别大的不适合做索引列， 

如用户表的 userid 字段；通常**筛选后的数据满足在百万以内为最佳**。

## 2.3 表参数 
Index_granularity 是用来控制索引粒度的，默认是 8192，如非必须不建议调整。 
如果表中不是必须保留全量历史数据，建议指定 TTL（生存时间值），可以免去手动过期历史数据的麻烦，TTL 也可以通过 alter table 语句随时修改。

## 2.4 写入和删除优化 
（1）尽量不要执行单条或小批量删除和插入操作，这样会产生小分区文件，给后台 Merge 任务带来巨大压力 
（2）不要一次写入太多分区，或数据写入太快，数据写入太快会导致 Merge 速度跟不上而报错，一般建议每秒钟发起 2-3 次写入操作，每次操作写入 2w~5w 条数据（依服务器性能而定）
写入过快报错，报错信息： 
```sql
1. Code: 252, e.displayText() = DB::Exception: Too many parts(304). 
Merges are processing significantly slower than inserts 
2. Code: 241, e.displayText() = DB::Exception: Memory limit (for query) 
exceeded:would use 9.37 GiB (attempt to allocate chunk of 301989888 
bytes), maximum: 9.31 GiB
```
处理方式： 
“ Too many parts 处理 ” ：使用 WAL 预写日志，提高写入性能。 
in_memory_parts_enable_wal 默认为 true 
在服务器内存充裕的情况下增加内存配额，一般通过 max_memory_usage 来实现 
在服务器内存不充裕的情况下，建议将超出部分内容分配到系统硬盘上，但会降低执行速度，一般通过 max_bytes_before_external_group_by、max_bytes_before_external_sort 参数来实现。 

## 2.5 常见配置 
配置项主要在 config.xml 或 users.xml 中， 基本上都在 users.xml 里 

- config.xml 的配置项 

https://clickhouse.tech/docs/en/operations/server-configuration-parameters/settings/ 

- users.xml 的配置项 

https://clickhouse.tech/docs/en/operations/settings/settings/ 

### 2.5.1 CPU 资源
| 配置  | 描述  |
| --- | --- |
| background_pool_size | 后台线程池的大小，merge 线程就是在该线程中执行，该线程池不仅仅是给 merge 线程用的，默认值 16，允许的前提下建议改成 cpu 个数的 2 倍（线程数）。  |
| background_schedule_pool_size | 执行后台任务（复制表、Kafka 流、DNS 缓存更新）的线程数。默认 128，建议改成 cpu 个数的 2 倍（线程数）。 |
| background_distributed_schedule_pool_size  | 设置为分布式发送执行后台任务的线程数，默认 16，建议改成 cpu个数的 2 倍（线程数）。  |
| max_concurrent_queries | 最大并发处理的请求数(包含 select,insert 等)，默认值 100，推荐 150(不够再加)~300。  |
| max_threads  | 设置单个查询所能使用的最大 cpu 个数，默认是 cpu 核数 |


### 2.5.2 内存资源 
| 配置  | 描述  |
| --- | --- |
| max_memory_usage | 此参数在 users.xml 中,表示单次 Query 占用内存最大值，该值可以设置的比较大，这样可以提升集群查询的上限。 
保留一点给 OS，比如 128G 内存的机器，设置为 100GB。 |
| max_bytes_before_external_group_by  | 一般按照 max_memory_usage 的一半设置内存，当 group 使用内存超过阈值后会刷新到磁盘进行。 
因为 clickhouse 聚合分两个阶段：查询并及建立中间数据、合并中间数据，结合上一项，建议 50GB。  |
| max_bytes_before_external_sort | 当 order by 已使用 max_bytes_before_external_sort 内存就进行溢写磁盘(基于磁盘排序)，如果不设置该值，那么当内存不够时直接抛错，设置了该值 order by 可以正常完成，但是速度相对存内存来 
说肯定要慢点(实测慢的非常多，无法接受)。  |
| max_table_size_to_drop | 此参数在 config.xml 中，应用于需要删除表或分区的情况，默认是50GB，意思是如果删除 50GB 以上的分区表会失败。建议修改为 0，这样不管多大的分区表都可以删除。 |


### 2.5.3 存储 
ClickHouse 不支持设置多数据目录，为了提升数据 io 性能，可以挂载虚拟券组，一个券组绑定多块物理磁盘提升读写性能，多数据查询场景 SSD 会比普通机械硬盘快 2-3 倍。


# 3. ClickHouse 语法优化规则 
ClickHouse 的 SQL 优化规则是基于 RBO(Rule Based Optimization)，下面是一些优化规则
 
## 3.1 COUNT 优化 
在调用 count 函数时，如果使用的是 count() 或者 count(*)，且没有 where 条件，则会直接使用 system.tables 的 total_rows，例如:
```sql
EXPLAIN SELECT count()FROM datasets.hits_v1;

Union
  Expression (Projection)
    Expression (Before ORDER BY and SELECT)
      MergingAggregated
        ReadNothing (Optimized trivial count)
```
注意 Optimized trivial count ，这是对 count 的优化。 
如果 count 具体的列字段，则不会使用此项优化： 
```sql
EXPLAIN SELECT count(CounterID) FROM datasets.hits_v1; 
  Union 
    Expression (Projection) 
      Expression (Before ORDER BY and SELECT) 
        Aggregating 
          Expression (Before GROUP BY) 
             ReadFromStorage (Read from MergeTree)
```

## 3.2 消除子查询重复字段 
下面语句子查询中有两个重复的 id 字段，会被去重: 
```sql
EXPLAIN SYNTAX SELECT 
  a.UserID, 
  b.VisitID, 
  a.URL, 
  b.UserID 
  FROM 
  hits_v1 AS a 
  LEFT JOIN ( 
    SELECT 
      UserID, 
      UserID as HaHa, 
      VisitID 
    FROM visits_v1) AS b 
    USING (UserID) 
    limit 3; 


//返回优化语句： 
SELECT 
  UserID, 
  VisitID, 
  URL, 
  b.UserID 
FROM hits_v1 AS a 
ALL LEFT JOIN 
(  
  SELECT 
    UserID, 
    VisitID 
  FROM visits_v1 
) AS b USING (UserID) 
LIMIT 3
```

## 3.3 谓词下推 
当 group by 有 having 子句，但是没有 with cube、with rollup 或者 with totals 修饰的时候，having 过滤会下推到 where 提前过滤。例如下面的查询，HAVING name 变成了 WHERE name，在 group by 之前过滤：
```sql
EXPLAIN SYNTAX SELECT UserID FROM hits_v1 GROUP BY UserID HAVING UserID = '8585742290196126178';

//返回优化语句
SELECT UserID
FROM hits_v1
WHERE UserID = \'8585742290196126178\'
GROUP BY UserID
```
  子查询也支持谓词下推：
```sql
EXPLAIN SYNTAX
SELECT *
FROM 
(
  SELECT UserID
  FROM visits_v1
)
WHERE UserID = '8585742290196126178'

//返回优化后的语句
SELECT UserID
FROM 
(
  SELECT UserID
  FROM visits_v1
  WHERE UserID = \'8585742290196126178\' 
)
WHERE UserID = \'8585742290196126178\'
```
   再来一个复杂例子：
```sql
EXPLAIN SYNTAX 
SELECT * FROM (
  SELECT 
      * 
  FROM 
  (
    SELECT 
      UserID 
    FROM visits_v1
  ) 
  UNION ALL 
  SELECT 
      *
  FROM
  (
    SELECT 
      UserID 
    FROM visits_v1
  )
)
  WHERE UserID = '8585742290196126178'

//返回优化后的语句
SELECT UserID
FROM 
(
  SELECT UserID
  FROM 
  (
      SELECT UserID
      FROM visits_v1
      WHERE UserID = \'8585742290196126178\' 
  )
  WHERE UserID = \'8585742290196126178\'
  UNION ALL
  SELECT UserID
  FROM 	
  (
    SELECT UserID
    FROM visits_v1
    WHERE UserID = \'8585742290196126178\' 
  )
  WHERE UserID = \'8585742290196126178\' 
)
WHERE UserID = \'8585742290196126178\'
```


## 3.4 聚合计算外推 
聚合函数内的计算，会外推，例如：
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650718114457-45d2a547-f970-4524-b3d5-ac1bb6752000.png#clientId=u8279787c-d242-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=327&id=uad21cf5e&margin=%5Bobject%20Object%5D&name=image.png&originHeight=327&originWidth=435&originalType=binary&ratio=1&rotation=0&showTitle=false&size=53889&status=done&style=none&taskId=ua339c514-5c07-4252-92ff-e1dd377f6e7&title=&width=435)

## 3.5 聚合函数消除 
如果对聚合键，也就是 group by key 使用 min、max、any 聚合函数，则将函数消除， 
例如：
```sql
EXPLAIN SYNTAX
SELECT
  sum(UserID * 2),
  max(VisitID),
  max(UserID)
FROM visits_v1
GROUP BY UserID

//返回优化后的语句
SELECT 
  sum(UserID) * 2,
  max(VisitID),
  UserID
FROM visits_v1
GROUP BY UserID
```

## 3.6 删除重复的 order by key 
例如下面的语句，重复的聚合键 id 字段会被去重:
```sql
EXPLAIN SYNTAX
SELECT *
FROM visits_v1
ORDER BY
  UserID ASC,
  UserID ASC,
  VisitID ASC,
  VisitID ASC

//返回优化后的语句：
select
……
FROM visits_v1
ORDER BY 
  UserID ASC,
  VisitID ASC
```

## 3.7 删除重复的 limit by key 
例如下面的语句，重复声明的 name 字段会被去重： 
```sql
EXPLAIN SYNTAX 
SELECT * 
FROM visits_v1 
LIMIT 3 BY 
  VisitID, 
  VisitID 
LIMIT 10 

//返回优化后的语句： 
select 
…… 
FROM visits_v1 
LIMIT 3 BY VisitID 
LIMIT 10
```

## 3.8 删除重复的 USING Key 
例如下面的语句，重复的关联键 id 字段会被去重： 
```sql
EXPLAIN SYNTAX
SELECT
  a.UserID,
  a.UserID,
  b.VisitID,
  a.URL,
  b.UserID
FROM hits_v1 AS a
LEFT JOIN visits_v1 AS b USING (UserID, UserID)

//返回优化后的语句：
SELECT 
  UserID,
  UserID,
  VisitID,
  URL,
  b.UserID
FROM hits_v1 AS a
ALL LEFT JOIN visits_v1 AS b USING (UserID)
```

## 3.9 标量替换 
如果子查询只返回一行数据，在被引用的时候用标量替换，例如下面语句中的 total_disk_usage 字段：
```sql
EXPLAIN SYNTAX
WITH 
  (
    SELECT sum(bytes)
    FROM system.parts
    WHERE active
  ) AS total_disk_usage
SELECT
  (sum(bytes) / total_disk_usage) * 100 AS table_disk_usage,
  table
FROM system.parts
GROUP BY table
ORDER BY table_disk_usage DESC
LIMIT 10; 

//返回优化后的语句：
WITH CAST(0, \'UInt64\') AS total_disk_usage
SELECT 
  (sum(bytes) / total_disk_usage) * 100 AS table_disk_usage,
  table
FROM system.parts
GROUP BY table
ORDER BY table_disk_usage DESC
LIMIT 10
```

## 3.10 三元运算优化 
如果开启了 optimize_if_chain_to_multiif 参数，三元运算符会被替换成 multiIf 函数， 
例如：
```sql
EXPLAIN SYNTAX 
SELECT number = 1 ? 'hello' : (number = 2 ? 'world' : 'mhk') 
FROM numbers(10) 
settings optimize_if_chain_to_multiif = 1; 

//返回优化后的语句：
SELECT multiIf(number = 1, \'hello\', number = 2, \'world\', \'mhk\')
FROM numbers(10)
SETTINGS optimize_if_chain_to_multiif = 1
```

# 4. 查询优化 
## 4.1 单表查询 
### 4.1.1 Prewhere 替代 where 
Prewhere 和 where 语句的作用相同，用来过滤数据。不同之处在于 prewhere 只支持 *MergeTree 族系列引擎的表，首先会读取指定的列数据，来判断数据过滤，等待数据过滤之后再读取 select 声明的列字段来补全其余属性。 

当查询列明显多于筛选列时使用 Prewhere 可十倍提升查询性能，Prewhere 会自动优化执行过滤阶段的数据读取方式，降低 io 操作。 

在某些场合下，prewhere 语句比 where 语句处理的数据量更少性能更高。
```sql
#关闭 where 自动转 prewhere(默认情况下， where 条件会自动优化成 prewhere)
set optimize_move_to_prewhere=0; 
# 使用 where
select WatchID, 
  JavaEnable, 
  Title, 
  GoodEvent, 
  EventTime, 
  EventDate, 
  CounterID, 
  ClientIP, 
  ClientIP6, 
  RegionID, 
  UserID, 
  CounterClass, 
  OS, 
  UserAgent, 
  URL, 
  Referer, 
  URLDomain, 
  RefererDomain, 
  Refresh, 
  IsRobot, 
  RefererCategories, 
  URLCategories, 
  URLRegions, 
  RefererRegions, 
  ResolutionWidth, 
  ResolutionHeight, 
  ResolutionDepth, 
  FlashMajor, 
  FlashMinor, 
  FlashMinor2
from datasets.hits_v1 where UserID='3198390223272470366';
# 使用 prewhere 关键字
select WatchID, 
  JavaEnable,
  Title, 
  GoodEvent, 
  EventTime, 
  EventDate, 
  CounterID, 
  ClientIP, 
  ClientIP6, 
  RegionID, 
  UserID, 
  CounterClass, 
  OS, 
  UserAgent, 
  URL, 
  Referer, 
  URLDomain, 
  RefererDomain, 
  Refresh, 
  IsRobot, 
  RefererCategories, 
  URLCategories, 
  URLRegions, 
  RefererRegions, 
  ResolutionWidth, 
  ResolutionHeight, 
  ResolutionDepth, 
  FlashMajor, 
  FlashMinor, 
  FlashMinor2
from datasets.hits_v1 prewhere UserID='3198390223272470366';
```
默认情况，我们肯定不会关闭 where 自动优化成 prewhere，但是某些场景即使开启优化，也不会自动转换成 prewhere，需要手动指定 prewhere： 

- 使用常量表达式 
- 使用默认值为 alias 类型的字段 
- 包含了 arrayJOIN，globalIn，globalNotIn 或者 indexHint 的查询 
- select 查询的列字段和 where 的谓词相同 
- 使用了主键字段 
### 4.1.2 数据采样 
通过采样运算可极大提升数据分析的性能 
```sql
SELECT Title,count(*) AS PageViews 
FROM hits_v1 
SAMPLE 0.1 #代表采样 10%的数据,也可以是具体的条数 
WHERE CounterID =57 
GROUP BY Title 
ORDER BY PageViews DESC LIMIT 1000 
```
采样修饰符只有在 MergeTree engine 表中才有效，且在创建表时需要指定采样策略。

### 4.1.3 列裁剪与分区裁剪 
数据量太大时应避免使用 select * 操作，查询的性能会与查询的字段大小和数量成线性 
表换，字段越少，消耗的 io 资源越少，性能就会越高。
```sql
反例：
select * from datasets.hits_v1;

正例：
select WatchID, 
  JavaEnable, 
  Title, 
  GoodEvent, 
  EventTime, 
  EventDate, 
  CounterID, 
  ClientIP, 
  ClientIP6, 
  RegionID, 
  UserID
from datasets.hits_v1;
```
  分区裁剪就是只读取需要的分区，在过滤条件中指定。 
```sql
select WatchID, 
  JavaEnable, 
  Title, 
  GoodEvent, 
  EventTime, 
  EventDate, 
  CounterID, 
  ClientIP, 
  ClientIP6, 
  RegionID, 
  UserID 
from datasets.hits_v1 
where EventDate='2014-03-23'; 
```

### 4.1.4 orderby 结合 where、limit 
千万以上数据集进行 order by 查询时需要搭配 where 条件和 limit 语句一起使用。
```sql
#正例：
SELECT UserID,Age
FROM hits_v1 
WHERE CounterID=57
ORDER BY Age DESC LIMIT 1000

#反例：
SELECT UserID,Age
FROM hits_v1 
ORDER BY Age DESC
```
  
### 4.1.5 避免构建虚拟列 
如非必须，不要在结果集上构建虚拟列，虚拟列非常消耗资源浪费性能，可以考虑在前端进行处理，或者在表中构造实际字段进行额外存储。 
```sql
反例：
SELECT Income,Age,Income/Age as IncRate FROM datasets.hits_v1;

正例：拿到 Income 和 Age 后，考虑在前端进行处理，或者在表中构造实际字段进行额外存储
SELECT Income,Age FROM datasets.hits_v1;
```

### 4.1.6 uniqCombined 替代 distinct 
性能可提升 10 倍以上，uniqCombined 底层采用类似 HyperLogLog 算法实现，能接收 2% 左右的数据误差，可直接使用这种去重方式提升查询性能。Count(distinct )会使用 uniqExact 精确去重。
 
不建议在千万级不同数据上执行 distinct 去重查询，改为近似去重 uniqCombined
```sql
反例：
select count(distinct rand()) from hits_v1;

正例：
SELECT uniqCombined(rand()) from datasets.hits_v1
```
 
### 4.1.7 其他注意事项 
**（1）查询熔断 **
为了避免因个别慢查询引起的服务雪崩的问题，除了可以为单个查询设置超时以外，还可以配置周期熔断，在一个查询周期内，如果用户频繁进行慢查询操作超出规定阈值后将无法继续进行查询操作。 

**（2）关闭虚拟内存 **
物理内存和虚拟内存的数据交换，会导致查询变慢，资源允许的情况下关闭虚拟内存。 

**（3）配置 join_use_nulls **
为每一个账户添加 join_use_nulls 配置，左表中的一条记录在右表中不存在，右表的相应字段会返回该字段相应数据类型的默认值，而不是标准 SQL 中的 Null 值。 

**（4）批量写入时先排序 **
批量写入数据时，必须控制每个批次的数据中涉及到的分区的数量，在写入之前最好对需要导入的数据进行排序。无序的数据或者涉及的分区太多，会导致 ClickHouse 无法及时对新导入的数据进行合并，从而影响查询性能。 

**（5）关注 CPU **
cpu 一般在 50%左右会出现查询波动，达到 70%会出现大范围的查询超时，cpu 是最关键的指标，要非常关注。

## 4.2 多表关联 
### 4.2.1 准备表和数据
```sql
#创建小表
CREATE TABLE visits_v2 
ENGINE = CollapsingMergeTree(Sign)
PARTITION BY toYYYYMM(StartDate)
ORDER BY (CounterID, StartDate, intHash32(UserID), VisitID)
SAMPLE BY intHash32(UserID)
SETTINGS index_granularity = 8192
as select * from visits_v1 limit 10000;

#创建 join 结果表：避免控制台疯狂打印数据
CREATE TABLE hits_v2 
ENGINE = MergeTree()
PARTITION BY toYYYYMM(EventDate)
ORDER BY (CounterID, EventDate, intHash32(UserID))
SAMPLE BY intHash32(UserID)
SETTINGS index_granularity = 8192
as select * from hits_v1 where 1=0;
```
 
### 4.2.2 用 IN 代替 JOIN 
当多表联查时，查询的数据仅从其中一张表出时，可考虑用 IN 操作而不是 JOIN
```sql
insert into hits_v2
select a.* from hits_v1 a where a.CounterID in (select CounterID from visits_v1);

#反例：使用 join
insert into table hits_v2
select a.* from hits_v1 a left join visits_v1 b on a.CounterID=b.CounterID;
```
 
### 4.2.3 大小表 JOIN 
多表 join 时要满足小表在右的原则，右表关联时被加载到内存中与左表进行比较， ClickHouse 中无论是 Left join 、Right join 还是 Inner join 永远都是拿着右表中的每一条记录到左表中查找该记录是否存在，所以右表必须是小表。
 
### 4.2.4 注意谓词下推（版本差异） 
ClickHouse 在 join 查询时不会主动发起谓词下推的操作，需要每个子查询提前完成过滤操作，需要注意的是，是否执行谓词下推，对性能影响差别很大（新版本中已经不存在此问题，但是需要注意谓词的位置的不同依然有性能的差异）
```sql
Explain syntax
select a.* from hits_v1 a left join visits_v2 b on a.CounterID=b.CounterID
having a.EventDate = '2014-03-17';

Explain syntax
select a.* from hits_v1 a left join visits_v2 b on a.CounterID=b.CounterID
having b.StartDate = '2014-03-17';

insert into hits_v2
select a.* from hits_v1 a left join visits_v2 b on a.CounterID=b.CounterID
where a.EventDate = '2014-03-17';

insert into hits_v2
select a.* from (
    select * from 
    hits_v1 
where EventDate = '2014-03-17'
) a left join visits_v2 b on a.CounterID=b.CounterID;
```

### 4.2.5 分布式表使用 GLOBAL 
两张分布式表上的 IN 和 JOIN 之前必须加上 GLOBAL 关键字，右表只会在接收查询请求的那个节点查询一次，并将其分发到其他节点上。如果不加 GLOBAL 关键字的话，每个节点都会单独发起一次对右表的查询，而右表又是分布式表，就导致右表一共会被查询 N²次（N是该分布式表的分片数量），这就是查询放大，会带来很大开销。 

### 4.2.6 使用字典表 
将一些需要关联分析的业务创建成字典表进行 join 操作，前提是字典表不宜太大，因为字典表会常驻内存 

### 4.2.7 提前过滤 
通过增加逻辑过滤可以减少数据扫描，达到提高执行速度及降低内存消耗的目的


ck的Join
1. 原理： 右表加载到内存，再去匹配
2. 为什么join不行？ 因为1
3. 非要使用join，怎么用比较好：
    能先过滤的过滤，特别是右表
    右边放小表
    特殊场景可以考虑使用字典表
    可以替换的话，尽量不要使用join，比如用 IN 实现
# 5. 数据一致性
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650722867114-c373e377-1355-4063-b0ef-141292fc4546.png#clientId=u8279787c-d242-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=224&id=ufa586daa&margin=%5Bobject%20Object%5D&name=image.png&originHeight=224&originWidth=777&originalType=binary&ratio=1&rotation=0&showTitle=false&size=104212&status=done&style=none&taskId=u594a5647-5eed-4b4b-bea5-b4906b27545&title=&width=777)
数据一致性：  replacingMergeTree 不能保证查询时没重复，只能保证最终一致性
解决方案：
    1. 手动执行： 生产环境不推荐
    2. 通过SQL实现去重： group by ==》高级一点的用法，加标记字段
    3. 使用final：
        20.5之前的版本，final是单线程
        20.5之后的版本，final可以是多线程，但是读取数据是串行的
    4. 重复一点无所谓： 100万日活，统计出来100万1千

# 6. 物化视图
ClickHouse 的物化视图是一种查询结果的持久化，它确实是给我们带来了查询效率的提升。用户查起来跟表没有区别，它就是一张表，它也像是一张时刻在预计算的表，创建的过程它是用了一个特殊引擎，加上后来 as select，就是 create 一个 table as select 的写法。 

“查询结果集”的范围很宽泛，可以是基础表中部分数据的一份简单拷贝，也可以是多表 join 之后产生的结果或其子集，或者原始数据的聚合指标等等。所以，物化视图不会随着基础表的变化而变化，所以它也称为快照（snapshot） 

## 6.1 概述 
### 6.1.1 物化视图与普通视图的区别 
**普通视图不保存数据，保存的仅仅是查询语句**，查询的时候还是从原表读取数据，可以将普通视图理解为是个子查询。**物化视图则是把查询的结果根据相应的引擎存入到了磁盘或内存中**，对数据重新进行了组织，你可以理解物化视图是完全的一张新表。

### 6.1.2 优缺点 
优点：查询速度**快**，要是把物化视图这些规则全部写好，它比原数据查询快了很多，总的行数少了，因为都预计算好了。 

缺点：它的本质是一个流式数据的使用场景，是累加式的技术，所以要用历史数据做去重、去核这样的分析，在物化视图里面是不太好用的。在某些场景的使用也是有限的。而且如果一张表加了好多物化视图，在写这张表的时候，就会消耗很多机器的资源，比如数据带宽占满、存储一下子增加了很多。

### 6.1.3 基本语法 
也是 create 语法，会创建一个隐藏的目标表来保存视图数据。也可以 TO 表名，保存到一张显式的表。没有加 TO 表名，表名默认就是 .inner.物化视图名 
```sql
CREATE [MATERIALIZED] VIEW [IF NOT EXISTS] [db.]table_name [TO[db.]name] 
[ENGINE = engine] [POPULATE] AS SELECT ... 
```
populate：不建议添加，加上这个参数在创建视图的时候会尝试将历史所有数据重新走一遍并呈下来
**1）创建物化视图的限制 **

1. 必须指定物化视图的 engine 用于数据存储 
1. TO [db].[table]语法的时候，不得使用 POPULATE。 
1. 查询语句(select）可以包含下面的子句： DISTINCT, GROUP BY, ORDER BY, LIMIT… 
1. 物化视图的 alter 操作有些限制，操作起来不大方便。 
1. 若物化视图的定义使用了 TO [db.]name 子语句，则可以将目标表的视图 卸载 DETACH 再装载 ATTACH 



**2）物化视图的数据更新 **
（1）物化视图创建好之后，若源表被写入新数据则物化视图也会同步更新 
（2）POPULATE 关键字决定了物化视图的更新策略： 

- 若有 POPULATE 则在创建视图的过程会将源表已经存在的数据一并导入，类似于 create table ... as 
- 若无 POPULATE 则物化视图在创建之后没有数据，只会在创建只有同步之后写入源表的数据 
- clickhouse 官方并不推荐使用 POPULATE，因为在创建物化视图的过程中同时写入 

的数据不能被插入物化视图。 
（3）物化视图不支持同步删除，若源表的数据不存在（删除了）则物化视图的数据仍然保留 
（4）物化视图是一种特殊的数据表，可以用 show tables 查看 
（5）物化视图数据的删除： 
（6）物化视图的删除：
