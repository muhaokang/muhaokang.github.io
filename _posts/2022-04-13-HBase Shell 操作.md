# 1. 基本操作

**1．进入 HBase 客户端命令行 **
```shell
[mhk@hadoop102 hbase-1.3.1]$ bin/hbase shell
```
**2．查看帮助命令 **
```shell
hbase(main):001:0> help
HBase Shell, version 1.3.1, r930b9a55528fe45d8edce7af42fef2d35e77677a, Thu Apr  6 19:36:54 PDT 2017
Type 'help "COMMAND"', (e.g. 'help "get"' -- the quotes are necessary) for help on a specific command.
Commands are grouped. Type 'help "COMMAND_GROUP"', (e.g. 'help "general"') for help on a command group.

COMMAND GROUPS:
  Group name: general
  Commands: status, table_help, version, whoami

  Group name: ddl
  Commands: alter, alter_async, alter_status, create, describe, disable, disable_all, drop, drop_all, enable, enable_all, exists, get_table, is_disabled, is_enabled, list, locate_region, show_filters

  Group name: namespace
  Commands: alter_namespace, create_namespace, describe_namespace, drop_namespace, list_namespace, list_namespace_tables

  Group name: dml
  Commands: append, count, delete, deleteall, get, get_counter, get_splits, incr, put, scan, truncate, truncate_preserve

  Group name: tools
  Commands: assign, balance_switch, balancer, balancer_enabled, catalogjanitor_enabled, catalogjanitor_run, catalogjanitor_switch, close_region, compact, compact_rs, flush, major_compact, merge_region, move, normalize, normalizer_enabled, normalizer_switch, split, splitormerge_enabled, splitormerge_switch, trace, unassign, wal_roll, zk_dump

  Group name: replication
  Commands: add_peer, append_peer_tableCFs, disable_peer, disable_table_replication, enable_peer, enable_table_replication, get_peer_config, list_peer_configs, list_peers, list_replicated_tables, remove_peer, remove_peer_tableCFs, set_peer_tableCFs, show_peer_tableCFs

  Group name: snapshots
  Commands: clone_snapshot, delete_all_snapshot, delete_snapshot, delete_table_snapshots, list_snapshots, list_table_snapshots, restore_snapshot, snapshot

  Group name: configuration
  Commands: update_all_config, update_config

  Group name: quotas
  Commands: list_quotas, set_quota

  Group name: security
  Commands: grant, list_security_capabilities, revoke, user_permission

  Group name: procedures
  Commands: abort_procedure, list_procedures

  Group name: visibility labels
  Commands: add_labels, clear_auths, get_auths, list_labels, set_auths, set_visibility

SHELL USAGE:
Quote all names in HBase Shell such as table and column names.  Commas delimit
command parameters.  Type <RETURN> after entering a command to run it.
Dictionaries of configuration used in the creation and alteration of tables are
Ruby Hashes. They look like this:

  {'key1' => 'value1', 'key2' => 'value2', ...}

and are opened and closed with curley-braces.  Key/values are delimited by the
'=>' character combination.  Usually keys are predefined constants such as
NAME, VERSIONS, COMPRESSION, etc.  Constants do not need to be quoted.  Type
'Object.constants' to see a (messy) list of all constants in the environment.

If you are using binary keys or values and need to enter them in the shell, use
double-quote'd hexadecimal representation. For example:

  hbase> get 't1', "key\x03\x3f\xcd"
  hbase> get 't1', "key\003\023\011"
  hbase> put 't1', "test\xef\xff", 'f1:', "\x01\x33\x40"

The HBase shell is the (J)Ruby IRB with the above HBase-specific commands added.
For more on the HBase Shell, see http://hbase.apache.org/book.html

```
**3．查看当前数据库中有哪些表 **
```shell
hbase(main):002:0> list
TABLE                                                                                                  
0 row(s) in 0.6870 seconds

=> []
```

# 2. 表的操作
**1．创建表 **
```shell
hbase(main):003:0> create 'student','info'
0 row(s) in 2.6380 seconds

=> Hbase::Table - student

hbase(main):005:0> create 'stu','info1','info2'
0 row(s) in 2.3180 seconds

=> Hbase::Table - stu

hbase(main):006:0> list
TABLE                                                                                                  
stu                                                                                                    
student                                                                                                
2 row(s) in 0.0240 seconds

=> ["stu", "student"]

hbase(main):011:0> create_namespace 'mhk'
0 row(s) in 1.2260 seconds

hbase(main):012:0> list_namespace
NAMESPACE                                                                                              
default                                                                                                
hbase                                                                                                  
mhk                                                                                                    
3 row(s) in 0.1410 seconds

hbase(main):013:0> create 'mhk:stu','info'
0 row(s) in 2.2640 seconds

=> Hbase::Table - mhk:stu
hbase(main):014:0> list
TABLE                                                                                                  
mhk:stu                                                                                                
stu                                                                                                    
student                                                                                                
3 row(s) in 0.0250 seconds

=> ["mhk:stu", "stu", "student"]

```
**2．插入数据到表 **
```shell
hbase(main):003:0> put 'student','1001','info:sex','male' 
hbase(main):004:0> put 'student','1001','info:age','18' 
hbase(main):005:0> put 'student','1002','info:name','Janna' 
hbase(main):006:0> put 'student','1002','info:sex','female' 
hbase(main):007:0> put 'student','1002','info:age','20' 
```
**3．扫描查看表数据 **
```shell
hbase(main):019:0> scan 'student'
ROW                        COLUMN+CELL                                                                 
 1001                      column=info:age, timestamp=1649732463800, value=18                          
 1001                      column=info:sex, timestamp=1649729775042, value=male                        
 1002                      column=info:age, timestamp=1649732716233, value=20                          
 1002                      column=info:name, timestamp=1649732473758, value=Janna                      
 1002                      column=info:sex, timestamp=1649732706857, value=female                      
2 row(s) in 0.1560 seconds

hbase(main):020:0> scan 'student',{STARTROW => '1001', STOPROW => '1001'}
ROW                        COLUMN+CELL                                                                 
 1001                      column=info:age, timestamp=1649732463800, value=18                          
 1001                      column=info:sex, timestamp=1649729775042, value=male                        
1 row(s) in 0.0550 seconds

左闭右开
hbase(main):008:0> scan 'student',{STARTROW => '1001',STOPROW =>'1002'}
ROW                        COLUMN+CELL                                                                 
 1001                      column=info:age, timestamp=1649738076812, value=18                          
 1001                      column=info:sex, timestamp=1649738063585, value=male                        
1 row(s) in 0.2100 seconds


hbase(main):021:0> scan 'student',{STARTROW => '1001'}
ROW                        COLUMN+CELL                                                                 
 1001                      column=info:age, timestamp=1649732463800, value=18                          
 1001                      column=info:sex, timestamp=1649729775042, value=male                        
 1002                      column=info:age, timestamp=1649732716233, value=20                          
 1002                      column=info:name, timestamp=1649732473758, value=Janna                      
 1002                      column=info:sex, timestamp=1649732706857, value=female                      
2 row(s) in 0.2290 seconds
```
**4．查看表结构 **
```shell
hbase(main):001:0> describe 'student'
Table student is ENABLED                                                                               
student                                                                                                
COLUMN FAMILIES DESCRIPTION                                                                            
{NAME => 'info', BLOOMFILTER => 'ROW', VERSIONS => '1', IN_MEMORY => 'false', KEEP_DELETED_CELLS => 'FA
LSE', DATA_BLOCK_ENCODING => 'NONE', TTL => 'FOREVER', COMPRESSION => 'NONE', MIN_VERSIONS => '0', BLOC
KCACHE => 'true', BLOCKSIZE => '65536', REPLICATION_SCOPE => '0'}                                      
1 row(s) in 1.0330 seconds
```
**5．更新指定字段的数据 **
```shell
hbase(main):022:0> put 'student','1001','info:name','Nick'
0 row(s) in 0.0470 seconds

hbase(main):023:0> put 'student','1001','info:age','100'
0 row(s) in 0.0330 seconds
```

**6．查看“指定行”或“指定列族:列”的数据 **
```shell
hbase(main):002:0> get 'student','1001'
COLUMN                     CELL                                                                        
 info:age                  timestamp=1649733079650, value=100                                          
 info:name                 timestamp=1649733071082, value=Nick                                         
 info:sex                  timestamp=1649729775042, value=male                                         
1 row(s) in 0.3120 seconds

hbase(main):003:0> get 'student','1001','info:name'
COLUMN                     CELL                                                                        
 info:name                 timestamp=1649733071082, value=Nick                                         
1 row(s) in 0.0660 seconds
```
**7．统计表数据行数 **
```shell
hbase(main):004:0> count 'student'
2 row(s) in 0.0860 seconds

=> 2
```
**8．删除数据 **
删除某 rowkey 的全部数据： 
```shell
 deleteall 'student','1001'
```
删除某 rowkey 的某一列数据：
```shell
hbase(main):006:0> delete 'student','1002','info:sex'
0 row(s) in 0.0570 seconds
```
**9．清空表数据 **
```shell
hbase(main):007:0> truncate 'student'
Truncating 'student' table (it may take a while):
 - Disabling table...
 - Truncating table...
0 row(s) in 4.7150 seconds
```
提示：清空表的操作顺序为先 disable，然后再 truncate。 

**10．删除表 **
首先需要先让该表为 disable 状态： 
```shell
hbase(main):008:0> disable 'student'
0 row(s) in 2.3030 seconds
```
然后才能 drop 这个表： 
```shell
hbase(main):009:0> drop 'student'
0 row(s) in 1.3620 seconds
```
提示：如果直接 drop 表，会报错：ERROR: Table student is enabled. Disable it first. 

**11．变更表信息 **
将 info 列族中的数据存放 3 个版本： 
```shell
hbase(main):001:0> describe 'student'
Table student is ENABLED                                                                               
student                                                                                                
COLUMN FAMILIES DESCRIPTION                                                                            
{NAME => 'info', BLOOMFILTER => 'ROW', VERSIONS => '1', IN_MEMORY => 'false', KEEP_DELETED_CELLS => 'FA
LSE', DATA_BLOCK_ENCODING => 'NONE', TTL => 'FOREVER', COMPRESSION => 'NONE', MIN_VERSIONS => '0', BLOC
KCACHE => 'true', BLOCKSIZE => '65536', REPLICATION_SCOPE => '0'}                                      
1 row(s) in 1.1010 seconds

hbase(main):002:0> alter 'student',{NAME=>'info',VERSIONS=>3}
Updating all regions with the new schema...
0/1 regions updated.
1/1 regions updated.
Done.
0 row(s) in 3.4050 seconds

hbase(main):003:0> describe 'student'
Table student is ENABLED                                                                               
student                                                                                                
COLUMN FAMILIES DESCRIPTION                                                                            
{NAME => 'info', BLOOMFILTER => 'ROW', VERSIONS => '3', IN_MEMORY => 'false', KEEP_DELETED_CELLS => 'FA
LSE', DATA_BLOCK_ENCODING => 'NONE', TTL => 'FOREVER', COMPRESSION => 'NONE', MIN_VERSIONS => '0', BLOC
KCACHE => 'true', BLOCKSIZE => '65536', REPLICATION_SCOPE => '0'}                                      
1 row(s) in 0.0530 seconds

hbase(main):004:0> get 'student','1001',{COLUMN=>'info:name',VERSIONS=>3}
COLUMN                     CELL                                                                        
0 row(s) in 0.3190 seconds
```

