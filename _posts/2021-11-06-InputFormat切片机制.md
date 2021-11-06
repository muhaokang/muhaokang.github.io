---
layout: post
title: "InputFormat切片机制"
author: Haokang Mu
excerpt: InputFormat切片机制.md
tags:
- Hadoop
- MapReduce

---


## FileInputFormat切片机制

### 1. FileInputFormat切片源码解析(input.getSplits(job))

（1）程序首先找到你数据存储的目录

（2）开始遍历处理（规划切片）目录下的每一个文件

（3）遍历第一个文件hello.txt (300MB)

a) 获取文件大小fs.sizeOf(hello.txt)

b）计算切片大小
```
computeSplitSize(Math.max(minSize,Math. min(maxSize,blocksize)))=blocksize=128M
```

**c) 默认情况下，切片大小=blocksize**

d)开始切，形成第1个切片: hello.txt -- 0:128M
第2个切片: hello.txt -- 128:256M
第3个切片: hello.txt -- 256M:300M 
**(每次切片时，都要判断切完剩下的部分是否大于块的1.1倍，不大于1.1倍就划分一块切片)**

e) 将切片信息写到一个切片规划文件中

f) 整个切片的核心过程在getSplit()方法中完成

g) **InputSplit只记录了切片的元数据信息**，比如起始位置、长度以及所在的节点列表等。

**(4) 提交切片规划文件到YARN上，YARN. 上的MrAppMaster就可以根据切片规划文件计算开启MapTask个数。**

### 2. 切片机制

（1）简单的按照文件的内容长度进行切片

（2）切片的大小，默认等于Block大小

**（3）切片时不考虑数据集整体，而是逐个针对每一个文件单独切片**

### 3. 案例分析
（1）输入数据有两个文件：

file1.txt    320MB
file2.txt    10MB

（2）经过FileInputFormat的切片机制运算后，形成的切片信息如下：

file1.txt.split1 --    0 ~ 128
file1.txt.split2 --    128 ~ 256
file1.txt.split3 --    256 ~ 320
file2.txt.split1 --    0 ~ 10

### 4. FileInputFormat切片大小的参数配置

（1）源码中计算切片大小的公式

```
Math.max(minSize,Math.min(maxSize,blockSize));
mapreduce.input.fileinputformat.split.minsize=1;//默认值为1
mapreduce.input.fileinputformat.split.maxsize=Long.MAXValue;//默认值Long.MAXValue
```
因此，**默认情况下，切片大小=blocksize**

（2）切片大小设置

maxsize（切片最大值）：参数如果调的比blocksize小，则会让切片变小，而且就等于配置的这个参数的值。

minsize（切片最小值）：参数调的比blocksize大，则会让切片变得比blocksize还大。

（3）获取切片信息API

```
//获取切片的文件名称
String name = inputSpilt.getPath().getName();

//根据文件类型获取切片信息
FileSpilt inputSplit = (FileSplit) context.getInputSplit();
```

## TextInputFormat

### 1. FileInputFormat实现类

思考：在运行MapReduce程序时，输入的文件格式包括：基于行的日志文件、二进制格式文件、数据库表等。那么，针对不同的数据类型，MapReduce是如何读取这些数据的呢？

FileInputFormat常见的接口实现类包括：**TextInputFormat、KeyValueTextInputFormat、NLineInputFormat、CombineTextInputFormat和自定义InputFormat**等。

### 2. TextInputFormat

TextInputFormat是默认的FileInputFormat实现类。按行读取每条记录。**键是存储该行在整个文件中的起始字节偏移量， LongWritable类型。值是这行的内容，不包括任何行终止符（换行符和回车符），Text类型。**

以下是一个示例，比如，一个分片包含了如下4条文本记录。
```
Rich learning form
Intelligent learning engine
Learning more convenient
From the real demand for more close to the enterprise
```

每条记录表示为以下键/值对：
```
(0,Rich learning form)
(20,Intelligent learning engine)
(49,Learning more convenient)
(74,From the real demand for more close to the enterprise)
```

## CombineTextInputFormat切片机制

框架默认的TextInputFormat切片机制是对任务按文件规划切片，**不管文件多小，都会是一个单独的切片**，都会交给一个MapTask，这样如果有大量小文件，就会**产生大量的MapTask**，处理效率极其低下。

### 1. 应用场景：

CombineTextInputFormat用于小文件过多的场景，它可以将多个小文件从逻辑上规划到一个切片中，这样，多个小文件就可以交给一个MapTask处理。

### 2. 虚拟存储切片最大值设置
```
CombineTextInputFormat.setMaxInputSplitSize(job, 4194304);// 4m
```
注意：虚拟存储切片最大值设置最好根据实际的小文件大小情况来设置具体的值。

### 3. 切片机制
生成切片过程包括：虚拟存储过程和切片过程二部分。

![1A71420D975FF4F2251F40A35C5557AB](https://user-images.githubusercontent.com/65494322/140609007-da0dbee8-ddef-4ada-8ede-f1bf717ad42f.png)


#### （1）虚拟存储过程：

将输入目录下所有文件大小，依次和设置的setMaxInputSplitSize值比较，如果不大于设置的最大值，逻辑上划分一个块。如果输入文件大于设置的最大值且大于两倍，那么以最大值切割一块；**当剩余数据大小超过设置的最大值且不大于最大值2倍，此时将文件均分成2个虚拟存储块（防止出现太小切片）。**

例如setMaxInputSplitSize值为4M，输入文件大小为8.02M，则先逻辑上分成一个4M。剩余的大小为4.02M，如果按照4M逻辑划分，就会出现0.02M的小的虚拟存储文件，所以将剩余的4.02M文件切分成（2.01M和2.01M）两个文件。

#### （2）切片过程：

（a）判断虚拟存储的文件大小是否大于setMaxInputSplitSize值，大于等于则单独形成一个切片。

（b）如果不大于则跟下一个虚拟存储文件进行合并，共同形成一个切片。

**（c）测试举例：有4个小文件大小分别为1.7M、5.1M、3.4M以及6.8M这四个小文件，则虚拟存储之后形成6个文件块，大小分别为：
1.7M，（2.55M、2.55M），3.4M以及（3.4M、3.4M）
最终会形成3个切片，大小分别为：
（1.7+2.55）M，（2.55+3.4）M，（3.4+3.4）M**




