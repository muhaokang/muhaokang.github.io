---
layout: post
title: "ZooKeeper选举机制"
author: Haokang Mu
excerpt: ZooKeeper选举机制.md
tags:
- ZooKeeper

---



# 1. ZooKeeper选举机制---第一次启动
![截屏2022-01-10 下午6.50.55.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1641811881759-0fe5b93a-5064-467c-a2fb-b51901b0cca3.png#clientId=ua00b2caf-4083-4&crop=0&crop=0&crop=1&crop=1&from=ui&id=udf91fc0d&margin=%5Bobject%20Object%5D&name=%E6%88%AA%E5%B1%8F2022-01-10%20%E4%B8%8B%E5%8D%886.50.55.png&originHeight=611&originWidth=1217&originalType=binary&ratio=1&rotation=0&showTitle=false&size=253601&status=done&style=none&taskId=u795555d5-1656-4c9b-8355-c16ec6158c2&title=)

1. 服务器1启动，发起一次选举，服务器1投自己一票。此时服务器1票数1票，不够半数以上（3票），选举无法完成，服务器1状态保持为LOOKING；
1. 服务器2启动，再发起一次选举，服务器1和2分别投自己一票并交换选票信息，此时服务器1发现服务器2的myid比自己目前投票推举的（服务器1）大，更改选票为推举服务器2。此时服务器1票数0票，服务器2票数2票，依然不够半数以上（3票），选举无法完成，服务器1和2状态保持LOOKING；
1. 服务器3启动，再发起一次选举，此时服务器1和2都会更改选票为服务器3。此次投票结果：服务器1为0票，服务器2为0票，服务器3为3票已经超过半数，服务器3当选Leader，服务器1和2更改状态为FOLLOWING，服务器3更改状态为LEADING；
1. 服务器4启动，发起一次选举，此时服务器1、2、3已经不是LOOKING状态了，不会更改选票信息，交换选票信息结果：服务器3为3票，服务器4为1票。此时服务器4服从多数，更改选票信息为服务器3，并更改状态为FOLLOWING；
1. 服务器5启动，同4一样当小弟。

​

# 2. ZooKeeper选举机制---非第一次启动
![截屏2022-01-10 下午7.06.36.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1641812815264-ef25b1ad-4cbf-4b0a-8d3e-396baf0b1024.png#clientId=ua00b2caf-4083-4&crop=0&crop=0&crop=1&crop=1&from=ui&id=u37bd43b2&margin=%5Bobject%20Object%5D&name=%E6%88%AA%E5%B1%8F2022-01-10%20%E4%B8%8B%E5%8D%887.06.36.png&originHeight=607&originWidth=1215&originalType=binary&ratio=1&rotation=0&showTitle=false&size=241344&status=done&style=none&taskId=ucad60444-ca7d-4dd8-a313-817da9df02b&title=)


1. 当ZooKeeper集群中的一台服务器出现以下两种情况之一时，就会开始进入Leader选举：
- 服务器初始化启动（参考上文）
- 服务器运行期间无法与Leader保持连接

比如服务器5，突然和Leader通信连接不上了，但服务器5不会认为是自己坏掉的原因，而是会认为其他节点可能挂掉了，要重新发起选举（反了反了，小弟要自立为王了）


2. 而当一台机器进入Leader选举流程时，当前集群可能会处于以下两种状态：
- 集群中本来就已经存在一个Leader

对于第一种已经存在Leader的情况，机器试图去选举Leader的时候，会被告知当前服务器的Leader信息，对于该机器来说，仅仅需要和Leader机器建立连接，并进行状态同步即可
服务器5要想当选Leader，需要半数以上的选票，当服务器5与其他节点通信交换选票信息的时候，会被其他节点告知集群Leader已经存在，你不能选举，你只能尝试去连接Leader

- **集群中确实不存在Leader**

假设ZooKeeper由5台服务器组成，SID分别为1、2、3、4、5，ZXID分别为8、8、8、7、7，并且此时SID为3的服务器是Leader。某一时刻3和5服务器出现故障，因此开始进行Leader选举
服务器1：=> EPOCH：1		ZXID：8		SID：1
服务器2：=> EPOCH：1		ZXID：8		SID：2
服务器4：=> EPOCH：1		ZXID：7		SID：4
选举Leader原则：
（1）EPOCH大的直接胜出
（2）EPOCH相同，事务ID大的胜出
（3）事务ID相同，服务器ID大的胜出
​

最终服务器2当选为新的Leader


​

