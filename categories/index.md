---
title: 技术专题
layout: page
description: 按技术主题浏览数据处理、存储检索和云原生学习笔记。
---

<p class="page-intro">从一个技术主题开始，沿着标签阅读相关笔记。</p>

{% assign topics = "数据处理与分析|Hadoop,HDFS,MapReduce,Shuffle,YARN,Yarn,Hive,Spark,SQL|从分布式计算基础，到数据处理与查询。;存储、检索与消息|HBase,ClickHouse,Elasticsearch,Redis,Kafka,ZooKeeper|记录不同存储系统、检索引擎和消息组件的使用。;容器与可观测性|Docker,k8s,Prometheus,HA,systemd|整理部署、容器编排、监控与高可用实践。;工程与成长|实习|保留学习阶段的实践记录与思考。" | split: ";" %}
<div class="topic-grid">
{% for topic in topics %}
  {% assign fields = topic | split: "|" %}
  {% assign topic_tags = fields[1] | split: "," %}
  <section class="topic-card">
    <h2>{{ fields[0] }}</h2>
    <p>{{ fields[2] }}</p>
    <div class="topic-tags">
    {% for tag_name in topic_tags %}
      {% assign tagged_posts = site.tags[tag_name] %}
      {% if tagged_posts.size > 0 %}
      <a href="{{ '/tags/' | relative_url }}#{{ tag_name | uri_escape }}">{{ tag_name | escape }} <span>{{ tagged_posts.size }}</span></a>
      {% endif %}
    {% endfor %}
    </div>
  </section>
{% endfor %}
</div>

<p class="archive-link"><a href="{{ '/blog/' | relative_url }}">浏览全部文章 →</a></p>
