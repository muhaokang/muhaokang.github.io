# 1. 下载软件 
Elasticsearch 的官方地址：https://www.elastic.co/cn/   
我选择 7.8.0 版本
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650104297306-9d9763e3-68c5-4ed5-8ad5-7d5bb0e00abc.png#clientId=ue5a300bb-fb59-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=237&id=uf5902fd6&margin=%5Bobject%20Object%5D&name=image.png&originHeight=237&originWidth=948&originalType=binary&ratio=1&rotation=0&showTitle=false&size=62248&status=done&style=none&taskId=u01cae41f-05ff-402d-b0e1-3618d575b74&title=&width=948)
# 2. 安装软件
## 2.1 将软件从本地上传到Linux
```shell
[mhk@hadoop102 software]$ ll

-rw-rw-r--. 1 mhk  mhk  319112561 3月  16 16:22 elasticsearch-7.8.0-linux-x86_64.tar.gz
```
## 2.2 解压缩到指定路径
```shell
[mhk@hadoop102 software]$ tar -zxvf elasticsearch-7.8.0-linux-x86_64.tar.gz -C /opt/module/
```
## 2.3 运行bin目录下的启动脚本
```shell
[mhk@hadoop102 elasticsearch-7.8.0]$ bin/elasticsearch
...
[2022-04-16T16:36:09,824][INFO ][o.e.h.AbstractHttpServerTransport] [hadoop102] publish_address {127.0.0.1:9200}, bound_addresses {[::1]:9200}, {127.0.0.1:9200}
[2022-04-16T16:36:09,826][INFO ][o.e.n.Node               ] [hadoop102] started
[2022-04-16T16:36:11,078][INFO ][o.e.l.LicenseService     ] [hadoop102] license [7ee9cff5-bb62-4949-b1b9-86535854a73e] mode [basic] - valid
[2022-04-16T16:36:11,081][INFO ][o.e.x.s.s.SecurityStatusChangeListener] [hadoop102] Active license is now [BASIC]; Security is disabled
[2022-04-16T16:36:11,391][INFO ][o.e.g.GatewayService     ] [hadoop102] recovered [0] indices into cluster_state
```
## 2.4 配置远程访问
打开 config/ 目录下的 elasticsearch.yml，修改配置
```shell
[mhk@hadoop102 elasticsearch-7.8.0]$ cd config/
[mhk@hadoop102 config]$ ll
总用量 40
-rw-rw----. 1 mhk mhk   199 4月  16 16:24 elasticsearch.keystore
-rw-rw----. 1 mhk mhk  2813 4月  16 17:16 elasticsearch.yml
-rw-rw----. 1 mhk mhk  2301 6月  15 2020 jvm.options
drwxr-x---. 2 mhk mhk     6 6月  15 2020 jvm.options.d
-rw-rw----. 1 mhk mhk 17419 6月  15 2020 log4j2.properties
-rw-rw----. 1 mhk mhk   473 6月  15 2020 role_mapping.yml
-rw-rw----. 1 mhk mhk   197 6月  15 2020 roles.yml
-rw-rw----. 1 mhk mhk     0 6月  15 2020 users
-rw-rw----. 1 mhk mhk     0 6月  15 2020 users_roles

[mhk@hadoop102 config]$ vim elasticsearch.yml

network.host: 0.0.0.0
```
再次运行启动脚本，发现报错
```shell
ERROR: [2] bootstrap checks failed
[1]: max file descriptors [4096] for elasticsearch process is too low, increase to at least [65535]
[2]: max virtual memory areas vm.max_map_count [65530] is too low, increase to at least [262144]
[3]: the default discovery settings are unsuitable for production use; at least one of [discovery.seed_hosts, discovery.seed_providers, cluster.initial_master_nodes] must be configured
ERROR: Elasticsearch did not exit normally - check the logs at /opt/module/elasticsearch-7.8.0/logs/elasticsearch.log
```
针对这三点，逐个击破
**1、Linux系统的soft、hard值配置过低，至少65535**
```shell
vim /etc/security/limits.conf
#*               soft    core            0
#*               hard    rss             10000
*               soft    nofile           65535
*               hard    nofile           65535
```
建议重启虚拟机

**2、Linux系统vm.max_map_count值配置过低，至少262144**
```shell
vim /etc/sysctl.conf
vm.max_map_count=262144
#sysctl -p   生效
[mhk@hadoop102 etc]$ sysctl -p
vm.max_map_count = 262144
```


**3、缺少默认配置**
至少需要配置 discovery.seed_hosts、discovery.seed_providers、cluster.initial_master_nodes 中的一个参数.

- discovery.seed_hosts:  集群主机列表
- discovery.seed_providers: 基于配置文件配置集群主机列表
- cluster.initial_master_nodes: 启动时初始化的参与选主的node，生产环境必填
```shell
vim config/elasticsearch.yml
 
 
#添加配置
discovery.seed_hosts: ["hadoop102"]

cluster.initial_master_nodes: ["hadoop102"]
```
## 2.5 重启软件，访问web界面
[http://10.211.55.11:9200/](http://10.211.55.11:9200/)
```shell
[mhk@hadoop102 elasticsearch-7.8.0]$ bin/elasticsearch
...
[2022-04-16T17:46:23,701][INFO ][o.e.h.AbstractHttpServerTransport] [hadoop102] publish_address {10.211.55.11:9200}, bound_addresses {[::]:9200}
[2022-04-16T17:46:23,725][INFO ][o.e.n.Node               ] [hadoop102] started
[2022-04-16T17:46:25,348][INFO ][o.e.l.LicenseService     ] [hadoop102] license [7ee9cff5-bb62-4949-b1b9-86535854a73e] mode [basic] - valid
[2022-04-16T17:46:25,352][INFO ][o.e.x.s.s.SecurityStatusChangeListener] [hadoop102] Active license is now [BASIC]; Security is disabled
[2022-04-16T17:46:25,496][INFO ][o.e.g.GatewayService     ] [hadoop102] recovered [0] indices into cluster_state
```
![D6AC1022D571B06B1EF0514B661464AA.jpg](https://cdn.nlark.com/yuque/0/2022/jpeg/25452040/1650105666436-348a2353-ebc1-4d33-9208-0bd4e31d51f2.jpeg#clientId=ue5a300bb-fb59-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=347&id=u4d6e7bef&margin=%5Bobject%20Object%5D&name=D6AC1022D571B06B1EF0514B661464AA.jpg&originHeight=347&originWidth=573&originalType=binary&ratio=1&rotation=0&showTitle=false&size=61398&status=done&style=none&taskId=u20db2931-a53b-47a4-b49f-89190919777&title=&width=573)
