# 1. 本地模式安装
## 1.1 安装前准备

1. 安装JDK
2. 官网下载apache-zookeeper-3.5.7-bin.tar.gz安装包，并拷贝到Linux系统下
2. 解压到指定目录
```shell
[mhk@hadoop102 software]$ tar -zxvf apache-zookeeper-3.5.7-bin.tar.gz -C /opt/module/
```

4. 修改名称
```shell
[mhk@hadoop102 module]$ mv apache-zookeeper-3.5.7-bin/ zookeeper-3.5.7
```
## 1.2 配置修改

1. 将/opt/module/zookeeper-3.5.7/conf 这个路径下的 zoo_sample.cfg 修改为 zoo.cfg；
```shell
[mhk@hadoop102 conf]$ mv zoo_sample.cfg zoo.cfg 
```

2. 在/opt/module/zookeeper-3.5.7下创建zkData目录
```shell
[mhk@hadoop102 zookeeper-3.5.7]$ mkdir zkData
[mhk@hadoop102 zookeeper-3.5.7]$ ll
总用量 32
drwxr-xr-x. 2 mhk mhk   232 2月  10 2020 bin
drwxr-xr-x. 2 mhk mhk    70 1月  10 16:44 conf
drwxr-xr-x. 5 mhk mhk  4096 2月  10 2020 docs
drwxrwxr-x. 2 mhk mhk  4096 1月  10 16:14 lib
-rw-r--r--. 1 mhk mhk 11358 9月  13 2018 LICENSE.txt
-rw-r--r--. 1 mhk mhk   432 2月  10 2020 NOTICE.txt
-rw-r--r--. 1 mhk mhk  1560 2月   7 2020 README.md
-rw-r--r--. 1 mhk mhk  1347 2月   7 2020 README_packaging.txt
drwxrwxr-x. 2 mhk mhk     6 1月  10 16:46 zkData
[mhk@hadoop102 zookeeper-3.5.7]$ cd zkData/
[mhk@hadoop102 zkData]$ pwd
/opt/module/zookeeper-3.5.7/zkData
```

3. 打开 zoo.cfg 文件，修改 dataDir 路径：
```shell
[mhk@hadoop102 conf]$ vim zoo.cfg 
```
修改如下内容：
```shell
dataDir=/opt/module/zookeeper-3.5.7/zkData
```
## 1.3 操作Zookeeper

1. 启动ZooKeeper
```shell
[mhk@hadoop102 zookeeper-3.5.7]$ bin/zkServer.sh start
ZooKeeper JMX enabled by default
Using config: /opt/module/zookeeper-3.5.7/bin/../conf/zoo.cfg
Starting zookeeper ... STARTED
```

2. 查看进程是否启动
```shell
[mhk@hadoop102 zookeeper-3.5.7]$ jps
1528 Jps
1497 QuorumPeerMain
```

3. 查看状态
```shell
[mhk@hadoop102 zookeeper-3.5.7]$ bin/zkServer.sh status
ZooKeeper JMX enabled by default
Using config: /opt/module/zookeeper-3.5.7/bin/../conf/zoo.cfg
Client port found: 2181. Client address: localhost.
Mode: standalone
```

4. 启动客户端
```shell
[mhk@hadoop102 zookeeper-3.5.7]$ bin/zkCli.sh 
```

5. 退出客户端
```shell
[zk: localhost:2181(CONNECTED) 0] quit

WATCHER::

WatchedEvent state:Closed type:None path:null
2022-01-10 16:55:54,486 [myid:] - INFO  [main:ZooKeeper@1422] - Session: 0x1000029b31f0000 closed
2022-01-10 16:55:54,486 [myid:] - INFO  [main-EventThread:ClientCnxn$EventThread@524] - EventThread shut down for session: 0x1000029b31f0000
[mhk@hadoop102 zookeeper-3.5.7]$ 
```

6. 停止ZooKeeper
```shell
[mhk@hadoop102 zookeeper-3.5.7]$ bin/zkServer.sh stop
ZooKeeper JMX enabled by default
Using config: /opt/module/zookeeper-3.5.7/bin/../conf/zoo.cfg
Stopping zookeeper ... STOPPED
[mhk@hadoop102 zookeeper-3.5.7]$ jps
1631 Jps
```
# 2. 配置参数解读
ZooKeeper中的配置文件zoo.cfg中参数含义解读如下：
​


1. tickTime = 2000：通信心跳时间，Zookeeper服务器与客户端心跳时间，单位毫秒，也就是2秒

![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1641805363736-e40f5e8e-ed06-42c3-b49a-5c84ae84d6bb.png#clientId=ub1b885a6-acc4-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=161&id=ua4d64f30&margin=%5Bobject%20Object%5D&name=image.png&originHeight=161&originWidth=688&originalType=binary&ratio=1&rotation=0&showTitle=false&size=44984&status=done&style=none&taskId=u0a27cecc-8603-4e51-89ab-283d2a3739f&title=&width=688)


2. initLimit = 10：LF初始通信时限

![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1641805410281-b98079a2-ccab-45d3-854b-a9fb0dc51fe6.png#clientId=ub1b885a6-acc4-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=114&id=u5ef3159e&margin=%5Bobject%20Object%5D&name=image.png&originHeight=114&originWidth=555&originalType=binary&ratio=1&rotation=0&showTitle=false&size=17348&status=done&style=none&taskId=ubaddd579-cc8d-4a7a-b9d7-4fa3f131131&title=&width=555)
Leader和Follower初始连接时能容忍的最多心跳数（tickTime的数量）如果在10*2秒=20秒内还没建立连接，就认为这次通信失败
​


3. syncLimit = 5：LF同步通信时限

![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1641805457327-03e75ec7-f5dc-45b2-9394-288d4e391078.png#clientId=ub1b885a6-acc4-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=114&id=ucff5f48f&margin=%5Bobject%20Object%5D&name=image.png&originHeight=114&originWidth=555&originalType=binary&ratio=1&rotation=0&showTitle=false&size=17348&status=done&style=none&taskId=uf85d2fb9-f305-4052-9bef-503f8792dcd&title=&width=555)
Leader和Follower之间通信时间如果超过syncLimit * tickTime，5*2秒=10秒，Leader认为Follwer死掉，从服务器列表中删除Follwer
​


4. dataDir：保存Zookeeper中的数据

注意：默认的tmp目录，容易被Linux系统定期删除，所以一般不用默认的tmp目录
​


5. clientPort = 2181：客户端连接端口，通常不做修改。

​

# 3. 集群操作
## 3.1 集群安装
### 3.1.1 集群规划
在 hadoop102、hadoop103 和 hadoop104 三个节点上都部署 Zookeeper。
​

思考：如果是 10 台服务器，需要部署多少台 Zookeeper？
安装奇数台
生产经验：
10 台服务器： 3 台 zk
20 台服务器： 5 台 zk
100 台服务器： 11 台 zk
200 台服务器： 11 台 zk
服务器台数多：好处，提高可靠性；坏处：提高通信延时
​

### 3.1.2 解压安装
见上文本地模式安装
​

### 3.1.3 配置服务器编号


（1）在/opt/module/zookeeper-3.5.7/zkData 目录下创建一个 myid 的文件
```shell
[mhk@hadoop102 zookeeper-3.5.7]$ cd zkData/
[mhk@hadoop102 zkData]$ vim myid
```
在文件中添加与 server 对应的编号（注意：上下不要有空行，左右不要有空格）
​

（2）拷贝配置好的 zookeeper 到其他机器上
```shell
[mhk@hadoop102 module]$ xsync zookeeper-3.5.7/
```
并分别在 hadoop103、hadoop104 上修改 myid 文件中内容为 3、4
```shell
[mhk@hadoop103 zkData]$ vim myid 
[mhk@hadoop103 zkData]$ cat myid 
3
```
```shell
[mhk@hadoop104 zkData]$ vim myid 
[mhk@hadoop104 zkData]$ cat myid 
4
```
​

### 3.1.4 配置zoo.cfg文件


（1）打开 zoo.cfg 文件，增加如下配置
```shell
#######################cluster##########################
server.2=hadoop102:2888:3888
server.3=hadoop103:2888:3888
server.4=hadoop104:2888:3888
```
（2）配置参数解读
```shell
server.A=B:C:D
```
A 是一个数字，表示这个是第几号服务器；
集群模式下配置一个文件 myid，这个文件在 dataDir 目录下，这个文件里面有一个数据
就是 A 的值，Zookeeper 启动时读取此文件，拿到里面的数据与 zoo.cfg 里面的配置信息比
较从而判断到底是哪个 server。
 B 是这个服务器的地址；
C 是这个服务器 Follower 与集群中的 Leader 服务器交换信息的端口；
D 是万一集群中的 Leader 服务器挂了，需要一个端口来重新进行选举，选出一个新的
Leader，而这个端口就是用来执行选举时服务器相互通信的端口。
​

（3）同步 zoo.cfg 配置文件
```shell
[mhk@hadoop102 ~]$ xsync zoo.cfg 
```


### 3.1.5 集群操作
（1）分别启动ZooKeeper
首先在hadoop102这台服务器上启动ZooKeeper，发现出现了error
```shell
[mhk@hadoop102 zookeeper-3.5.7]$ bin/zkServer.sh start
ZooKeeper JMX enabled by default
Using config: /opt/module/zookeeper-3.5.7/bin/../conf/zoo.cfg
Starting zookeeper ... STARTED
[mhk@hadoop102 zookeeper-3.5.7]$ bin/zkServer.sh status
ZooKeeper JMX enabled by default
Using config: /opt/module/zookeeper-3.5.7/bin/../conf/zoo.cfg
Client port found: 2181. Client address: localhost.
Error contacting service. It is probably not running.
```
		原因是只启动了一台，这有三台服务器，没有超过半数。没有超过半数，就不会选出对应的Leader，集群就没法工作
接着在hadoop103上启动ZooKeeper
```shell
[mhk@hadoop103 zookeeper-3.5.7]$ bin/zkServer.sh start
ZooKeeper JMX enabled by default
Using config: /opt/module/zookeeper-3.5.7/bin/../conf/zoo.cfg
Starting zookeeper ... STARTED
[mhk@hadoop103 zookeeper-3.5.7]$ bin/zkServer.sh status
ZooKeeper JMX enabled by default
Using config: /opt/module/zookeeper-3.5.7/bin/../conf/zoo.cfg
Client port found: 2181. Client address: localhost.
Mode: leader

[mhk@hadoop102 zookeeper-3.5.7]$ bin/zkServer.sh status
ZooKeeper JMX enabled by default
Using config: /opt/module/zookeeper-3.5.7/bin/../conf/zoo.cfg
Client port found: 2181. Client address: localhost.
Mode: follower
```
发现在103上选举出了Leader，接着检查102中的ZooKeeper的状态，发现变成了Follower
继续启动104上的ZooKeeper，不出意外，是Follower
```shell
[mhk@hadoop104 zookeeper-3.5.7]$ bin/zkServer.sh start
ZooKeeper JMX enabled by default
Using config: /opt/module/zookeeper-3.5.7/bin/../conf/zoo.cfg
Starting zookeeper ... STARTED
[mhk@hadoop104 zookeeper-3.5.7]$ bin/zkServer.sh status
ZooKeeper JMX enabled by default
Using config: /opt/module/zookeeper-3.5.7/bin/../conf/zoo.cfg
Client port found: 2181. Client address: localhost.
Mode: follower
```
​

## 3.2 ZooKeeper群起群停脚本
（1）在 hadoop102 的/home/mhk/bin 目录下创建脚本
```shell
[mhk@hadoop102 bin]$ vim zk.sh
```
在脚本中编写如下内容
```shell
#!/bin/bash
case $1 in
"start"){
   for i in hadoop102 hadoop103 hadoop104
   do
   
   echo ---------- zookeeper $i 启动 ------------
   ssh $i "/opt/module/zookeeper-3.5.7/bin/zkServer.sh start"
done
};;
"stop"){
   for i in hadoop102 hadoop103 hadoop104
   do
   
   echo ---------- zookeeper $i 停止 ------------
   ssh $i "/opt/module/zookeeper-3.5.7/bin/zkServer.sh stop"
done
};;
"status"){
   for i in hadoop102 hadoop103 hadoop104
   do
   
   echo ---------- zookeeper $i 状态 ------------
   ssh $i "/opt/module/zookeeper-3.5.7/bin/zkServer.sh status"
done
};;
esac
```
​

（2）增加脚本执行权限
```shell
[mhk@hadoop102 bin]$ chmod u+x zk.sh
```
（3）ZooKeeper集群启动脚本
```shell
[mhk@hadoop102 bin]$ zk.sh start
---------- zookeeper hadoop102 启动 ------------
ZooKeeper JMX enabled by default
Using config: /opt/module/zookeeper-3.5.7/bin/../conf/zoo.cfg
Starting zookeeper ... STARTED
---------- zookeeper hadoop103 启动 ------------
ZooKeeper JMX enabled by default
Using config: /opt/module/zookeeper-3.5.7/bin/../conf/zoo.cfg
Starting zookeeper ... STARTED
---------- zookeeper hadoop104 启动 ------------
ZooKeeper JMX enabled by default
Using config: /opt/module/zookeeper-3.5.7/bin/../conf/zoo.cfg
Starting zookeeper ... STARTED
[mhk@hadoop102 bin]$ jpsall 
=============== hadoop102 ===============
2152 QuorumPeerMain
=============== hadoop103 ===============
1837 QuorumPeerMain
=============== hadoop104 ===============
1867 QuorumPeerMain
```
​

（4）ZooKeeper集群停止脚本
```shell
[mhk@hadoop102 bin]$ zk.sh stop
---------- zookeeper hadoop102 停止 ------------
ZooKeeper JMX enabled by default
Using config: /opt/module/zookeeper-3.5.7/bin/../conf/zoo.cfg
Stopping zookeeper ... STOPPED
---------- zookeeper hadoop103 停止 ------------
ZooKeeper JMX enabled by default
Using config: /opt/module/zookeeper-3.5.7/bin/../conf/zoo.cfg
Stopping zookeeper ... STOPPED
---------- zookeeper hadoop104 停止 ------------
ZooKeeper JMX enabled by default
Using config: /opt/module/zookeeper-3.5.7/bin/../conf/zoo.cfg
Stopping zookeeper ... STOPPED
[mhk@hadoop102 bin]$ jpsall 
=============== hadoop102 ===============
=============== hadoop103 ===============
=============== hadoop104 ===============
```
