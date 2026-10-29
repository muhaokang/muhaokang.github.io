---
title: 标签
layout: page
description: 按技术标签查找历史文章。
---

<p class="page-intro">按技术标签查找文章。每篇笔记保留原始发布时间。</p>

{% assign sorted_tags = site.tags | sort %}
<div class="tag-index" aria-label="文章标签">
{% for tag in sorted_tags %}
  <a href="#{{ tag[0] | uri_escape }}">{{ tag[0] | escape }} <span>{{ tag[1].size }}</span></a>
{% endfor %}
</div>

{% for tag in sorted_tags %}
<section class="tag-section" id="{{ tag[0] | escape }}">
  <h2>{{ tag[0] | escape }} <span class="post-count">{{ tag[1].size }} 篇</span></h2>
  <ul class="listing">
  {% for post in tag[1] %}
    <li class="listing-item">
      <time datetime="{{ post.date | date: '%Y-%m-%d' }}">{{ post.date | date: '%Y-%m-%d' }}</time>
      <a href="{{ post.url | relative_url }}">{{ post.title | escape }}</a>
    </li>
  {% endfor %}
  </ul>
</section>
{% endfor %}
