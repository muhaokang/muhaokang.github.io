# 1. 事先提醒
首先准备安装包，然后重新解压
万万不可将hadoop102节点上的 elasticsearch-7.8.0/ 分发到其他节点，这样会导致集群中只有hadoop102这一个节点，因为我们本来部署单点模式的时候用了es做了好多次案例，es会存储data

# 2. 解压压缩包
```shell
[mhk@hadoop102 software]$ tar -zxvf elasticsearch-7.8.0-linux-x86_64.tar.gz -C /opt/module/
```
分发
```shell
[mhk@hadoop102 module]$ xsync elasticsearch-7.8.0/
```
# 3. 修改配置文件
修改/opt/module/es/config/elasticsearch.yml 文件，分发文件
```yaml
#集群名称
cluster.name: cluster-es

#节点名称，每个节点的名称不能重复
node.name: node-1

#ip 地址，每个节点的地址不能重复
network.host: hadoop102

#是不是有资格主节点
node.master: true
node.data: true
http.port: 9200

# head 插件需要这打开这两个配置
http.cors.allow-origin: "*"
http.cors.enabled: true
http.max_content_length: 200mb

#es7.x 之后新增的配置，初始化一个新的集群时需要此配置来选举 master
cluster.initial_master_nodes: ["node-1"]

#es7.x 之后新增的配置，节点发现
discovery.seed_hosts: ["hadoop102:9300","hadoop103:9300","hadoop104:9300"]
gateway.recover_after_nodes: 2
network.tcp.keep_alive: true
network.tcp.no_delay: true
transport.tcp.compress: true

#集群内同时启动的数据任务个数，默认是 2 个
cluster.routing.allocation.cluster_concurrent_rebalance: 16

#添加或删除节点及负载均衡时并发恢复的线程个数，默认 4 个
cluster.routing.allocation.node_concurrent_recoveries: 16

#初始化数据恢复时，并发恢复线程的个数，默认 4 个
cluster.routing.allocation.node_initial_primaries_recoveries: 16
```
分发后，hadoop102，hadoop103两台节点修改名称和地址


修改/etc/security/limits.conf ，分发文件
```yaml
* 	 soft 		nofile 		65536
*		 hard 		nofile 		65536
```

修改/etc/security/limits.d/20-nproc.conf，分发文件
```yaml
# 在文件末尾中增加下面内容
* 		soft 		nofile 		65536
* 		hard 		nofile 		65536
* 		hard 		nproc 		4096
# 注：* 带表 Linux 所有用户名称
```

修改/etc/sysctl.conf
```yaml
vm.max_map_count=655360
```

重新加载 
```yaml
sysctl -p 
```
# 
# 4. 启动软件 
分别在不同节点上启动 ES 软件
```yaml
cd /opt/module/elasticsearch-7.8.0
#启动
bin/elasticsearch
#后台启动
bin/elasticsearch -d
```

# 5. 测试集群
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650243878054-0039055f-bd88-4d08-8b2c-7687ec90c273.png#clientId=u460153c8-e799-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=447&id=u817cff25&margin=%5Bobject%20Object%5D&name=image.png&originHeight=447&originWidth=855&originalType=binary&ratio=1&rotation=0&showTitle=false&size=102908&status=done&style=none&taskId=u63a951be-61d3-4bb8-8950-10f9933b849&title=&width=855)
