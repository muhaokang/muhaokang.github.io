# 1. 概念


1. ZooKeeper主要是文件系统和通知机制
- 文件系统主要是用来存储数据
- 通知机制主要是服务器或者客户端进行通知，并且监督



​


2. ZooKeeper特点

![截屏2022-01-11 上午10.49.39.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1641869407976-2c366670-db8c-404a-910a-7c3d0f510410.png#clientId=uac4bbb28-ce3a-4&crop=0&crop=0&crop=1&crop=1&from=ui&id=ube58247b&margin=%5Bobject%20Object%5D&name=%E6%88%AA%E5%B1%8F2022-01-11%20%E4%B8%8A%E5%8D%8810.49.39.png&originHeight=379&originWidth=1230&originalType=binary&ratio=1&rotation=0&showTitle=false&size=101464&status=done&style=none&taskId=u6f8e5540-30b2-4c83-80da-3fe1cee10a7&title=)

- 一个leader，多个follower的集群
- 集群只要有半数以上包括半数就可正常服务，一般安装奇数台服务器
- 全局数据一致，每个Server保存一份相同的数据副本，Client无论连接到哪个Server，数据都是一致的。 
- 更新的请求顺序保持顺序，来自同一个Client的更新请求按其发送顺序依次执行。
- 数据更新的原子性，数据要么成功要么失败
- 数据实时更新性很快，在一定时间范围内，Client能读到最新数据。 

​


3. 主要的集群步骤为

![截屏2022-01-10 下午9.09.59.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1641820216424-152edfe5-fc93-4ac7-8847-2b6b15ca52fb.png#clientId=uac4bbb28-ce3a-4&crop=0&crop=0&crop=1&crop=1&from=ui&id=u255aef42&margin=%5Bobject%20Object%5D&name=%E6%88%AA%E5%B1%8F2022-01-10%20%E4%B8%8B%E5%8D%889.09.59.png&originHeight=611&originWidth=1101&originalType=binary&ratio=1&rotation=0&showTitle=false&size=217169&status=done&style=none&taskId=u149660b8-89b7-4c5f-97e0-689b570bfbc&title=)
（1）服务器启动时去注册信息（创建的都是临时节点）
（2）客户端获得到当前在线服务器列表，并进行监听
（3）服务器节点下线
（4）服务器节点上下线事件通知
（5）process(){客户端重新再去获取服务器列表，并注册监听}
​


4. 数据结构  

ZooKeeper 数据模型的结构与 Unix 文件系统很类似，整体上可以看作是一棵树，每个节点称做一个ZNode。
每一个 ZNode 默认能够存储 1MB 的数据，每个 ZNode 都可以通过其路径唯一标识。
![截屏2022-01-11 上午11.07.31.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1641870506115-614f8c43-6960-428d-90d7-b24ac0a45c15.png#clientId=uac4bbb28-ce3a-4&crop=0&crop=0&crop=1&crop=1&from=ui&id=u183c3ff0&margin=%5Bobject%20Object%5D&name=%E6%88%AA%E5%B1%8F2022-01-11%20%E4%B8%8A%E5%8D%8811.07.31.png&originHeight=368&originWidth=1000&originalType=binary&ratio=1&rotation=0&showTitle=false&size=52428&status=done&style=none&taskId=u9425e09a-a6da-4c65-8b94-60b8b97e3bf&title=)


5. 应用场景

提供的服务包括：统一命名服务、统一配置管理、统一集群管理、服务器节点动态上下线、软负载均衡等。
​

（1）统一命名服务（域名服务）
![截屏2022-01-11 上午11.20.24.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1641871240471-ab476752-0f9b-4aa5-80c5-e5d0e0d47cb9.png#clientId=uac4bbb28-ce3a-4&crop=0&crop=0&crop=1&crop=1&from=ui&id=u571045b9&margin=%5Bobject%20Object%5D&name=%E6%88%AA%E5%B1%8F2022-01-11%20%E4%B8%8A%E5%8D%8811.20.24.png&originHeight=538&originWidth=1012&originalType=binary&ratio=1&rotation=0&showTitle=false&size=94931&status=done&style=none&taskId=u5c0a72ab-b703-4b0a-8425-3473305c27d&title=)




（2）统一配置管理（一个集群中的所有配置都一致，且也要实时更新同步）
	  将配置信息写入ZooKeeper上的一个Znode，各个客户端服务器监听这个Znode。一旦Znode中的数据被修改，ZooKeeper将通知各个客户端服务器
![截屏2022-01-11 上午11.21.12.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1641871286935-1f2966bd-09b9-4567-a0a4-7343ebdc4689.png#clientId=uac4bbb28-ce3a-4&crop=0&crop=0&crop=1&crop=1&from=ui&id=u68c53c2b&margin=%5Bobject%20Object%5D&name=%E6%88%AA%E5%B1%8F2022-01-11%20%E4%B8%8A%E5%8D%8811.21.12.png&originHeight=550&originWidth=1031&originalType=binary&ratio=1&rotation=0&showTitle=false&size=134374&status=done&style=none&taskId=u6b6f7647-1126-4daa-be94-b2975c56268&title=)




（3）统一集群管理（掌握实时状态）
将节点信息写入ZooKeeper上的一个ZNode。监听ZNode获取实时状态变化
![截屏2022-01-11 上午11.21.50.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1641871324056-0634d724-ca76-46a9-ae8c-eaef47c68198.png#clientId=uac4bbb28-ce3a-4&crop=0&crop=0&crop=1&crop=1&from=ui&id=fTftd&margin=%5Bobject%20Object%5D&name=%E6%88%AA%E5%B1%8F2022-01-11%20%E4%B8%8A%E5%8D%8811.21.50.png&originHeight=512&originWidth=1010&originalType=binary&ratio=1&rotation=0&showTitle=false&size=112231&status=done&style=none&taskId=ub26df8b3-6d00-47c9-bd2c-20ac0736356&title=)


（4）软负载均衡（根据每个节点的访问数，让访问数最少的服务器处理最新的数据需求）
![截屏2022-01-11 上午11.23.36.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1641871433413-05a309dc-29ae-40b1-89f0-accd4aad9727.png#clientId=uac4bbb28-ce3a-4&crop=0&crop=0&crop=1&crop=1&from=ui&id=u3b9b300d&margin=%5Bobject%20Object%5D&name=%E6%88%AA%E5%B1%8F2022-01-11%20%E4%B8%8A%E5%8D%8811.23.36.png&originHeight=551&originWidth=1009&originalType=binary&ratio=1&rotation=0&showTitle=false&size=105327&status=done&style=none&taskId=uf1e53f1f-6c5a-4674-b9c6-1a3b5d96592&title=)




（5）服务器节点动态上下线
![截屏2022-01-11 上午11.22.22.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1641871357964-b4f13cb0-3048-4bb2-8981-c2ac93e6eb1f.png#clientId=uac4bbb28-ce3a-4&crop=0&crop=0&crop=1&crop=1&from=ui&id=ua99deb28&margin=%5Bobject%20Object%5D&name=%E6%88%AA%E5%B1%8F2022-01-11%20%E4%B8%8A%E5%8D%8811.22.22.png&originHeight=571&originWidth=1015&originalType=binary&ratio=1&rotation=0&showTitle=false&size=153765&status=done&style=none&taskId=u9e5fe7c3-dd33-4702-be5c-ca6901f8e07&title=)




# 2. 部署安装
[https://www.yuque.com/jike195muhaokang/gdvqbd/ih9gfh](https://www.yuque.com/jike195muhaokang/gdvqbd/ih9gfh)
​

# 3. ZooKeeper集群操作
## 3.1 集群操作
[https://www.yuque.com/jike195muhaokang/gdvqbd/ih9gfh](https://www.yuque.com/jike195muhaokang/gdvqbd/ih9gfh)


## 3.2 客户端命令行操作
### 3.2.1 常用命令
启动客户端的时候默认是本地的localhost
如果要启动专门的服务器
启动客户端的时候后缀要加上 bin/zkCli.sh - server 服务器名:2182
例如：启动客户端，显示所有命令操作
```shell
[mhk@hadoop102 zookeeper-3.5.7]$ bin/zkCli.sh -server hadoop102:2181
...
[zk: hadoop102:2181(CONNECTED) 0] 
[zk: hadoop102:2181(CONNECTED) 0] help
```
​


| 命令基本语法 | 功能描述 |
| --- | --- |
| help | 显示所以操作命令 |
| ls path | 使用 ls 命令来查看当前znode的子节点[可监听]
-w  监听子节点变化
-s    附加次级信息 |
| create | 普通创建
-s  含有序列
-e  临时（重启或者超时消失） |
| get path | 获得节点的值[可监听]
-w 监听节点内容变化
-s  附加次级信息 |
| set | 设置节点的具体值 |
| stat | 查看节点状态 |
| delete | 删除节点 |
| deleteall | 递归删除节点 |





### 3.2.2 znode 节点数据信息 
**1）查看当前znode中所包含的内容 **
```shell
[zk: hadoop102:2181(CONNECTED) 1] ls /
[zookeeper]
```
**2）查看当前节点详细数据**
```shell
[zk: hadoop102:2181(CONNECTED) 2] ls -s /
[zookeeper]cZxid = 0x0
ctime = Thu Jan 01 08:00:00 CST 1970
mZxid = 0x0
mtime = Thu Jan 01 08:00:00 CST 1970
pZxid = 0x0
cversion = -1
dataVersion = 0
aclVersion = 0
ephemeralOwner = 0x0
dataLength = 0
numChildren = 1
```
（1）cZxid：创建节点的事务 Zxid
每次修改 ZooKeeper 状态都会产生一个 ZooKeeper 事务 ID。事务 ID 是 ZooKeeper 中所有修改总的次序。每次修改都有唯一的 zxid，如果 zxid1 小于 zxid2，那么 zxid1 在 zxid2 之前发生。
（2）ctime：znode 被创建的毫秒数（从 1970 年开始）
（3）mZxid：znode 最后更新的事务 Zxid
（4）mtime：znode 最后修改的毫秒数（从 1970 年开始）
（5）pZxid：znode 最后更新的子节点 Zxid
（6）cversion：znode 子节点变化号，znode 子节点修改次数
（7）dataVersion：znode 数据变化号
（8）aclVersion：znode 访问控制列表的变化号
（9）ephemeralOwner：如果是临时节点，这个是 znode 拥有者的 session id。如果不是临时节点则是 0。 
（10）dataLength：znode 的数据长度
（11）numChildren：znode 子节点数量


### 3.2.3 节点类型(持久/短暂/有序号/无序号)

- 持久（Persistent）：客户端和服务器端断开连接后，创建的节点不删除
- 短暂（Ephemeral）：客户端和服务器端断开连接后，创建的节点自己删除



说明：创建znode时设置顺序标识，znode名称后会附加一个值，顺序号是一个单调递增的计数器，由父节点维护
注意：在分布式系统中，顺序号可以被用于为所有的事件进行全局排序，这样客户端可以通过顺序号推断事件的顺序。
​

（1）持久化目录节点
客户端与Zookeeper断开连接后，该节点依旧存在
​

（2）持久化顺序编号目录节点
客户端与Zookeeper断开连接后，该节点依旧存在，只是Zookeeper给该节点名称进行顺序编号
​

（3）临时目录节点
客户端与Zookeeper断开连接后，该节点被删除
​

（4）临时顺序编号目录节点
客户端与 Zookeeper 断开连接后，该节点被删除 ， 只是Zookeeper给该节点名称进行顺序编号
​

![截屏2022-01-11 下午2.22.56.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1641882497995-0dd554a8-b150-4ca9-8e24-9e5b4d93a2c6.png#clientId=uedb83b36-3150-4&crop=0&crop=0&crop=1&crop=1&from=ui&id=u5fdf51a8&margin=%5Bobject%20Object%5D&name=%E6%88%AA%E5%B1%8F2022-01-11%20%E4%B8%8B%E5%8D%882.22.56.png&originHeight=432&originWidth=1328&originalType=binary&ratio=1&rotation=0&showTitle=false&size=79745&status=done&style=none&taskId=u716b953f-e7c0-4c2a-bd4b-8b409d44f2e&title=)


**1）分别创建2个普通节点（永久节点 + 不带序号）**
```shell
[zk: hadoop102:2181(CONNECTED) 3] create /sanguo "lvbu"
Created /sanguo
[zk: hadoop102:2181(CONNECTED) 4] create /sanguo/shuguo "liubei"
Created /sanguo/shuguo
```
注意：创建节点时，要赋值
​

**2）获得节点的值**
```shell
[zk: hadoop102:2181(CONNECTED) 5] get -s /sanguo
lvbu
cZxid = 0x500000001
ctime = Tue Jan 11 00:59:34 CST 2022
mZxid = 0x500000001
mtime = Tue Jan 11 00:59:34 CST 2022
pZxid = 0x500000002
cversion = 1
dataVersion = 0
aclVersion = 0
ephemeralOwner = 0x0
dataLength = 4
numChildren = 1
[zk: hadoop102:2181(CONNECTED) 6] get -s /sanguo/shuguo
liubei
cZxid = 0x500000002
ctime = Tue Jan 11 01:00:07 CST 2022
mZxid = 0x500000002
mtime = Tue Jan 11 01:00:07 CST 2022
pZxid = 0x500000002
cversion = 0
dataVersion = 0
aclVersion = 0
ephemeralOwner = 0x0
dataLength = 6
numChildren = 0
```
**3）创建带序号的节点（永久节点 + 带序号）**
（1）先创建一个普通的根节点/sanguo/weiguo
```shell
[zk: hadoop102:2181(CONNECTED) 7] create /sanguo/weiguo "caocao"
Created /sanguo/weiguo
```
​

（2）创建带序号的节点
```shell
[zk: hadoop102:2181(CONNECTED) 8] create -s /sanguo/weiguo/zhangliao "zhangliao"
Created /sanguo/weiguo/zhangliao0000000000
[zk: hadoop102:2181(CONNECTED) 9] create -s /sanguo/weiguo/zhangliao "zhangliao"
Created /sanguo/weiguo/zhangliao0000000001
[zk: hadoop102:2181(CONNECTED) 10] create -s /sanguo/weiguo/zhangliao "caoren"
Created /sanguo/weiguo/zhangliao0000000002
```
如果原来没有序号节点，序号从 0 开始依次递增。如果原节点下已有 2 个节点，则再排
序时从 2 开始，以此类推。
​

​

**4）创建短暂节点（短暂节点 + 不带序号 or 带序号）**
（1）创建短暂的不带序号的节点
```shell
[zk: hadoop102:2181(CONNECTED) 11] create -e /sanguo/wuguo "zhouyu"
Created /sanguo/wuguo
```
​

（2）创建短暂的带序号的节点
```shell
[zk: hadoop102:2181(CONNECTED) 12] create -e -s /sanguo/wuguo "zhouyu"
Created /sanguo/wuguo0000000003
```
​

（3）在当前客户端是能查看到的
```shell
[zk: hadoop102:2181(CONNECTED) 13] ls /sanguo
[shuguo, weiguo, wuguo, wuguo0000000003]
```
​

（4）退出当前客户端然后再重启客户端
```shell
[zk: hadoop102:2181(CONNECTED) 14] quit

[mhk@hadoop102 zookeeper-3.5.7]$ bin/zkCli.sh -server hadoop102:2181
```
​

（5）再次查看根目录下短暂节点已经删除
```shell
[zk: hadoop102:2181(CONNECTED) 0] ls /sanguo
[shuguo, weiguo]
```


**5）修改节点数据值**
```shell
[zk: hadoop102:2181(CONNECTED) 1] get -s /sanguo/weiguo
caocao
cZxid = 0x500000003
ctime = Tue Jan 11 01:08:38 CST 2022
mZxid = 0x500000003
mtime = Tue Jan 11 01:08:38 CST 2022
pZxid = 0x500000006
cversion = 3
dataVersion = 0
aclVersion = 0
ephemeralOwner = 0x0
dataLength = 6
numChildren = 3
[zk: hadoop102:2181(CONNECTED) 2] set /sanguo/weiguo "simayi"
[zk: hadoop102:2181(CONNECTED) 3] get -s /sanguo/weiguo
simayi
cZxid = 0x500000003
ctime = Tue Jan 11 01:08:38 CST 2022
mZxid = 0x50000000b
mtime = Tue Jan 11 01:17:16 CST 2022
pZxid = 0x500000006
cversion = 3
dataVersion = 1
aclVersion = 0
ephemeralOwner = 0x0
dataLength = 6
numChildren = 3
```




### 3.2.4 监听器原理
客户端注册监听它关心的目录节点，当目录节点发生变化（数据改变、节点删除、子目录节点增加删除）时，ZooKeeper 会通知客户端。监听机制保证 ZooKeeper 保存的任何的数据的任何改变都能快速的响应到监听了该节点的应用程序。
![截屏2022-01-11 下午3.14.43.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1641885505501-cccf6b0e-4b3a-46a8-b375-509b518e5335.png#clientId=uedb83b36-3150-4&crop=0&crop=0&crop=1&crop=1&from=ui&id=u36468c94&margin=%5Bobject%20Object%5D&name=%E6%88%AA%E5%B1%8F2022-01-11%20%E4%B8%8B%E5%8D%883.14.43.png&originHeight=355&originWidth=1291&originalType=binary&ratio=1&rotation=0&showTitle=false&size=86801&status=done&style=none&taskId=ue9d39048-d641-48d0-b549-166cfcb894b&title=)
​


1. **监听器原理详解**

1）首先要有一个main()线程
2）在main线程中创建Zookeeper客户端，这时就会创建两个线程，一个负责网络连接通信（connet），一个负责监听（listener）。 
3）通过connect线程将注册的监听事件发送给Zookeeper。 
4）在Zookeeper的注册监听器列表中将注册的监听事件添加到列表中。 
5）Zookeeper监听到有数据或路径变化，就会将这个消息发送给listener线程。 
6）listener线程内部调用了process()方法。
​


2. **常见的监听**

1）监听节点数据的变化
```shell
get path [watch]
```
​

2）监听子节点增减的变化
```shell
ls path [watch]
```
​


3. **案例实操**

1）节点的值变化监听
（1）在 hadoop104 主机上注册监听/sanguo 节点数据变化
```shell
[zk: localhost:2181(CONNECTED) 0] get -s /sanguo
lvbu
cZxid = 0x500000001
ctime = Tue Jan 11 00:59:34 CST 2022
mZxid = 0x500000001
mtime = Tue Jan 11 00:59:34 CST 2022
pZxid = 0x500000009
cversion = 6
dataVersion = 0
aclVersion = 0
ephemeralOwner = 0x0
dataLength = 4
numChildren = 2
[zk: localhost:2181(CONNECTED) 1] get -w /sanguo
lvbu
```
​

（2）在 hadoop103 主机上修改/sanguo 节点的数据
```shell
[zk: localhost:2181(CONNECTED) 0] set /sanguo "dongzhuo"
```
​

（3）观察 hadoop104 主机收到数据变化的监听
```shell
[zk: localhost:2181(CONNECTED) 2]
WATCHER::

WatchedEvent state:SyncConnected type:NodeDataChanged path:/sanguo

```
注意：在hadoop103再多次修改/sanguo的值，hadoop104上不会再收到监听。因为注册一次，只能监听一次。想再次监听，需要再次注册。
​

2）节点的子节点变化监听（路径变化）
（1）在 hadoop104 主机上注册监听/sanguo 节点的子节点变化
```shell
[zk: localhost:2181(CONNECTED) 0] ls -w /sanguo
[shuguo, weiguo]
```
​

（2）在 hadoop103 主机/sanguo 节点上创建子节点
```shell
[zk: localhost:2181(CONNECTED) 0] create /sanguo/jin "simayan"
Created /sanguo/jin
```
​

（3）观察 hadoop104 主机收到子节点变化的监听
```shell
[zk: localhost:2181(CONNECTED) 1]
WATCHER::

WatchedEvent state:SyncConnected type:NodeChildrenChanged path:/sanguo

```
注意：节点的路径变化，也是注册一次，生效一次。想多次生效，就需要多次注册
​

### 3.2.5 节点删除与查看
​


1. 删除节点
```shell
[zk: localhost:2181(CONNECTED) 4] delete /sanguo/jin
```
​


2. 递归删除节点
```shell
[zk: localhost:2181(CONNECTED) 17] delete /sanguo/shuguo
Node not empty: /sanguo/shuguo
[zk: localhost:2181(CONNECTED) 7] deleteall /sanguo/shuguo
[zk: localhost:2181(CONNECTED) 8] ls /sanguo
[jin1, weiguo]
```
​


3. 查看节点状态
```shell
[zk: localhost:2181(CONNECTED) 20] stat /sanguo
cZxid = 0x500000001
ctime = Tue Jan 11 00:59:34 CST 2022
mZxid = 0x500000016
mtime = Tue Jan 11 02:16:46 CST 2022
pZxid = 0x500000023
cversion = 14
dataVersion = 4
aclVersion = 0
ephemeralOwner = 0x0
dataLength = 8
numChildren = 2
```


## 3.3 客户端API操作
前提：保证 hadoop102、hadoop103、hadoop104 服务器上 Zookeeper 集群服务端启动。
​

### 3.3.1 IDEA 环境搭建


**1）创建一个工程：zookeeper**
​

**2）添加pom文件**
```xml
<dependencies>
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <version>RELEASE</version>
        </dependency>

        <dependency>
            <groupId>org.apache.logging.log4j</groupId>
            <artifactId>log4j-core</artifactId>
            <version>2.8.2</version>
        </dependency>

        <dependency>
            <groupId>org.apache.zookeeper</groupId>
            <artifactId>zookeeper</artifactId>
            <version>3.5.7</version>
        </dependency>
    </dependencies>
```


**3）拷贝log4j.properties文件到项目根目录**
需要在项目的 src/main/resources 目录下，新建一个文件，命名为“log4j.properties”，在
文件中填入。
```properties
log4j.rootLogger=INFO, stdout 
log4j.appender.stdout=org.apache.log4j.ConsoleAppender 
log4j.appender.stdout.layout=org.apache.log4j.PatternLayout 
log4j.appender.stdout.layout.ConversionPattern=%d %p [%c] - %m%n 
log4j.appender.logfile=org.apache.log4j.FileAppender 
log4j.appender.logfile.File=target/spring.log 
log4j.appender.logfile.layout=org.apache.log4j.PatternLayout 
log4j.appender.logfile.layout.ConversionPattern=%d %p [%c] - %m%n
```
**4）创建包名com.mz.zk**
​

**5）创建类名称zkClient**
**​**

### 3.3.2 创建ZooKeeper客户端
```java
public class zkClient {

    //注意逗号前后不能有空格
    private String connectString = "hadoop102:2181,hadoop103:2181,hadoop103:2181";
    private int sessionTimeout = 2000;
    private ZooKeeper zkClient;//command + alt + F 升级成全局变量

    @Before
    public void init() throws IOException {

        zkClient = new ZooKeeper(connectString, sessionTimeout, new Watcher() {
            @Override
            public void process(WatchedEvent watchedEvent) {
                System.out.println("-----------------------------------");
                List<String> children = null;
                try {
                    children = zkClient.getChildren("/", true);

                    for (String child : children) {
                        System.out.println(child);
                    }
                    System.out.println("-----------------------------------");
                } catch (KeeperException e) {
                    e.printStackTrace();
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        });
    }

```
### 3.3.3 创建子节点
```java
 @Test
    public void create() throws KeeperException, InterruptedException {
	// 参数 1：要创建的节点的路径； 参数 2：节点数据 ； 参数 3：节点权限 ；参数 4：节点的类型
        String nodeCreated = zkClient.create("/muhaokang", "Jooye".getBytes(), ZooDefs.Ids.OPEN_ACL_UNSAFE, CreateMode.PERSISTENT);
    }
```
测试：在hadoop103客户端上查看子节点的创建情况
```xml
[zk: localhost:2181(CONNECTED) 1] ls /
[muhaokang, sanguo, zookeeper]
[zk: localhost:2181(CONNECTED) 2] get -s /muhaokang
Jooye
cZxid = 0x500000027
ctime = Tue Jan 11 04:03:29 CST 2022
mZxid = 0x500000027
mtime = Tue Jan 11 04:03:29 CST 2022
pZxid = 0x500000027
cversion = 0
dataVersion = 0
aclVersion = 0
ephemeralOwner = 0x0
dataLength = 5
numChildren = 0
```
### 3.3.4 获取子节点并监听节点变化
```java
 @Test//获取子节点
    public void getChildren() throws KeeperException, InterruptedException {
        List<String> children = zkClient.getChildren("/", true);

        for (String child : children) {
            System.out.println(child);
        }
      //延迟阻塞
        Thread.sleep(Long.MAX_VALUE);
    }
```
（1）在IDEA控制台上看到如下结果
```java
zookeeper
muhaokang
sanguo
```
（2）在hadoop103的客户端再创建一个节点/xiaozhuoyi，观察IDEA控制台
```shell
[zk: localhost:2181(CONNECTED) 4] create /xiaozhuoyi "mhk"
Created /xiaozhuoyi
```
```java
zookeeper
muhaokang
xiaozhuoyi
sanguo
```


### 3.3.5 判断ZNode是否存在
```java
@Test
    public void exists() throws KeeperException, InterruptedException {
        Stat stat = zkClient.exists("/muhaokang", false);
        System.out.println(stat==null ? "not exists!" : "exists!");
    }
```


## 3.4 客户端向服务端写数据流程


### 3.4.1 写流程之写入请求直接发送给Leader节点


通俗解释：客户端给服务器的leader发送写请求，写完数据后给手下发送写请求，手下写完发送给leader，超过半票以上都写了则发回给客户端。之后leader在给其他手下让他们写，写完在发数据给leader
![截屏2022-01-11 下午6.22.46.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1641896667243-69777451-e44f-415e-83fe-2db0b15a9fe1.png#clientId=uedb83b36-3150-4&crop=0&crop=0&crop=1&crop=1&from=ui&id=u241da705&margin=%5Bobject%20Object%5D&name=%E6%88%AA%E5%B1%8F2022-01-11%20%E4%B8%8B%E5%8D%886.22.46.png&originHeight=569&originWidth=1002&originalType=binary&ratio=1&rotation=0&showTitle=false&size=67031&status=done&style=none&taskId=uaa9c3e46-c2bd-410c-bfca-3cd46876f99&title=)


![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1642063174474-80e2c8dd-3a6e-4b3f-b3c0-bfcb8da22a5a.png#clientId=u258324d2-5a4e-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=359&id=u24a20960&margin=%5Bobject%20Object%5D&name=image.png&originHeight=359&originWidth=666&originalType=binary&ratio=1&rotation=0&showTitle=false&size=55189&status=done&style=none&taskId=u82840430-1c38-44e2-ac24-7561cfaa232&title=&width=666)


### 3.4.2 写流程之写入请求发送给Follower节点


通俗解释：客户端给手下发送写的请求，手下给leader发送写的请求，写完后，给手下发送写的请求，手下写完后给leader发送确认，超过半票，leader确认后，发给刻划断，之后leader在发送写请求给其他手下
![截屏2022-01-11 下午6.23.06.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1641896865335-af7e071a-12cb-4ac1-a63e-66f83953ee56.png#clientId=uedb83b36-3150-4&crop=0&crop=0&crop=1&crop=1&from=ui&id=uc93b0312&margin=%5Bobject%20Object%5D&name=%E6%88%AA%E5%B1%8F2022-01-11%20%E4%B8%8B%E5%8D%886.23.06.png&originHeight=546&originWidth=1285&originalType=binary&ratio=1&rotation=0&showTitle=false&size=69533&status=done&style=none&taskId=u326f12a7-5654-4c5c-893d-6ee75b333e8&title=)




![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1642063216652-67d24528-e34a-4d7d-b9c0-35e8a2b1d5e5.png#clientId=u258324d2-5a4e-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=396&id=ubcec8aaa&margin=%5Bobject%20Object%5D&name=image.png&originHeight=396&originWidth=713&originalType=binary&ratio=1&rotation=0&showTitle=false&size=51629&status=done&style=none&taskId=ube39caa9-810f-4e60-92d3-554348d6b28&title=&width=713)


# 4. 服务器动态上下线监听案例
## 4.1 需求
某分布式系统中，主节点可以有多台，可以动态上下线，任意一台客户端都能实时感知到主节点服务器的上下线。
## 4.2 需求分析

1. 服务器上线的时候其实就是服务器启动时去注册信息（创建的都是临时节点）
1. 客户端获取到当前在线的服务器列表后
1. 服务器节点下线后给集群管理
1. 集群管理服务器节点的下件时间通知给客户端
1. 客户端通过获取服务器列表重选选择服务器

![截屏2022-01-11 下午6.54.32.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1641898965045-0340576d-991c-454e-a533-ebf6dd793c41.png#clientId=uedb83b36-3150-4&crop=0&crop=0&crop=1&crop=1&from=ui&id=u00a3a0a7&margin=%5Bobject%20Object%5D&name=%E6%88%AA%E5%B1%8F2022-01-11%20%E4%B8%8B%E5%8D%886.54.32.png&originHeight=726&originWidth=1433&originalType=binary&ratio=1&rotation=0&showTitle=false&size=372309&status=done&style=none&taskId=ub13fd368-ca05-4408-a0ef-b04e811b485&title=)


## 4.3 具体实现
（1）先在集群上创建/servers节点
```shell
[zk: localhost:2181(CONNECTED) 9] create /servers "servers"
Created /servers
```
（2）创建包名com.mz.zkcase1


（3）服务器代码

- 获取zookeeper集群的连接，通过zookeeper的构造函数ZooKeeper(connectString, sessionTimeout, new Watcher(){})
- 将其服务注册到zookeeper集群中，具体通过create的函数，通过获取每个服务器名字、其值、权限、节点类型
- 执行该函数通过延迟函数
```java
public class DistributeServer {
    private String connectString = "hadoop102:2181,hadoop103:2181,hadoop104:2181";
    private int sessionTimeout = 2000;
    private ZooKeeper zk;

    public static void main(String[] args) throws IOException, KeeperException, InterruptedException {

        DistributeServer server = new DistributeServer();
        //1.获取zk连接
        server.getConnect();

        //2.注册服务器到zk集群
        server.regist(args[0]);

        //3.启动业务逻辑（睡觉）
        server.business();
    }

    private void business() throws InterruptedException {
        Thread.sleep(Long.MAX_VALUE);
    }

    private void regist(String hostname) throws KeeperException, InterruptedException {

        String s = zk.create("/servers", hostname.getBytes(), ZooDefs.Ids.OPEN_ACL_UNSAFE, CreateMode.EPHEMERAL_SEQUENTIAL);
        System.out.println(hostname + "is online!");
    }

    private void getConnect() throws IOException {

        zk = new ZooKeeper(connectString, sessionTimeout, new Watcher() {
            @Override
            public void process(WatchedEvent watchedEvent) {

            }
        });
    }
}

```


（4）客户端代码

- 获取zookeeper集群的连接，通过zookeeper的构造函数ZooKeeper(connectString, sessionTimeout, new Watcher(){})
- 客户端通过监听每个节点，具体监听通过getChildren函数，获取其节点位置，以及是否使用初始化的监听函数，true为使用。获取到的都是以列表存在，输出的时候通过遍历实现，输出的还是一些数组格式。将这些数组都封装到一个列表中，最后统一输出列表即可
- 执行该函数通过延迟函数

​

因为注册的时候记录一次
所以在初始化的时候，将其注册放在初始化内部getServerList();
```java
public class DistributeClient {
    private String connectString = "hadoop102:2181,hadoop103:2181,hadoop104:2181";
    private int sessionTimeout = 2000;
    private ZooKeeper zk = null;
    private String parentNode = "/servers";

    public static void main(String[] args) throws IOException, KeeperException, InterruptedException {

        DistributeClient client = new DistributeClient();

        //1.获取zk连接
        client.getConnect();

        //2.监听servers下面子节点的增加和删除
        client.getServerList();

        //3.业务逻辑（睡觉）
        client.business();
    }

    private void business() throws InterruptedException {
        Thread.sleep(Long.MAX_VALUE);
    }

    private void getServerList() throws KeeperException, InterruptedException {

        List<String> children = zk.getChildren("/servers", true);

        ArrayList<String> servers = new ArrayList<>();

        for (String child : children) {
            byte[] data = zk.getData("/servers/"+child, false, null);

            servers.add(new String(data));
        }

        //打印
        System.out.println(servers);
    }

    private void getConnect() throws IOException {

        zk = new ZooKeeper(connectString, sessionTimeout, new Watcher() {
             @Override
             public void process(WatchedEvent watchedEvent) {

                 try {
                     getServerList();
                 } catch (KeeperException e) {
                     e.printStackTrace();
                 } catch (InterruptedException e) {
                     e.printStackTrace();
                 }
             }
         });
    }
}

```
​

具体测试的逻辑：​

- 启动客户端，通过虚拟机进行create -e -s 节点信息（临时带序号的节点），或者delete进行更新
- 启动服务器，判定节点是否正常上下线
# 5. ZooKeeper分布式锁案例
什么叫做分布式锁呢？
比如说"进程 1"在使用该资源的时候，会先去获得锁，"进程 1"获得锁以后会对该资源保持独占，这样其他进程就无法访问该资源，"进程 1"用完该资源以后就将锁释放掉，让其他进程来获得锁，那么通过这个锁机制，我们就能保证了分布式系统中多个进程能够有序的访问该临界资源。那么我们把这个分布式环境下的这个锁叫作分布式锁。
​

分布式锁案例分析
![截屏2022-01-12 上午11.26.46.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1641958029499-9bc4c722-dab4-411f-bbac-80e2cd18a22b.png#clientId=uedb83b36-3150-4&crop=0&crop=0&crop=1&crop=1&from=ui&id=uf291f736&margin=%5Bobject%20Object%5D&name=%E6%88%AA%E5%B1%8F2022-01-12%20%E4%B8%8A%E5%8D%8811.26.46.png&originHeight=583&originWidth=1243&originalType=binary&ratio=1&rotation=0&showTitle=false&size=127749&status=done&style=none&taskId=u31af33f4-5122-4b71-92a6-aa44880c04b&title=)
（1）集群接受客户端请求后，在/locks节点下创建一个临时顺序节点
（2）节点判断自己是不是当前节点下最小的节点：
是，获取到锁
不是，对前一个节点进行监听
（3）获取到锁，处理完业务后，delete节点释放锁，然后下面的节点将收到通知，重复第二步判断
​

## 5.1 原生ZooKeeper实现分布式锁案例


创建节点，判断是否是最小的节点
如果不是最小的节点，需要监听前一个的节点
​

健壮性可以通过CountDownLatch类:
当我们需要实现并发请求，或者一个线程需要等待其他线程执行完成之后再执行时 ，我们可以使用CountDownLatch
CountDownLatch 是一个同步工具类，它允许一个或多个线程一直等待，直到其他线程的操作执行完毕再执行。从命名可以解读到 countDown 是倒数的意思，类似于我们倒计时的概念。CountDownLatch 提供了两个方法，一个是 countDown，一个是 await，CountDownLatch 初始化的时候需要传入一个整数，在这个整数倒数到 0 之前，调用了 await 方法的程序都必须要等待，然后通过 countDown 来倒数。
​

监听函数
如果集群状态是连接，则释放connectLatch
如果集群类型是删除，且前一个节点的位置等于该节点的文职，则释放该节点
判断节点是否存在不用一直监听
获取节点信息要一直监听getData


```java
public class DistributedLock{

    private final String connectString = "hadoop102:2181,hadoop103:2181,hadoop104:2181";
    private final int sessionTimeout = 2000;
    private final ZooKeeper zk;

    private CountDownLatch connectLatch = new CountDownLatch(1);
    private CountDownLatch waitLatch = new CountDownLatch(1);
    private String waitPath;
    private String currentNode;

    public DistributedLock() throws IOException, InterruptedException, KeeperException {

        //获取连接
        zk = new ZooKeeper(connectString, sessionTimeout, new Watcher() {
            @Override
            public void process(WatchedEvent watchedEvent) {
                // connectLatch 如果连接上zk，可以释放
                if (watchedEvent.getState() == Event.KeeperState.SyncConnected){
                    connectLatch.countDown();
                }

                // waitLatch 需要释放
                if (watchedEvent.getType() == Event.EventType.NodeDeleted && watchedEvent.getPath().equals(waitPath)){
                    waitLatch.countDown();
                }

            }
        });

        //等待zk正常连接后，往下走程序
        connectLatch.await();

        //判断根节点/lockss是否存在
        Stat stat = zk.exists("/locks", false);

        if (stat == null){
            zk.create("/locks","locks".getBytes(), ZooDefs.Ids.OPEN_ACL_UNSAFE,CreateMode.PERSISTENT);
        }

    }

    //对zk加锁
    public void zkLock(){
        //创建对应的临时带序号的节点
        try {
            currentNode = zk.create("/locks/" + "seq-", null, ZooDefs.Ids.OPEN_ACL_UNSAFE, CreateMode.EPHEMERAL_SEQUENTIAL);

            //判断创建的节点是否是当前最小序号节点，如果是：获取到锁；如果不是：监听它序号前一个节点
            List<String> children = zk.getChildren("/locks", false);

            //如果children只有一个值，那就直接获取锁；如果有多个节点，需要判断，谁最小
            if (children.size() == 1){
                return;
            }else {
                Collections.sort(children);

                //获取节点名称 seq-00000000
                String thisNode = currentNode.substring("/locks/".length());
                //通过seq-00000000 ， 获取该节点在children集合的位置
                int index = children.indexOf(thisNode);

                //判断
                if (index == -1){
                    System.out.println("数据异常");
                }else if ((index == 0)){
                    //就一个节点，可以获取锁了
                    return;
                }else {
                    //需要监听 它前一个节点变化
                    waitPath = "/locks/" + children.get(index - 1);
                    zk.getData(waitPath,true,null);

                    //等待监听
                    waitLatch.await();

                    return;
                }
            }



        } catch (KeeperException e) {
            e.printStackTrace();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }



    }

    //解锁
    public void unZkLock()  {

        //删除节点
        try {
            zk.delete(currentNode,-1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        } catch (KeeperException e) {
            e.printStackTrace();
        }
    }
}

```


测试类需要new 两个 DistributedLock，因为在同一台机器里的并发线程都是用的同一个锁对象，而在在不同主机里的线程那就用的是不同的锁对象，这里模拟的是分布式锁的场景，所以需要new 两个锁对象。 
​

```java
public class DistributedLockTest {
    public static void main(String[] args) throws InterruptedException, IOException, KeeperException {
        final DistributedLock lock1 = new DistributedLock();
        final DistributedLock lock2 = new DistributedLock();

        new Thread(new Runnable() {
            @Override
            public void run() {

                try {
                    lock1.zkLock();
                    System.out.println("线程1 启动，获取到锁");
                    Thread.sleep(5*1000);

                    lock1.unZkLock();
                    System.out.println("线程1 释放锁");
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }).start();

        new Thread(new Runnable() {
            @Override
            public void run() {

                try {
                    lock2.zkLock();
                    System.out.println("线程2 启动，获取到锁");
                    Thread.sleep(5*1000);

                    lock2.unZkLock();
                    System.out.println("线程2 释放锁");
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }).start();
    }
}

```
观察控制台输出
```java
 线程1 启动，获取到锁
线程1 释放锁
线程2 启动，获取到锁
线程2 释放锁
```
## 5.2 Curator框架实现分布式锁案例
### 5.2.1 原生的 Java API 开发存在的问题
（1）会话连接是异步的，需要自己去处理。比如使用 CountDownLatch
（2）Watch 需要重复注册，不然就不能生效
（3）开发的复杂性还是比较高的
（4）不支持多节点删除和创建。需要自己去递归
​

### 5.2.2 Curator 是一个专门解决分布式锁的框架，解决了原生 JavaAPI 开发分布式遇到的问题。
详情请查看官方文档：[https://curator.apache.org/index.html](https://curator.apache.org/index.html)
​

### 5.3.3 Curator 案例实操
（1）添加依赖
```java
		<dependency>
            <groupId>org.apache.curator</groupId>
            <artifactId>curator-recipes</artifactId>
            <version>4.3.0</version>
        </dependency>

        <dependency>
            <groupId>org.apache.curator</groupId>
            <artifactId>curator-framework</artifactId>
            <version>4.3.0</version>
        </dependency>

        <dependency>
            <groupId>org.apache.curator</groupId>
            <artifactId>curator-client</artifactId>
            <version>4.3.0</version>
        </dependency>
```
（2）代码实现
```java
public class CuratorLockTest {
    public static void main(String[] args) {

        //创建分布式锁1
        InterProcessMutex lock1 = new InterProcessMutex(getCuratorFramework(), "/locks");

        //创建分布式锁2
        InterProcessMutex lock2 = new InterProcessMutex(getCuratorFramework(), "/locks");

        new Thread(new Runnable() {
            @Override
            public void run() {

                try {
                    lock1.acquire();
                    System.out.println("线程1 获取到锁");

                    lock1.acquire();;
                    System.out.println("线程1 再次获取到锁");

                    Thread.sleep(5*1000);

                    lock1.release();
                    System.out.println("线程1 释放锁");

                    lock1.release();
                    System.out.println("线程1 再次释放锁");



                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        }).start();

        new Thread(new Runnable() {
            @Override
            public void run() {

                try {
                    lock2.acquire();
                    System.out.println("线程2 获取到锁");

                    lock2.acquire();;
                    System.out.println("线程2 再次获取到锁");

                    Thread.sleep(5*1000);

                    lock2.release();
                    System.out.println("线程2 释放锁");

                    lock2.release();
                    System.out.println("线程2 再次释放锁");

                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        }).start();

    }

    private static CuratorFramework getCuratorFramework() {

        ExponentialBackoffRetry policy = new ExponentialBackoffRetry(3000, 3);

        CuratorFramework client = CuratorFrameworkFactory.builder().connectString("hadoop102:2181,hadoop103:2181,hadoop104:2181")
                .connectionTimeoutMs(2000)
                .sessionTimeoutMs(2000)
                .retryPolicy(policy).build();

        //启动客户端
        client.start();
        System.out.println("ZooKeeper启动成功！");
        return client;
    }
}
```
（3）获得结果
```java
线程1 获取到锁
线程1 再次获取到锁
线程1 释放锁
线程1 再次释放锁
线程2 获取到锁
线程2 再次获取到锁
线程2 释放锁
线程2 再次释放锁
```
