# Minimal Python Static Blog

A small Markdown blog generator with no frontend tooling, JavaScript, templates, or framework.

## Structure

- `build.py` contains the site settings and generator.
- `articles/` contains Markdown articles with `title`, `date`, and `slug` frontmatter.
- `about.md` supplies the About page.
- `images/` is copied unchanged to `public/images/`.
- `public/` is disposable generated output.

## Build locally

```bash
pip install -r requirements.txt
python build.py
```

Preview `public/` with any static-file server, for example:

```bash
python -m http.server --directory public
```

## Content

Edit `SITE_TITLE`, `SITE_TITLE_ART`, and `SITE_URL` in `build.py`. The title art is preserved in a `<pre>` element.

Add an article to `articles/`:

```markdown
---
title: Article title
date: 2026-08-26
slug: article-title
---

Article text.
```

Put images in `images/` and use paths such as `/images/photo.jpg` in Markdown.

## Deployment

Vercel runs `python build.py` and serves `public/`.
