# Minimal Python Static Blog Generator

A small Markdown-to-HTML generator for a personal blog. It has no frontend tooling, JavaScript, templates, or framework.

## Use

Create and activate a virtual environment, then install the two dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python build.py
```

On Windows PowerShell, activate it with:

```powershell
.venv\Scripts\Activate.ps1
```

Edit `SITE_TITLE`, `SITE_TITLE_ART`, and `SITE_URL` at the top of `build.py`. `SITE_TITLE_ART` is rendered unchanged inside a `<pre>` element, so it can contain Unicode terminal artwork.

Add articles as Markdown files in `articles/`, with `title`, `date`, and `slug` frontmatter fields. Add unprocessed image files to `images/` and reference them in Markdown as `/images/filename.jpg`.

Run `python build.py` whenever content changes, then inspect the regenerated `public/` directory. It is disposable: every build removes and recreates it.
