#!/usr/bin/env python3
import sys
import json
from pathlib import Path

BLOCKS_DIR = Path("blocks")

OUT_CSS = Path("site.css")
OUT_JS = Path("site.js")


def die(msg: str):
    raise SystemExit(f"ERROR: {msg}")


def load_site_json(path: Path) -> dict:
    if not path.exists():
        die(f"site json not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if "blocks" not in data or not isinstance(data["blocks"], dict):
        die("site json must contain object 'blocks'")

    return data


def collect_assets(site_data: dict):
    css_parts = []
    js_parts = []

    for block_name in site_data["blocks"].keys():
        block_dir = BLOCKS_DIR / block_name
        if not block_dir.exists():
            continue

        css_file = block_dir / "base.css"
        js_file = block_dir / "base.js"

        if css_file.exists():
            css_parts.append(f"\n/* ===== {block_name} ===== */\n" + css_file.read_text(encoding="utf-8").strip())

        if js_file.exists():
            js_parts.append(f"\n// ===== {block_name} =====\n" + js_file.read_text(encoding="utf-8").strip())

    return css_parts, js_parts


def main(realization_name: str) -> None:
    site_data = load_site_json(Path(f"sites/{realization_name}.json"))
    css_parts, js_parts = collect_assets(site_data)

    if css_parts:
        OUT_CSS.write_text("\n\n".join(css_parts) + "\n", encoding="utf-8")
        print(f"OK: generated {OUT_CSS}")
    else:
        print("INFO: no css generated")

    if js_parts:
        OUT_JS.write_text("\n\n".join(js_parts) + "\n", encoding="utf-8")
        print(f"OK: generated {OUT_JS}")
    else:
        print("INFO: no js generated")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        die("usage: generate_site_assets.py <realization_name>")
    realization_name = sys.argv[1]
    main(realization_name=realization_name)
