---
layout: post
title: "ClickHouse副本和分片集群"
author: Haokang Mu
excerpt: ClickHouse副本和分片集群.md
tags:
- ClickHouse

---

# 1. 副本
副本的目的主要是保障数据的高可用性，即使一台 ClickHouse 节点宕机，那么也可以从其他服务器获得相同的数据。 
[https://clickhouse.tech/docs/en/engines/table-engines/mergetree-family/replication/](https://clickhouse.tech/docs/en/engines/table-engines/mergetree-family/replication/)
## 1.1 副本写入流程
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650584988116-bf7b99ae-899a-47da-a7cc-18c16ee19f62.png#clientId=u7a1c0ee1-d60c-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=290&id=ub75bc128&margin=%5Bobject%20Object%5D&name=image.png&originHeight=290&originWidth=739&originalType=binary&ratio=1&rotation=0&showTitle=false&size=57571&status=done&style=none&taskId=u7fe0a75e-f1f5-45c3-9113-e3aa4f05202&title=&width=739)
## 1.2 配置步骤 
（1）启动 zookeeper 集群 
（2）在 hadoop102 的/etc/clickhouse-server/config.d 目录下创建一个名为 metrika.xml 的配置文件,内容如下： 
注：也可以不创建外部文件，直接在 config.xml 中指定<zookeeper>
```xml
<?xml version="1.0"?>
<yandex>
  <zookeeper-servers>
    <node index="1">
      <host>hadoop102</host>
      <port>2181</port>
    </node>
    <node index="2">
      <host>hadoop103</host>
      <port>2181</port>
    </node>
    <node index="3">
      <host>hadoop104</host>
      <port>2181</port>
    </node>
  </zookeeper-servers>
</yandex>
```

（3）同步到 hadoop103 和 hadoop104 上 
```xml
[root@hadoop102 clickhouse-server]# xsync config.d/
```

（4）在 hadoop102 的/etc/clickhouse-server/config.xml 中增加
```xml
<zookeeper incl="zookeeper-servers" optional="true" />
<include_from>/etc/clickhouse-server/config.d/metrika.xml</include_from>
```

（5）同步到 hadoop103 和 hadoop104 上
```xml
[root@hadoop102 clickhouse-server]# xsync config.xml 
```

分别在 hadoop102 和 hadoop103 上启动 ClickHouse 服务 
注意：因为修改了配置文件，如果以前启动了服务需要重启
```shell
 sudo clickhouse restart
```
注意：我们演示副本操作只需要在 hadoop102 和 hadoop103 两台服务器即可，上面的操作，我们 hadoop104 可以你不用同步，我们这里为了保证集群中资源的一致性，做了同步。 
（6）在 hadoop102 和 hadoop103 上分别建表 
副本只能同步数据，不能同步表结构，所以我们需要在每台机器上自己手动建表 
①hadoop102
```sql
create table t_order_rep2 (
  id UInt32,
  sku_id String,
  total_amount Decimal(16,2),
  create_time Datetime
) engine =ReplicatedMergeTree('/clickhouse/table/01/t_order_rep','rep_102')
partition by toYYYYMMDD(create_time)
primary key (id)
    order by (id,sku_id);
```

②hadoop103
```sql
create table t_order_rep2 (
    id UInt32,
    sku_id String,
    total_amount Decimal(16,2),
    create_time Datetime
) engine =ReplicatedMergeTree('/clickhouse/table/01/t_order_rep','rep_103')
    partition by toYYYYMMDD(create_time)
    primary key (id)
    order by (id,sku_id);
```
 
③参数解释 
ReplicatedMergeTree 中， 
**第一个参数**是分片的 zk_path 一般按照：/clickhouse/table/{shard}/{table_name} 的格式写，如果只有一个分片就写 01 即可。 
**第二个参数**是副本名称，相同的分片副本名称不能相同。 

（7）在 hadoop102 上执行 insert 语句
```sql
insert into t_order_rep2 values
(101,'sku_001',1000.00,'2020-06-01 12:00:00'),
(102,'sku_002',2000.00,'2020-06-01 12:00:00'),
(103,'sku_004',2500.00,'2020-06-01 12:00:00'),
(104,'sku_002',2000.00,'2020-06-01 12:00:00'),
(105,'sku_003',600.00,'2020-06-02 12:00:00');
```

（8）在 hadoop103 上执行 select，可以查询出结果，说明副本配置正确
```sql
hadoop103 :) select * from t_order_rep2;

SELECT *
FROM t_order_rep2

Query id: 4c800260-a5e1-40ff-b7b1-75a0eef9487b

┌──id─┬─sku_id──┬─total_amount─┬─────────create_time─┐
│ 105 │ sku_003 │       600.00 │ 2020-06-02 12:00:00 │
└─────┴─────────┴──────────────┴─────────────────────┘
┌──id─┬─sku_id──┬─total_amount─┬─────────create_time─┐
│ 101 │ sku_001 │      1000.00 │ 2020-06-01 12:00:00 │
│ 102 │ sku_002 │      2000.00 │ 2020-06-01 12:00:00 │
│ 103 │ sku_004 │      2500.00 │ 2020-06-01 12:00:00 │
│ 104 │ sku_002 │      2000.00 │ 2020-06-01 12:00:00 │
└─────┴─────────┴──────────────┴─────────────────────┘

5 rows in set. Elapsed: 0.007 sec. 
```

# 2. 分片集群   
副本虽然能够提高数据的可用性，降低丢失风险，但是每台服务器实际上必须容纳全量数据，对数据的横向扩容没有解决。 
要解决数据水平切分的问题，需要引入分片的概念。通过分片把一份完整的数据进行切分，不同的分片分布到不同的节点上，再通过 Distributed 表引擎把数据拼接起来一同使用。 
Distributed 表引擎本身不存储数据，有点类似于 MyCat 之于 MySql，成为一种中间件，通过分布式逻辑表来写入、分发、路由来操作多台节点不同分片的分布式数据。
注意：ClickHouse 的集群是表级别的，实际企业中，大部分做了高可用，但是没有用分片，避免降低查询性能以及操作集群的复杂性。
  
## 2.1 集群写入流程（3 分片 2 副本共 6 个节点）
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650586701399-bf474dfa-2d55-4c6a-b866-b1855df0a09f.png#clientId=u7a1c0ee1-d60c-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=434&id=u0f127260&margin=%5Bobject%20Object%5D&name=image.png&originHeight=434&originWidth=872&originalType=binary&ratio=1&rotation=0&showTitle=false&size=92434&status=done&style=none&taskId=u7dd33eb5-db5c-4a83-84b4-500414d0fc1&title=&width=872)

## 2.2 集群读取流程（3 分片 2 副本共 6 个节点）
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650586729181-7bd442d5-e64f-473a-b1dc-54a5c7e8d491.png#clientId=u7a1c0ee1-d60c-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=449&id=udf8baf32&margin=%5Bobject%20Object%5D&name=image.png&originHeight=449&originWidth=824&originalType=binary&ratio=1&rotation=0&showTitle=false&size=82292&status=done&style=none&taskId=ua7dc8487-6ff2-47a5-8323-03d9cdd8062&title=&width=824)

# 2.3 3 分片 2 副本共 6 个节点集群配置（供参考） 
配置的位置还是在之前的/etc/clickhouse-server/config.d/metrika.xml，内容如下
```xml
<yandex>
  <remote_servers>
    <gmall_cluster> <!-- 集群名称--> 
      <shard> <!--集群的第一个分片-->
        <internal_replication>true</internal_replication>
        <!--该分片的第一个副本-->
        <replica> 
          <host>hadoop101</host>
          <port>9000</port>
        </replica>
        <!--该分片的第二个副本-->
        <replica> 
          <host>hadoop102</host>
          <port>9000</port>
        </replica>
      </shard>
      <shard> <!--集群的第二个分片--> 
        <internal_replication>true</internal_replication>
        <replica> <!--该分片的第一个副本-->
          <host>hadoop103</host>
          <port>9000</port>
        </replica>
        <replica> <!--该分片的第二个副本-->
          <host>hadoop104</host>
          <port>9000</port>
        </replica>
      </shard>
      <shard> <!--集群的第三个分片-->
        <internal_replication>true</internal_replication>
        <replica> <!--该分片的第一个副本-->
          <host>hadoop105</host>
          <port>9000</port>
        </replica>
        <replica> <!--该分片的第二个副本-->
          <host>hadoop106</host>
          <port>9000</port>
        </replica>
      </shard>
    </gmall_cluster>
  </remote_servers>
</yandex>
```
