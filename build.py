"""Build this blog into the disposable public/ directory."""

import html
import re
import shutil
from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

import markdown
import yaml


# Edit these values for your own site.
SITE_TITLE = "Weltanschauung"
SITE_URL = "weltanschauung-ten.vercel.app"
SITE_TITLE_ART = r""" 
 __     __     ______     __         ______   ______     __   __                        
/\ \  _ \ \   /\  ___\   /\ \       /\__  _\ /\  __ \   /\ "-.\ \                       
\ \ \/ ".\ \  \ \  __\   \ \ \____  \/_/\ \/ \ \  __ \  \ \ \-.  \                      
 \ \__/".~\_\  \ \_____\  \ \_____\    \ \_\  \ \_\ \_\  \ \_\\"\_\                     
  \/_/   \/_/   \/_____/   \/_____/     \/_/   \/_/\/_/   \/_/ \/_/                     
                                                                                        
 ______     ______     __  __     ______     __  __     __  __     __   __     ______   
/\  ___\   /\  ___\   /\ \_\ \   /\  __ \   /\ \/\ \   /\ \/\ \   /\ "-.\ \   /\  ___\  
\ \___  \  \ \ \____  \ \  __ \  \ \  __ \  \ \ \_\ \  \ \ \_\ \  \ \ \-.  \  \ \ \__ \ 
 \/\_____\  \ \_____\  \ \_\ \_\  \ \_\ \_\  \ \_____\  \ \_____\  \ \_\\"\_\  \ \_____\
  \/_____/   \/_____/   \/_/\/_/   \/_/\/_/   \/_____/   \/_____/   \/_/ \/_/   \/_____/"""

ROOT = Path(__file__).parent
ARTICLES_DIR = ROOT / "articles"
IMAGES_DIR = ROOT / "images"
OUTPUT_DIR = ROOT / "public"
REQUIRED_ARTICLE_FIELDS = ("title", "date", "slug")
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:[a-z0-9-]*[a-z0-9])?$")


@dataclass
class Article:
    title: str
    published: date
    slug: str
    body: str


def fail(source: Path, message: str) -> ValueError:
    return ValueError(f"{source}: {message}")


def parse_markdown_file(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise fail(path, "missing YAML frontmatter (expected opening ---)")

    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        raise fail(path, "missing closing frontmatter delimiter (---)")

    try:
        metadata = yaml.safe_load(parts[0][4:])
    except yaml.YAMLError as error:
        raise fail(path, f"invalid YAML frontmatter: {error}") from error
    if not isinstance(metadata, dict):
        raise fail(path, "frontmatter must be a YAML mapping")
    return metadata, parts[1]


def parse_article(path: Path) -> Article:
    metadata, body = parse_markdown_file(path)
    missing = [field for field in REQUIRED_ARTICLE_FIELDS if not metadata.get(field)]
    if missing:
        raise fail(path, f"missing required frontmatter field(s): {', '.join(missing)}")

    published = metadata["date"]
    if isinstance(published, datetime):
        published = published.date()
    if not isinstance(published, date):
        try:
            published = date.fromisoformat(str(published))
        except ValueError as error:
            raise fail(path, "date must be a valid ISO date (YYYY-MM-DD)") from error

    title = str(metadata["title"])
    slug = str(metadata["slug"])
    if not SLUG_PATTERN.fullmatch(slug):
        raise fail(path, "slug must use lowercase letters, numbers, and hyphens")
    return Article(title, published, slug, body)


def markdown_to_html(source: str) -> str:
    return markdown.markdown(source, extensions=["fenced_code"])


def date_display(value: date) -> str:
    return value.strftime("%d/%m/%Y")


def page_shell(title: str, content: str) -> str:
    site_title = html.escape(SITE_TITLE)
    title_art = html.escape(SITE_TITLE_ART)
    return f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(title)} | {site_title}</title>
    <link rel="stylesheet" href="/style.css">
    <link rel="alternate" type="application/rss+xml" title="RSS" href="/rss.xml">
</head>
<body>
    <main>
        <header>
            <pre>{title_art}</pre>
            <nav><a href="/">Home</a>  <a href="/about.html">About</a></nav>
        </header>
{content}
    </main>
</body>
</html>
"""


def write_page(relative_path: Path, title: str, content: str) -> None:
    destination = OUTPUT_DIR / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(page_shell(title, content), encoding="utf-8")


def render_index(articles: list[Article]) -> None:
    entries = "\n".join(
        f'        <p><a href="/articles/{html.escape(article.slug)}.html">'
        f"{html.escape(article.title)}</a> - {date_display(article.published)}</p>"
        for article in articles
    )
    write_page(Path("index.html"), SITE_TITLE, entries)


def render_article(article: Article) -> None:
    content = markdown_to_html(article.body)
    write_page(Path("articles") / f"{article.slug}.html", article.title, f"""        <article>
            <h1>{html.escape(article.title)}</h1>
            <time datetime="{article.published.isoformat()}">{date_display(article.published)}</time>
            {content}
        </article>""")


def render_about() -> None:
    about_path = ROOT / "about.md"
    metadata, body = parse_markdown_file(about_path)
    title = str(metadata.get("title", "About"))
    write_page(Path("about.html"), title, f"""        <article>
            <h1>{html.escape(title)}</h1>
            {markdown_to_html(body)}
        </article>""")


def absolute_url(path: str) -> str:
    return f"{SITE_URL.rstrip('/')}{path}"


def generate_rss(articles: list[Article]) -> None:
    items = []
    for article in articles:
        url = absolute_url(f"/articles/{article.slug}.html")
        published = datetime.combine(article.published, time.min, tzinfo=timezone.utc)
        description = markdown_to_html(article.body)
        items.append(f"""    <item>
      <title>{xml_escape(article.title)}</title>
      <link>{xml_escape(url)}</link>
      <guid>{xml_escape(url)}</guid>
      <pubDate>{format_datetime(published, usegmt=True)}</pubDate>
      <description>{xml_escape(description)}</description>
    </item>""")
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{xml_escape(SITE_TITLE)}</title>
    <link>{xml_escape(absolute_url('/'))}</link>
    <description>{xml_escape(SITE_TITLE)}</description>
{chr(10).join(items)}
  </channel>
</rss>
"""
    (OUTPUT_DIR / "rss.xml").write_text(feed, encoding="utf-8")


def build() -> None:
    if not ARTICLES_DIR.is_dir():
        raise FileNotFoundError(f"articles directory not found: {ARTICLES_DIR}")
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir()

    articles = [parse_article(path) for path in ARTICLES_DIR.glob("*.md")]
    slugs = [article.slug for article in articles]
    if len(slugs) != len(set(slugs)):
        raise ValueError("article slugs must be unique")
    articles.sort(key=lambda article: article.published, reverse=True)

    shutil.copy2(ROOT / "style.css", OUTPUT_DIR / "style.css")
    if IMAGES_DIR.exists():
        shutil.copytree(IMAGES_DIR, OUTPUT_DIR / "images")
    render_index(articles)
    for article in articles:
        render_article(article)
    render_about()
    generate_rss(articles)
    print(f"Built {len(articles)} article(s) in {OUTPUT_DIR}")


if __name__ == "__main__":
    build()
