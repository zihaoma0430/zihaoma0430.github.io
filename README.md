# Zihao Ma · Personal Homepage

可直接部署到 GitHub Pages 的静态个人主页，无需安装第三方依赖。页面无需 JavaScript 即可完整浏览。

## 本地预览

在项目目录运行：

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

访问 <http://127.0.0.1:8000>。也可以直接用浏览器打开 `index.html`。

## 更新内容

1. 修改 `content/site.json` 中的个人信息、文章或论文。
2. 运行 `python3 scripts/build.py` 重新生成 HTML。
3. 预览后，将内容文件与生成的 HTML 一起提交。

个人信息集中在 `profile` 中：

- `name`、`tagline`、`affiliation`：姓名、首页副标题、所属机构。
- `avatar`、`avatar_alt`：头像路径与替代文字。可将照片放进 `assets/images/`，再更新路径。
- `email`、`github`、`scholar`：联系方式。填写邮箱地址后自动生成邮件链接；空值不生成链接。
- `bio`：简介段落；`bio_note`：待补充提示，正式上线前可设为空字符串。
- `interests`：研究兴趣列表。填写后替换简介下的 Explore 导航。

`posts` 为文章列表：`category` 选择 `Research`、`Engineering`、`Product`；`date` 使用 `YYYY-MM-DD`；`body` 中每个字符串为一个段落。首页按日期倒序展示最近八篇。可设置 `url` 直接链接外部文章。未设置 `url` 时使用本地详情页。

`publications` 为论文列表：可填写标题、作者、会议或期刊、摘要、图片，以及 `url`、`pdf`、`code` 和 `bibtex`。没有资源地址时不会生成空按钮。

初版文章与论文均为明确标注的占位内容，不代表真实经历或成果。替换后将对应的 `placeholder` 改为 `false`。`slug` 用于详情页目录，使用小写英文字母、数字和短横线，列表内不可重复。删除条目或更改 slug 时，也需删除不再使用的旧详情页目录。

## 文件结构

```text
content/site.json          # 编辑个人信息与内容
scripts/build.py          # Python 标准库静态页面生成器
assets/css/main.css       # 配色、排版与移动端样式
assets/images/            # 头像、论文配图、网站图标
index.html                # Home
research/index.html       # Research
engineering/index.html    # Engineering
product/index.html        # Product
posts/                    # 文章详情页
publications/             # 论文详情页
```

## GitHub Pages

将这些文件推送到仓库后，在 GitHub 仓库的 **Settings → Pages** 中选择 **Deploy from a branch**，选择对应分支和 **/ (root)**。`.nojekyll` 让 Pages 直接提供生成的静态文件，无需 Jekyll 构建。

初版仅创建本地文件；是否已发布以仓库 Pages 配置及部署状态为准。

## 设计参考

配色与学术主页排版参考 [Jiaxuan Zou 的主页](https://jiaxuanzou0714.github.io/)。采用参考站浅色背景 `#f7f9fc`、正文色 `#101828`、链接色 `#115fb3`，内容容器最大宽度为 930px。样式和页面生成代码为本项目独立实现，未使用参考站的个人照片、简介、文章或论文。
