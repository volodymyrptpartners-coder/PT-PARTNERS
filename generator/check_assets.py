import os
from bs4 import BeautifulSoup

ROOT_DIR = "sites"
HTML_EXT = ".html"

# html_file -> list of problems
RESULTS = {}


def is_external(url: str) -> bool:
    return url.startswith((
        "http://",
        "https://",
        "//",
        "mailto:",
        "tel:",
        "#",
    ))


def report_problem(html_file, tag, attr, link, resolved, reason):
    RESULTS.setdefault(html_file, []).append({
        "tag": tag,
        "attr": attr,
        "link": link,
        "resolved": resolved,
        "reason": reason,
    })


def check_file_exists(html_file, link, tag, attr):
    if not link or is_external(link):
        return

    # ❌ абсолютні шляхи заборонені
    if link.startswith("/"):
        report_problem(
            html_file,
            tag,
            attr,
            link,
            None,
            "absolute path is not allowed"
        )
        return

    # ✔ тільки відносні шляхи (від HTML-файлу)
    path = os.path.normpath(os.path.join(os.path.dirname(html_file), link))

    if not os.path.exists(path):
        report_problem(
            html_file,
            tag,
            attr,
            link,
            path,
            "file not found"
        )


def scan_html(html_file):
    RESULTS.setdefault(html_file, [])

    with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f, "lxml")

    # <a href>
    for a in soup.find_all("a", href=True):
        check_file_exists(html_file, a["href"], "a", "href")

    # <link href>
    for link in soup.find_all("link", href=True):
        check_file_exists(html_file, link["href"], "link", "href")

    # <img src>, <script src>
    for tag in soup.find_all(src=True):
        check_file_exists(html_file, tag["src"], tag.name, "src")

    # SVG <use href | xlink:href>
    for use in soup.find_all("use"):
        href = use.get("href") or use.get("xlink:href")
        if href:
            file_part = href.split("#")[0]
            if file_part:
                check_file_exists(html_file, file_part, "use", "href")


def main():
    for root, _, files in os.walk(ROOT_DIR):
        for file in files:
            if file.endswith(HTML_EXT):
                scan_html(os.path.join(root, file))

    has_errors = False

    for html_file, issues in sorted(RESULTS.items()):
        if not issues:
            print(f"[OK] {html_file}")
        else:
            has_errors = True
            print(f"[BROKEN] {html_file}")
            for i in issues:
                if i["reason"] == "absolute path is not allowed":
                    print(
                        f"  <{i['tag']}> {i['attr']}=\"{i['link']}\"\n"
                        f"  → absolute paths are forbidden"
                    )
                else:
                    print(
                        f"  <{i['tag']}> {i['attr']}=\"{i['link']}\"\n"
                        f"  → not found: {i['resolved']}"
                    )
            print()

    if has_errors:
        exit(1)


if __name__ == "__main__":
    main()

