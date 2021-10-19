## YARN框架简介:
YARN （Yet Another Resource Negotiator，另一种资源协调者）是一种新的 Hadoop 资源管理器，它是一个通用资源管理系统，可为上层应用提供统一的资源管理和调度，它的引入为集群在利用率、资源统一管理和数据共享等方面带来了巨大好处。
## YARN概念:
YARN的基本思想是将JobTracker(Job跟踪器)的两个主要功能（资源管理和作业调度/监控）分离，主要方法是创建一个全局的ResourceManager（RM）和若干个针对应用程序的ApplicationMaster（AM）。这里的应用程序是指传统的MapReduce作业或作业的DAG（有向无环图）。

YARN 分层结构的本质是 ResourceManager。这个实体控制整个集群并管理应用程序向基础计算资源的分配。ResourceManager 将各个资源部分（计算、内存、带宽等）精心安排给基础 NodeManager（YARN 的每节点代理）。ResourceManager 还与 ApplicationMaster 一起分配资源，与 NodeManager 一起启动和监视它们的基础应用程序。在此上下文中，ApplicationMaster 承担了以前的 TaskTracker 的一些角色，ResourceManager 承担了 JobTracker 的角色。

ApplicationMaster 管理一个在 YARN 内运行的应用程序的每个实例。ApplicationMaster 负责协调来自 ResourceManager 的资源，并通过 NodeManager 监视容器的执行和资源使用（CPU、内存等的资源分配）。请注意，尽管目前的资源更加传统（CPU 核心、内存），但未来会带来基于手头任务的新资源类型（比如图形处理单元或专用处理设备）。从 YARN 角度讲，ApplicationMaster 是用户代码，因此存在潜在的安全问题。YARN 假设 ApplicationMaster 存在错误或者甚至是恶意的，因此将它们当作无特权的代码对待。

NodeManager 管理一个 YARN 集群中的每个节点。NodeManager 提供针对集群中每个节点的服务，从监督对一个容器的终生管理到监视资源和跟踪节点健康。MRv1 通过插槽管理 Map 和 Reduce 任务的执行，而 NodeManager 管理抽象容器，这些容器代表着可供一个特定应用程序使用的针对每个节点的资源。YARN 继续使用 HDFS 层。它的主要 NameNode 用于元数据服务，而 DataNode 用于分散在一个集群中的复制存储服务。

要使用一个 YARN 集群，首先需要来自包含一个应用程序的客户的请求。ResourceManager 协商一个容器的必要资源，启动一个 ApplicationMaster 来表示已提交的应用程序。通过使用一个资源请求协议，ApplicationMaster 协商每个节点上供应用程序使用的资源容器。执行应用程序时，ApplicationMaster 监视容器直到完成。当应用程序完成时，ApplicationMaster 从 ResourceManager 注销其容器，执行周期就完成了。

## YARN任务调度流程图:
![yarn任务调度流程图](assets/yarn%E4%BB%BB%E5%8A%A1%E8%B0%83%E5%BA%A6%E6%B5%81%E7%A8%8B%E5%9B%BE.png)



#### 执行job.waitforcompletion()方法,内置流程: 
- 向ResourceManager(RM)发起请求申请一个job
- RM返回job相关资源和job的jar提交路径(staging-dir),以及jobID
- 提交jar到staging-dir(HDFS路径)
- 汇报给RM提交结果
- RM将job加入到任务队列
- NodeManager(NM)节点领取任务
- NodeManager分配运行资源容器
- RM调用NodeManager中的一个节点运行- mrappMaster(ApplicationMaster)
- NodeManager运行mrappMaster的节点向RM注册
- mrappMaster分配一些NodeManager节点运行Map task任务
- 分配NodeManager节点运行Reducer task(任务)
- 当Reducer task 任务完成后向RM注销自己

### 本地模型运行

- 1.在windows的eclipse里面直接运行main方法，就会将job提交给本地执行器localjobrunner执行
      ----输入输出数据可以放在本地路径下（c:/wc/srcdata/）
      ----输入输出数据也可以放在hdfs中(hdfs://weekend110:9000/wc/srcdata)
	  
	  
- 2.在linux的eclipse里面直接运行main方法，但是不要添加yarn相关的配置，也会提交给localjobrunner执行
      ----输入输出数据可以放在本地路径下（/home/hadoop/wc/srcdata/）
      ----输入输出数据也可以放在hdfs中(hdfs://weekend110:9000/wc/srcdata)  
	  
	  
### 集群模式运行

- 1.将工程打成jar包，上传到服务器，然后用hadoop命令提交  hadoop jar wc.jar cn.itcast.hadoop.mr.wordcount.WCRunner
- 2.在linux的eclipse中直接运行main方法，也可以提交到集群中去运行，但是，必须采取以下措施：
      ----在工程src目录下加入 mapred-site.xml  和  yarn-site.xml (在实例化job对象时默认会将配置项加入)
      ----将工程打成jar包(wc.jar)，同时在实例化job对象时添加一个配置参数　conf.set("mapreduce.job.jar","wc.jar"(jar包目录));    
	 
```
Configuration conf = new Configuration();
conf.set("mapreduce.job.jar","wc.jar");
Job job = Job.getInstance(conf);
```
- 3.在windows的eclipse中直接运行main方法，也可以提交给集群中运行，但是因为平台不兼容，需要做很多的设置修改
        ----要在windows中存放一份hadoop的安装包（解压好的）
        ----要将其中的lib和bin目录替换成根据你的windows版本重新编译出的文件
        ----再要配置系统环境变量 HADOOP_HOME  和 PATH
        ----修改YarnRunner这个类的源码
		
## Job描述和提交类的标准写法(集群模式第二种方式)
```
package com.sy.hadoop.mapreduce;
 
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;
 
//这是job描述和提交类的规范写法
public class FlowSumRunner  extends Configured implements Tool {
 
    @Override
    public int run(String[] args) throws Exception {
 
        Configuration conf = new Configuration();
        conf.set("mapreduce.job.jar","wc.jar");
        Job job = Job.getInstance(conf);
        
        //配置jar运行类
        job.setJarByClass(FlowSumRunner.class);
        
        //配置map类
        job.setMapperClass(FlowSumMapper.class);
        
        //配置reduce类
        job.setReducerClass(FlowSumReducer.class);
 
        //配置map输出key类型
        job.setMapOutputKeyClass(Text.class);
        
        //配置map输出value类型
        job.setMapOutputValueClass(FlowBean.class);
 
        //通用配置如果map输出key和输出value和reduce一样那么就不用配置上面的,如果不一样就需要使用它单独配置reduce配置
        //配置reduce输出key类型
        job.setOutputKeyClass(Text.class);
        
        //配置reduce输出value类型
        job.setOutputValueClass(FlowBean.class);
 
        //配置log输入文件目录(map读取文件)
        FileInputFormat.setInputPaths(job, new Path(args[0]));
        //输出文件目录
        FileOutputFormat.setOutputPath(job, new Path(args[1]));
 
        //启动job
        return job.waitForCompletion(true)?0:1;
    }
 
 
    public static void main(String[] args) throws Exception {
        int res = ToolRunner.run(new Configuration(), new FlowSumRunner(), args);
        System.exit(res);
    }
 
}
```