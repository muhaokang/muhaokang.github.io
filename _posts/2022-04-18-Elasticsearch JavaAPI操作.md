# 1. 创建Maven项目，添加依赖
```xml
<dependencies>
  <dependency>
    <groupId>org.elasticsearch</groupId>
    <artifactId>elasticsearch</artifactId>
    <version>7.8.0</version>
  </dependency>
  <!-- elasticsearch 的客户端 -->
  <dependency>
    <groupId>org.elasticsearch.client</groupId>
    <artifactId>elasticsearch-rest-high-level-client</artifactId>
    <version>7.8.0</version>
  </dependency>
  <!-- elasticsearch 依赖 2.x 的 log4j -->
  <dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-api</artifactId>
    <version>2.8.2</version>
  </dependency>
  <dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-core</artifactId>
    <version>2.8.2</version>
  </dependency>
  <dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
    <version>2.9.9</version>
  </dependency>
  <!-- junit 单元测试 -->
  <dependency>
    <groupId>junit</groupId>
    <artifactId>junit</artifactId>
    <version>4.12</version>
  </dependency>
    </dependencies>
```
# 2. 创建客户端对象
```java
public class ESTest_Client {
    public static void main(String[] args) throws IOException {
        
        //创建ES客户端
        RestHighLevelClient esClient = new RestHighLevelClient(
            RestClient.builder(new HttpHost("hadoop102",9200))
        );
        
        //关闭ES客户端
        esClient.close();
    }
}
```
# 3. 索引操作
## 3.1 创建索引
```java
public class ESTest_Index_Create {
    public static void main(String[] args) throws IOException {

        //创建ES客户端
        RestHighLevelClient esClient = new RestHighLevelClient(
                RestClient.builder(new HttpHost("hadoop102",9200))
        );

        //创建索引
        CreateIndexRequest request = new CreateIndexRequest("users");
        CreateIndexResponse response = esClient.indices().create(request, RequestOptions.DEFAULT);

        //响应状态
        boolean acknowledged = response.isAcknowledged();
        System.out.println("索引操作：" + acknowledged);

        //关闭ES客户端
        esClient.close();
    }
}
```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650183816531-d2cc52ac-6661-4351-b2c2-079af13266f3.png#clientId=u07a2aa4f-bdc4-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=152&id=u9a5210b3&margin=%5Bobject%20Object%5D&name=image.png&originHeight=152&originWidth=262&originalType=binary&ratio=1&rotation=0&showTitle=false&size=30537&status=done&style=none&taskId=u1afff7e4-f4b6-4068-99db-f069e6be1c4&title=&width=262)
前往postman查看有没有创建成功
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650183895823-f46ba04b-f6d8-4f00-82b7-0367a5cd451d.png#clientId=u07a2aa4f-bdc4-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=466&id=u1b727264&margin=%5Bobject%20Object%5D&name=image.png&originHeight=466&originWidth=857&originalType=binary&ratio=1&rotation=0&showTitle=false&size=130301&status=done&style=none&taskId=u9c153486-06c5-4244-8165-81085eaa4eb&title=&width=857)
## 3.2 查看索引
```java
public class ESTest_Index_Search {
    public static void main(String[] args) throws IOException {

        //创建ES客户端
        RestHighLevelClient esClient = new RestHighLevelClient(
                RestClient.builder(new HttpHost("hadoop102",9200))
        );

        //查询索引
        GetIndexRequest request = new GetIndexRequest("users");
        GetIndexResponse response = esClient.indices().get(request, RequestOptions.DEFAULT);

        //响应状态
        System.out.println(response.getAliases());
        System.out.println(response.getMappings());
        System.out.println(response.getSettings());

        //关闭ES客户端
        esClient.close();
    }
}
```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650184254886-3ad437b8-5069-4fef-bd2f-bb7a1f4f9189.png#clientId=u07a2aa4f-bdc4-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=156&id=u7f7cdcc3&margin=%5Bobject%20Object%5D&name=image.png&originHeight=156&originWidth=1364&originalType=binary&ratio=1&rotation=0&showTitle=false&size=55130&status=done&style=none&taskId=u38223c33-2f8c-435f-9258-afb96b31195&title=&width=1364)

## 3.3 删除索引
```java
public class ESTest_Index_Delete {
    public static void main(String[] args) throws IOException {

        //创建ES客户端
        RestHighLevelClient esClient = new RestHighLevelClient(
                RestClient.builder(new HttpHost("hadoop102",9200))
        );

        //查询索引
        DeleteIndexRequest request = new DeleteIndexRequest("users");
        AcknowledgedResponse response = esClient.indices().delete(request, RequestOptions.DEFAULT);

        //响应状态
        System.out.println(response.isAcknowledged());

        //关闭ES客户端
        esClient.close();
    }
}
```
前往postman确认
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650184528596-c296d47d-100f-4033-a30c-ea8e54a4759e.png#clientId=u07a2aa4f-bdc4-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=432&id=u1c0e6314&margin=%5Bobject%20Object%5D&name=image.png&originHeight=432&originWidth=857&originalType=binary&ratio=1&rotation=0&showTitle=false&size=110333&status=done&style=none&taskId=ufcc411fa-3a61-43d7-ac6f-f0764003376&title=&width=857)
已经被删除
# 4. 文档操作
## 4.1 新增文档
创建数据模型
```java
public class Users {
    private String name;
    private String sex;
    private Integer age;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getSex() {
        return sex;
    }

    public void setSex(String sex) {
        this.sex = sex;
    }

    public Integer getAge() {
        return age;
    }

    public void setAge(Integer age) {
        this.age = age;
    }
}
```
```java
public class ESTest_Doc_Insert {
    public static void main(String[] args) throws IOException {

        //创建ES客户端
        RestHighLevelClient esClient = new RestHighLevelClient(
                RestClient.builder(new HttpHost("hadoop102",9200))
        );

        //插入数据
        IndexRequest request = new IndexRequest();
        request.index("users").id("1001");

        Users users = new Users();
        users.setName("zhangsan");
        users.setAge(22);
        users.setSex("男");

        //向ES插入数据，必须将数据转换成JSON格式
        ObjectMapper mapper = new ObjectMapper();
        String usersJson = mapper.writeValueAsString(users);
        request.source(usersJson, XContentType.JSON);

        IndexResponse response = esClient.index(request, RequestOptions.DEFAULT);
        System.out.println(response.getResult());

        //关闭ES客户端
        esClient.close();
    }
}
```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650185316904-3c444319-f8f0-49c0-86e1-e96e9133a98f.png#clientId=u07a2aa4f-bdc4-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=106&id=ud9f38235&margin=%5Bobject%20Object%5D&name=image.png&originHeight=106&originWidth=254&originalType=binary&ratio=1&rotation=0&showTitle=false&size=19218&status=done&style=none&taskId=uebf654c0-c56e-4a0d-bb21-05ac8ead076&title=&width=254)
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650185379566-551d1112-a830-4350-ae3f-d53c785399f1.png#clientId=u07a2aa4f-bdc4-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=609&id=u8c7918ee&margin=%5Bobject%20Object%5D&name=image.png&originHeight=609&originWidth=848&originalType=binary&ratio=1&rotation=0&showTitle=false&size=145223&status=done&style=none&taskId=ueceebec0-ad4a-4bd2-b11f-3a5daf37341&title=&width=848)
## 4.2 修改文档
```java
public class ESTest_Doc_Update {
    public static void main(String[] args) throws IOException {
        //创建ES客户端
        RestHighLevelClient esClient = new RestHighLevelClient(
                RestClient.builder(new HttpHost("hadoop102",9200))
        );

        //修改数据
        UpdateRequest request = new UpdateRequest();
        request.index("users").id("1001");
        request.doc(XContentType.JSON,"name","李四");

        UpdateResponse response = esClient.update(request, RequestOptions.DEFAULT);
        
        System.out.println(response.getResult());

        //关闭ES客户端
        esClient.close();
    }
}
```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650185689525-582bd844-0e06-44ad-b9b2-61b77470f095.png#clientId=u07a2aa4f-bdc4-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=140&id=u672201ec&margin=%5Bobject%20Object%5D&name=image.png&originHeight=140&originWidth=270&originalType=binary&ratio=1&rotation=0&showTitle=false&size=35133&status=done&style=none&taskId=ucef688e9-0cf3-4208-94c7-38919469772&title=&width=270)
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650185717490-d1e3ad06-ddc5-44d4-8f78-5ade462964bf.png#clientId=u07a2aa4f-bdc4-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=614&id=u52119739&margin=%5Bobject%20Object%5D&name=image.png&originHeight=614&originWidth=892&originalType=binary&ratio=1&rotation=0&showTitle=false&size=151461&status=done&style=none&taskId=u29622791-c247-4372-a8e1-b45444d0c51&title=&width=892)
## 4.3 查询文档
```java
public class ESTest_Doc_Get {
    public static void main(String[] args) throws IOException {
        //创建ES客户端
        RestHighLevelClient esClient = new RestHighLevelClient(
                RestClient.builder(new HttpHost("hadoop102",9200))
        );

        //查询数据
        GetRequest request = new GetRequest();
        request.index("users").id("1001");

        GetResponse response = esClient.get(request, RequestOptions.DEFAULT);

        System.out.println(response.getSourceAsString());

        //关闭ES客户端
        esClient.close();
    }
}
```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650186106311-cbe9950f-66c9-4acb-8be6-5ad0f23582d1.png#clientId=u07a2aa4f-bdc4-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=128&id=u49e995bb&margin=%5Bobject%20Object%5D&name=image.png&originHeight=128&originWidth=317&originalType=binary&ratio=1&rotation=0&showTitle=false&size=26659&status=done&style=none&taskId=uaf9b2f6d-5e98-4af4-bf5e-62bee0273e9&title=&width=317)
## 4.4 删除文档
```java
public class ESTest_Doc_Delete {
    public static void main(String[] args) throws IOException {
        //创建ES客户端
        RestHighLevelClient esClient = new RestHighLevelClient(
                RestClient.builder(new HttpHost("hadoop102",9200))
        );

        DeleteRequest request = new DeleteRequest();
        request.index("users").id("1001");

        DeleteResponse response = esClient.delete(request, RequestOptions.DEFAULT);

        System.out.println(response.toString());

        //关闭ES客户端
        esClient.close();
    }
}
```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650186304855-39fecc60-91f2-4c20-85dd-ef070855df21.png#clientId=u07a2aa4f-bdc4-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=158&id=u4817785f&margin=%5Bobject%20Object%5D&name=image.png&originHeight=158&originWidth=1077&originalType=binary&ratio=1&rotation=0&showTitle=false&size=43808&status=done&style=none&taskId=uae403df3-f58a-4b36-8763-a5187f85c81&title=&width=1077)
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650186617326-60f806ce-57bc-4e1a-9162-cc8daa6c738e.png#clientId=u07a2aa4f-bdc4-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=488&id=u714d4c9a&margin=%5Bobject%20Object%5D&name=image.png&originHeight=488&originWidth=855&originalType=binary&ratio=1&rotation=0&showTitle=false&size=106668&status=done&style=none&taskId=u36f90e11-69bb-45b7-a813-26d0df649ca&title=&width=855)
## 4.5 批量新增
```java
public class ESTest_Doc_Insert_Batch {
    public static void main(String[] args) throws IOException {

        //创建ES客户端
        RestHighLevelClient esClient = new RestHighLevelClient(
                RestClient.builder(new HttpHost("hadoop102",9200))
        );

        //批量插入数据
        BulkRequest request = new BulkRequest();
        request.add(new IndexRequest().index("users").id("1001").source(XContentType.JSON,"name","张三"));
        request.add(new IndexRequest().index("users").id("1002").source(XContentType.JSON,"name","李四"));
        request.add(new IndexRequest().index("users").id("1003").source(XContentType.JSON,"name","王五"));

        BulkResponse response = esClient.bulk(request, RequestOptions.DEFAULT);
        System.out.println(response.getTook());
        System.out.println(response.getItems());

        //关闭ES客户端
        esClient.close();
    }
}
```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650186873748-5ef31e90-643b-46c2-ad6a-dd572158ece9.png#clientId=u07a2aa4f-bdc4-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=168&id=u77c1ebab&margin=%5Bobject%20Object%5D&name=image.png&originHeight=168&originWidth=538&originalType=binary&ratio=1&rotation=0&showTitle=false&size=43423&status=done&style=none&taskId=uaed466f9-f537-4ff2-a852-ae2d4c22981&title=&width=538)
## 4.6 批量删除
```java
public class ESTest_Doc_Delete_Batch {
    public static void main(String[] args) throws IOException {

        //创建ES客户端
        RestHighLevelClient esClient = new RestHighLevelClient(
                RestClient.builder(new HttpHost("hadoop102",9200))
        );

        //批量删除数据
        BulkRequest request = new BulkRequest();

        request.add(new DeleteRequest().index("user").id("1001"));
        request.add(new DeleteRequest().index("user").id("1002"));
        request.add(new DeleteRequest().index("user").id("1003"));
        BulkResponse response = esClient.bulk(request, RequestOptions.DEFAULT);
        System.out.println(response.getTook());
        System.out.println(response.getItems());

        //关闭ES客户端
        esClient.close();
    }
}
```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650187801034-f6ee3f41-e6e1-4479-bc5c-1e5e0d557b89.png#clientId=u07a2aa4f-bdc4-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=157&id=u4aa7bdc7&margin=%5Bobject%20Object%5D&name=image.png&originHeight=157&originWidth=521&originalType=binary&ratio=1&rotation=0&showTitle=false&size=41566&status=done&style=none&taskId=uc74f95dc-3e5b-4d6b-8904-b95c252c352&title=&width=521)
## 4.7 全量查询
```java
public class ESTest_Doc_Query {
    public static void main(String[] args) throws IOException {
        //创建ES客户端
        RestHighLevelClient esClient = new RestHighLevelClient(
                RestClient.builder(new HttpHost("hadoop102",9200))
        );

        //全量查询
        SearchRequest request = new SearchRequest();
        request.indices("users");

        //构造查询条件
        request.source(new SearchSourceBuilder().query(QueryBuilders.matchAllQuery()));

        SearchResponse response = esClient.search(request, RequestOptions.DEFAULT);

        SearchHits hits = response.getHits();

        System.out.println(response.getTook());
        System.out.println(hits.getTotalHits());

        for (SearchHit hit : hits) {
            System.out.println(hit.getSourceAsString());
        }

        //关闭ES客户端
        esClient.close();
    }
}
```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650189384212-4e018894-bb73-4bc3-b695-a807928d31bf.png#clientId=u07a2aa4f-bdc4-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=242&id=u76598ca5&margin=%5Bobject%20Object%5D&name=image.png&originHeight=242&originWidth=441&originalType=binary&ratio=1&rotation=0&showTitle=false&size=67473&status=done&style=none&taskId=u9901cc81-9fb5-4831-90b4-1cf5dc5ce2a&title=&width=441)

## 4.8 条件查询
```java
        SearchRequest request = new SearchRequest();
        request.indices("users");

        //构造查询条件termQuery
        request.source(new SearchSourceBuilder().query(QueryBuilders.termQuery("age",30)));

        SearchResponse response = esClient.search(request, RequestOptions.DEFAULT);

        SearchHits hits = response.getHits();

        System.out.println(response.getTook());
        System.out.println(hits.getTotalHits());

        for (SearchHit hit : hits) {
            System.out.println(hit.getSourceAsString());
        }

```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650194676495-fb444355-e4d0-4573-ab6b-fe34bb57d122.png#clientId=u07a2aa4f-bdc4-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=147&id=u8103eab7&margin=%5Bobject%20Object%5D&name=image.png&originHeight=147&originWidth=344&originalType=binary&ratio=1&rotation=0&showTitle=false&size=35204&status=done&style=none&taskId=u28111a02-7224-44bb-900f-bc1ad8a5414&title=&width=344)
## 4.9 分页查询
```java
        SearchRequest request = new SearchRequest();
        request.indices("users");

        //构造查询条件
        SearchSourceBuilder builder = new SearchSourceBuilder().query(QueryBuilders.matchAllQuery());
        //（当前页码-1）* 每页显示的条数
        builder.from(0);
        builder.size(2);    //每页两条数据
        request.source(builder);

        SearchResponse response = esClient.search(request, RequestOptions.DEFAULT);

        SearchHits hits = response.getHits();

        System.out.println(response.getTook());
        System.out.println(hits.getTotalHits());

        for (SearchHit hit : hits) {
            System.out.println(hit.getSourceAsString());
        }
```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650194954705-7407ac78-7fc5-41ef-bbc1-2e843ce69c29.png#clientId=u07a2aa4f-bdc4-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=147&id=u5d62caa0&margin=%5Bobject%20Object%5D&name=image.png&originHeight=147&originWidth=335&originalType=binary&ratio=1&rotation=0&showTitle=false&size=35969&status=done&style=none&taskId=ucd05ecfb-3593-4262-a835-851239551c4&title=&width=335)
## 4.10 查询排序
```java
        SearchRequest request = new SearchRequest();
        request.indices("users");

        //构造查询条件
        SearchSourceBuilder builder = new SearchSourceBuilder().query(QueryBuilders.matchAllQuery());
        builder.sort("age", SortOrder.DESC);
        request.source(builder);

        SearchResponse response = esClient.search(request, RequestOptions.DEFAULT);

        SearchHits hits = response.getHits();

        System.out.println(response.getTook());
        System.out.println(hits.getTotalHits());

        for (SearchHit hit : hits) {
            System.out.println(hit.getSourceAsString());
        }

```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650195272387-9b7b2db6-15d0-4692-a6e6-7fab9e3dee75.png#clientId=u07a2aa4f-bdc4-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=228&id=u8b0a405e&margin=%5Bobject%20Object%5D&name=image.png&originHeight=228&originWidth=428&originalType=binary&ratio=1&rotation=0&showTitle=false&size=65523&status=done&style=none&taskId=u0d773968-bdb8-49aa-9b40-aa55b6b1f0e&title=&width=428)
## 4.11 过滤字段
```java
        SearchRequest request = new SearchRequest();
        request.indices("users");

        //构造查询条件
        SearchSourceBuilder builder = new SearchSourceBuilder().query(QueryBuilders.matchAllQuery());

        String[] excludes = {};
        String[] includes = {"name"};
        builder.fetchSource(includes,excludes);

        request.source(builder);

        SearchResponse response = esClient.search(request, RequestOptions.DEFAULT);

        SearchHits hits = response.getHits();

        System.out.println(response.getTook());
        System.out.println(hits.getTotalHits());

        for (SearchHit hit : hits) {
            System.out.println(hit.getSourceAsString());
        }
```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650195509585-e8c06695-9c3e-49c6-b237-0a1d98c719ce.png#clientId=u07a2aa4f-bdc4-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=226&id=ub3fa1fce&margin=%5Bobject%20Object%5D&name=image.png&originHeight=226&originWidth=332&originalType=binary&ratio=1&rotation=0&showTitle=false&size=49881&status=done&style=none&taskId=u604bb4b0-a6fe-44cb-a6d2-9a7383e01bc&title=&width=332)
## 4.11 组合查询
```java
        //6. 组合查询
        SearchRequest request = new SearchRequest();
        request.indices("users");

        //构造查询条件
        SearchSourceBuilder builder = new SearchSourceBuilder();
        BoolQueryBuilder boolQueryBuilder = QueryBuilders.boolQuery();
//        boolQueryBuilder.must(QueryBuilders.matchQuery("age",30));
//        boolQueryBuilder.must(QueryBuilders.matchQuery("sex","男"));
//        boolQueryBuilder.mustNot(QueryBuilders.matchQuery("sex","男"));
        boolQueryBuilder.should(QueryBuilders.matchQuery("age",30));
        boolQueryBuilder.should(QueryBuilders.matchQuery("age",40));

        builder.query(boolQueryBuilder);
        
        request.source(builder);

        SearchResponse response = esClient.search(request, RequestOptions.DEFAULT);

        SearchHits hits = response.getHits();

        System.out.println(response.getTook());
        System.out.println(hits.getTotalHits());

        for (SearchHit hit : hits) {
            System.out.println(hit.getSourceAsString());
        }

```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650203258060-224e5d64-dd19-4ced-9b07-29416b4c985c.png#clientId=u07a2aa4f-bdc4-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=216&id=u559fd42f&margin=%5Bobject%20Object%5D&name=image.png&originHeight=216&originWidth=368&originalType=binary&ratio=1&rotation=0&showTitle=false&size=60729&status=done&style=none&taskId=u2d312d52-b9ca-449e-aab8-d6113099de8&title=&width=368)
## 4.12 范围查询
```java
        //7. 范围查询
        SearchRequest request = new SearchRequest();
        request.indices("users");

        //构造查询条件
        SearchSourceBuilder builder = new SearchSourceBuilder();
        RangeQueryBuilder rangeQuery = QueryBuilders.rangeQuery("age");

        rangeQuery.gte(30);
        rangeQuery.lte(40);

        builder.query(rangeQuery);

        request.source(builder);

        SearchResponse response = esClient.search(request, RequestOptions.DEFAULT);

        SearchHits hits = response.getHits();

        System.out.println(response.getTook());
        System.out.println(hits.getTotalHits());

        for (SearchHit hit : hits) {
            System.out.println(hit.getSourceAsString());
        }
```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650203466989-c8596755-efa6-481d-be49-5c66cc331000.png#clientId=u07a2aa4f-bdc4-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=253&id=ufc39ad6d&margin=%5Bobject%20Object%5D&name=image.png&originHeight=253&originWidth=383&originalType=binary&ratio=1&rotation=0&showTitle=false&size=67284&status=done&style=none&taskId=u8265ac81-1c76-43ca-9bc4-e0fb2dc2417&title=&width=383)
## 4.13 模糊查询
```java
        //7. 模糊查询
        SearchRequest request = new SearchRequest();
        request.indices("users");

        //构造查询条件
        SearchSourceBuilder builder = new SearchSourceBuilder();
        FuzzyQueryBuilder fuzziness = QueryBuilders.fuzzyQuery("name", "王五").fuzziness(Fuzziness.ONE);//差一个字符

        builder.query(fuzziness);

        request.source(builder);

        SearchResponse response = esClient.search(request, RequestOptions.DEFAULT);

        SearchHits hits = response.getHits();

        System.out.println(response.getTook());
        System.out.println(hits.getTotalHits());

        for (SearchHit hit : hits) {
            System.out.println(hit.getSourceAsString());
        }
```
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650203904064-4fd2c21c-e001-4127-9a97-7ad15ed84113.png#clientId=u07a2aa4f-bdc4-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=184&id=uda951b44&margin=%5Bobject%20Object%5D&name=image.png&originHeight=184&originWidth=355&originalType=binary&ratio=1&rotation=0&showTitle=false&size=48437&status=done&style=none&taskId=u48ff9f02-ec88-487e-a55b-7fafdb9947a&title=&width=355)
## 4.14 高亮查询
```java
       //8. 高亮查询
        SearchRequest request = new SearchRequest();
        request.indices("users");

        //构造查询条件
        SearchSourceBuilder builder = new SearchSourceBuilder();
        TermQueryBuilder termQueryBuilder = QueryBuilders.termQuery("name", "张三");

        HighlightBuilder highlightBuilder = new HighlightBuilder();
        highlightBuilder.preTags("<font color ='red'>");
        highlightBuilder.postTags("</font>");
        highlightBuilder.field("name");

        builder.highlighter(highlightBuilder);
        builder.query(termQueryBuilder);

        request.source(builder);

        SearchResponse response = esClient.search(request, RequestOptions.DEFAULT);

        SearchHits hits = response.getHits();

        System.out.println(response.getTook());
        System.out.println(hits.getTotalHits());

        for (SearchHit hit : hits) {
            System.out.println(hit.getSourceAsString());
        }
```
## 4.15 聚合查询
```java
        //9. 聚合查询
        SearchRequest request = new SearchRequest();
        request.indices("users");

        //构造查询条件
        SearchSourceBuilder builder = new SearchSourceBuilder();
        AggregationBuilder aggregationBuilder = AggregationBuilders.max("maxAge").field("age");

        builder.aggregation(aggregationBuilder);

        request.source(builder);

        SearchResponse response = esClient.search(request, RequestOptions.DEFAULT);

        SearchHits hits = response.getHits();

        System.out.println(response.getTook());
        System.out.println(hits.getTotalHits());

        for (SearchHit hit : hits) {
            System.out.println(hit.getSourceAsString());
        }
```
## 4.16 分组查询
```java
        //10. 分组查询
        SearchRequest request = new SearchRequest();
        request.indices("users");

        //构造查询条件
        SearchSourceBuilder builder = new SearchSourceBuilder();
        AggregationBuilder aggregationBuilder = AggregationBuilders.terms("ageGroup").field("age");

        builder.aggregation(aggregationBuilder);

        request.source(builder);

        SearchResponse response = esClient.search(request, RequestOptions.DEFAULT);

        SearchHits hits = response.getHits();

        System.out.println(response.getTook());
        System.out.println(hits.getTotalHits());

        for (SearchHit hit : hits) {
            System.out.println(hit.getSourceAsString());
        }
```
