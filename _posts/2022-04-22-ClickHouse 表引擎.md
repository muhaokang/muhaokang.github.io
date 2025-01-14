---
layout: post
title: "ClickHouse表引擎"
author: Haokang Mu
excerpt: ClickHouse表引擎.md
tags:
- ClickHouse

---

# 1. 表引擎的使用 
表引擎是 ClickHouse 的一大特色。可以说， 表引擎决定了如何存储表的数据。包括： 

- 数据的存储方式和位置，写到哪里以及从哪里读取数据。 
- 支持哪些查询以及如何支持。 
- 并发数据访问。 
- 索引的使用（如果存在）。 
- 是否可以执行多线程请求。 
- 数据复制参数。 

表引擎的使用方式就是必须显式在创建表时定义该表使用的引擎，以及引擎使用的相关参数。 
特别注意：引擎的名称大小写敏感

# 2. TinyLog 
以列文件的形式保存在磁盘上，不支持索引，没有并发控制。一般保存少量数据的小表， 
生产环境上作用有限。可以用于平时练习测试用。 
如： 
```sql
hadoop102 :) create table t_tinylog ( id String, name String) engine=TinyLog;

CREATE TABLE t_tinylog
(
    `id` String,
    `name` String
)
ENGINE = TinyLog

Query id: 1198d2f9-aa70-4661-a6ab-a648d467e049

Ok.

0 rows in set. Elapsed: 0.008 sec. 
```

# 3. Memory 
内存引擎，数据以未压缩的原始形式直接保存在内存当中，服务器重启数据就会消失。 
读写操作不会相互阻塞，不支持索引。简单查询下有非常非常高的性能表现（超过 10G/s）。
 
一般用到它的地方不多，除了用来测试，就是在需要非常高的性能，同时数据量又不太大（上限大概 1 亿行）的场景。
Version:0.9 StartHTML:0000000105 EndHTML:0000002532 StartFragment:0000000141 EndFragment:0000002492   
# 4. MergeTree 
ClickHouse 中最强大的表引擎当属 MergeTree（合并树）引擎及该系列（*MergeTree）中的其他引擎，支持索引和分区，地位可以相当于 innodb 之于 Mysql。而且基于 MergeTree，还衍生除了很多小弟，也是非常有特色的引擎。
**1）建表语句**
```sql
create table t_order_mt(
  id UInt32,
  sku_id String,
  total_amount Decimal(16,2),
  create_time Datetime
) engine =MergeTree
  partition by toYYYYMMDD(create_time)
  primary key (id)
  order by (id,sku_id);
```

**2）插入数据**
```sql
insert into t_order_mt values
(101,'sku_001',1000.00,'2020-06-01 12:00:00') ,
(102,'sku_002',2000.00,'2020-06-01 11:00:00'),
(102,'sku_004',2500.00,'2020-06-01 12:00:00'),
(102,'sku_002',2000.00,'2020-06-01 13:00:00'),
(102,'sku_002',12000.00,'2020-06-01 13:00:00'),
(102,'sku_002',600.00,'2020-06-02 12:00:00');
```

MergeTree 其实还有很多参数(绝大多数用默认值即可)，但是三个参数是更加重要的， 
也涉及了关于 MergeTree 的很多概念。
  
## 4.1 partition by 分区(可选) 
**1）作用**
学过 hive 的应该都不陌生，分区的目的主要是降低扫描的范围，优化查询速度 

**2）如果不填 **
只会使用一个分区。 

**3）分区目录 **
MergeTree 是以列文件+索引文件+表定义文件组成的，但是如果设定了分区那么这些文件就会保存到不同的分区目录中。 

**4）并行 **
分区后，面对涉及跨分区的查询统计，ClickHouse 会以分区为单位并行处理。 

**5）数据写入与分区合并 **
任何一个批次的数据写入都会产生一个临时分区，不会纳入任何一个已有的分区。写入后的某个时刻（大概 10-15 分钟后），ClickHouse 会自动执行合并操作（等不及也可以手动通过 optimize 执行），把临时分区的数据，合并到已有分区中。 
```sql
optimize table xxxx final; 
```

**6）例如 **
再次执行上面的插入操作
```sql
insert into t_order_mt values
(101,'sku_001',1000.00,'2020-06-01 12:00:00') ,
(102,'sku_002',2000.00,'2020-06-01 11:00:00'),
(102,'sku_004',2500.00,'2020-06-01 12:00:00'),
(102,'sku_002',2000.00,'2020-06-01 13:00:00'),
(102,'sku_002',12000.00,'2020-06-01 13:00:00'),
(102,'sku_002',600.00,'2020-06-02 12:00:00');
```
查看数据并没有纳入任何分区
```sql
hadoop102 :) select * from t_order_mt;

SELECT *
FROM t_order_mt

Query id: 05f4c4a0-fce7-4bd3-8d01-14c87ebf7d79

┌──id─┬─sku_id──┬─total_amount─┬─────────create_time─┐
│ 101 │ sku_001 │      1000.00 │ 2020-06-01 12:00:00 │
│ 102 │ sku_002 │      2000.00 │ 2020-06-01 11:00:00 │
│ 102 │ sku_002 │      2000.00 │ 2020-06-01 13:00:00 │
│ 102 │ sku_002 │     12000.00 │ 2020-06-01 13:00:00 │
│ 102 │ sku_004 │      2500.00 │ 2020-06-01 12:00:00 │
└─────┴─────────┴──────────────┴─────────────────────┘
┌──id─┬─sku_id──┬─total_amount─┬─────────create_time─┐
│ 101 │ sku_001 │      1000.00 │ 2020-06-01 12:00:00 │
│ 102 │ sku_002 │      2000.00 │ 2020-06-01 11:00:00 │
│ 102 │ sku_002 │      2000.00 │ 2020-06-01 13:00:00 │
│ 102 │ sku_002 │     12000.00 │ 2020-06-01 13:00:00 │
│ 102 │ sku_004 │      2500.00 │ 2020-06-01 12:00:00 │
└─────┴─────────┴──────────────┴─────────────────────┘
┌──id─┬─sku_id──┬─total_amount─┬─────────create_time─┐
│ 102 │ sku_002 │       600.00 │ 2020-06-02 12:00:00 │
└─────┴─────────┴──────────────┴─────────────────────┘
┌──id─┬─sku_id──┬─total_amount─┬─────────create_time─┐
│ 102 │ sku_002 │       600.00 │ 2020-06-02 12:00:00 │
└─────┴─────────┴──────────────┴─────────────────────┘
```

手动 optimize 之后
```sql
hadoop102 :) optimize table t_order_mt final;

OPTIMIZE TABLE t_order_mt FINAL

Query id: 5c63b117-9150-4245-9bf4-b047ff37e64d

Ok.

0 rows in set. Elapsed: 0.005 sec. 

hadoop102 :) select * from t_order_mt;

SELECT *
FROM t_order_mt

Query id: 5db17a7a-fd16-4ea4-9bce-1987adc0c020

┌──id─┬─sku_id──┬─total_amount─┬─────────create_time─┐
│ 102 │ sku_002 │       600.00 │ 2020-06-02 12:00:00 │
│ 102 │ sku_002 │       600.00 │ 2020-06-02 12:00:00 │
└─────┴─────────┴──────────────┴─────────────────────┘
┌──id─┬─sku_id──┬─total_amount─┬─────────create_time─┐
│ 101 │ sku_001 │      1000.00 │ 2020-06-01 12:00:00 │
│ 101 │ sku_001 │      1000.00 │ 2020-06-01 12:00:00 │
│ 102 │ sku_002 │      2000.00 │ 2020-06-01 11:00:00 │
│ 102 │ sku_002 │      2000.00 │ 2020-06-01 13:00:00 │
│ 102 │ sku_002 │     12000.00 │ 2020-06-01 13:00:00 │
│ 102 │ sku_002 │      2000.00 │ 2020-06-01 11:00:00 │
│ 102 │ sku_002 │      2000.00 │ 2020-06-01 13:00:00 │
│ 102 │ sku_002 │     12000.00 │ 2020-06-01 13:00:00 │
│ 102 │ sku_004 │      2500.00 │ 2020-06-01 12:00:00 │
│ 102 │ sku_004 │      2500.00 │ 2020-06-01 12:00:00 │
└─────┴─────────┴──────────────┴─────────────────────┘
```

## 4.2 primary key 主键(可选) 
ClickHouse 中的主键，和其他数据库不太一样，**它只提供了数据的一级索引，但是却不是唯一约束。**这就意味着是可以存在相同 primary key 的数据的。 

主键的设定主要依据是查询语句中的 where 条件。 

根据条件通过对主键进行某种形式的二分查找，能够定位到对应的 index granularity，避免了全表扫描。
 
index granularity： 直接翻译的话就是索引粒度，指在稀疏索引中两个相邻索引对应数据的间隔。ClickHouse 中的 MergeTree 默认是 8192。官方不建议修改这个值，除非该列存在大量重复值，比如在一个分区中几万行才有一个不同数据。 
**稀疏索引：**
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650536950294-b18ba132-2a34-436e-a9f3-5d2273058049.png#clientId=u01ebed79-edcc-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=414&id=u1f6c1fe6&margin=%5Bobject%20Object%5D&name=image.png&originHeight=414&originWidth=751&originalType=binary&ratio=1&rotation=0&showTitle=false&size=249522&status=done&style=none&taskId=u9c94c0c4-5bf8-405e-83b1-7d2e4cef002&title=&width=751)
稀疏索引的好处就是可以用很少的索引数据，定位更多的数据，代价就是只能定位到索引粒度的第一行，然后再进行进行一点扫描。

## 4.3 order by（必选） 
order by 设定了分区内的数据按照哪些字段顺序进行有序保存。 
order by 是 MergeTree 中唯一一个必填项，甚至比 primary key 还重要，因为当用户不设置主键的情况，很多处理会依照 order by 的字段进行处理（比如后面会讲的去重和汇总）。 
要求：主键必须是 order by 字段的前缀字段。 
比如 order by 字段是 (id,sku_id) 那么主键必须是 id 或者(id,sku_id)

## 4.4 二级索引 
目前在 ClickHouse 的官网上二级索引的功能在 v20.1.2.4 之前是被标注为实验性的，在这个版本之后默认是开启的。 

**1）老版本使用二级索引前需要增加设置 **
是否允许使用实验性的二级索引（v20.1.2.4 开始，这个参数已被删除，默认开启） 
```sql
set allow_experimental_data_skipping_indices=1;
```

**2）创建测试表**
```sql
create table t_order_mt2(
  id UInt32,
  sku_id String,
  total_amount Decimal(16,2),
  create_time Datetime,
  INDEX a total_amount TYPE minmax GRANULARITY 5
) engine =MergeTree
  partition by toYYYYMMDD(create_time)
  primary key (id)
  order by (id, sku_id);
```
其中 GRANULARITY N 是设定二级索引对于一级索引粒度的粒度。

**3）插入数据**
```sql
insert into t_order_mt2 values
(101,'sku_001',1000.00,'2020-06-01 12:00:00') ,
(102,'sku_002',2000.00,'2020-06-01 11:00:00'),
(102,'sku_004',2500.00,'2020-06-01 12:00:00'),
(102,'sku_002',2000.00,'2020-06-01 13:00:00'),
(102,'sku_002',12000.00,'2020-06-01 13:00:00'),
(102,'sku_002',600.00,'2020-06-02 12:00:00');
```

**4）对比效果 **
那么在使用下面语句进行测试，可以看出二级索引能够为非主键字段的查询发挥作用。
```sql
 [mhk@hadoop102 ~]$ clickhouse-client --send_logs_level=trace <<< 'select * from t_order_mt2 where total_amount > toDecimal32(900., 2)';
[hadoop102] 2022.04.21 11:02:48.734615 [ 3080 ] {a6707ccc-7da3-4b07-80a9-15d42c6db6f6} <Debug> executeQuery: (from [::1]:47482, using production parser) select * from t_order_mt2 where total_amount > toDecimal32(900., 2) 
[hadoop102] 2022.04.21 11:02:48.738641 [ 3080 ] {a6707ccc-7da3-4b07-80a9-15d42c6db6f6} <Debug> InterpreterSelectQuery: MergeTreeWhereOptimizer: condition "total_amount > toDecimal32(900., 2)" moved to PREWHERE
[hadoop102] 2022.04.21 11:02:48.739326 [ 3080 ] {a6707ccc-7da3-4b07-80a9-15d42c6db6f6} <Trace> ContextAccess (default): Access granted: SELECT(id, sku_id, total_amount, create_time) ON default.t_order_mt2
[hadoop102] 2022.04.21 11:02:48.739672 [ 3080 ] {a6707ccc-7da3-4b07-80a9-15d42c6db6f6} <Trace> InterpreterSelectQuery: FetchColumns -> Complete
[hadoop102] 2022.04.21 11:02:48.740449 [ 3080 ] {a6707ccc-7da3-4b07-80a9-15d42c6db6f6} <Debug> default.t_order_mt2 (d745abc9-fa2e-4e8d-9745-abc9fa2e8e8d) (SelectExecutor): Key condition: unknown
[hadoop102] 2022.04.21 11:02:48.740858 [ 3080 ] {a6707ccc-7da3-4b07-80a9-15d42c6db6f6} <Debug> default.t_order_mt2 (d745abc9-fa2e-4e8d-9745-abc9fa2e8e8d) (SelectExecutor): MinMax index condition: unknown
[hadoop102] 2022.04.21 11:02:48.743255 [ 3080 ] {a6707ccc-7da3-4b07-80a9-15d42c6db6f6} <Debug> default.t_order_mt2 (d745abc9-fa2e-4e8d-9745-abc9fa2e8e8d) (SelectExecutor): Index `a` has dropped 1/2 granules.
[hadoop102] 2022.04.21 11:02:48.743363 [ 3080 ] {a6707ccc-7da3-4b07-80a9-15d42c6db6f6} <Debug> default.t_order_mt2 (d745abc9-fa2e-4e8d-9745-abc9fa2e8e8d) (SelectExecutor): Selected 2/2 parts by partition key, 1 parts by primary key, 2/2 marks by primary key, 1 marks to read from 1 ranges
[hadoop102] 2022.04.21 11:02:48.743492 [ 3080 ] {a6707ccc-7da3-4b07-80a9-15d42c6db6f6} <Debug> MergeTreeSelectProcessor: Reading 1 ranges from part 20200601_1_1_0, approx. 5 rows starting from 0
101     sku_001 1000.00 2020-06-01 12:00:00
102     sku_002 2000.00 2020-06-01 11:00:00
102     sku_002 2000.00 2020-06-01 13:00:00
102     sku_002 12000.00        2020-06-01 13:00:00
102     sku_004 2500.00 2020-06-01 12:00:00
[hadoop102] 2022.04.21 11:02:48.750132 [ 3080 ] {a6707ccc-7da3-4b07-80a9-15d42c6db6f6} <Information> executeQuery: Read 5 rows, 160.00 B in 0.015278276 sec., 327 rows/sec., 10.23 KiB/sec.
[hadoop102] 2022.04.21 11:02:48.750215 [ 3080 ] {a6707ccc-7da3-4b07-80a9-15d42c6db6f6} <Debug> MemoryTracker: Peak memory usage (for query): 0.00 B.
```

## 4.5 数据 TTL 
TTL 即 Time To Live，MergeTree 提供了可以管理数据表或者列的生命周期的功能。 
**1）列级别 TTL **
（1）创建测试表
```sql
create table t_order_mt3(
  id UInt32,
  sku_id String,
  total_amount Decimal(16,2) TTL create_time+interval 10 SECOND,
  create_time Datetime 
) engine =MergeTree
  partition by toYYYYMMDD(create_time)
  primary key (id)
  order by (id, sku_id);	
```
  
（2）插入数据（注意：根据实际时间改变）
```sql
insert into t_order_mt3 values
(106,'sku_001',1000.00,'2022-04-21 18:53:30'),
(107,'sku_002',2000.00,'2022-04-21 18:53:31'),
(110,'sku_003',600.00,'2022-04-21 18:53:32');
```

（3）手动合并，查看效果 到期后，指定的字段数据归 0
如果不成功重启ClickHouse试试
```sql
hadoop102 :) select * from t_order_mt3;

SELECT *
FROM t_order_mt3

Query id: dd37debb-0ae6-4a21-9ee8-f92659f483d7

┌──id─┬─sku_id──┬─total_amount─┬─────────create_time─┐
│ 110 │ sku_003 │         0.00 │ 2020-06-13 12:00:00 │
└─────┴─────────┴──────────────┴─────────────────────┘
┌──id─┬─sku_id──┬─total_amount─┬─────────create_time─┐
│ 106 │ sku_001 │         0.00 │ 2020-06-12 22:52:30 │
│ 107 │ sku_002 │         0.00 │ 2020-06-12 22:52:30 │
└─────┴─────────┴──────────────┴─────────────────────┘
```

**2）表级 TTL **
下面的这条语句是数据会在 create_time 之后 10 秒丢失 
```sql
alter table t_order_mt3 MODIFY TTL create_time + INTERVAL 10 SECOND; 
```
```sql
hadoop102 :) select * from t_order_mt3;

SELECT *
FROM t_order_mt3

Query id: e775e83a-02a5-4f49-87ad-23999b19026f

ok.

0 rows in set. Elapsed: 0.004 sec.
```
涉及判断的字段必须是 Date 或者 Datetime 类型，推荐使用分区的日期字段。 
能够使用的时间周期： 

- SECOND 
- MINUTE 
- HOUR 
- DAY 
- WEEK 
- MONTH 
- QUARTER 
- YEAR

  
# 5. ReplacingMergeTree 
ReplacingMergeTree 是 MergeTree 的一个变种，它存储特性完全继承 MergeTree，只是多了一个去重的功能。 尽管 MergeTree 可以设置主键，但是 primary key 其实没有唯一约束的功能。如果你想处理掉重复的数据，可以借助这个 ReplacingMergeTree。 
**1）去重时机 **
数据的去重只会在合并的过程中出现。合并会在未知的时间在后台进行，所以你无法预先作出计划。有一些数据可能仍未被处理。

**2）去重范围 **
如果表经过了分区，去重只会在分区内部进行去重，不能执行跨分区的去重。 
所以 ReplacingMergeTree 能力有限， ReplacingMergeTree 适用于在后台清除重复的数据以节省空间，但是它不保证没有重复的数据出现。

**3）案例演示 **
（1）创建表
```sql
create table t_order_rmt(
  id UInt32,
  sku_id String,
  total_amount Decimal(16,2) ,
  create_time Datetime 
) engine =ReplacingMergeTree(create_time)
  partition by toYYYYMMDD(create_time)
  primary key (id)
  order by (id, sku_id);
```
 ReplacingMergeTree() 填入的参数为版本字段，重复数据保留版本字段值最大的。 
如果不填版本字段，默认按照插入顺序保留最后一条。

（2）向表中插入数据
```sql
insert into t_order_rmt values
(101,'sku_001',1000.00,'2020-06-01 12:00:00') ,
(102,'sku_002',2000.00,'2020-06-01 11:00:00'),
(102,'sku_004',2500.00,'2020-06-01 12:00:00'),
(102,'sku_002',2000.00,'2020-06-01 13:00:00'),
(102,'sku_002',12000.00,'2020-06-01 13:00:00'),
(102,'sku_002',600.00,'2020-06-02 12:00:00');
```
   
（3）执行第一次查询
```sql
hadoop102 :) select * from t_order_rmt;

SELECT *
FROM t_order_rmt

Query id: e88b72cc-a3b7-44c3-a105-390068c2cf04

┌──id─┬─sku_id──┬─total_amount─┬─────────create_time─┐
│ 102 │ sku_002 │       600.00 │ 2020-06-02 12:00:00 │
└─────┴─────────┴──────────────┴─────────────────────┘
┌──id─┬─sku_id──┬─total_amount─┬─────────create_time─┐
│ 101 │ sku_001 │      1000.00 │ 2020-06-01 12:00:00 │
│ 102 │ sku_002 │      2000.00 │ 2020-06-01 11:00:00 │
│ 102 │ sku_002 │      2000.00 │ 2020-06-01 13:00:00 │
│ 102 │ sku_002 │     12000.00 │ 2020-06-01 13:00:00 │
│ 102 │ sku_004 │      2500.00 │ 2020-06-01 12:00:00 │
└─────┴─────────┴──────────────┴─────────────────────┘
```

（4）手动合并
```sql
hadoop102 :) OPTIMIZE TABLE t_order_rmt FINAL;

OPTIMIZE TABLE t_order_rmt FINAL

Query id: cc6fe5c5-93b9-4899-af8a-c2ff2afc6a91

Ok.

0 rows in set. Elapsed: 0.005 sec. 
```

（5）再执行一次查询
```sql

hadoop102 :) select * from t_order_rmt;

SELECT *
FROM t_order_rmt

Query id: 392da567-ad3b-43ab-8fa9-de976f59d10c

┌──id─┬─sku_id──┬─total_amount─┬─────────create_time─┐
│ 102 │ sku_002 │       600.00 │ 2020-06-02 12:00:00 │
└─────┴─────────┴──────────────┴─────────────────────┘
┌──id─┬─sku_id──┬─total_amount─┬─────────create_time─┐
│ 101 │ sku_001 │      1000.00 │ 2020-06-01 12:00:00 │
│ 102 │ sku_002 │     12000.00 │ 2020-06-01 13:00:00 │
│ 102 │ sku_004 │      2500.00 │ 2020-06-01 12:00:00 │
└─────┴─────────┴──────────────┴─────────────────────┘
```
   
**4）通过测试得到结论 ** 

- 实际上是使用 order by 字段作为唯一键 
- 去重不能跨分区 
- 只有同一批插入（新版本）或合并分区时才会进行去重 
- 认定重复的数据保留，版本字段值最大的 
- 如果版本字段相同则按插入顺序保留最后一笔

# 6. SummingMergeTree 
对于不查询明细，只关心以维度进行汇总聚合结果的场景。如果只使用普通的MergeTree的话，无论是存储空间的开销，还是查询时临时聚合的开销都比较大。 
ClickHouse 为了这种场景，提供了一种能够“预聚合”的引擎 SummingMergeTree 
**1）案例演示 **
（1）创建表
```sql
create table t_order_smt(
  id UInt32,
  sku_id String,
  total_amount Decimal(16,2) ,
  create_time Datetime 
) engine =SummingMergeTree(total_amount)
  partition by toYYYYMMDD(create_time)
  primary key (id)
  order by (id,sku_id );
```

（2）插入数据
```sql
insert into t_order_smt values
(101,'sku_001',1000.00,'2020-06-01 12:00:00'),
(102,'sku_002',2000.00,'2020-06-01 11:00:00'),
(102,'sku_004',2500.00,'2020-06-01 12:00:00'),
(102,'sku_002',2000.00,'2020-06-01 13:00:00'),
(102,'sku_002',12000.00,'2020-06-01 13:00:00'),
(102,'sku_002',600.00,'2020-06-02 12:00:00');
```
  
（3）执行第一次查询
```sql
hadoop102 :) select * from t_order_smt;

SELECT *
FROM t_order_smt

Query id: a3c82de5-cc78-4bf8-aaed-96411d8caa0f

┌──id─┬─sku_id──┬─total_amount─┬─────────create_time─┐
│ 102 │ sku_002 │       600.00 │ 2020-06-02 12:00:00 │
└─────┴─────────┴──────────────┴─────────────────────┘
┌──id─┬─sku_id──┬─total_amount─┬─────────create_time─┐
│ 101 │ sku_001 │      1000.00 │ 2020-06-01 12:00:00 │
│ 102 │ sku_002 │      2000.00 │ 2020-06-01 11:00:00 │
│ 102 │ sku_002 │      2000.00 │ 2020-06-01 13:00:00 │
│ 102 │ sku_002 │     12000.00 │ 2020-06-01 13:00:00 │
│ 102 │ sku_004 │      2500.00 │ 2020-06-01 12:00:00 │
└─────┴─────────┴──────────────┴─────────────────────┘
```

（4）手动合并
```sql
hadoop102 :) OPTIMIZE TABLE t_order_smt FINAL;
```

（5）再执行一次查询
```sql
hadoop102 :) select * from t_order_smt;

SELECT *
FROM t_order_smt

Query id: a3c82de5-cc78-4bf8-aaed-96411d8caa0f

┌──id─┬─sku_id──┬─total_amount─┬─────────create_time─┐
│ 102 │ sku_002 │       600.00 │ 2020-06-02 12:00:00 │
└─────┴─────────┴──────────────┴─────────────────────┘
┌──id─┬─sku_id──┬─total_amount─┬─────────create_time─┐
│ 101 │ sku_001 │      1000.00 │ 2020-06-01 12:00:00 │
│ 102 │ sku_002 │     16000.00 │ 2020-06-01 11:00:00 │
│ 102 │ sku_004 │      2500.00 │ 2020-06-01 12:00:00 │
└─────┴─────────┴──────────────┴─────────────────────┘
```
 
**2）通过结果可以得到以下结论 **

- 以 SummingMergeTree（）中指定的列作为汇总数据列 
- 可以填写多列必须数字列，如果不填，以所有非维度列且为数字列的字段为汇总数据列 
- 以 order by 的列为准，作为维度列 
- 其他的列按插入顺序保留第一行 
- 不在一个分区的数据不会被聚合 
- 只有在同一批次插入(新版本)或分片合并时才会进行聚合 



**3）开发建议 **
设计聚合表的话，唯一键值、流水号可以去掉，所有字段全部是维度、度量或者时间戳。 

**4）问题 **
能不能直接执行以下 SQL 得到汇总值
```sql
select total_amount from XXX where province_name=’’ and create_date=’xxx’ 
```
不行，可能会包含一些还没来得及聚合的临时明细 

如果要是获取汇总值，还是需要使用 sum 进行聚合，这样效率会有一定的提高，但本身 ClickHouse 是列式存储的，效率提升有限，不会特别明显。 
```sql
select sum(total_amount) from province_name=’’ and create_date=‘xxx’
```

