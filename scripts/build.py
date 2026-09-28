#!/usr/bin/env python3
"""Build a dependency-free static site from content/site.json."""

import json
import posixpath
import re
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "content/site.json").read_text(encoding="utf-8"))
PROFILE = DATA["profile"]
NAVIGATION = (("Home", "index.html"), ("Research", "research/index.html"),
              ("Engineering", "engineering/index.html"), ("Product", "product/index.html"))
CATEGORIES = {
    "Research": "研究问题、阅读笔记与论文。",
    "Engineering": "工程项目、技术实践与实现过程。",
    "Product": "产品观察、设计过程与迭代思考。",
}
ICONS = {
    "github": '<path fill="currentColor" d="M12 2a10 10 0 0 0-3.16 19.49c.5.09.68-.22.68-.48v-1.86c-2.78.6-3.37-1.18-3.37-1.18-.45-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.61.07-.61 1 .07 1.53 1.03 1.53 1.03.89 1.53 2.34 1.09 2.91.83.09-.65.35-1.09.64-1.34-2.22-.25-4.56-1.11-4.56-4.94 0-1.09.39-1.98 1.03-2.68-.1-.25-.45-1.27.1-2.65 0 0 .84-.27 2.75 1.03A9.6 9.6 0 0 1 12 6.83c.85 0 1.71.11 2.51.34 1.91-1.3 2.75-1.03 2.75-1.03.55 1.38.2 2.4.1 2.65.64.7 1.03 1.59 1.03 2.68 0 3.84-2.34 4.69-4.57 4.94.36.31.68.92.68 1.85v2.75c0 .27.18.58.69.48A10 10 0 0 0 12 2Z"/>',
    "email": '<g fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 6 9 7 9-7"/></g>',
    "scholar": '<g fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"><path d="m2 9 10-6 10 6-10 6L2 9Z"/><path d="M6 12v6c4 3 8 3 12 0v-6M22 9v9"/></g>',
}


def e(value):
    return escape(str(value), quote=True)


def icon(name):
    return f'<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


def href(target, current):
    """Keep links usable on GitHub Pages, subpaths, and direct file previews."""
    if urlsplit(target).scheme:
        return target
    return posixpath.relpath(target, posixpath.dirname(current) or ".")


def link(target, label, current, css="", extra=""):
    external = urlsplit(target).scheme in ("http", "https")
    attrs = ' target="_blank" rel="noopener noreferrer"' if external else ""
    class_attr = f' class="{css}"' if css else ""
    return f'<a href="{e(href(target, current))}"{class_attr}{attrs}{extra}>{label}</a>'


def validate():
    for collection in ("posts", "publications"):
        slugs = set()
        for item in DATA[collection]:
            slug = item["slug"]
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or slug in slugs:
                raise ValueError(f"Invalid or duplicate slug in {collection}: {slug}")
            slugs.add(slug)
            if collection == "posts":
                if item["category"] not in CATEGORIES:
                    raise ValueError(f"Unknown post category: {item['category']}")
                if item.get("date"):
                    date.fromisoformat(item["date"])
            for key in ("url", "pdf", "code"):
                target = item.get(key)
                if target and urlsplit(target).scheme not in ("", "https", "http"):
                    raise ValueError(f"Unsupported link: {target}")
    for key in ("github", "scholar"):
        target = PROFILE.get(key)
        if target and urlsplit(target).scheme not in ("https", "http"):
            raise ValueError(f"Unsupported profile link: {target}")


def write_page(current, title, body, active="Home", description=""):
    nav = "\n".join(
        "<li>" + link(path, label, current, extra=' aria-current="page"' if label == active else "") + "</li>"
        for label, path in NAVIGATION
    )
    full_title = PROFILE["name"] if current == "index.html" else f"{title} | {PROFILE['name']}"
    desc = description or f"{PROFILE['name']} 的个人主页：研究、工程、产品，以及最新文章与论文。"
    output = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#f7f9fc">
  <meta name="description" content="{e(desc)}">
  <meta name="author" content="{e(PROFILE['name'])}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{e(full_title)}">
  <meta property="og:description" content="{e(desc)}">
  <title>{e(full_title)}</title>
  <link rel="icon" href="{e(href('assets/images/favicon.svg', current))}" type="image/svg+xml">
  <link rel="stylesheet" href="{e(href('assets/css/main.css', current))}">
</head>
<body>
  <a class="skip-link" href="#main">跳转到正文</a>
  <header class="site-header">
    <nav class="container navigation" aria-label="Main navigation" lang="en">
      <ul>{nav}</ul>
    </nav>
  </header>
  <main id="main" class="container page" tabindex="-1">
{body}
  </main>
  <footer class="site-footer">
    <div class="container footer-inner">
      <p>© {date.today().year} {e(PROFILE['name'])}</p>
      <p>{e(PROFILE['tagline'])}</p>
    </div>
  </footer>
</body>
</html>
'''
    path = ROOT / current
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(output, encoding="utf-8")
    print(f"Built {current}")


def badge(item):
    return '<span class="placeholder-label">待补充</span>' if item.get("placeholder") else ""


def date_markup(post):
    if not post.get("date"):
        return '<span class="post-date">待更新</span>'
    parsed = date.fromisoformat(post["date"])
    months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
    display = f"{months[parsed.month - 1]} {parsed.day:02d}, {parsed.year}"
    return f'<time class="post-date" datetime="{e(post["date"])}" lang="en">{display}</time>'


def post_target(post):
    return post.get("url") or f"posts/{post['slug']}/index.html"


def publication_target(publication):
    return publication.get("url") or f"publications/{publication['slug']}/index.html"


def publications_markup(current):
    rows = []
    for publication in DATA["publications"]:
        target = publication_target(publication)
        preview = ""
        if publication.get("image"):
            img = f'<img src="{e(href(publication["image"], current))}" alt="{e(publication.get("image_alt", publication["title"]))}" width="320" height="208" loading="lazy">'
            preview = link(target, img, current, "publication-preview", extra=f' aria-label="{e(publication["title"])}"')
        resources = link(f"publications/{publication['slug']}/index.html", "Details ↗", current, "small-link")
        for key, label in (("pdf", "PDF ↗"), ("code", "Code ↗")):
            if publication.get(key):
                resources += link(publication[key], label, current, "small-link")
        rows.append(f'''<li class="publication">
          {preview or '<div aria-hidden="true"></div>'}
          <div>
            <h3>{link(target, e(publication['title']), current)}</h3>
            <p>{e(publication['authors'])}</p>
            <p class="venue">{e(publication['venue'])}</p>
            <div class="publication-links">{resources}{badge(publication)}</div>
          </div>
        </li>''')
    return '<ul class="publications-list">' + "\n".join(rows) + "</ul>" if rows else '<p class="empty-note">论文将在这里更新。</p>'


def home():
    current = "index.html"
    contacts = []
    for key, label in (("email", "Email"), ("github", "GitHub"), ("scholar", "Scholar")):
        target = PROFILE.get(key)
        if target:
            if key == "email":
                target = f"mailto:{target}"
            contacts.append(link(target, icon(key) + label, current))
    pending_email = "" if PROFILE.get("email") else f'<p class="contact-pending">{icon("email")}<span>邮箱待补充</span></p>'
    bio = "\n".join(f"<p>{e(paragraph)}</p>" for paragraph in PROFILE["bio"])
    if PROFILE.get("bio_note"):
        bio += f'<p class="bio-note">{e(PROFILE["bio_note"])}</p>'
    if PROFILE.get("interests"):
        items = "".join(f"<li>{e(item)}</li>" for item in PROFILE["interests"])
        topics = f'<h2 lang="en">Research Interests</h2><ul class="interests">{items}</ul>'
    else:
        topics = '<h2 lang="en">Explore</h2><div class="topic-links">' + "".join(
            link(path, label + '<span aria-hidden="true">↗</span>', current)
            for label, path in NAVIGATION[1:]
        ) + '</div>'
    posts = "\n".join(
        f'<li class="post-row">{date_markup(post)}<div>{link(post_target(post), e(post["title"]), current)}{badge(post)}</div></li>'
        for post in sorted(DATA["posts"], key=lambda item: item.get("date", ""), reverse=True)[:8]
    )
    posts_html = f'<ul class="posts-list">{posts}</ul>' if posts else '<p class="empty-note">文章将在这里更新。</p>'
    write_page(current, "Home", f'''
    <header class="page-heading">
      <h1 lang="en">{e(PROFILE['name'])}</h1>
      <p class="tagline" lang="en">{e(PROFILE['tagline'])}</p>
    </header>
    <div class="intro">
      <aside class="profile" aria-label="个人信息与联系方式">
        <img class="avatar" src="{e(PROFILE['avatar'])}" alt="{e(PROFILE['avatar_alt'])}" width="230" height="230" fetchpriority="high">
        <p class="affiliation">{e(PROFILE['affiliation'])}</p>
        <div class="contact-links" lang="en">{''.join(contacts)}</div>
        {pending_email}
      </aside>
      <div class="bio">
        <p class="greeting" lang="en">Hi, I’m <strong>{e(PROFILE['name'])}</strong>.</p>
        {bio}
        <div class="bio-topics">{topics}</div>
      </div>
    </div>
    <section class="content-section" aria-labelledby="latest-posts">
      <h2 id="latest-posts" lang="en">Latest Posts</h2>
      {posts_html}
    </section>
    <section class="content-section" aria-labelledby="publications">
      <h2 id="publications" lang="en">Publications</h2>
      {publications_markup(current)}
    </section>''')


def category_pages():
    for category, description in CATEGORIES.items():
        current = f"{category.lower()}/index.html"
        rows = []
        for post in sorted(DATA["posts"], key=lambda item: item.get("date", ""), reverse=True):
            if post["category"] != category:
                continue
            rows.append(f'''<li class="category-item">
        {date_markup(post)}
        <h2>{link(post_target(post), e(post['title']), current)}{badge(post)}</h2>
        <p>{e(post['summary'])}</p>
      </li>''')
        listing = '<ul class="category-list">' + "\n".join(rows) + "</ul>" if rows else '<p class="empty-note">内容将在这里更新。</p>'
        publications = f'<section class="content-section" aria-labelledby="publications"><h2 id="publications" lang="en">Publications</h2>{publications_markup(current)}</section>' if category == "Research" else ""
        write_page(current, category, f'''
    <header class="page-heading">
      <h1 lang="en">{category}</h1>
      <p class="tagline">{description}</p>
    </header>
    {listing}
    {publications}''', active=category, description=description)


def detail_pages():
    for post in DATA["posts"]:
        current = f"posts/{post['slug']}/index.html"
        category_path = f"{post['category'].lower()}/index.html"
        paragraphs = "\n".join(f"<p>{e(paragraph)}</p>" for paragraph in post.get("body", []))
        notice = '<p class="draft-notice">占位文章 · 正式内容待补充</p>' if post.get("placeholder") else ""
        write_page(current, post["title"], f'''
    <article class="article">
      {link(category_path, '← ' + post['category'], current, 'back-link')}
      <header class="article-heading">
        <div class="article-meta">{e(post['category'])} · {date_markup(post)}</div>
        <h1>{e(post['title'])}</h1>
      </header>
      {notice}
      <div class="article-body">{paragraphs}</div>
      <hr class="article-divider">
      {link('index.html', '← 返回 Home', current, 'back-link')}
    </article>''', active=post["category"], description=post["summary"])

    for publication in DATA["publications"]:
        current = f"publications/{publication['slug']}/index.html"
        notice = '<p class="draft-notice">论文占位条目 · 尚未添加正式论文</p>' if publication.get("placeholder") else ""
        resources = "".join(
            link(publication[key], label, current, "small-link")
            for key, label in (("url", "Paper ↗"), ("pdf", "PDF ↗"), ("code", "Code ↗"))
            if publication.get(key)
        )
        citation = f'<details class="bibtex"><summary>BibTeX</summary><pre><code>{e(publication["bibtex"])}</code></pre></details>' if publication.get("bibtex") else ""
        write_page(current, publication["title"], f'''
    <article class="article">
      {link('research/index.html', '← Research', current, 'back-link')}
      <header class="article-heading">
        <div class="article-meta" lang="en">Publication</div>
        <h1>{e(publication['title'])}</h1>
        <p>{e(publication['authors'])}</p>
        <p class="article-meta">{e(publication['venue'])}</p>
      </header>
      {notice}
      <div class="article-body">
        <h2 lang="en">Abstract</h2>
        <p>{e(publication['abstract'])}</p>
      </div>
      <div class="publication-links article-resource-links">{resources}</div>
      {citation}
      <hr class="article-divider">
      {link('index.html', '← 返回 Home', current, 'back-link')}
    </article>''', active="Research", description=publication["abstract"])


if __name__ == "__main__":
    validate()
    home()
    category_pages()
    detail_pages()
