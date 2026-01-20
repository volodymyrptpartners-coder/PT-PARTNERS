from pathlib import Path


SITES_DIR = Path("sites")
OUTPUT_FILE = Path("404.html")


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>404</title>
  <meta name="robots" content="noindex, nofollow">
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
      background: #f5f5f5;
      color: #1a1a1a;
    }}

    .box {{
      background: #ffffff;
      padding: 40px;
      border-radius: 16px;
      max-width: 520px;
      width: 100%;
    }}

    h1 {{
      margin: 0 0 16px;
      font-size: 32px;
      font-weight: 600;
    }}

    p {{
      margin: 0 0 24px;
      color: #555;
      font-size: 16px;
    }}

    ul {{
      margin: 0;
      padding: 0;
      list-style: none;
    }}

    li + li {{
      margin-top: 8px;
    }}

    a {{
      text-decoration: none;
      color: #1a1a1a;
      border-bottom: 1px solid #ccc;
    }}

    a:hover {{
      border-color: #1a1a1a;
    }}
  </style>
</head>
<body>

  <div class="box">
    <h1>404</h1>
    <p>Available pages:</p>
    <ul>
      {links}
    </ul>
  </div>

</body>
</html>
"""


def generate_404() -> None:
    if not SITES_DIR.exists():
        raise RuntimeError(f"{SITES_DIR} directory not found")

    pages = sorted(
        p.name
        for p in SITES_DIR.glob("*.html")
        if p.name != "404.html"
    )

    links_html = "\n".join(
        f'<li><a href="sites/{page}">{page}</a></li>'
        for page in pages
    )

    html = HTML_TEMPLATE.format(links=links_html)

    OUTPUT_FILE.write_text(html, encoding="utf-8")
    print(f"[OK] generated {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_404()

