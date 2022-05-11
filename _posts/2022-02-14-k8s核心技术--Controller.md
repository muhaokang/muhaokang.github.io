# 1. 什么是Controller
K8S是容器资源管理和调度平台，容器跑在Pod里，Pod是K8S里最小的单元。所以，这些Pod作为一个个单元我们肯定需要去操作它的状态和生命周期。那么如何操作？这里就需要用到控制器了。

这里一个比较通俗的公式：**应用APP = 网络 + 载体 + 存储**
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1644831796941-18a1f4a5-43ba-4ed6-9970-5d1d11d6814d.png#clientId=ue8c7e90e-db13-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=245&id=u82d37d08&margin=%5Bobject%20Object%5D&name=image.png&originHeight=245&originWidth=1023&originalType=binary&ratio=1&rotation=0&showTitle=false&size=78317&status=done&style=none&taskId=u32eefc33-b2cc-41ea-84fe-3820972c1e4&title=&width=1023)
这里应用一般分为无状态应用、有状态应用、守护型应用、批处理应用这四种。

**无状态应用**：应用实例不涉及事务交互，不产生持久化数据存储在本地，并且多个应用实例对于同一个请求响应的结果是完全一致的。举例：nginx或者tomcat
**有状态应用**：有状态服务可以说是需要数据存储功能的服务或者指多线程类型的服务、队列等。举例：mysql数据库、kafka、redis、zookeeper等。
**守护型应用**：类似守护进程一样，长期保持运行，监听持续的提供服务。举例：filebeat等。
**批处理应用**：工作任务型的服务，通常是一次性的。举例：运行一个批量改文件夹名字的脚本。

这些类型的应用服务如果是安装在传统的物理机或者虚拟机上，那么我们一般会通过人肉方式或者自动化工具的方式去管理编排。但是这些服务一旦容器化了跑在了Pod里，那么就应该按照K8S的控制方式来管理了。上一篇文章我们讲到了编排，那么K8S靠什么具体的操作来做编排？答案就是这些控制器。

# 2. k8s有哪些控制器
既然应用的类型有上面说的这些无状态、有状态的，那么K8S肯定要实现一些控制器来专门处理对应类型的应用。总体来说，K8S有五种控制器，分别对应处理无状态应用、有状态应用、守护型应用和批处理应用
## 2.1 Deployment
### 2.1.1 Deployment的应用

- Deployment控制器可以部署无状态应用
- 管理Pod和ReplicaSet
- 部署，滚动升级等功能
- 应用场景：web服务，微服务

Deployment表示用户对K8S集群的一次更新操作。Deployment是一个比RS( Replica Set, RS) 应用模型更广的 API 对象，可以是创建一个新的服务，更新一个新的服务，也可以是滚动升级一个服务。滚动升级一个服务，实际是创建一个新的RS，然后逐渐将新 RS 中副本数增加到理想状态，将旧RS中的副本数减少到0的复合操作。

这样一个复合操作用一个RS是不好描述的，所以用一个更通用的Deployment来描述。以K8S的发展方向，未来对所有长期伺服型的业务的管理，都会通过Deployment来管理。

### 2.1.2 Deployment部署应用
之前我们也使用Deployment部署过应用，如下代码所示
```shell
kubectrl create deployment web --image=nginx
```
但是上述代码不是很好的进行复用，因为每次我们都需要重新输入代码，所以我们都是通过YAML进行配置

1. 我们可以尝试使用上面的代码创建一个镜像【只是尝试，不会创建】
```shell
kubectl create deployment web --image=nginx --dry-run -o yaml > nginx.yaml
```

2. 然后输出一个yaml配置文件nginx.yaml ，配置文件如下所示
```shell
apiVersion: apps/v1
kind: Deployment
metadata:
  creationTimestamp: null
  labels:
    app: web
  name: web
spec:
  replicas: 1
  selector:
    matchLabels:
      app: web
  strategy: {}
  template:
    metadata:
      creationTimestamp: null
      labels:
        app: web
    spec:
      containers:
      - image: nginx
        name: nginx
        resources: {}
status: {}
```
我们看到的 selector 和 label 就是我们Pod 和 Controller之间建立关系的桥梁
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1644832391762-445f6182-9a17-4d50-bac3-96762af5561e.png#clientId=ue8c7e90e-db13-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=264&id=u9501cffc&margin=%5Bobject%20Object%5D&name=image.png&originHeight=264&originWidth=369&originalType=binary&ratio=1&rotation=0&showTitle=false&size=50324&status=done&style=none&taskId=u32a96c9a-6437-4ea4-8ffd-32e72a81b40&title=&width=369)

3. 通过刚刚的代码，我们已经生成了YAML文件，下面我们就可以使用该配置文件快速创建Pod镜像了
```shell
[root@k8s-master ~]# kubectl apply -f nginx.yaml
deployment.apps/nginx created
[root@k8s-master ~]# kubectl get pods
NAME                    READY   STATUS              RESTARTS   AGE
nginx-f89759699-njkj4   0/1     ContainerCreating   0          4s
```

4. 但是因为这个方式创建的，我们只能在集群内部进行访问，所以我们还需要对外暴露端口
```shell
[root@k8s-master ~]# kubectl expose deployment web --port=80 --type=NodePort --target-port=80 --name=web
service/web exposed
```
关于上述命令，有几个参数

- --port：就是我们内部的端口号
- --target-port：就是暴露外面访问的端口号
- --name：名称
- --type：类型
5. 同理，我们一样可以导出对应的配置文件
```shell
[root@k8s-master ~]# kubectl expose deployment web --port=80 --type=NodePort --target-port=80 --name=web2 -o yaml > web2.yaml
[root@k8s-master ~]# cat web2.yaml 
apiVersion: v1
kind: Service
metadata:
  creationTimestamp: "2022-02-14T10:04:54Z"
  labels:
    app: web
  managedFields:
  - apiVersion: v1
    fieldsType: FieldsV1
    fieldsV1:
      f:metadata:
        f:labels:
          .: {}
          f:app: {}
      f:spec:
        f:externalTrafficPolicy: {}
        f:ports:
          .: {}
          k:{"port":80,"protocol":"TCP"}:
            .: {}
            f:port: {}
            f:protocol: {}
            f:targetPort: {}
        f:selector:
          .: {}
          f:app: {}
        f:sessionAffinity: {}
        f:type: {}
    manager: kubectl
    operation: Update
    time: "2022-02-14T10:04:54Z"
  name: web2
  namespace: default
  resourceVersion: "155843"
  selfLink: /api/v1/namespaces/default/services/web2
  uid: 802c85d5-0cf5-4026-bec9-8e44e7470547
spec:
  clusterIP: 10.104.205.5
  externalTrafficPolicy: Cluster
  ports:
  - nodePort: 30886
    port: 80
    protocol: TCP
    targetPort: 80
  selector:
    app: web
  sessionAffinity: None
  type: NodePort
status:
  loadBalancer: {}
```

6. 然后我们可以通过下面的命令来查看对外暴露的服务
```shell
[root@k8s-master ~]# kubectl get pods,svc
NAME                      READY   STATUS    RESTARTS   AGE
pod/web-65b7447c7-88rjd   1/1     Running   0          3m59s

NAME                 TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)        AGE
service/kubernetes   ClusterIP   10.96.0.1        <none>        443/TCP        2d1h
service/nginx        NodePort    10.107.175.33    <none>        80:32762/TCP   2d
service/web          NodePort    10.97.116.53     <none>        80:31386/TCP   3m43s
service/web1         NodePort    10.109.192.119   <none>        80:31664/TCP   21h
service/web2         NodePort    10.104.205.5     <none>        80:30886/TCP   2m7s
```

7. 然后我们访问对应的url，即可看到 nginx了[http://10.211.55.15:30886/](http://10.211.55.15:30886/)

![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1644833382808-00d71283-5b9c-46bf-994b-8451d69aff38.png#clientId=ue8c7e90e-db13-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=236&id=ud3708a64&margin=%5Bobject%20Object%5D&name=image.png&originHeight=236&originWidth=576&originalType=binary&ratio=1&rotation=0&showTitle=false&size=64068&status=done&style=none&taskId=u0287a40e-053c-40e7-bda8-0df2d49d3ee&title=&width=576)
### 2.1.3 升级回滚和弹性伸缩

- 升级： 假设从版本为1.14 升级到 1.15 ，这就叫应用的升级【升级可以保证服务不中断】
- 回滚：从版本1.15 变成 1.14，这就叫应用的回滚
- 弹性伸缩：我们根据不同的业务场景，来改变Pod的数量对外提供服务，这就是弹性伸缩

#### 应用的升级和回滚

1. 修改yaml文件，把版本修改为1.14
```shell
[root@k8s-master ~]# vim web.yaml 
containers:
      - image: nginx:1.14
        name: nginx
```

2. 开始创建我们的Pod
```shell
[root@k8s-master ~]# kubectl apply -f web.yaml 
deployment.apps/web configured
[root@k8s-master ~]# kubectl get pods
NAME                    READY   STATUS              RESTARTS   AGE
web-66bf4959f5-lw8tx    0/1     ContainerCreating   0          27s
```

3. 我们使用下面的命令，可以将nginx从 1.14 升级到 1.15
```shell
[root@k8s-master ~]# kubectl set image deployment web nginx=nginx:1.15
deployment.apps/web image updated
[root@k8s-master ~]# kubectl get pod
NAME                   READY   STATUS              RESTARTS   AGE
web-65b7447c7-88rjd    1/1     Running             0          18m
web-7d9697b7f8-9w4z8   0/1     ContainerCreating   0          5s

[root@k8s-master ~]# kubectl get pod
NAME                   READY   STATUS        RESTARTS   AGE
web-65b7447c7-88rjd    0/1     Terminating   0          19m
web-7d9697b7f8-9w4z8   1/1     Running       0          55s

[root@k8s-master ~]# kubectl get pod
NAME                   READY   STATUS    RESTARTS   AGE
web-7d9697b7f8-9w4z8   1/1     Running   0          2m18s
```

- 首先是开始的nginx 1.14版本的Pod在运行，然后 1.15版本的在创建
- 然后在1.15版本创建完成后，就会暂停1.14版本
- 最后把1.14版本的Pod移除，完成我们的升级

我们在下载 1.15版本，容器就处于ContainerCreating状态，然后下载完成后，就用 1.15版本去替换1.14版本了，这么做的好处就是：升级可以保证服务不中断

4. 查看升级状态
```shell
[root@k8s-master ~]# kubectl rollout status deployment web
deployment "web" successfully rolled out
```

5. 查看历史版本
```shell
[root@k8s-master ~]# kubectl rollout history deployment web
deployment.apps/web 
REVISION  CHANGE-CAUSE
1         <none>
2         <none>
```

6. 我们可以使用下面命令，完成回滚操作，也就是回滚到上一个版本
```shell
[root@k8s-master ~]# kubectl rollout undo deployment web
deployment.apps/web rolled back
[root@k8s-master ~]# kubectl get pod
NAME                  READY   STATUS    RESTARTS   AGE
web-65b7447c7-lcc58   1/1     Running   0          4s
[root@k8s-master ~]# kubectl rollout status deployment web
deployment "web" successfully rolled out
```

7. 我们还可以回滚到指定版本
```shell
[root@k8s-master ~]# kubectl rollout undo deployment web --to-revision=2
deployment.apps/web rolled back
[root@k8s-master ~]# kubectl get pod
NAME                   READY   STATUS    RESTARTS   AGE
web-7d9697b7f8-dw9lq   1/1     Running   0          5s
```
可以观察到编号的变化

#### 弹性伸缩
弹性伸缩，也就是我们通过命令一下创建多个副本
```shell
[root@k8s-master ~]# kubectl scale deployment web --replicas=10
deployment.apps/web scaled
[root@k8s-master ~]# kubectl get pod -o wide
NAME                   READY   STATUS              RESTARTS   AGE    IP            NODE        NOMINATED NODE   READINESS GATES
web-7d9697b7f8-4xgjm   0/1     ContainerCreating   0          13s    <none>        k8s-node2   <none>           <none>
web-7d9697b7f8-5r947   1/1     Running             0          13s    10.244.1.10   k8s-node1   <none>           <none>
web-7d9697b7f8-6f92s   0/1     ContainerCreating   0          13s    <none>        k8s-node2   <none>           <none>
web-7d9697b7f8-7dngg   1/1     Running             0          13s    10.244.1.13   k8s-node1   <none>           <none>
web-7d9697b7f8-8g8mx   0/1     ContainerCreating   0          13s    <none>        k8s-node2   <none>           <none>
web-7d9697b7f8-b82vt   0/1     ContainerCreating   0          13s    <none>        k8s-node2   <none>           <none>
web-7d9697b7f8-dw9lq   1/1     Running             0          107s   10.244.1.9    k8s-node1   <none>           <none>
web-7d9697b7f8-qj9rz   0/1     ContainerCreating   0          13s    <none>        k8s-node2   <none>           <none>
web-7d9697b7f8-qzvqz   1/1     Running             0          13s    10.244.1.11   k8s-node1   <none>           <none>
web-7d9697b7f8-vxc4k   1/1     Running             0          13s    10.244.1.12   k8s-node1   <none>           <none>
```
## 2.2 StatefulSet
Statefulset主要是用来部署有状态应用
对于StatefulSet中的Pod，每个Pod挂载自己独立的存储，如果一个Pod出现故障，从其他节点启动一个同样名字的Pod，要挂载上原来Pod的存储继续以它的状态提供服务。

StatefulSet的出现是K8S为了解决 “有状态” 应用落地而产生的，Stateful这个单词本身就是“有状态”的意思。之前大家一直怀疑有状态应用落地K8S的可行性，StatefulSet很有效解决了这个问题。有状态应用一般都需要具备一致性，它们有固定的网络标记、持久化存储、顺序部署和扩展、顺序滚动更新等等。总结两个词就是需要稳定、有序。
那么StatefulSet如何做到Pod的稳定、有序？具体有了哪些内在机制和方法？主要概况起来有这几个方面：

- 给Pod一个唯一和持久的标识（例:Pod name）
- 给予Pod一份持久化存储
- 部署Pod都是顺序性的，0 ~ N-1
- 扩容Pod必须前面的Pod还存在着
- 终止Pod，后面Pod也一并终止

举个例子：创建了zk01、zk02、zk03 三个Pod，zk01就是给的命名，如果要扩容zk04，那么前面01、02、03必须存在，否则不成功；如果删除了zk02，那么zk03也会被删除。

无状态应用：
我们原来使用 deployment，部署的都是无状态的应用，那什么是无状态应用？

- 认为Pod都是一样的
- 没有顺序要求
- 不考虑应用在哪个node上运行
- 能够进行随意伸缩和扩展

有状态应用
上述的因素都需要考虑到

- 让每个Pod独立的
- 让每个Pod独立的，保持Pod启动顺序和唯一性
- 唯一的网络标识符，持久存储
- 有序，比如mysql中的主从

StatefulSet的另一种典型应用场景是作为一种比普通容器更稳定可靠的模拟虚拟机的机制。传统的虚拟机正是一种有状态的宠物，运维人员需要不断地维护它，容器刚开始流行时，我们用容器来模拟虚拟机使用，所有状态都保存在容器里，而这已被证明是非常不安全、不可靠的。

使用StatefulSet，Pod仍然可以通过漂移到不同节点提供高可用，而存储也可以通过外挂的存储来提供 高可靠性，StatefulSet做的只是将确定的Pod与确定的存储关联起来保证状态的连续性。

## 2.3 DaemonSet
DaemonSet 即后台支撑型服务，主要是用来部署守护进程

长期伺服型和批处理型的核心在业务应用，可能有些节点运行多个同类业务的Pod，有些节点上又没有这类的Pod运行；而后台支撑型服务的核心关注点在K8S集群中的节点(物理机或虚拟机)，要保证每个节点上都有一个此类Pod运行。节点可能是所有集群节点，也可能是通过 nodeSelector选定的一些特定节点。典型的后台支撑型服务包括：存储、日志和监控等。在每个节点上支撑K8S集群运行的服务。

守护进程在我们每个节点上，运行的是同一个pod，新加入的节点也同样运行在同一个pod里面

- 例子：在每个node节点安装数据采集工具
```shell
[root@k8s-master ~]# vim ds.yaml 
apiVersion: apps/v1
kind: DaemonSet
metadata:
  labels:
    app: filebeat
  name: filebeat
spec:
  selector:
    matchLabels:
      app: filebeat
  template:
    metadata:
      labels:
        app: filebeat
    spec:
      containers:
      - image: nginx
        name: logs
        ports:
        - containerPort: 80
        volumeMounts:
        - name: varlog
          mountPath: /tmp/log
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
[root@k8s-master ~]# kubectl apply -f ds.yaml 
daemonset.apps/filebeat created
[root@k8s-master ~]# kubectl get pod
NAME             READY   STATUS    RESTARTS   AGE
filebeat-7mh82   1/1     Running   0          108s
filebeat-rg6p9   1/1     Running   0          108s

[root@k8s-master ~]# kubectl exec -it filebeat-7mh82 bash
kubectl exec [POD] [COMMAND] is DEPRECATED and will be removed in a future version. Use kubectl kubectl exec [POD] -- [COMMAND] instead.
root@filebeat-7mh82:/# ls /tmp/log 
anaconda           btmp-20220212  cron-20220213       lastlog           messages-20220212  rhsm             spooler-20220212  yum.log
audit              chrony         dmesg               maillog           messages-20220213  secure           spooler-20220213  yum.log-20220212
boot.log           containers     dmesg.old           maillog-20220212  ntpstats           secure-20220212  tallylog
boot.log-20220212  cron           firewalld           maillog-20220213  pods               secure-20220213  tuned
btmp               cron-20220212  grubby_prune_debug  messages          qemu-ga            spooler          wtmp
```
这里是不是一个FileBeat镜像，主要是为了做日志采集工作

## 2.4 Job和CornJob
一次性任务 和 定时任务

- 一次性任务：一次性执行完就结束
- 定时任务：周期性执行

Job是K8S中用来控制批处理型任务的API对象。批处理业务与长期伺服业务的主要区别就是批处理业务的运行有头有尾，而长期伺服业务在用户不停止的情况下永远运行。
Job管理的Pod根据用户的设置把任务成功完成就自动退出了。
成功完成的标志根据不同的 spec.completions 策略而不同：单Pod型任务有一个Pod成功就标志完成；定数成功行任务保证有N个任务全部成功；工作队列性任务根据应用确定的全局成功而标志成功。

### 2.4.1 Job
Job也即一次性任务
```shell
apiVersion: batch/v1
kind: Job
metadata:
  name: pi
spec:
  template:
    spec:
      containers:
      - image: prel
        name: pi
        command: ["perl", "-Mbignum=bpi", "-wle", "print bpi(2000)"]
      restartPolicy: Never
  backoffLimit: 4
```
用上述的配置文件，创建一个一次性任务，并查看
```shell
[root@k8s-master ~]# kubectl apply -f job.yaml 
job.batch/pi created
[root@k8s-master ~]# kubectl get job
NAME   COMPLETIONS   DURATION   AGE
pi     0/1           6s         6s
[root@k8s-master ~]# kubectl get pod
NAME             READY   STATUS              RESTARTS   AGE
filebeat-7mh82   1/1     Running             0          18m
filebeat-rg6p9   1/1     Running             0          18m
pi-dwsbm         0/1     ContainerCreating   0          9s
[root@k8s-master ~]# kubectl get pod
NAME             READY   STATUS      RESTARTS   AGE
filebeat-7mh82   1/1     Running     0          98m
filebeat-rg6p9   1/1     Running     0          98m
pi-dwsbm         0/1     Completed   0          80m
```
我们可以通过查看日志，查看到一次性任务的结果
```shell
[root@k8s-master ~]# kubectl logs pi-dwsbm
3.141592653589793238462643383279502884197......
```
### 2.4.2 CronJob
定时任务，cronjob.yaml如下所示
```shell
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: hello
spec:
  schedule: "*/1 * * * *"
  jobTemplate:
    spec:
      template:
        sec:
          containers:
            - image: busybox
              name: hello
              args:
              - /bin/sh
              - -c
              - date; echo Hello from the Kubernetes cluster
            restartPolicy: OnFailure
```
这里面的命令就是每个一段时间，这里是通过 cron 表达式配置的，通过 schedule字段
然后下面命令就是每个一段时间输出
我们首先用上述的配置文件，创建一个定时任务
```shell
kubectl apply -f cronjob.yaml

```
创建完成后，我们就可以通过下面命令查看定时任务
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1644843367529-ffea53d8-d95e-4a8b-b08e-7731091bd497.png#clientId=ue8c7e90e-db13-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=68&id=uf760da08&margin=%5Bobject%20Object%5D&name=image.png&originHeight=68&originWidth=568&originalType=binary&ratio=1&rotation=0&showTitle=false&size=40057&status=done&style=none&taskId=u1677574d-02ee-4fca-b616-92eef55a693&title=&width=568)
我们可以通过日志进行查看
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1644843391706-0a54b90c-33db-4895-8bcf-c748d0513180.png#clientId=ue8c7e90e-db13-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=65&id=u43d3f77d&margin=%5Bobject%20Object%5D&name=image.png&originHeight=65&originWidth=535&originalType=binary&ratio=1&rotation=0&showTitle=false&size=33261&status=done&style=none&taskId=u510834f2-5e60-4f24-a760-7f5583ecf92&title=&width=535)
然后每次执行，就会多出一个 pod
![image.png](https://cdn.nlark.com/yuque/0/2022/png/25452040/1644843419531-57644344-d8fd-4b88-9549-4e01262293c0.png#clientId=ue8c7e90e-db13-4&crop=0&crop=0&crop=1&crop=1&from=paste&height=171&id=u97180044&margin=%5Bobject%20Object%5D&name=image.png&originHeight=171&originWidth=565&originalType=binary&ratio=1&rotation=0&showTitle=false&size=101134&status=done&style=none&taskId=ua89f1376-8a7e-4f98-ae3c-02def687ee9&title=&width=565)

## 2.5 Replication Controller
Replication Controller 简称 **RC**，是K8S中的复制控制器。RC是K8S集群中最早的保证Pod高可用的API对象。通过监控运行中的Pod来保证集群中运行指定数目的Pod副本。指定的数目可以是多个也可以是1个；少于指定数目，RC就会启动新的Pod副本；多于指定数目，RC就会杀死多余的Pod副本。

即使在指定数目为1的情况下，通过RC运行Pod也比直接运行Pod更明智，因为RC也可以发挥它高可用的能力，保证永远有一个Pod在运行。RC是K8S中较早期的技术概念，只适用于长期伺服型的业务类型，比如控制Pod提供高可用的Web服务。

## 2.6 Replica Set 
Replica Set 检查 RS，也就是副本集。RS是新一代的RC，提供同样高可用能力，区别主要在于RS后来居上，能够支持更多种类的匹配模式。副本集对象一般不单独使用，而是作为Deployment的理想状态参数来使用
