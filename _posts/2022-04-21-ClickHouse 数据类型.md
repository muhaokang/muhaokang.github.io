# 1. 整型
固定长度的整型，包括有符号整型或无符号整型。 
整型范围（-2^(n-1) ~ 2^(n-1)-1）： 
Int8 - [-128 : 127] 
Int16 - [-32768 : 32767] 
Int32 - [-2147483648 : 2147483647] 
Int64 - [-9223372036854775808 : 9223372036854775807] 
无符号整型范围（0~(2^n)-1）： 
UInt8 - [0 : 255] 
UInt16 - [0 : 65535] 
UInt32 - [0 : 4294967295] 
UInt64 - [0 : 18446744073709551615] 
**使用场景： 个数、数量、也可以存储型 id。 **

# 2. 浮点型 
Float32 - float 
Float64 – double 
建议尽可能以整数形式存储数据。例如，将固定精度的数字转换为整数值，如时间用毫秒为单位表示，因为浮点型进行计算时可能引起四舍五入的误差。
```shell
hadoop102 :) select 1-0.9;

SELECT 1 - 0.9

Query id: e741974d-f149-4162-9147-01c3a9981677

┌───────minus(1, 0.9)─┐
│ 0.09999999999999998 │
└─────────────────────┘

1 rows in set. Elapsed: 0.008 sec. 
```
**使用场景：一般数据值比较小，不涉及大量的统计计算，精度要求不高的时候。比如 **
**保存商品的重量。 **

# 3. 布尔型 
没有单独的类型来存储布尔值。可以使用 UInt8 类型，取值限制为 0 或 1。 

# 4. Decimal 型 
有符号的浮点数，可在加、减和乘法运算过程中保持精度。对于除法，最低有效数字会被丢弃（不舍入）。 
有三种声明： 

- Decimal32(s)，相当于 Decimal(9-s,s)，有效位数为 1~9 
- Decimal64(s)，相当于 Decimal(18-s,s)，有效位数为 1~18 
- Decimal128(s)，相当于 Decimal(38-s,s)，有效位数为 1~38 

s 标识小数位 
```
123.123.123.123

decimal32(5)    ===>    整数+小数一共9位，小数部分有5位   123.12312
decimal64(5)    ===>    整数+小数一共18位，小数部分有5位   123.12312
```
使用场景： 一般金额字段、汇率、利率等字段为了保证小数点精度，都使用 Decimal 进行存储。 

# 5. 字符串 
**1）String **
字符串可以任意长度的。它可以包含任意的字节集，包含空字节。 

**2）FixedString(N) **
固定长度 N 的字符串，N 必须是严格的正自然数。当服务端读取长度小于 N 的字符串时候，通过在字符串末尾添加空字节来达到 N 字节长度。 当服务端读取长度大于 N 的字符串时候，将返回错误消息。 

与 String 相比，极少会使用 FixedString，因为使用起来不是很方便。

使用场景：名称、文字描述、字符型编码。 固定长度的可以保存一些定长的内容，比如一些编码，性别等但是考虑到一定的变化风险，带来收益不够明显，所以定长字符串使用意义有限。 

# 6. 枚举类型 
包括 Enum8 和 Enum16 类型。Enum 保存 'string'= integer 的对应关系。 
Enum8 用 'String'= Int8 对描述。 
Enum16 用 'String'= Int16 对描述。 

**1）用法演示 **
创建一个带有一个枚举 Enum8('hello' = 1, 'world' = 2) 类型的列
```
hadoop102 :) CREATE TABLE t_enum
:-] (
:-]     x Enum8('hello' = 1, 'world' = 2)
:-] )
:-] ENGINE = TinyLog;

CREATE TABLE t_enum
(
    `x` Enum8('hello' = 1, 'world' = 2)
)
ENGINE = TinyLog

Query id: deb02552-6fb4-4836-b210-640211e9440b

Ok.

0 rows in set. Elapsed: 0.005 sec. 
```

**2）这个 x 列只能存储类型定义中列出的值：'hello'或'world'**
```
hadoop102 :) select * from t_enum;

SELECT *
FROM t_enum

Query id: 5a0532b8-d186-4402-9491-8bd688693005

┌─x─────┐
│ hello │
│ world │
│ hello │
└───────┘

3 rows in set. Elapsed: 0.003 sec. 
```

**3）如果尝试保存任何其他值，ClickHouse 抛出异常**
```
hadoop102 :) insert into t_enum values('a');

INSERT INTO t_enum VALUES

Query id: bcbe515e-4247-4ecf-bb62-a6ca509d0aa0


Exception on client:
Code: 36. DB::Exception: Unknown element 'a' for enum: data for INSERT was parsed from query

Connecting to localhost:9000 as user default.
Connected to ClickHouse server version 21.7.3 revision 54449.
```

**4）如果需要看到对应行的数值，则必须将 Enum 值转换为整数类型**
```
hadoop102 :) SELECT CAST(x, 'Int8') FROM t_enum;

SELECT CAST(x, 'Int8')
FROM t_enum

Query id: 68450b03-5d18-4e3d-99e3-5d42451caa25

┌─CAST(x, 'Int8')─┐
│               1 │
│               2 │
│               1 │
└─────────────────┘

3 rows in set. Elapsed: 0.005 sec. 
```

使用场景：对一些状态、类型的字段算是一种空间优化，也算是一种数据约束。但是实际使用中往往因为一些数据内容的变化增加一定的维护成本，甚至是数据丢失问题。所以谨慎使用。

# 7. 时间类型 
目前 ClickHouse 有三种时间类型 

- Date 接受**年-月-日**的字符串比如 ‘2019-12-16’ 
- Datetime 接受**年-月-日 时:分:秒**的字符串比如 ‘2019-12-16 20:50:10’ 
- Datetime64 接受**年-月-日 时:分:秒.亚秒**的字符串比如‘2019-12-16 20:50:10.66’ 

日期类型，用两个字节存储，表示从 1970-01-01 (无符号) 到当前的日期值。 
还有很多数据结构，可以参考官方文档：https://clickhouse.yandex/docs/zh/data_types/ 

# 8. 数组 
**Array(T)：**由 T 类型元素组成的数组。 
T 可以是任意类型，包含数组类型。 但不推荐使用多维数组，ClickHouse 对多维数组的支持有限。例如，不能在 MergeTree 表中存储多维数组。 
（1）创建数组方式 1，使用 array 函数
```
hadoop102 :) SELECT array(1, 2) AS x, toTypeName(x) ;

SELECT
    [1, 2] AS x,
    toTypeName(x)

Query id: e0b7b306-a943-454d-9ac7-3118b4823d71

┌─x─────┬─toTypeName(array(1, 2))─┐
│ [1,2] │ Array(UInt8)            │
└───────┴─────────────────────────┘

1 rows in set. Elapsed: 0.014 sec. 
```

（2）创建数组方式 2：使用方括号
```
hadoop102 :) SELECT [1, 2] AS x, toTypeName(x);

SELECT
    [1, 2] AS x,
    toTypeName(x)

Query id: cb94f85c-8946-4a36-8cdc-cc28d5c1e26d

┌─x─────┬─toTypeName([1, 2])─┐
│ [1,2] │ Array(UInt8)       │
└───────┴────────────────────┘

1 rows in set. Elapsed: 0.003 sec. 
```
