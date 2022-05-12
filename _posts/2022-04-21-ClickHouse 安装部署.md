# 1 准备工作 
## 1.1 确定防火墙处于关闭状态 
## 1.2 CentOS 取消打开文件数限制 
（1）在 hadoop102 的 /etc/security/limits.conf 文件的末尾加入以下内容
```shell
[mhk@hadoop102 ~]$ sudo vim /etc/security/limits.conf
* soft nofile 65536
* hard nofile 65536
* soft nproc 131072
* hard nproc 131072
```
 
（2）在 hadoop102 的/etc/security/limits.d/20-nproc.conf 文件的末尾加入以下内容
```shell
[mhk@hadoop102 ~]$ sudo vim /etc/security/limits.d/20-nproc.conf
* soft nofile 65536
* hard nofile 65536
* soft nproc 131072
* hard nproc 131072
```

（3）执行同步操作
xsync分发脚本
```shell
#!/bin/bash
#1. 判断参数个数
if [ $# -lt 1 ]
then
  echo Not Enough Arguement!
  exit;
fi
#2. 遍历集群所有机器
for host in hadoop102 hadoop103 hadoop104
do
  echo ====================  $host  ====================
  #3. 遍历所有目录，挨个发送
  for file in $@
  do
    #4. 判断文件是否存在
    if [ -e $file ]
    then
      #5. 获取父目录
      pdir=$(cd -P $(dirname $file); pwd)
      #6. 获取当前文件的名称
      fname=$(basename $file)
      ssh $host "mkdir -p $pdir"
      rsync -av $pdir/$fname $host:$pdir
    else
      echo $file does not exists!
    fi
  done
done
```
```shell
[mhk@hadoop102 ~]$ sudo /home/mhk/bin/xsync /etc/security/limits.conf
[mhk@hadoop102 ~]$ sudo /home/mhk/bin/xsync /etc/security/limits.d/20-nproc.conf
```

## 1.3 安装依赖
```shell
[mhk@hadoop102 ~]$ sudo yum install -y libtool
[mhk@hadoop102 ~]$ sudo yum install -y *unixODBC*
```
在 hadoop103、hadoop104 上执行以上操作

## 1.4 CentOS 取消 SELINUX 
（1）修改/etc/selinux/config 中的 SELINUX=disabled 
```shell
[mhk@hadoop102 ~]$ sudo vim /etc/selinux/config 
SELINUX=disabled 
注意：别改错了 
```
（2）执行同步操作 
```shell
[mhk@hadoop102 ~]$ sudo /home/atguigu/bin/xsync /etc/selinux/config 
```
（3）重启三台服务器，修改内核级别的东西需要重启

# 2 单机安装 
官网：https://clickhouse.tech/ 
下载地址：http://repo.red-soft.biz/repos/clickhouse/stable/el7/ 
## 2.1 在 hadoop102 的/opt/software 下创建 clickhouse 目录
```shell
[mhk@hadoop102 software]$ mkdir clickhouse
```
 
## 2.2 将以下 4 个文件上传到 hadoop102 的 **software/clickhouse 目录下**
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1650448886421-e4152b6b-965a-45fc-9a96-d22a517f2dbd.png#clientId=ud73da38b-4b8b-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=82&id=u6f7518c4&margin=%5Bobject%20Object%5D&name=image.png&originHeight=82&originWidth=214&originalType=binary&ratio=1&rotation=0&showTitle=false&size=14603&status=done&style=none&taskId=uced851eb-9f9a-4014-a171-b54a9e227ad&title=&width=214)
## 2.3 将安装文件同步到 hadoop103、hadoop104
```shell
[mhk@hadoop102 software]$ xsync clickhouse
```
   
## 2.4 分别在三台机子上安装这 4 个 rpm 文件
```shell
[mhk@hadoop103 clickhouse]$ sudo rpm -ivh *.rpm

[mhk@hadoop103 clickhouse]$ sudo rpm -qa|grep clickhouse
clickhouse-server-21.7.3.14-2.noarch
clickhouse-client-21.7.3.14-2.noarch
clickhouse-common-static-dbg-21.7.3.14-2.x86_64
clickhouse-common-static-21.7.3.14-2.x86_64
```

## 2.5 修改配置文件
```shell
[mhk@hadoop102 clickhouse]$ sudo vim /etc/clickhouse-server/config.xml
```

（1）把 <listen_host>::</listen_host> 的注释打开，这样的话才能让 ClickHouse 被除本机以外的服务器访问

（2）分发配置文件 
```shell
sudo /home/mhk/bin/xsync /etc/clickhouse-server/config.xml 
```
在这个文件中，有 ClickHouse 的一些默认路径配置，比较重要的 
数据文件路径：<path>/var/lib/clickhouse/</path> 
日志文件路径：<log>/var/log/clickhouse-server/clickhouse-server.log</log>

## 2.6 启动 Server
```shell
[mhk@hadoop102 bin]$ sudo clickhouse start
 chown --recursive clickhouse '/var/run/clickhouse-server/'
Will run su -s /bin/sh 'clickhouse' -c '/usr/bin/clickhouse-server --config-file /etc/clickhouse-server/config.xml --pid-file /var/run/clickhouse-server/clickhouse-server.pid --daemon'
Waiting for server to start
Waiting for server to start
Server started
```
   
## 2.7 三台机器上关闭开机自启
```shell
[mhk@hadoop102 ~]$ sudo systemctl disable clickhouse-server
Removed symlink /etc/systemd/system/multi-user.target.wants/clickhouse-server.service.
```

## 2.8 使用 client 连接 server
```shell
[mhk@hadoop102 bin]$ clickhouse-client -m
ClickHouse client version 21.7.3.14 (official build).
Connecting to localhost:9000 as user default.
Connected to ClickHouse server version 21.7.3 revision 54449.

hadoop102 :) 


-m 表示可以换行，以分号来识别语句的结束

远程访问
clickhouse-client -h hadoop103 -p 端口   

clickhouse-client --query "查询语句"
类似于
hive -e ""
写SQL，我不进去，给我返回结果
```
```shell
hadoop102 :) show databases;

SHOW DATABASES

Query id: 0a19d7e7-274b-40b2-a25c-b0d173b6077c

┌─name────┐
│ default │
│ system  │
└─────────┘

2 rows in set. Elapsed: 0.006 sec. 

hadoop102 :) use system;

USE system

Query id: 2bca7a0e-f42d-4777-942a-8fcddee70e69

Ok.

0 rows in set. Elapsed: 0.004 sec. 
```

# 3. 其他
文件所在地
bin/    ====>   /usr/bin/
conf/   ====>   /etc/clickhouse-server/
lib/    ====>   /var/lib/clickhouse/
log/    ====>   /var/log/clickhouse/
