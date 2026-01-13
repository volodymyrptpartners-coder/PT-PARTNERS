#!/usr/bin/env python3

import json
import sys
from typing import Any, Dict
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, StrictUndefined

SITE_CSS = 'site.css'
SITE_JS = 'site.js'


def die(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def jinja_raise(message: str) -> None:
    raise RuntimeError(message)

def load_file(path:str)->str:
    with open(path,mode='r',encoding='utf-8') as f:
        data = f.read()
    return data

def load_json(path: Path) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        die(f"file not found: {path}")
    except json.JSONDecodeError as e:
        die(f"invalid JSON in {path}: {e}")

    if not isinstance(data, dict):
        die(f"JSON root must be an object in {path}")
    return data


def render_block(block_name: str, realization_name: str, include_css:bool=False, include_js:bool=False ) -> str:
    inline_block = {}

    blocks_root = Path("blocks")
    block_dir = blocks_root / str(block_name)
    template_path = block_dir / "base.j2"
    realization_path = block_dir / "realization" / f"{realization_name}.json"

    if include_css:
        if not Path(SITE_CSS).exists():
            die(f"{SITE_CSS} file is not found")
        inline_block['include_css'] = load_file(path=SITE_CSS)

    if include_js:
        if not Path(SITE_JS).exists():
            die(f"{SITE_JS} file is not found")
        inline_block['include_js'] = load_file(path=SITE_JS)
    
    if not blocks_root.exists():
        die(f"blocks directory not found, {blocks_root}")

    if not block_dir.exists():
        die(f"block not found: {block_name}")

    if not template_path.exists():
        die(f"template not found: {template_path}")

    if not realization_path.exists():
        die(f"realization not found: {realization_path}")

    realization_data = load_json(realization_path)

    if "inline_block" in realization_data:
        for inline in realization_data["inline_block"]:

            if not isinstance(inline, dict):
                die(f"inline_block must be an object in {realization_path}")
    
            if "block_name" not in inline:
                die(f"inline_block must contain block_name in {realization_path}")
            
            
            sub_realization_name = inline.get("realization_name",realization_name)          
            inline_block[inline["block_name"]] = render_block(block_name=inline["block_name"], realization_name=sub_realization_name)

    env = Environment(
        loader=FileSystemLoader("./"),
        undefined=StrictUndefined,
        autoescape=False,
    )
    env.globals["raise"] = jinja_raise

    template = env.get_template(str(template_path))
    return template.render(content=realization_data, inline_block=inline_block)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        die("usage: render_block.py <block_name> <realization_name>")
    block_name = sys.argv[1]
    realization_name = sys.argv[2]
    print(f"block_name\t\t{block_name}  \nrealization_name\t{realization_name}")
    html_rendered = render_block(block_name=block_name, realization_name=realization_name,include_css=True, include_js=True)

    output_path = Path("b_index.html")
    output_path.write_text(html_rendered, encoding="utf-8")
    print(f"OK: rendered block '{block_name}' with realization '{realization_name}' → {output_path}")
