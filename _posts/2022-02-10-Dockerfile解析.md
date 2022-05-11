# ![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1644482872925-9045d88d-84c9-4a16-8177-e26d0786b990.png#clientId=uc4b6cf48-48c5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=530&id=uc55a6721&margin=%5Bobject%20Object%5D&name=image.png&originHeight=530&originWidth=778&originalType=binary&ratio=1&rotation=0&showTitle=false&size=267893&status=done&style=none&taskId=ua061d0c8-91ea-4144-9aff-e335da99ac5&title=&width=778)
# 1. 是什么？
Dockerfile是用来构建Docker镜像的文本文件，是由一条条构建镜像所需的指令和参数构成的脚本。

**概述**
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1644482840543-0c459521-ac56-43a5-81fe-4c78acd9516f.png#clientId=uc4b6cf48-48c5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=720&id=u76497b2c&margin=%5Bobject%20Object%5D&name=image.png&originHeight=720&originWidth=874&originalType=binary&ratio=1&rotation=0&showTitle=false&size=1891689&status=done&style=none&taskId=u41fa81ca-5e41-48a4-825f-698026fd068&title=&width=874)
构建三步骤

- 编写Dockerfile文件
- docker build命令构建镜像
- docker run依镜像运行容器实例

# 2. Dockerfile构建过程解析
## 2.1 Dockerfile内容基础知识

1. 每条保留字指令都必须为大写字母且后面要跟随至少一个参数
1. 指令按照从上到下，顺序执行
1. #表示注释
1. 每条指令都会创建一个新的镜像层并对镜像进行提交

## 2.2 Docker执行Dockerfile的大致流程

1. docker从基础镜像运行一个容器
1. 执行一条指令并对容器作出修改
1. 执行类似docker commit的操作提交一个新的镜像层
1. docker再基于刚提交的镜像运行一个新容器
1. 执行dockerfile中的下一条指令直到所有指令都执行完成

## 2.3 小总结
从应用软件的角度来看，Dockerfile、Docker镜像与Docker容器分别代表软件的三个不同阶段，

- Dockerfile是软件的原材料
- Docker镜像是软件的交付品
- Docker容器则可以认为是软件镜像的运行态，也即依照镜像运行的容器实例

Dockerfile面向开发，Docker镜像成为交付标准，Docker容器则涉及部署与运维，三者缺一不可，合力充当Docker体系的基石。
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1644483221205-85c25c98-a34f-459e-ab99-6a15cd3bbf0b.png#clientId=uc4b6cf48-48c5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=545&id=ue3045f44&margin=%5Bobject%20Object%5D&name=image.png&originHeight=545&originWidth=1280&originalType=binary&ratio=1&rotation=0&showTitle=false&size=2096804&status=done&style=none&taskId=uc3f75f88-4115-43e9-b6d6-d62af3fa937&title=&width=1280)

1. Dockerfile，需要定义一个Dockerfile，Dockerfile定义了进程需要的一切东西。Dockerfile涉及的内容包括执行代码或者是文件、环境变量、依赖包、运行时环境、动态链接库、操作系统的发行版、服务进程和内核进程(当应用进程需要和系统服务和内核进程打交道，这时需要考虑如何设计namespace的权限控制)等等;

2. Docker镜像，在用Dockerfile定义一个文件之后，docker build时会产生一个Docker镜像，当运行 Docker镜像时会真正开始提供服务;

3. Docker容器，容器是直接提供服务的。

# 3. Dockerfile常用保留字指令
## 3.1 FROM
基础镜像，当前新镜像是基于哪个镜像的，指定一个已经存在的镜像作为模板，第一条必须是FROM
## 3.2 MAINTAINER
镜像维护者的姓名和邮箱地址
## 3.3 RUN
容器构建时需要运行的命令
两种格式：
（1）shell格式![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1644483552624-336e0194-a3f7-47f2-8782-5e450380022c.png#clientId=uc4b6cf48-48c5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=215&id=u8e9387e4&margin=%5Bobject%20Object%5D&name=image.png&originHeight=215&originWidth=1280&originalType=binary&ratio=1&rotation=0&showTitle=false&size=827224&status=done&style=none&taskId=ua5eb69a3-dc43-4e82-8761-2cd6f8c5aa7&title=&width=1280)
RUN yum -y install vim
（2）exec格式
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1644483632820-240c2430-89b1-4b66-9234-2fa68d6d45a1.png#clientId=uc4b6cf48-48c5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=200&id=u65a51d7c&margin=%5Bobject%20Object%5D&name=image.png&originHeight=200&originWidth=1280&originalType=binary&ratio=1&rotation=0&showTitle=false&size=769515&status=done&style=none&taskId=u7fc39155-ffe7-4a6c-9b31-dc369cf8874&title=&width=1280)
RUN是在 docker build时运行
## 3.4. EXPOSE
当前容器对外暴露出的端口
## 3.5. WORKDIR
指定在创建容器后，终端默认登陆的进来工作目录，一个落脚点
## 3.6. USER
指定该镜像以什么样的用户去执行，如果都不指定，默认是root
## 3.7. ENV
用来在构建镜像过程中设置环境变量
ENV MY_PATH /usr/mytest
这个环境变量可以在后续的任何RUN指令中使用，这就如同在命令前面指定了环境变量前缀一样；
也可以在其它指令中直接使用这些环境变量，
比如：WORKDIR $MY_PATH
## 3.8. ADD
将宿主机目录下的文件拷贝进镜像且会自动处理URL和解压tar压缩包
## 3.9. COPY
类似ADD，拷贝文件和目录到镜像中。 将从构建上下文目录中 <源路径> 的文件/目录复制到新的一层的镜像内的 <目标路径> 位置
COPY src dest
COPY ["src", "dest"]
<src源路径>：源文件或者源目录
<dest目标路径>：容器内的指定路径，该路径不用事先建好，路径不存在的话，会自动创建。
## 3.10. VOLUME
容器数据卷，用于数据保存和持久化工作
## 3.11. CMD
指定容器启动后的要干的事情
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1644484066378-20c8bb8b-aef2-426c-b8ae-a7bd7429b2b2.png#clientId=uc4b6cf48-48c5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=370&id=uf7f9625a&margin=%5Bobject%20Object%5D&name=image.png&originHeight=370&originWidth=1280&originalType=binary&ratio=1&rotation=0&showTitle=false&size=1897911&status=done&style=none&taskId=u5c421567-76c0-4488-b678-900dff2be9b&title=&width=1280)
注意
Dockerfile 中可以有多个 CMD 指令，但只有最后一个生效，CMD 会被 docker run 之后的参数替换
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1644484159626-e3bffa49-990b-49ea-b083-1f10787fe9a4.png#clientId=uc4b6cf48-48c5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=88&id=u9a24aeef&margin=%5Bobject%20Object%5D&name=image.png&originHeight=88&originWidth=1280&originalType=binary&ratio=1&rotation=0&showTitle=false&size=338634&status=done&style=none&taskId=ud4c9e01e-146c-4726-8d36-294ab916617&title=&width=1280)

它和前面RUN命令的区别
CMD是在docker run 时运行。
RUN是在 docker build时运行。
## 3.12. ENTRYPOINT
也是用来指定一个容器启动时要运行的命令
类似于 CMD 指令，但是ENTRYPOINT不会被docker run后面的命令覆盖， 而且这些命令行参数会被当作参数送给 ENTRYPOINT 指令指定的程序
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1644484267823-6c634f50-11fd-4516-a3b1-36ebc11dafe3.png#clientId=uc4b6cf48-48c5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=109&id=u75f1a39d&margin=%5Bobject%20Object%5D&name=image.png&originHeight=109&originWidth=1280&originalType=binary&ratio=1&rotation=0&showTitle=false&size=419430&status=done&style=none&taskId=ub100bdd1-a7c3-4a90-85a2-74db4da03dd&title=&width=1280)
ENTRYPOINT可以和CMD一起用，一般是变参才会使用 CMD ，这里的 CMD 等于是在给 ENTRYPOINT 传参。
当指定了ENTRYPOINT后，CMD的含义就发生了变化，不再是直接运行其命令而是将CMD的内容作为参数传递给ENTRYPOINT指令，他两个组合会变成![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1644484315252-e4ec7e8b-8f78-42d3-905d-cd2caf57b521.png#clientId=uc4b6cf48-48c5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=52&id=u53ef1017&margin=%5Bobject%20Object%5D&name=image.png&originHeight=226&originWidth=1280&originalType=binary&ratio=1&rotation=0&showTitle=false&size=869540&status=done&style=none&taskId=u6d79b5eb-512d-4d7f-b14c-85ef33caec2&title=&width=294)
案例如下：假设已通过 Dockerfile 构建了 nginx:test 镜像：
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1644484414103-81ba63ff-a5a8-479d-9901-016744fff50c.png#clientId=uc4b6cf48-48c5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=170&id=uc83963c2&margin=%5Bobject%20Object%5D&name=image.png&originHeight=395&originWidth=1280&originalType=binary&ratio=1&rotation=0&showTitle=false&size=1519729&status=done&style=none&taskId=ud9222394-95cb-4115-a6be-80e63c62009&title=&width=552)

| 是否传参 | 按照dockerfile编写执行 | 传参运行 |
| --- | --- | --- |
| Docker命令 | docker run  nginx:test | docker run  nginx:test -c /etc/nginx/new.conf |
| 衍生出的实际命令 | nginx -c /etc/nginx/nginx.conf | nginx -c /etc/nginx/new.conf |

优点
在执行docker run的时候可以指定 ENTRYPOINT 运行所需的参数。
注意
如果 Dockerfile 中如果存在多个 ENTRYPOINT 指令，仅最后一个生效。
## 3.13. 小总结
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1644485149489-03ad8ffb-c7c5-4b68-a46f-c565a1fba66e.png#clientId=uc4b6cf48-48c5-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=720&id=u01fd3606&margin=%5Bobject%20Object%5D&name=image.png&originHeight=720&originWidth=1046&originalType=binary&ratio=1&rotation=0&showTitle=false&size=2263804&status=done&style=none&taskId=u79713452-7f1f-4759-9a42-4b0bfb71cae&title=&width=1046)

# 4. 案例演示
自定义镜像mycentosjava8
要求:
Centos7镜像具备vim+ifconfig+jdk8
## 4.1. 准备编写Dockerfile文件
```shell
[root@AliyunServer myfile]# pwd
/myfile
[root@AliyunServer myfile]# ll
总用量 186424
-rw-r--r-- 1 root root       744 2月  10 16:30 Dockerfile
-rw-r--r-- 1 root root 190890122 2月  10 16:03 jdk-8u171-linux-x64.tar.gz
```
```shell
#注意：如果是lastest版本的centos，会在安装vim编辑器那里出错，最新版的centos8不支持那样下载，
#这时就不能单纯的 FROM centos 了
#改为 FROM centos:7.9.2009

FROM centos:7.9.2009
MAINTAINER mhk<hkmu9248@gmail.com>

ENV MYPATH /usr/local
WORKDIR $MYPATH

#安装vim编辑器
RUN yum -y install vim
#安装ifconfig命令查看网络IP
RUN yum -y install net-tools
#安装java8及lib库
RUN yum -y install glibc.i686
RUN mkdir /usr/local/java
#ADD 是相对路径jar,把jdk-8u171-linux-x64.tar.gz添加到容器中,安装包必须要和Dockerfile文件在同一位置
ADD jdk-8u171-linux-x64.tar.gz /usr/local/java/
#配置java环境变量
ENV JAVA_HOME /usr/local/java/jdk1.8.0_171
ENV JRE_HOME $JAVA_HOME/jre
ENV CLASSPATH $JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar:$JRE_HOME/lib:$CLASSPATH
ENV PATH $JAVA_HOME/bin:$PATH

EXPOSE 80

CMD echo $MYPATH
CMD echo "success--------------ok"
CMD /bin/bash
```
## 4.2. 构建
docker build -t 新镜像名字:TAG .
后面这个 . 千万不能忽略
docker build -t centosjava8:1.5 .
```shell
[root@AliyunServer myfile]# docker build -t centosjava8:1.5 .
Sending build context to Docker daemon  190.9MB
Step 1/17 : FROM centos:7.9.2009
 ---> eeb6ee3f44bd
Step 2/17 : MAINTAINER mhk<hkmu9248@gmail.com>
 ---> Running in 25afd897b9a3
Removing intermediate container 25afd897b9a3
 ---> aeb91d5e32c2
Step 3/17 : ENV MYPATH /usr/local
 ---> Running in 1401a9b5fe23
Removing intermediate container 1401a9b5fe23
 ---> 4448bd9822a3
Step 4/17 : WORKDIR $MYPATH
 ---> Running in 8a9a888f9a27
Removing intermediate container 8a9a888f9a27
 ---> 3a800b88feb3
Step 5/17 : RUN yum -y install vim
 ---> Running in e241a95e665e
Loaded plugins: fastestmirror, ovl
Determining fastest mirrors
 * base: mirrors.huaweicloud.com
 * extras: mirrors.bupt.edu.cn
 * updates: mirrors.tuna.tsinghua.edu.cn
 ...
```
## 4.3 查看镜像并运行
```shell
[root@AliyunServer myfile]# docker images
REPOSITORY                                       TAG        IMAGE ID       CREATED          SIZE
centosjava8                                      1.5        e6a6c6f56a77   12 seconds ago   1.15GB
<none>                                           <none>     a9c13e287bed   13 minutes ago   231MB
172.28.109.11:5000/mhk/ubuntu                    1.3        67aed549da77   22 hours ago     108MB
mhk/ubuntu                                       1.3        67aed549da77   22 hours ago     108MB

[root@AliyunServer myfile]# docker run -it e6a6c6f56a77 /bin/bash
[root@f0861bf507ac local]# pwd
/usr/local
[root@f0861bf507ac local]# java -version
java version "1.8.0_171"
Java(TM) SE Runtime Environment (build 1.8.0_171-b11)
Java HotSpot(TM) 64-Bit Server VM (build 25.171-b11, mixed mode)
[root@f0861bf507ac local]# ifconfig 
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 172.17.0.2  netmask 255.255.0.0  broadcast 172.17.255.255
        ether 02:42:ac:11:00:02  txqueuelen 0  (Ethernet)
        RX packets 8  bytes 656 (656.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```
# 5. 虚悬镜像
## 5.1 是什么？
仓库名、标签都是<none>的镜像，俗称dangling image
## 5.2 为什么会有 <none> 这样命名的镜像？
当镜像被新的镜像覆盖时候，老版本镜像名称会变成 <none> 。

## 5.3 查看
docker image ls -f dangling=true
```shell
[root@AliyunServer myfile]# docker image ls -f dangling=true
REPOSITORY   TAG       IMAGE ID       CREATED       SIZE
<none>       <none>    a9c13e287bed   2 hours ago   231MB
```
## 5.4 删除
docker image prune
虚悬镜像已经失去存在价值，可以删除
```shell
[root@AliyunServer myfile]# docker image prune
WARNING! This will remove all dangling images.
Are you sure you want to continue? [y/N] y
Total reclaimed space: 0B
[root@AliyunServer myfile]# docker image ls -f dangling=true
REPOSITORY   TAG       IMAGE ID       CREATED       SIZE
<none>       <none>    a9c13e287bed   2 hours ago   231MB

[root@AliyunServer myfile]# docker rmi $(docker images -q -f dangling=true)
Error response from daemon: conflict: unable to delete a9c13e287bed (must be forced) - image is being used by stopped container 79af6edf5714
[root@AliyunServer myfile]# docker rmi -f $(docker images -q -f dangling=true)
Deleted: sha256:a9c13e287bed2463d8395cd60834f4a98659961929db67ca785a3fd5106b18eb
Deleted: sha256:9aa6460c8d064738830cd6c40e19cfb7dbfc3a314d514edccdf2f5cf6edae57d
Deleted: sha256:5125480652540bb320619be1f6cef9fa508bb9001a2f5c4762de64194e1f4d0e
[root@AliyunServer myfile]# docker image ls -f dangling=true
REPOSITORY   TAG       IMAGE ID   CREATED   SIZE
```
