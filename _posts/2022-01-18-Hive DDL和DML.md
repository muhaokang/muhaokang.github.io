- 数据操纵语言 DML：包括插入、更新、删除；
- 数据定义语言 DDL：包括创建数据库中的对象——表、视图、索引等；
# 1. DDL 数据定义
## 1.1 创建数据库
```sql
CREATE DATABASE [IF NOT EXISTS] database_name 
[COMMENT database_comment]
[LOCATION hdfs_path]
[WITH DBPROPERTIES (property_name=property_value, ...)];
```

- IF NOT EXISTS 最好加上，防止冲突；
- LOCATION hdfs_path 加载 hdfs 上的数据；
- WITH DBPROPERTIES 可以设置属性和值，会存储在 Mysql 中的元数据库中。

#### 1）创建一个数据库，数据库在 HDFS 上的默认存储路径是/user/hive/warehouse/*.db
```sql
hive (default)> create database hive;
```
#### 2）避免要创建的数据库已经存在错误，增加 if not exists 判断。（标准写法）
```sql
hive (default)> create database hive;
FAILED: Execution Error, return code 1 from 
org.apache.hadoop.hive.ql.exec.DDLTask. Database db_hive already exists 

hive (default)> create database if not exists hive;
```
#### 3）创建一个数据库，指定数据库在 HDFS 上存放的位置
```sql
hive (default)> create database hive2 location '/hive2.db'; 
```
## 
## 1.2 查询数据库
### 1.2.1 显示数据库
#### 1）显示数据库
```sql
hive (default)> show databases;
OK
database_name
default
hive
hive1
hive2
Time taken: 0.108 seconds, Fetched: 4 row(s)
```
#### 2）过滤显示查询的数据库
```sql
hive (hive2)> show databases like 'hi*';
OK
database_name
hive
hive1
hive2
Time taken: 0.047 seconds, Fetched: 3 row(s)
```
### 1.2.2 查看数据库详情
#### 1）显示数据库信息
```sql
hive (hive)> desc database hive;
OK
db_name comment location        owner_name      owner_type      parameters
hive            hdfs://hadoop102:9820/user/hive/warehouse/hive.db       mhk     USER
```
#### 2）显示数据库详细信息，extended
```sql
hive (hive)> desc database extended hive;
OK
db_name comment location        owner_name      owner_type      parameters
hive            hdfs://hadoop102:9820/user/hive/warehouse/hive.db       mhk     USER    {createTime=2022-01-17}
```
### 1.2.3 切换当前数据库
```sql
hive (default)> use hive;
OK
Time taken: 0.048 seconds
hive (hive)> 
```
## 
## 1.3 修改数据库
用户可以使用 ALTER DATABASE 命令为某个数据库的 DBPROPERTIES 设置键-值对属性值，来描述这个数据库的属性信息。
```sql
hive (hive2)> desc database extended hive2;
OK
db_name comment location        owner_name      owner_type      parameters
hive2           hdfs://hadoop102:9820/hive2.db  mhk     USER
Time taken: 0.071 seconds, Fetched: 1 row(s)

hive (hive2)> alter database hive2
            > set dbproperties('createtime'='2022-01-18');
OK
Time taken: 0.145 seconds

hive (hive2)> desc database extended hive2;
OK
db_name comment location        owner_name      owner_type      parameters
hive2           hdfs://hadoop102:9820/hive2.db  mhk     USER    {createtime=2022-01-18}
Time taken: 0.083 seconds, Fetched: 1 row(s)
```
## 1.4 删除数据库
#### **1）删除空数据库**
```sql
hive (hive2)> drop database hive3;
OK
```
#### **2）如果删除的数据库不存在，最好采用 if exists 判断数据库是否存在**
```sql
hive (hive2)> drop database hive3;
FAILED: SemanticException [Error 10072]: Database does not exist: hive3
hive (hive2)> drop database if exists hive3;
OK
```
#### 3）如果数据库不为空，可以采用 cascade 命令，强制删除
```sql
hive (hive2)> drop database hive2;
FAILED: Execution Error, return code 1 from org.apache.hadoop.hive.ql.exec.DDLTask. InvalidOperationException(message:Database hive2 is not empty. One or more tables exist.)
hive (hive2)> drop database hive2 cascade;
OK
```
## 1.5 创建表
#### 1）建表语法
```sql
CREATE [EXTERNAL] TABLE [IF NOT EXISTS] table_name
[(col_name data_type [COMMENT col_comment], ...)] 
[COMMENT table_comment]
[PARTITIONED BY (col_name data_type [COMMENT col_comment], ...)] 
[CLUSTERED BY (col_name, col_name, ...)
[SORTED BY (col_name [ASC|DESC], ...)] INTO num_buckets BUCKETS] 
[ROW FORMAT row_format]
[STORED AS file_format] 
[LOCATION hdfs_path]
[TBLPROPERTIES (property_name=property_value, ...)] 
[AS select_statement]
```
#### 2）字段解释说明
（1）CREATE TABLE  创建一个指定名字的表。如果相同名字的表已经存在，则抛出异常；用户可以用 IF NOT EXISTS  选项来忽略这个异常。
（2）EXTERNAL 关键字可以让用户创建一个外部表，在建表的同时可以指定一个指向实际数据的路径（LOCATION），在删除表的时候，内部表的元数据和数据会被一起删除，而外部表只删除元数据，不删除数据。
（3）COMMENT：为表和列添加注释。
（4）PARTITIONED BY 创建分区表
（5）CLUSTERED BY 创建分桶表
（6）SORTED BY 不常用，对桶中的一个或多个列另外排序
（7）ROW FORMAT DELIMITED [FIELDS TERMINATED BY char] [COLLECTION ITEMS TERMINATED BY char] [MAP KEYS TERMINATED BY char] [LINES TERMINATED BY char]
|   SERDE   serde_name   [WITH   SERDEPROPERTIES   (property_name=property_value, property_name=property_value, ...)]
用户在建表的时候可以自定义 SerDe  或者使用自带的 SerDe。如果没有指定 ROW FORMAT 或者 ROW FORMAT DELIMITED，将会使用自带的 SerDe。在建表的时候，用户还需 要为表指定列，用户在指定表的列的同时也会指定自定义的 SerDe，Hive 通过 SerDe 确定表的具体的列的数据。
SerDe 是 Serialize/Deserilize 的简称，hive 使用 Serde 进行行对象的序列与反序列化。
（8）STORED AS 指定存储文件类型 常用的存储文件类型：SEQUENCEFILE（二进制序列文件）、TEXTFILE（文本）、RCFILE（列
式存储格式文件）
如果文件数据是纯文本，可以使用 STORED AS TEXTFILE。如果数据需要压缩，使用 STORED AS SEQUENCEFILE。
（9）LOCATION  ：指定表在 HDFS 上的存储位置。
（10）AS：后跟查询语句，根据查询结果创建表。
（11）LIKE 允许用户复制现有的表结构，但是不复制数据。

### 1.5.1 管理表（内部表）
#### **1）理论**
默认创建的表都是所谓的管理表，有时也被称为内部表。因为这种表，Hive 会（或多或少地）控制着数据的生命周期。 Hive  默认情况下会将这些表的数据存储在由配置项hive.metastore.warehouse.dir(例如，/user/hive/warehouse)所定义的目录的子目录下。 
当我们删除一个管理表时，Hive 也会删除这个表中数据。管理表不适合和其他工具共享
数据。
#### 2）案例实操
（0）原始数据
```sql
1001	mhk
1002	jooye
1003	taylor
1004	jisoo
```
（1）普通创建表并导入数据
```sql
hive (default)> create table student1(id string, name string) 
              > row format delimited fields terminated by '\t'
              > stored as textfile
              > location '/user/hive/warehouse/student';
OK

hive (default)> load data local inpath '/opt/module/hive/student.txt' into table default.student1;
Loading data to table default.student1
OK
```
（2）根据查询结果创建表（查询的结果会添加到新创建的表中）
```sql
hive (default)> create table if not exists student5 as select id, name from student1;
OK
Time taken: 0.078 seconds
hive (default)> select * from student5;
OK
student5.id     student5.name
1001    mhk
1002    jooye
1003    taylor
1004    jisoo


hive (default)> load data local inpath '/opt/module/hive/student.txt' into table default.student1;
Loading data to table default.student1
OK
```
（3）根据已经存在的表结构创建表
```sql
hive (default)> create table if not exists student6 like student1;
OK
Time taken: 0.19 seconds
hive (default)> select * from student6;
OK
student6.id     student6.name
Time taken: 0.275 seconds
```
（4）查询表的类型
```sql
hive (default)> desc formatted student1;
OK
col_name        data_type       comment
# col_name              data_type               comment             
id                      string                                      
name                    string                                      
                 
# Detailed Table Information             
Database:               default                  
OwnerType:              USER                     
Owner:                  mhk                      
CreateTime:             Tue Jan 18 18:26:35 CST 2022     
LastAccessTime:         UNKNOWN                  
Retention:              0                        
Location:               hdfs://hadoop102:9820/user/hive/warehouse/student1       
Table Type:             MANAGED_TABLE            
Table Parameters:                
        bucketing_version       2                   
        numFiles                1                   
        numRows                 0                   
        rawDataSize             0                   
        totalSize               43                  
        transient_lastDdlTime   1642501720          
                 
# Storage Information            
SerDe Library:          org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe       
InputFormat:            org.apache.hadoop.mapred.TextInputFormat         
OutputFormat:           org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat       
Compressed:             No                       
Num Buckets:            -1                       
Bucket Columns:         []                       
Sort Columns:           []                       
Storage Desc Params:             
        field.delim             \t                  
        serialization.format    \t             
```
### 1.5.2 外部表
#### **1）理论**
因为表是外部表，所以 Hive 并非认为其完全拥有这份数据。删除该表并不会删除掉这份数据，不过描述表的元数据信息会被删除掉。
#### **2）管理表和外部表的使用场景**
每天将收集到的网站日志定期流入 HDFS 文本文件。在外部表（原始日志表）的基础上做大量的统计分析，用到的中间表、结果表使用内部表存储，数据通过 SELECT+INSERT 进入内部表。
#### **3）案例实操**
（0）原始数据
```sql
1001	mhk
1002	jooye
1003	taylor
1004	jisoo
```
（1）创建外部表并导入数据
```sql
hive (hive2)> create external table student(id string, name string) row format delimited fields terminated by '\t';
OK

hive (hive2)> load data local inpath '/opt/module/hive/student.txt' into table hive2.student;
Loading data to table hive2.student
OK
```
（2）查看创建的表
```sql
hive (hive2)> show tables;
OK
tab_name
student
```
（3）查看表格式化数据
```sql
hive (hive2)> desc formatted student;
OK
col_name        data_type       comment
# col_name              data_type               comment             
id                      string                                      
name                    string                                      
                 
# Detailed Table Information             
Database:               hive2                    
OwnerType:              USER                     
Owner:                  mhk                      
CreateTime:             Tue Jan 18 18:59:17 CST 2022     
LastAccessTime:         UNKNOWN                  
Retention:              0                        
Location:               hdfs://hadoop102:9820/user/hive/warehouse/hive2.db/student       
Table Type:             EXTERNAL_TABLE           
...
```
（5）删除外部表
```sql
hive (hive2)> drop table student;
OK

hive (hive2)> show tables;
OK
tab_name
```
外部表删除后，hdfs 中的数据还在，但是 metadata 中 student 的元数据已被删除
![截屏2022-01-18 下午7.14.22.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1642504490034-5a2527d0-baa2-4f9a-9b5f-85eca89afdd5.png#clientId=u8d1a1448-1844-4&crop=0&crop=0&crop=1&crop=1&from=ui&id=ubbd63619&margin=%5Bobject%20Object%5D&name=%E6%88%AA%E5%B1%8F2022-01-18%20%E4%B8%8B%E5%8D%887.14.22.png&originHeight=343&originWidth=1174&originalType=binary&ratio=1&rotation=0&showTitle=false&size=50133&status=done&style=none&taskId=uc97c36e6-d3af-4a37-918d-3ed008704f8&title=)
但当再次创建student表时（必须和被删除的表名一致），hive还会访问到数据
```sql
hive (hive2)> create external table student(id string, name string) row format delimited fields terminated by '\t';
OK
Time taken: 0.13 seconds
hive (hive2)> select * from student;
OK
student.id      student.name
1001    mhk
1002    jooye
1003    taylor
1004    jisoo
```
### **1.5.3 管理表与外部表的互相转换**
（1）查询表的类型
```sql
hive (hive)> desc formatted student1;
OK
col_name        data_type       comment
# col_name              data_type               comment             
id                      string                                      
name                    string                                      
                 
# Detailed Table Information             
Database:               hive                     
OwnerType:              USER                     
Owner:                  mhk                      
CreateTime:             Tue Jan 18 15:38:01 CST 2022     
LastAccessTime:         UNKNOWN                  
Retention:              0                        
Location:               hdfs://hadoop102:9820/user/hive/warehouse/hive.db/student1       
Table Type:             MANAGED_TABLE 
```
（2）修改内部表 student1为外部表
```sql
hive (hive)> alter table student1 set tblproperties('EXTERNAL'='TRUE'); 
OK
```
（3）查询表的类型
```sql
hive (hive)> desc formatted student1;
OK
col_name        data_type       comment
# col_name              data_type               comment             
id                      string                                      
name                    string                                      
                 
# Detailed Table Information             
Database:               hive                     
OwnerType:              USER                     
Owner:                  mhk                      
CreateTime:             Tue Jan 18 15:38:01 CST 2022     
LastAccessTime:         UNKNOWN                  
Retention:              0                        
Location:               hdfs://hadoop102:9820/user/hive/warehouse/hive.db/student1       
Table Type:             EXTERNAL_TABLE    
```
（4）修改外部表 student1为内部表
```sql
hive (hive)> alter table student1 set tblproperties('EXTERNAL'='FALSE'); 
OK
```
（5）查询表的类型
```sql
hive (hive)> desc formatted student1;
OK
col_name        data_type       comment
# col_name              data_type               comment             
id                      string                                      
name                    string                                      
                 
# Detailed Table Information             
Database:               hive                     
OwnerType:              USER                     
Owner:                  mhk                      
CreateTime:             Tue Jan 18 15:38:01 CST 2022     
LastAccessTime:         UNKNOWN                  
Retention:              0                        
Location:               hdfs://hadoop102:9820/user/hive/warehouse/hive.db/student1       
Table Type:             MANAGED_TABLE  
```
## 
## 1.6 修改表
### 1.6.1 **重命名表**
#### 1）语法
```sql
ALTER TABLE table_name RENAME TO new_table_name
```
#### 2）实操案例
```sql
hive (hive)> show tables;
OK
tab_name
student
student1
Time taken: 0.075 seconds, Fetched: 2 row(s)
hive (hive)> alter table student rename to student2;
OK
Time taken: 0.538 seconds
hive (hive)> show tables;
OK
tab_name
student1
student2
```

### 1.6.2 增加/修改/替换列信息
#### **1）语法**
（1）更新列
```sql
ALTER TABLE table_name CHANGE [COLUMN] col_old_name col_new_name column_type [COMMENT col_comment] [FIRST|AFTER column_name]      
```
（2）增加和替换列
```sql
ALTER TABLE table_name ADD|REPLACE COLUMNS (col_name data_type [COMMENT col_comment], ...)
```
注：ADD 是代表新增一字段，字段位置在所有列后面(partition 列前)，
REPLACE 则是表示替换表中所有字段。
#### **2）实操案例**
（1）查询表结构
```sql
hive (hive)> desc student1;
OK
col_name        data_type       comment
id                      string                                      
name                    string         
```
（2）添加列
```sql
hive (hive)> alter table student1 add columns (age int);
OK
```
（3）查询表结构
```sql
hive (hive)> desc student1;
OK
col_name        data_type       comment
id                      string                                      
name                    string                                      
age                     int   
```
（4）更新列
```sql
hive (hive)> alter table student1 change column age ages int;
OK
```
（5）查询表结构
```sql
hive (hive)> desc student1;
OK
col_name        data_type       comment
id                      string                                      
name                    string                                      
ages                    int   
```
（6）替换列
```sql
hive (hive)> alter table student1 replace columns(stu_id string,stu_name string,stu_age int);
OK
```
（7）查询表结构
```sql
hive (hive)> desc student1;
OK
col_name        data_type       comment
stu_id                  string                                      
stu_name                string                                      
stu_age                 int   
```

## 
## 1.7 删除表
```sql
hive (hive)> drop table student1;
```


# 2. DML 数据操作
## 2.1 数据导入
### 2.1.1 向表中装载数据（Load）
#### **1）语法**
```sql
hive> load data [local] inpath '数据的 path' [overwrite] into table
student [partition (partcol1=val1,…)];
```
（1）load data:表示加载数据
（2）local:表示从本地加载数据到 hive 表；否则从 HDFS 加载数据到 hive 表
（3）inpath:表示加载数据的路径
（4）overwrite:表示覆盖表中已有数据，否则表示追加
（5）into table:表示加载到哪张表
（6）student:表示具体的表
（7）partition:表示上传到指定分区

#### **2）实操案例**
（0）创建一张表
```sql
hive (hive2) > create external table student(id string, name string) row format delimited fields terminated by '\t';
OK
```

（1）加载本地文件到 hive
```sql
hive (hive2)> load data local inpath '/opt/module/hive/student.txt' into table hive2.student;
Loading data to table hive2.student
OK
Time taken: 0.459 seconds
hive (hive2)> select * from student;
OK
student.id      student.name
1001    mhk
1002    jooye
1003    taylor
1004    jisoo
```

（2）加载 HDFS 文件到 hive 中 
上传文件到 HDFS
```sql
hive (hive)> dfs -put /opt/module/hive/student.txt /user/mhk;
```
加载 HDFS 上数据
```sql
hive (hive)> load data inpath '/user/mhk/student.txt' into table hive.student3;
Loading data to table hive.student3
OK
Time taken: 0.466 seconds
hive (hive)> select * from student3;
OK
student3.id     student3.name
1001    mhk
1002    jooye
1003    taylor
1004    jisoo
```
（3）加载数据覆盖表中已有的数据 
上传文件到 HDFS(load本地文件相当于复制，load HDFS的文件相当于剪切，因为上次上传的文件被剪切走了，所以需要在上传一遍)
```sql
hive (hive)> dfs -put /opt/module/hive/student.txt /user/mhk;
```
加载数据覆盖表中已有的数据
```sql
hive (hive)> load data inpath '/user/mhk/student.txt' overwrite into table hive.student3;
Loading data to table hive.student3
OK
Time taken: 0.575 seconds
hive (hive)> select * from student3;
OK
student3.id     student3.name
1001    mhk
1002    jooye
1003    taylor
1004    jisoo
```

### 2.1.2 通过查询语句向表中插入数据（Insert）
#### **1）创建一张表**
```sql
hive (hive)> create table student5(id string, name string) row format delimited fields terminated by '\t';
OK
```

#### 2）基本插入数据
```sql
hive (hive)> insert into table student5 values(1001,'mhk'),(1002,'jooye'),(1003,'taylor'),(1004,'jisoo');
```

#### 3）基本模式插入（根据单张表查询结果）
```sql
hive (hive)> insert into student5
           > select * from student2;
          
hive (hive)> select * from student5;
OK
student5.id     student5.name
1001    mhk
1002    jooye
1003    taylor
1004    jisoo
1001    mhk
1002    jooye
1003    taylor
1004    jisoo

hive (hive)> insert overwrite table student5
           > select * from student2;

hive (hive)> select * from student5;
OK
student5.id     student5.name
1001    mhk
1002    jooye
1003    taylor
1004    jisoo
```
insert into：以追加数据的方式插入到表或分区，原有数据不会删除 
insert overwrite：会覆盖表中已存在的数据，会删除原有数据重新写一个文件（在HDFSweb界面可以验证）。一般生产环境用这个来更改数据而不用update
注意：HQL insert 不支持插入部分字段，需将字段补全，没有数据的字段插入空值。

#### 4）多表（多分区）插入模式（根据多张表查询结果）
```sql
hive (hive)> create table student6(id string, name string) row format delimited fields terminated by '\t';
OK												//先创建一个空表
Time taken: 0.419 seconds
hive (hive)> from student2
           > insert into table student5 
           > select id,name
           > insert into table student6
           > select id,name;				//向student5和6中插入数据
           
hive (hive)> select * from student5;
OK
student5.id     student5.name
1001    mhk
1002    jooye
1003    taylor
1004    jisoo
1001    mhk
1002    jooye
1003    taylor
1004    jisoo
Time taken: 0.4 seconds, Fetched: 8 row(s)
hive (hive)> select * from student6;
OK
student6.id     student6.name
1001    mhk
1002    jooye
1003    taylor
1004    jisoo
```
### 
### 2.1.3 查询语句中创建表并加载数据（As Select）
详见 1.5章创建表。 根据查询结果创建表（查询的结果会添加到新创建的表中）
```sql
hive (default)> create table if not exists student5 as select id, name from student1;
OK
Time taken: 0.078 seconds
hive (default)> select * from student5;
OK
student5.id     student5.name
1001    mhk
1002    jooye
1003    taylor
1004    jisoo
```
### 
### **2.1.4 创建表时通过 Location 指定加载数据路径**
#### **1）上传数据到 hdfs 上**
```sql
hive (hive)> dfs -mkdir /student;
hive (hive)> dfs -put /opt/module/hive/student.txt /student;
```
#### 2）创建表，并指定在 hdfs 上的位置
生产环境中，如果这样创建表，一般都会用外部表，因为这个路径的数据可能是别人上传的，你指定这个路径建表万一用完删除了，那么这个数据也就没了。
```sql
hive (hive)> create external table if not exists student(id string, name string) 
							row format delimited fields terminated by '\t' 
              location '/student';
OK
Time taken: 0.54 seconds
```
#### 3）查询数据
```sql
hive (hive)> select * from student;
OK
student.id      student.name
1001    mhk
1002    jooye
1003    taylor
1004    jisoo
```
### 
### **2.1.5 Import 数据到指定 Hive 表中**
```sql
hive (hive)> import table student7
           > from '/user/hive/warehouse/export/student';
Copying data from hdfs://hadoop102:9820/user/hive/warehouse/export/student/data
Copying file: hdfs://hadoop102:9820/user/hive/warehouse/export/student/data/student.txt
Loading data to table hive.student7
OK
Time taken: 2.33 seconds
hive (hive)> select * from student7;
OK
student7.id     student7.name
1001    mhk
1002    jooye
1003    taylor
1004    jisoo
```



## 2.2 数据导出
### 2.2.1 Insert 导出
#### 1）将查询的结果导出到本地
```sql
hive (hive)> insert overwrite local directory '/opt/module/hive/export/student'
           > select * from student;
           
           
[mhk@hadoop102 student]$ ll
总用量 4
-rw-r--r--. 1 mhk mhk 43 1月  19 12:06 000000_0
[mhk@hadoop102 student]$ cat 000000_0 
1001mhk
1002jooye
1003taylor
1004jisoo
```
#### 2）将查询的结果格式化导出到本地
```sql
hive (hive)> insert overwrite local directory '/opt/module/hive/export/student1'  
           > row format delimited fields terminated by ','
           > select * from student;
           
           
[mhk@hadoop102 student1]$ ll
总用量 4
-rw-r--r--. 1 mhk mhk 43 1月  19 12:11 000000_0
[mhk@hadoop102 student1]$ cat 000000_0 
1001,mhk
1002,jooye
1003,taylor
1004,jisoo
```
#### 3）将查询的结果导出到 HDFS 上(没有 local)
```sql
hive (hive)> insert overwrite directory '/user/mhk/student'
           > row format delimited fields terminated by '\t'
           > select * from student;
```

### 2.2.2 Hadoop 命令导出到本地
```sql
[mhk@hadoop102 export]$ hadoop fs -get /user/hive/warehouse/hive.db/student1/student.txt /opt/module/hive/export/student.txt
2022-01-19 12:22:49,204 INFO sasl.SaslDataTransferClient: SASL encryption trust check: localHostTrusted = false, remoteHostTrusted = false
[mhk@hadoop102 export]$ ll
总用量 4
drwxrwxr-x. 2 mhk mhk 43 1月  19 12:06 student
drwxrwxr-x. 2 mhk mhk 43 1月  19 12:11 student1
drwxrwxr-x. 2 mhk mhk 43 1月  19 12:14 student3
-rw-r--r--. 1 mhk mhk 43 1月  19 12:22 student.txt
[mhk@hadoop102 export]$ cat student.txt 
1001    mhk
1002    jooye
1003    taylor
1004    jisoo
```

### 2.2.3 Hive Shell 命令导出
基本语法：（hive -f/-e  执行语句或者脚本> file）
>覆盖
>>追加
```sql
[mhk@hadoop102 hive]$ touch student1.txt 
[mhk@hadoop102 hive]$ bin/hive -e "select * from hive.student" > student1.txt 
which: no hbase in (/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/opt/module/hadoop-3.1.3/bin:/opt/module/hadoop-3.1.3/sbin:/opt/module/jdk1.8.0_212/bin:/opt/module/hive/bin:/home/mhk/.local/bin:/home/mhk/bin)
Hive Session ID = 7e24de6a-1193-47ec-a421-261b5af11ada

Logging initialized using configuration in file:/opt/module/hive/conf/hive-log4j2.properties Async: true
Hive Session ID = cb4d7228-60d0-4144-9a46-44e7ec70d400
OK
Time taken: 5.929 seconds, Fetched: 4 row(s)
[mhk@hadoop102 hive]$ cat student1.txt 
student.id      student.name
1001    mhk
1002    jooye
1003    taylor
1004    jisoo
```

### **2.2.4 Export 导出到 HDFS 上**
```sql
hive (hive)> export table student
           > to '/user/hive/warehouse/export/student';
```
![截屏2022-01-19 下午12.37.34.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1642567199733-92158c0e-626d-4135-9e77-12f8d265e4c2.png#clientId=u8d1a1448-1844-4&crop=0&crop=0&crop=1&crop=1&from=ui&id=ua0f31f12&margin=%5Bobject%20Object%5D&name=%E6%88%AA%E5%B1%8F2022-01-19%20%E4%B8%8B%E5%8D%8812.37.34.png&originHeight=310&originWidth=1181&originalType=binary&ratio=1&rotation=0&showTitle=false&size=49717&status=done&style=none&taskId=u065470dd-eb91-4086-89d8-1703729441f&title=)
export 和 import 主要用于两个 Hadoop 平台集群之间 Hive 表迁移。

### 2.2.5 清除表中数据（Truncate）
注意：Truncate 只能删除管理表，不能删除外部表中数据
```sql
hive (hive)> truncate table student7;
OK
Time taken: 2.013 seconds
hive (hive)> select * from student7;
OK
student7.id     student7.name
Time taken: 1.747 seconds
```
```sql
hive (hive)> create external table student8(id string, name string) row format delimited fields terminated by '\t';
OK

hive (hive)> insert overwrite table student8 select id,name from student;

hive (hive)> select * from student8;OK
student8.id     student8.name
1001    mhk
1002    jooye
1003    taylor
1004    jisoo

hive (hive)> truncate table student8;
FAILED: SemanticException [Error 10146]: Cannot truncate non-managed table student8.
```
