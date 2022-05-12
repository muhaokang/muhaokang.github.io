---
layout: post
title: "Prometheus概述"
author: Haokang Mu
excerpt: Prometheus概述.md
tags:
- Prometheus

---

# 1. Prometheus 的特点 
Prometheus 是一个开源的完整监控解决方案，其对传统监控系统的测试和告警模型进行了彻底的颠覆，形成了基于中央化的规则计算、统一分析和告警的新模型。 相比于传统监控系统，Prometheus 具有以下优点：
## 1.1 易于管理 

- Prometheus 核心部分只有一个单独的二进制文件，不存在任何的第三方依赖(数据库，缓存等等)。唯一需要的就是本地磁盘，因此不会有潜在级联故障的风险。 
- Prometheus 基于 Pull 模型的架构方式，可以在任何地方（本地电脑，开发环境，测试环境）搭建我们的监控系统。 
- 对于一些复杂的情况，还可以使用 Prometheus 服务发现(Service Discovery)的能力动态管理监控目标。 
## 1.2 监控服务的内部运行状态 
Pometheus 鼓励用户监控服务的内部状态，基于 Prometheus 丰富的 Client 库，用户可以轻松的在应用程序中添加对 Prometheus 的支持，从而让用户可以获取服务和应用内部真正的运行状态。
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1651749235833-f197af7c-d0b2-47dc-bee1-9e7d3a282a1c.png#clientId=ua4a51593-7502-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=298&id=ucb2a5983&margin=%5Bobject%20Object%5D&name=image.png&originHeight=298&originWidth=946&originalType=binary&ratio=1&rotation=0&showTitle=false&size=55110&status=done&style=none&taskId=u1b8f4f92-d1a7-4b62-841f-3587df3834b&title=&width=946)
## 1.3 强大的数据模型 
所有采集的监控数据均以指标(metric)的形式保存在**内置的时间序列数据库**当中 (**TSDB**)。所有的样本除了基本的指标名称以外，还包含一组用于描述该样本特征的标签。 
如下所示：
```shell
http_request_status{code='200',content_path='/api/path',environment='produment'} => 
[value1@timestamp1,value2@timestamp2...]
http_request_status{code='200',content_path='/api/path2',environment='produment'} => 
[value1@timestamp1,value2@timestamp2...]
```
每一条时间序列由**指标名称(Metrics Name)**以及一组**标签(Labels)**唯一标识。每条时间序列按照时间的先后顺序存储一系列的样本值。 

- http_request_status：指标名称(Metrics Name) 
- {code='200',content_path='/api/path',environment='produment'}：表示维度的标签，基于这些 Labels 我们可以方便地对监控数据进行聚合，过滤，裁剪。 
- [value1@timestamp1,value2@timestamp2...]：按照时间的先后顺序 存储的样本值。  
## 1.4 强大的查询语言 PromQL 
Prometheus 内置了一个强大的数据查询语言 PromQL。 通过 PromQL 可以实现对监控数据的查询、聚合。同时 PromQL 也被应用于数据可视化(如 Grafana)以及告警当中。 
通过 PromQL 可以轻松回答类似于以下问题： 

- 在过去一段时间中 95%应用延迟时间的分布范围？ 
- 预测在 4 小时后，磁盘空间占用大致会是什么情况？ 
- CPU 占用率前 5 位的服务有哪些？(过滤) 
## 1.5 高效 
对于监控系统而言，大量的监控任务必然导致有大量的数据产生。而 Prometheus 可以高效地处理这些数据，对于单一 Prometheus Server 实例而言它可以处理： 

- 数以百万的监控指标 
- 每秒处理数十万的数据点
## 1.6 可扩展 
可以在每个数据中心、每个团队运行独立的 Prometheus Sevrer。Prometheus 对于联邦集群的支持，可以让多个 Prometheus 实例产生一个逻辑集群，当单实例 Prometheus Server 处理的任务量过大时，通过使用功能分区(sharding)+联邦集群(federation)可以对其进行扩展。 
## 1.7 易于集成 
使用 Prometheus 可以快速搭建监控服务，并且可以非常方便地在应用程序中进行集成。目前支持：Java，JMX，Python，Go，Ruby，.Net，Node.js 等等语言的客户端 SDK，基于这些 SDK 可以快速让应用程序纳入到 Prometheus 的监控当中，或者开发自己的监控数据收集程序。 
同时这些客户端收集的监控数据，不仅仅支持 Prometheus，还能支持 Graphite 这些其他的监控工具。 
同时 Prometheus 还支持与其他的监控系统进行集成：Graphite，Statsd，Collected，Scollector， muini， Nagios 等。 Prometheus 社区还提供了大量第三方实现的监控数据采集支持：JMX，CloudWatch，EC2，MySQL，PostgresSQL，Haskell，Bash，SNMP，Consul，Haproxy，Mesos，Bind，CouchDB，Django，Memcached，RabbitMQ，Redis，RethinkDB，Rsyslog 等等。 
## 1.8 可视化

- Prometheus Server 中自带的 Prometheus UI，可以方便地直接对数据进行查询，并且支持直接以图形化的形式展示数据。同时 Prometheus 还提供了一个独立的基于 Ruby On Rails 的 Dashboard 解决方案 Promdash。 
- 最新的 Grafana 可视化工具也已经提供了完整的 Prometheus 支持，基于 Grafana 可以创建更加精美的监控图标。 
- 基于 Prometheus 提供的 API 还可以实现自己的监控可视化 UI。 
## 1.9 开放性 
通常来说当我们需要监控一个应用程序时，一般需要该应用程序提供对相应监控系统协议的支持，因此应用程序会与所选择的监控系统进行绑定。为了减少这种绑定所带来的限制，对于决策者而言要么你就直接在应用中集成该监控系统的支持，要么就在外部创建单独的服务来适配不同的监控系统。 
而对于 Prometheus 来说，使用 Prometheus 的 client library 的输出格式不止支持 Prometheus 的格式化数据，也可以输出支持其它监控系统的格式化数据，比如 Graphite。 
因此你甚至可以在不使用 Prometheus 的情况下，采用 Prometheus 的 client library 来让 
你的应用程序支持监控数据采集。

# 2. Prometheus 的架构
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1651749661875-1d4b580c-5735-4813-999e-96031a1e74bd.png#clientId=ua4a51593-7502-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=607&id=u4c840b6f&margin=%5Bobject%20Object%5D&name=image.png&originHeight=607&originWidth=920&originalType=binary&ratio=1&rotation=0&showTitle=false&size=137611&status=done&style=none&taskId=uff3ef4d8-0305-4410-8fd8-2807099d466&title=&width=920)
## 2.1 Prometheus 生态圈组件 

- Prometheus Server：主服务器，负责收集和存储时间序列数据 
- client libraies：应用程序代码插桩，将监控指标嵌入到被监控应用程序中 
- Pushgateway：推送网关，为支持 short-lived 作业提供一个推送网关 
- exporter：专门为一些应用开发的数据摄取组件—exporter，例如：HAProxy、StatsD、Graphite 等等。 
- Alertmanager：专门用于处理 alert 的组件 
## 2.2 架构理解 
Prometheus 既然设计为一个维度存储模型，可以把它理解为一个 OLAP 系统。 
#### 1、存储计算层 

- Prometheus Server，里面包含了存储引擎和计算引擎。 
- Retrieval 组件为取数组件，它会主动从 Pushgateway 或者 Exporter 拉取指标数据。 
- Service discovery，可以动态发现要监控的目标。 
- TSDB，数据核心存储与查询。 
- HTTP server，对外提供 HTTP 服务。 
#### 2、采集层 
采集层分为两类，一类是生命周期较短的作业，还有一类是生命周期较长的作业。 

- 短作业：直接通过 API，在退出时间指标推送给 Pushgateway。 
- 长作业：Retrieval 组件直接从 Job 或者 Exporter 拉取数据。 
#### 3、应用层 
应用层主要分为两种，一种是 AlertManager，另一种是数据可视化。 

- AlertManager 

对接 Pagerduty，是一套付费的监控报警系统。可实现短信报警、5 分钟无人 ack 打电话通知、仍然无人 ack，通知值班人员 Manager... 
Emial，发送邮件 
... ... 

- 数据可视化 

Prometheus build-in WebUI 
Grafana 
其他基于 API 开发的客户端

# 3. **Prometheus 的安装**
## 3.1 安装 Prometheus Server 
Prometheus 基于 Golang 编写，编译后的软件包，不依赖于任何的第三方依赖。只需要下载对应平台的二进制包，解压并且添加基本的配置即可正常启动 Prometheus Server。
### 3.1.1 修改配置文件 prometheus.yml
```yaml
scrape_configs:

  - job_name: 'prometheus'
    static_configs:
    - targets: ['hadoop202:9090']

# 添加 PushGateway 监控配置
  - job_name: 'pushgateway'
    static_configs:
    - targets: ['hadoop102:9091']
      labels:
      instance: pushgateway

# 添加 Node Exporter 监控配置
  - job_name: 'node exporter'
    static_configs:
    - targets: ['hadoop102:9100', 'hadoop103:9100', 'hadoop104:9100']
```
配置说明： 
**1、global 配置块**：控制 Prometheus 服务器的全局配置 

- scrape_interval：配置拉取数据的时间间隔，默认为 1 分钟。 
- evaluation_interval：规则验证（生成 alert）的时间间隔，默认为 1 分钟。 

**2、rule_files 配置块**：规则配置文件 
**3、scrape_configs 配置块**：配置采集目标相关， prometheus 监视的目标。Prometheus 
自身的运行信息可以通过 HTTP 访问，所以 Prometheus 可以监控自己的运行数据。 

- job_name：监控作业的名称 
- static_configs：表示静态目标配置，就是固定从某个 target 拉取数据 
- targets ： 指 定 监 控 的 目 标 ， 其 实 就 是 从 哪 儿 拉 取 数 据 。 Prometheus 会 从 

http://hadoop102:9090/metrics 上拉取数据。 
_Prometheus 是可以在运行时自动加载配置的。启动时需要添加：--web.enable-lifecycle_

## 3.2 安装 Pushgateway 
Prometheus 在正常情况下是采用拉模式从产生 metric 的作业或者 exporter（比如专门监控主机的 NodeExporter）拉取监控数据。但是我们要监控的是 Flink on YARN 作业，想要让 Prometheus 自动发现作业的提交、结束以及自动拉取数据显然是比较困难的。 
PushGateway 就是一个中转组件，通过配置 Flink on YARN 作业将 metric 推到 PushGateway，Prometheus 再从 PushGateway 拉取就可以了。

## 3.3 安装 Node Exporter（选择性安装） 
在 Prometheus 的架构设计中，Prometheus Server 主要负责数据的收集，存储并且对外提供数据查询支持，而实际的监控样本数据的收集则是由 Exporter 完成。因此为了能够监控到某些东西，如主机的 CPU 使用率，我们需要使用到 Exporter。Prometheus 周期性的从 Exporter 暴露的 HTTP 服务地址（通常是/metrics）拉取监控样本数据。 
Exporter 可以是一个相对开放的概念，其可以是一个独立运行的程序独立于监控目标以外，也可以是直接内置在监控目标中。只要能够向 Prometheus 提供标准格式的监控样本数据即可。 
为了能够采集到主机的运行指标如 CPU, 内存，磁盘等信息。我们可以使用 Node Exporter。Node Exporter 同样采用 Golang 编写，并且不存在任何的第三方依赖，只需要下载，解压即可运行。可以从 https://prometheus.io/download/ 获取最新的 node exporter 版本的二进制包。

启动并通过页面查看是否成功 
执行./node_exporter 
浏览器输入：http://hadoop102:9100/metrics，可以看到当前 node exporter 获取到的当前主机的所有监控数据。

### 3.3.1 节点分发 
将解压后的目录分发到要监控的节点 
```shell
xsync node_exporter-1.2.2 
```

修改 Prometheus 配置文件 prometheus.yml，在 之前已经添加过配置 
```yaml
- targets: ['hadoop202:9100', 'hadoop203:9100', 'hadoop204:9100']
```

### 3.3.2 设置为开机自启 
创建 service 文件
```shell
sudo vim /usr/lib/systemd/system/node_exporter.service

[Unit]
Description=node_export
Documentation=https://github.com/prometheus/node_exporter
After=network.target

[Service]
Type=simple
User=mhk
ExecStart= /opt/module/node_exporter-1.2.2/node_exporter
Restart=on-failure

[Install]
WantedBy=multi-user.target
```
 
分发文件 
```shell
sudo /home/atguigu/bin/xsync /usr/lib/systemd/system/node_exporter.service 
```
设为开机自启动（所有机器都执行） 
```shell
sudo systemctl enable node_exporter.service 
```
启动服务（所有机器都执行） 
```shell
sudo systemctl start node_exporter.service
```

## 3.4 安装 Alertmanager（选择性安装） 
### 3.4.1 上传安装包 
上传 alertmanager-0.23.0.linux-amd64.tar.gz 到虚拟机的/opt/software 目录 
### 3.4.2 解压安装包 
解压到/opt/module 目录下

## 3.5 启 动 Prometheus Server 、 Pushgateway 和 **Alertmanager **
### 3.5.1 Prometheus Server 目录下执行启动命令 
```shell
[mhk@hadoop102 prometheus-2.29.1]$ nohup ./prometheus --config.file=prometheus.yml > ./prometheus.log 2>&1 &
```
### 3.5.2 Pushgateway 目录下执行启动命令 
```shell
[mhk@hadoop102 pushgateway-1.4.1]$ nohup ./pushgateway --web.listen-address :9091 > ./pushgateway.log 2>&1 & 
```
### 3.5.3 在 Alertmanager 目录下启动 
```shell
[mhk@hadoop102 alertmanager-0.23.0]$ nohup ./alertmanager --config.file=alertmanager.yml > ./alertmanager.log 2>&1 & 
```
### 3.5.4 打开 web 页面查看 

- 浏览器输入：http://hadoop202:9090/ 
- 点击 Status，选中 Targets： 

![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1651758595892-1ddb24ff-de6a-4e13-b35f-166de53f4d9c.png#clientId=ua4a51593-7502-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=319&id=uc160755a&margin=%5Bobject%20Object%5D&name=image.png&originHeight=319&originWidth=856&originalType=binary&ratio=1&rotation=0&showTitle=false&size=74157&status=done&style=none&taskId=u22799cd6-809a-4bb0-b629-9ea0652c6d6&title=&width=856)

- prometheus、pushgateway 和 node exporter 都是 up 状态，表示安装启动成功：

![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1651758625322-56dc464e-cd7a-476a-a23b-f57d1b622272.png#clientId=ua4a51593-7502-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=363&id=u521f58a9&margin=%5Bobject%20Object%5D&name=image.png&originHeight=363&originWidth=797&originalType=binary&ratio=1&rotation=0&showTitle=false&size=188477&status=done&style=none&taskId=u32870179-1239-49b7-865e-560d813d788&title=&width=797)
