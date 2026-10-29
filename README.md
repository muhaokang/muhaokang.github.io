# Haokang Mu 的个人网站

个人主页与技术博客：[muhaokang.github.io](https://muhaokang.github.io/)。

网站使用 Jekyll，Markdown 文章保存在 `_posts/`。GitHub Pages 继续从 `master` 分支根目录构建，文章地址保留 `/:title/` 格式。

## 本地预览

使用 Ruby 3.3 和 Bundler。macOS 可用 Homebrew 安装 Ruby，不要向系统 Ruby 安装依赖：

```sh
brew install ruby@3.3
export PATH="$(brew --prefix ruby@3.3)/bin:$PATH"
bundle config set --local path vendor/bundle
bundle install
bundle exec jekyll serve --host 127.0.0.1
```

访问 <http://127.0.0.1:4000/>。修改页面或文章后会自动重建；修改 `_config.yml` 后需要重新启动。依赖版本记录在 `Gemfile.lock`，构建产物和本地依赖不提交。

## 写文章

在 `_posts/` 新建 `YYYY-MM-DD-文章标题.md`，例如：

```markdown
---
layout: post
title: "一次技术问题的排查记录"
date: 2026-10-29
tags: [实践笔记]
description: "记录问题、排查过程、验证方法和结论。"
---

## 问题

描述问题发生的背景。

## 排查与验证

记录关键步骤和证据。

## 结论

说明已经确认的结论，以及尚待验证的部分。
```

图片放到 `assets/` 下，使用 `/assets/文件名.png` 引用。文章的文件名或 `permalink` 会影响 URL；更新旧文时保持原地址。新增标签会自动进入标签索引，技术主题入口按现有标签组织。

未准备发布的文章放在 `_drafts/`，使用 `bundle exec jekyll serve --drafts` 预览。不要把工作中的内部标识、客户资料、凭证或未经确认的成果直接写入公开文章。

## 验证与发布

```sh
JEKYLL_ENV=production bundle exec jekyll build --trace
python3 scripts/check_site.py
```

检查脚本验证主要页面、导航和静态资源，以及 RSS、Atom、sitemap 的本站链接。它不联网检查旧文章中的所有外链和外部图片。

建议每次修改先提交独立分支，创建 Pull Request；确认构建检查通过、预览效果符合预期后合并到 `master`。GitHub Pages 随后自动构建发布，可在仓库的 Actions 和 Settings → Pages 查看结果。新增的 `Build website` 工作流只负责验证，不改变现有部署方式。

## 日常维护

- 写一篇有实际结论的笔记，再检查标题、标签、代码和图片。
- 定期查看首页、文章页、标签、订阅和手机阅读效果。
- 更新个人介绍时，只填写可以公开且仍然准确的信息。
- 升级依赖前对照 [GitHub Pages 依赖版本](https://pages.github.com/versions/)，本地构建成功后再提交新的锁文件。

历史文章与站点内容的许可沿用站内已有声明。
