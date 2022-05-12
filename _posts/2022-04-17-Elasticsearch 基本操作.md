# 1.**RESTful **
REST 指的是一组架构约束条件和原则。满足这些约束条件和原则的应用程序或设计就是 RESTful。Web 应用程序最重要的 REST 原则是，客户端和服务器之间的交互在请求之间是无状态的。从客户端到服务器的每个请求都必须包含理解请求所必需的信息。如果服务器在请求之间的任何时间点重启，客户端不会得到通知。此外，无状态请求可以由任何可用服务器回答，这十分适合云计算之类的环境。客户端可以缓存数据以改进性能。 

在服务器端，应用程序状态和功能可以分为各种资源。资源是一个有趣的概念实体，它向客户端公开。资源的例子有：应用程序对象、数据库记录、算法等等。每个资源都使用 URI (Universal Resource Identifier) 得到一个唯一的地址。所有资源都共享统一的接口，以便在客户端和服务器之间传输状态。使用的是标准的 HTTP 方法，比如 GET、PUT、POST 和 DELETE。
 
在 REST 样式的 Web 服务中，每个资源都有一个地址。资源本身都是方法调用的目标，方法列表对所有资源都是一样的。这些方法都是标准方法，包括 HTTP GET、POST、PUT、DELETE，还可能包括 HEAD 和 OPTIONS。简单的理解就是，如果想要访问互联网上的资源，就必须向资源所在的服务器发出请求，请求体中必须包含资源的网络路径，以及对资源进行的操作(增删改查)。

# 2. 客户端安装
如果直接通过浏览器向 Elasticsearch 服务器发请求，那么需要在发送的请求中包含HTTP 标准的方法，而 HTTP 的大部分特性且仅支持 GET 和 POST 方法。所以为了能方便地进行客户端的访问，可以使用 Postman 软件 

Postman 是一款强大的网页调试工具，提供功能强大的 Web API 和 HTTP 请求调试。软件功能强大，界面简洁明晰、操作方便快捷，设计得很人性化。Postman 中文版能够发送任何类型的 HTTP 请求 (GET, HEAD, POST, PUT..)，不仅能够表单提交，且可以附带任意类型请求体。 

Postman 官网：https://www.getpostman.com 
Postman 下载：https://www.getpostman.com/apps

# 3. 数据格式 
Elasticsearch 是面向文档型数据库，一条数据在这里就是一个文档。为了方便大家理解，我们将 Elasticsearch 里存储文档数据和关系型数据库 MySQL 存储数据的概念进行一个类比
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650106282634-8c401896-25e7-41a2-83c2-e9f15348456e.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=226&id=uf1b6a949&margin=%5Bobject%20Object%5D&name=image.png&originHeight=226&originWidth=808&originalType=binary&ratio=1&rotation=0&showTitle=false&size=93303&status=done&style=none&taskId=u0c8da7d8-60d8-40c2-bf4a-92846268d2f&title=&width=808)
ES 里的 Index 可以看做一个库，而 Types 相当于表，Documents 则相当于表的行。 
这里 Types 的概念已经被逐渐弱化，Elasticsearch 6.X 中，一个 index 下已经只能包含一个 type，Elasticsearch 7.X 中, Type 的概念已经被删除了。
6 用 JSON 作为文档序列化的格式，比如一条用户信息：
```shell
{
  "name" : "John",
  "sex" : "Male",
  "age" : 25,
  "birthDate": "1990/05/01",
  "about" : "I love to go rock climbing",
  "interests": [ "sports", "music" ]
}
```
   
# 4. HTTP 操作
## 4.1 索引操作
### 1) 创建索引 
对比关系型数据库，创建索引就等同于创建数据库 
在 Postman 中，向 ES 服务器发 **PUT **请求 ：[http://10.211.55.11:9200/shopping](http://10.211.55.11:9200/shopping)
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650108031938-eeec96bc-4ba2-4266-bfaa-3e91839f7282.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=608&id=uf94f184a&margin=%5Bobject%20Object%5D&name=image.png&originHeight=608&originWidth=861&originalType=binary&ratio=1&rotation=0&showTitle=false&size=118802&status=done&style=none&taskId=ueed6472c-3cb9-458c-a3b0-de6d4f988cb&title=&width=861)
```shell
{
    "acknowledged"【响应结果】: true, # true 操作成功
    "shards_acknowledged"【分片结果】: true, # 分片操作成功
    "index"【索引名称】: "shopping"
}
# 注意：创建索引库的分片数默认 1 片，在 7.0.0 之前的 Elasticsearch 版本中，默认 5 片
```
如果重复添加索引，会返回错误信息
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650108498721-9b38ddef-f590-42a0-83e0-23059b6b8352.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=277&id=u47f0b2f8&margin=%5Bobject%20Object%5D&name=image.png&originHeight=277&originWidth=766&originalType=binary&ratio=1&rotation=0&showTitle=false&size=144491&status=done&style=none&taskId=u694c9aee-46c7-4576-a153-156043d8e27&title=&width=766)

### 2) 查看所有索引 
在 Postman 中，向 ES 服务器发 **GET **请求 ：[http://10.211.55.11:9200/_cat/indices?v](http://10.211.55.11:9200/_cat/indices?v)

这里请求路径中的_cat 表示查看的意思，indices 表示索引，所以整体含义就是查看当前 ES 
服务器中的所有索引，就好像 MySQL 中的 show tables 的感觉，服务器响应结果如下
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650108641911-fafc2b7b-d50e-4c14-b07e-12664c6416e8.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=495&id=u23a7bb97&margin=%5Bobject%20Object%5D&name=image.png&originHeight=495&originWidth=850&originalType=binary&ratio=1&rotation=0&showTitle=false&size=101513&status=done&style=none&taskId=u79ed1a4f-e52b-4458-9dcb-45a6453a657&title=&width=850)
```shell
health status index    uuid                   pri rep docs.count docs.deleted store.size pri.store.size
yellow open   shopping ohQY_Mb0Rm2UG-Z9J0ZhMg   1   1          0            0       208b           208b
```
| health | 当前服务器健康状态：**green**(集群完整) **yellow**(单点正常、集群不完整) red(单点不正常) |
| --- | --- |
| status | 索引打开、关闭状态  |
| index  | 索引名 |
| uuid  | 索引统一编号  |
| pri | 主分片数量 |
| rep | 副本数量  |
| docs.count | 可用文档数量 |
| docs.deleted | 文档删除状态（逻辑删除）  |
| store.size  | 主分片和副分片整体占空间大小  |
| pri.store.size | 主分片占空间大小 |


### 3) 查看单个索引 
在 Postman 中，向 ES 服务器发 **GET **请求 : [http://10.211.55.11:9200/shopping](http://10.211.55.11:9200/shopping)

查看索引向 ES 服务器发送的请求路径和创建索引是一致的。但是 HTTP 方法不一致。这里可以体会一下 RESTful 的意义， 
请求后，服务器响应结果如下：
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650109165674-a1c66990-a7fc-48ae-9717-7464764f90ed.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=614&id=ue4bbe693&margin=%5Bobject%20Object%5D&name=image.png&originHeight=614&originWidth=881&originalType=binary&ratio=1&rotation=0&showTitle=false&size=145158&status=done&style=none&taskId=u3911cd3b-5d8c-4910-b892-2a31a6744a0&title=&width=881)
```json
{
  "shopping"【索引名】: {
    "aliases"【别名】: {},
    "mappings"【映射】: {},
    "settings"【设置】: {
      "index"【设置 - 索引】: {
        "creation_date"【设置 - 索引 - 创建时间】: "1650108007285",
        "number_of_shards"【设置 - 索引 - 主分片数量】: "1",
        "number_of_replicas"【设置 - 索引 - 副分片数量】: "1",
        "uuid"【设置 - 索引 - 唯一标识】: "ohQY_Mb0Rm2UG-Z9J0ZhMg",
        "version"【设置 - 索引 - 版本】: {
          "created": "7080099"
        },
        "provided_name"【设置 - 索引 - 名称】: "shopping"
      }
    }
  }
}
```

### 4) 删除索引 
在 Postman 中，向 ES 服务器发 **DELETE **请求 ：[http://10.211.55.11:9200/shopping](http://10.211.55.11:9200/shopping)
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650114661772-c14dd498-3dbe-4619-9cf6-b050b052ebec.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=519&id=ua446acca&margin=%5Bobject%20Object%5D&name=image.png&originHeight=519&originWidth=858&originalType=binary&ratio=1&rotation=0&showTitle=false&size=93369&status=done&style=none&taskId=u766abe91-37d5-42de-8961-3f23f49ae15&title=&width=858)
重新访问索引时，服务器返回响应：**索引不存在**
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650115411382-3131d3cb-ad24-463f-aad5-557bb0e406cf.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=618&id=u5852c1da&margin=%5Bobject%20Object%5D&name=image.png&originHeight=618&originWidth=855&originalType=binary&ratio=1&rotation=0&showTitle=false&size=151701&status=done&style=none&taskId=u1cd64cb4-c20f-46ac-bc85-d0b3662bf05&title=&width=855)

## 4.2 文档操作 
### 1) 创建文档 
索引已经创建好了，接下来我们来创建文档，并添加数据。这里的文档可以类比为关系型数据库中的表数据，添加的数据格式为 JSON 格式 
在 Postman 中，向 ES 服务器发 **POST **请求 ：http://10.211.55.11:9200/shopping**/_doc **
请求体内容为：
```json
{ 
  "title":"小米手机",
  "category":"小米",
  "images":"http://www.gulixueyuan.com/xm.jpg",
  "price":3999.00
}
```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650115683911-69e81188-4636-4f22-ae46-11ac92cddd20.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=417&id=u18f3bc33&margin=%5Bobject%20Object%5D&name=image.png&originHeight=417&originWidth=866&originalType=binary&ratio=1&rotation=0&showTitle=false&size=134780&status=done&style=none&taskId=u3b506108-1fe8-4c97-a7fd-4b6eef0adcd&title=&width=866)
此处发送请求的方式必须为 **POST**，不能是 **PUT**，否则会发生错误
PUT请求是幂等性的，POST请求不是幂等性的，每一次POST都返回不同的ID
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650115828658-95158cd9-e1e5-44d7-a536-2a923088a4c1.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=156&id=uc0e5b092&margin=%5Bobject%20Object%5D&name=image.png&originHeight=156&originWidth=815&originalType=binary&ratio=1&rotation=0&showTitle=false&size=67519&status=done&style=none&taskId=u8dd500bf-e040-4921-928f-9ca91b9251b&title=&width=815)

服务器响应结果如下：
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650115785649-496792db-d909-44b1-b543-3489fde30d19.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=347&id=u5870bc56&margin=%5Bobject%20Object%5D&name=image.png&originHeight=347&originWidth=849&originalType=binary&ratio=1&rotation=0&showTitle=false&size=112550&status=done&style=none&taskId=u8fbee92d-0292-40f4-b4de-690b7d185f2&title=&width=849)
```json
{
    "_index"【索引】: "shopping",
    "_type"【类型-文档】: "_doc",
    "_id"【唯一标识】: "1ZOPMoABrqtNwT9MR10m", #可以类比为 MySQL 中的主键，随机生成
    "_version"【版本】: 1,
    "result"【结果】: "created", #这里的 create 表示创建成功
    "_shards"【分片】: {
        "total"【分片 - 总数】: 2,
        "successful"【分片 - 成功】: 1,
        "failed"【分片 - 失败】: 0
    },
    "_seq_no": 0,
    "_primary_term": 1
}
```

上面的数据创建后，由于没有指定数据唯一性标识（ID），默认情况下，ES 服务器会随机生成一个。 
如果想要自定义唯一性标识，需要在创建时指定：http://10.211.55.11:9200/shopping/_doc/**1001**
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650116267023-567f5569-befa-483c-b9e0-8f1dc604f1b6.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=626&id=ued4363d2&margin=%5Bobject%20Object%5D&name=image.png&originHeight=626&originWidth=849&originalType=binary&ratio=1&rotation=0&showTitle=false&size=196176&status=done&style=none&taskId=u8feb13ae-2f1f-4438-838b-0955749a282&title=&width=849)
此处需要注意：如果增加数据时明确数据主键，那么请求方式也可以为 PUT

### 2) 查看文档 
查看文档时，需要指明文档的唯一性标识，类似于 MySQL 中数据的主键查询 
在 Postman 中，向 ES 服务器发 **GET **请求 ：http://10.211.55.11:9200/shopping**/_doc/1001**
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650116389541-77fd9101-24d2-45bd-a013-7a122c95f2d7.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=619&id=u7a1ffdb0&margin=%5Bobject%20Object%5D&name=image.png&originHeight=619&originWidth=890&originalType=binary&ratio=1&rotation=0&showTitle=false&size=213425&status=done&style=none&taskId=u437bebb8-f916-4c6e-833c-dfbcd4aafaf&title=&width=890)
```json
{
    "_index"【索引】: "shopping",
    "_type"【文档类型】: "_doc",
    "_id": "1001",
    "_version": 1,
    "_seq_no": 1,
    "_primary_term": 1,
    "found"【查询结果】: true, # true 表示查找到，false 表示未查找到
    "_source"【文档源信息】: {
        "title": "小米手机",
        "category": "小米",
        "images": "http://www.gulixueyuan.com/xm.jpg",
        "price": 3999.00
    }
}
```

全部查询：向 ES 服务器发 **GET **请求 ：http://10.211.55.11:9200/shopping**/_search**


### 3) 修改文档 
和新增文档一样，输入相同的 URL 地址请求，如果请求体变化，会将原有的数据内容覆盖 
在 Postman 中，向 ES 服务器发 **POST **请求 ：http://10.211.55.11:9200/shopping**/_doc/1001 **
请求体内容为: 
```json
{
  "title":"华为手机",
  "category":"华为",
  "images":"http://www.gulixueyuan.com/hw.jpg",
  "price":4999.00
}
```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650116923039-cccc696a-8e1c-4187-94ae-ce09c1a8bf65.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=622&id=ue1c34ede&margin=%5Bobject%20Object%5D&name=image.png&originHeight=622&originWidth=865&originalType=binary&ratio=1&rotation=0&showTitle=false&size=193471&status=done&style=none&taskId=udefb90ec-faaf-44b6-9b91-9203d359a5a&title=&width=865)
```json
{
    "_index": "shopping",
    "_type": "_doc",
    "_id": "1001",
    "_version"【版本】: 2,
    "result"【结果】: "updated", # updated 表示数据被更新
    "_shards": {
        "total": 2,
        "successful": 1,
        "failed": 0
    },
    "_seq_no": 2,
    "_primary_term": 1
}
```
   
### 4) 修改字段
局部修改：非幂等性，每次修改的内容都不一样，使用POST请求
[http://10.211.55.11:9200/shopping/_update/1001](http://10.211.55.11:9200/shopping/_update/1001)
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650117324522-020b4a85-5b7e-476f-9818-bf985ff64311.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=612&id=uc60f7e4a&margin=%5Bobject%20Object%5D&name=image.png&originHeight=612&originWidth=874&originalType=binary&ratio=1&rotation=0&showTitle=false&size=176955&status=done&style=none&taskId=u3945162d-fb71-4bfe-9546-4cddd1eef8d&title=&width=874)
根据唯一性标识，查询文档数据，文档数据已经更新
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650117483405-383929bb-1a29-4fc7-a070-a85c49e993d5.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=619&id=u43f6f0fe&margin=%5Bobject%20Object%5D&name=image.png&originHeight=619&originWidth=852&originalType=binary&ratio=1&rotation=0&showTitle=false&size=166689&status=done&style=none&taskId=u5a0a6da8-9649-4dd7-89b9-bf5967f4ddb&title=&width=852)

### 5) 删除文档 
删除一个文档不会立即从磁盘上移除，它只是被标记成已删除（逻辑删除）。 
在 Postman 中，向 ES 服务器发 **DELETE **请求 ：http://10.211.55.11:9200/shopping**/_doc/1001**
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650117601189-ce89396b-4b9a-4cf9-95fa-d9193bf9c35a.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=613&id=ua2134545&margin=%5Bobject%20Object%5D&name=image.png&originHeight=613&originWidth=862&originalType=binary&ratio=1&rotation=0&showTitle=false&size=151098&status=done&style=none&taskId=ue790e738-845a-4ede-821c-05e9c73b162&title=&width=862)
```json
{
    "_index": "shopping",
    "_type": "_doc",
    "_id": "1001",
    "_version"【版本】: 4, #对数据的操作，都会更新版本
    "result"【结果】: "deleted", # deleted 表示数据被标记为删除
    "_shards": {
        "total": 2,
        "successful": 1,
        "failed": 0
    },
    "_seq_no": 4,
    "_primary_term": 1
}
```
   
如果删除一个并不存在的文档
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650117744330-6cbe8d87-46de-4280-881e-c3a0dd70a8b0.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=616&id=u6b33d49c&margin=%5Bobject%20Object%5D&name=image.png&originHeight=616&originWidth=858&originalType=binary&ratio=1&rotation=0&showTitle=false&size=153624&status=done&style=none&taskId=uefda654f-7955-4ecd-b4ef-166507a42de&title=&width=858)
 not_found 表示未查找到

### 6) 条件删除文档 
一般删除数据都是根据文档的唯一性标识进行删除，实际操作时，也可以根据条件对多条数 
据进行删除 
首先分别增加多条数据: 
```json
{
  "title":"小米手机",
  "category":"小米",
  "images":"http://www.gulixueyuan.com/xm.jpg",
  "price":4000.00
}

{
  "title":"华为手机",
  "category":"华为",
  "images":"http://www.gulixueyuan.com/hw.jpg",
  "price":4000.00
}
```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650118725347-49b174d9-cbd9-48c3-aed9-83091e81bfdb.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=280&id=u47e307b0&margin=%5Bobject%20Object%5D&name=image.png&originHeight=280&originWidth=851&originalType=binary&ratio=1&rotation=0&showTitle=false&size=92200&status=done&style=none&taskId=ubd0b31be-d73e-4485-8093-b5c8052ec50&title=&width=851)
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650118704541-7e835f39-956b-44de-92a1-34b076e69894.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=266&id=u625cd02a&margin=%5Bobject%20Object%5D&name=image.png&originHeight=266&originWidth=844&originalType=binary&ratio=1&rotation=0&showTitle=false&size=88224&status=done&style=none&taskId=uca0b7b60-8907-4c8e-93e1-dfef9929cd7&title=&width=844)  
向 ES 服务器发 **POST **请求 ：http://10.211.55.11:9200/shopping**/_delete_by_query**
**请求的内容为**
```json
{
  "query":{
    "match":{
      "price":4000.00
    } 
  }
}
```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650118973050-f200849a-1f86-47f2-a73c-81c89b85556d.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=619&id=u277a1676&margin=%5Bobject%20Object%5D&name=image.png&originHeight=619&originWidth=860&originalType=binary&ratio=1&rotation=0&showTitle=false&size=181248&status=done&style=none&taskId=u7e1f8130-933d-45bb-9326-da6c2ae1bda&title=&width=860)
```json
{
    "took"【耗时】: 821,
    "timed_out"【是否超时】: false,
    "total"【总数】: 3,
    "deleted"【删除数量】: 3,
    "batches": 1,
    "version_conflicts": 0,
    "noops": 0,
    "retries": {
        "bulk": 0,
        "search": 0
    },
    "throttled_millis": 0,
    "requests_per_second": -1.0,
    "throttled_until_millis": 0,
    "failures": []
}
```


### 7) 条件查询
**查询种类是小米的请求**
**GET操作(请求路径)：**[http://10.211.55.11:9200/shopping/_search?q=catagory:](http://10.211.55.11:9200/shopping/_search?q=catagory:)小米
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650119185493-7b264e36-7bc5-4d7b-b4e3-253dd4201d5f.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=604&id=uad85bb4b&margin=%5Bobject%20Object%5D&name=image.png&originHeight=604&originWidth=859&originalType=binary&ratio=1&rotation=0&showTitle=false&size=145558&status=done&style=none&taskId=u7c29b04d-3e67-43ba-8090-b94be49dd6f&title=&width=859)

**请求体**
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650119351422-8c0ec2e3-0574-4599-b988-c1c943ec579c.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=610&id=u0ac67933&margin=%5Bobject%20Object%5D&name=image.png&originHeight=610&originWidth=869&originalType=binary&ratio=1&rotation=0&showTitle=false&size=170067&status=done&style=none&taskId=u71284db6-8ca8-432b-8e5b-cac860c482c&title=&width=869)
### 8) 多条件查询
同时成立：**must**
```json
{
	"query":{
		"bool":{
			"must":[
				{
					"match":{
						"cateaory":"小米"
					}
				},
				{
					"match":{
						"price":"2999.00"
					}
				}
			]
		}
	}
}
```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650157055379-d81b252d-882e-4f50-a4b4-2157dfcd6aae.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=542&id=ud2783ea2&margin=%5Bobject%20Object%5D&name=image.png&originHeight=542&originWidth=861&originalType=binary&ratio=1&rotation=0&showTitle=false&size=156893&status=done&style=none&taskId=u2d1cd282-3553-4957-a186-8680f1f4cbc&title=&width=861)

任何一个都满足条件：**should**
```json
{
	"query":{
		"bool":{
			"should":[
				{
					"match":{
						"cateaory":"小米"
					}
				},
				{
					"match":{
						"cateaory":"苹果"
					}
				}
			]
		}
	}
}
```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650157188681-73d2acae-175c-41aa-a37f-470bcbedd57d.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=508&id=ucd6787d4&margin=%5Bobject%20Object%5D&name=image.png&originHeight=508&originWidth=858&originalType=binary&ratio=1&rotation=0&showTitle=false&size=157079&status=done&style=none&taskId=ub1caaf33-c27e-4055-b067-9d09ec29346&title=&width=858)

范围操作：**filter** **range**
```json
{
	"query":{
		"bool":{
			"should":[
				{
					"match":{
						"cateaory":"小米"
					}
				},
				{
					"match":{
						"cateaory":"苹果"
					}
				}
			],
			"filter":{
				"range":{
					"price":{
						"gt":2000
					}
				}
			}
		}
	}
}
```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650157458071-2409c1cf-b3b4-4a74-9f26-05ed84499643.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=570&id=u42652187&margin=%5Bobject%20Object%5D&name=image.png&originHeight=570&originWidth=847&originalType=binary&ratio=1&rotation=0&showTitle=false&size=165256&status=done&style=none&taskId=uc861a855-cc94-4874-924b-2e8ccc06d8c&title=&width=847)
### 
### 9) 全文检索
当保存文档数据时，es会将数据文字进行分词拆解操作，并将拆解后的数据保存到倒排索引当中，那么即使使用文字的一部分，仍可以查询到数据，这种检索的方式称之为全文检索。es会将查询内容进行分词，在倒排索引中进行匹配
```json
{
    "query":{
        "match":{
            "category":"米"
        }
    }
}
```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650157917758-e34070d8-9e25-4db9-a07b-1fb0f2288669.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=598&id=u103cb014&margin=%5Bobject%20Object%5D&name=image.png&originHeight=598&originWidth=859&originalType=binary&ratio=1&rotation=0&showTitle=false&size=200840&status=done&style=none&taskId=ubcc436af-b3e3-4c00-8db1-c8a67e8f149&title=&width=859)

完全匹配：**match_phrase**
```json
{
    "query":{
        "match_phrase":{
            "category":"米华"
        }
    }
}
```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650158084451-922b2000-614d-419d-8ce7-c9099a1e9043.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=575&id=u899dc3ce&margin=%5Bobject%20Object%5D&name=image.png&originHeight=575&originWidth=886&originalType=binary&ratio=1&rotation=0&showTitle=false&size=173002&status=done&style=none&taskId=u9c2ad199-caac-4ef8-b46a-35f99e4832c&title=&width=886)

高亮查询
```json
{
    "query":{
        "match_phrase":{
            "category":"小米"
        }
    },
    "highlight":{
        "fields":{
            "category":{}
        }
    }
}
```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650158321048-9e8f345b-c6fe-44ad-b476-956f55f7e239.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=575&id=u14b51b03&margin=%5Bobject%20Object%5D&name=image.png&originHeight=575&originWidth=865&originalType=binary&ratio=1&rotation=0&showTitle=false&size=191414&status=done&style=none&taskId=ue5fb9995-8250-4cd5-a210-754f30b8410&title=&width=865)

### 10) 聚合操作
```json
{
    "aggs":{    //聚合操作
        "price_group":{     //统计结果的名称，任意取
            "terms":{       //分组
                "field":"price" //分组字段
            }
        }
    }
}
```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650158630603-9fcde9af-e0f9-41c5-8d1b-b9addd997f64.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=612&id=uf83287d9&margin=%5Bobject%20Object%5D&name=image.png&originHeight=612&originWidth=854&originalType=binary&ratio=1&rotation=0&showTitle=false&size=198073&status=done&style=none&taskId=u22c161ee-26e0-4c82-a01d-10ebc8f0f17&title=&width=854)

不显示原始数据
```json
{
    "aggs":{    //聚合操作
        "price_group":{     //统计结果的名称，任意取
            "terms":{       //分组
                "field":"price" //分组字段
            }
        }
    },
    "size":0   //不用显示原始数据
}
```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650158829629-be063b87-2a05-4b0e-9664-942200150eda.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=275&id=uc3d8d997&margin=%5Bobject%20Object%5D&name=image.png&originHeight=275&originWidth=617&originalType=binary&ratio=1&rotation=0&showTitle=false&size=84401&status=done&style=none&taskId=ufc234aab-6499-40f8-8a0e-64bbb0a6b28&title=&width=617)

求平均值
```json
{
    "aggs":{    //聚合操作
        "price_avg":{     //统计结果的名称，任意取
            "avg":{       //平均值
                "field":"price" //分组字段
            }
        }
    },
    "size":0   //不用显示原始数据
}
```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650158887334-ace2f9f1-5c9a-4c8e-8f6b-d79741d11820.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=144&id=ue0a58173&margin=%5Bobject%20Object%5D&name=image.png&originHeight=144&originWidth=331&originalType=binary&ratio=1&rotation=0&showTitle=false&size=31119&status=done&style=none&taskId=u1af87de4-1b17-431f-ad0b-be5b3016131&title=&width=331)

## 4.3 映射关系 
有了索引库，等于有了数据库中的 database。

接下来就需要建索引库(index)中的映射了，类似于数据库(database)中的表结构(table)。 

创建数据库表需要设置字段名称，类型，长度，约束等；索引库也一样，需要知道这个类型下有哪些字段，每个字段有哪些约束信息，这就叫做映射(mapping)。

### 1) 创建映射 
在 Postman 中，向 ES 服务器发 **PUT **请求 ：http://10.211.55.11:9200/user**/_mapping **
请求体内容为：
```json
{
  "properties": {
    "name":{
      "type": "text",
      "index": true
    },
    "sex":{
      "type": "keyword",	//不能够被分词
      "index": true
    },
    "tel":{
      "type": "keyword",
      "index": false	//不能够被索引	
    }
  } 
}
```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650159817033-9d7113cc-dba0-4a7d-aa3b-e94830125763.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=422&id=uff2070e6&margin=%5Bobject%20Object%5D&name=image.png&originHeight=422&originWidth=856&originalType=binary&ratio=1&rotation=0&showTitle=false&size=129305&status=done&style=none&taskId=u0769dd00-ecbc-46f3-8da0-0b4b4b618f7&title=&width=856)

映射数据说明： 

- 字段名：任意填写，下面指定许多属性，例如：title、subtitle、images、price 
- type：类型，Elasticsearch 中支持的数据类型非常丰富，说几个关键的： 

String 类型，又分两种： 
text：可分词
keyword：不可分词，数据会作为完整字段进行匹配   
Numerical：数值类型，分两类 
基本数据类型：long、integer、short、byte、double、float、half_float 
浮点数的高精度类型：scaled_float 
Date：日期类型 
Array：数组类型 
Object：对象 

- index：是否索引，默认为 true，也就是说你不进行任何配置，所有字段都会被索引。 

true：字段会被索引，则可以用来进行搜索 
false：字段不会被索引，不能用来搜索 

- store：是否将数据进行独立存储，默认为 false 

原始的文本会存储在_source 里面，默认情况下其他提取出来的字段都不是独立存储的，是从_source 里面提取出来的。当然你也可以独立的存储某个字段，只要设置 "store": true  即可，获取独立存储的字段要比从_source 中解析快得多，但是也会占用更多的空间，所以要根据实际业务需求来设置。 

- analyzer：分词器

### 2) 查看映射 
在 Postman 中，向 ES 服务器发 **GET **请求:[http://10.211.55.11:9200/user/_mapping](http://10.211.55.11:9200/user/_mapping)
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650160158293-bbb7a039-e333-40a3-9db6-ccf8dbbf9567.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=348&id=ucad1394a&margin=%5Bobject%20Object%5D&name=image.png&originHeight=348&originWidth=589&originalType=binary&ratio=1&rotation=0&showTitle=false&size=79124&status=done&style=none&taskId=u20c6236f-054d-49ed-9259-1f117aa26bc&title=&width=589)

### 3) 查询数据
```json
{
    "query":{
        "match":{
            "name":"小"
        }
    }
}
```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650160737757-a83824c4-c349-4e04-838e-82828d7c3c16.png#clientId=uc1b60b7a-85e5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=341&id=u53aa2714&margin=%5Bobject%20Object%5D&name=image.png&originHeight=341&originWidth=504&originalType=binary&ratio=1&rotation=0&showTitle=false&size=75299&status=done&style=none&taskId=u4dcdb3b8-e7b7-4efd-88a5-3941eb2115d&title=&width=504)
