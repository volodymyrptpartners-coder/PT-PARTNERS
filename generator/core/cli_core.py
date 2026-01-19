"Convention file and functions"

from pathlib import Path
from typing import List
import copy
import json
from jinja2 import Environment, FileSystemLoader, StrictUndefined


BLOCKS_DIR = "blocks"
REALIZATION_DIR = "realization"
SITES_DIR = "sites"
JSON_DIR = "json_backbone"


FILE_OUT_CSS = "/tmp/site.css"
FILE_OUT_JS = "/tmp/site.js"

BASE_CSS = "base.css"
BASE_JS = "base.js"
BASE_J2 = "base.j2"

CORE_SITE_JSON = {
    "meta": {
        "realization_name": "",
    },
    "blocks": {},
}
BLOCK_DICT = {
    "consular_": "template_consular_container",
    "auto_registration_": "template_consular_container",
}


def jinja_raise(message: str) -> None:
    raise RuntimeError(message)


def get_site_path(realization_name: str, check_exist: bool = False) -> str:
    site_path = Path(JSON_DIR) / f"{realization_name}.json"
    if check_exist and not site_path.exists():
        raise ValueError(f"{str(site_path)} not exists!")
    return str(site_path)


def get_json_schema_path(block_name: str) -> str:
    return str(Path(BLOCKS_DIR) / block_name / "schema.json")


def get_block_names() -> List[str]:
    result = []
    for block_dir in Path(BLOCKS_DIR).iterdir():
        if block_dir.is_dir():
            result.append(block_dir.name)
    return result


def get_realization_jsons(block_name: str) -> List[str]:
    result = []
    realization_dir = Path(BLOCKS_DIR) / block_name / REALIZATION_DIR
    for json_path in realization_dir.iterdir():
        result.append(str(json_path))
    return result


def get_language_by_realization_name(realization_name: str) -> str:
    for key, _ in BLOCK_DICT.items():
        if realization_name.startswith(key):
            return realization_name[len(key) :]
    raise KeyError(f"{realization_name!r} not found in BLOCK_DICT.")


def get_realization_path(block_name: str, realization_name: str, check_exist: bool = False, take_def: bool = False) -> str:
    base_path = Path(BLOCKS_DIR) / block_name / REALIZATION_DIR
    realization_path = base_path / f"{realization_name}.json"

    if not check_exist:
        return str(realization_path)

    # 1. якщо основний файл існує — використовуємо його
    if realization_path.exists():
        return str(realization_path)

    # 2. якщо основного файлу нема і fallback заборонений — помилка
    if not take_def:
        raise ValueError(f"{realization_path!r} not found!")

    # 3. fallback на default
    lang = get_language_by_realization_name(realization_name=realization_name)
    realization_path_default = base_path / f"default_{lang}.json"

    if not realization_path_default.exists():
        raise ValueError(f"{realization_path!r} not found! and {realization_path_default!r} not found!")

    return str(realization_path_default)


def merge(realization_name: str) -> None:
    result = copy.deepcopy(CORE_SITE_JSON)
    result["meta"]["realization_name"] = realization_name
    for block_name in get_block_names():
        realization_path = get_realization_path(block_name=block_name, realization_name=realization_name)
        if Path(realization_path).exists():
            with open(realization_path, "r", encoding="utf-8") as f:
                result["blocks"][block_name] = {"realization": json.load(f)}  # type: ignore

    raw_result = json.dumps(result, ensure_ascii=False, indent=2)
    out_file = Path(JSON_DIR) / f"{realization_name}.json"
    out_file.write_text(raw_result, encoding="utf-8")
    print(f"[OK]: wrote {out_file}")


def split(realization_name: str) -> None:
    infile = get_site_path(realization_name=realization_name, check_exist=True)
    with open(infile, "r", encoding="utf-8") as f:
        site_data = json.load(f)

    for block_name, block_data in site_data["blocks"].items():
        out_file = Path(get_realization_path(block_name=block_name, realization_name=realization_name))
        data = json.dumps(block_data["realization"], ensure_ascii=False, indent=2)
        out_file.write_text(data, encoding="utf-8")
        print(f"[OK]: wrote {out_file}")


def get_template_block_name(realization_name: str) -> str:
    for key, value in BLOCK_DICT.items():
        if realization_name.startswith(key):
            return value
    raise KeyError(f"{realization_name!r} not found in BLOCK_DICT.")


def load_file(path: str) -> str:
    if not Path(path).exists():
        raise ValueError(f"{path} file not found!")
    with open(path, mode="r", encoding="utf-8") as f:
        data = f.read()
    return data


def render(block_name: str, realization_name: str, include_css: bool = False, include_js: bool = False) -> str:
    inline_block = {}
    realization_path = get_realization_path(block_name=block_name, realization_name=realization_name, check_exist=True, take_def=True)
    if include_css:
        inline_block["include_css"] = load_file(path=FILE_OUT_CSS)

    if include_js:
        inline_block["include_js"] = load_file(path=FILE_OUT_JS)

    template_path = Path(BLOCKS_DIR) / block_name / BASE_J2
    if not template_path.exists():
        raise ValueError(f"template not found: {template_path}")

    realization_data = json.loads(load_file(path=realization_path))

    if "inline_block" in realization_data:
        for inline in realization_data["inline_block"]:
            if not isinstance(inline, dict):
                raise ValueError(f"inline_block must be an object in {realization_path}")

            if "block_name" not in inline:
                raise ValueError(f"inline_block must contain block_name in {realization_path}")

            sub_realization_name = inline.get("realization_name", realization_name)
            inline_block[inline["block_name"]] = render(block_name=inline["block_name"], realization_name=sub_realization_name)

    env = Environment(
        loader=FileSystemLoader("./"),
        undefined=StrictUndefined,
        autoescape=False,
    )
    env.globals["raise"] = jinja_raise

    template = env.get_template(str(template_path))
    return template.render(content=realization_data, inline_block=inline_block)


def get_block_name(realization_name: str) -> str:
    for key, value in BLOCK_DICT.items():
        if realization_name.startswith(key):
            return value
    raise KeyError(f"{realization_name!r} not found in BLOCK_DICT.")


def render_block(realization_name: str) -> None:
    block_name = get_block_name(realization_name=realization_name)
    html_rendered = render(block_name=block_name, realization_name=realization_name, include_css=True, include_js=True)
    output_path = Path(SITES_DIR) / f"{realization_name}.html"
    output_path.write_text(html_rendered, encoding="utf-8")
    print(f"[OK] rendered block '{block_name}' with realization '{realization_name}' → {output_path}")

def collect_block_names(block_name: str, realization_name: str, collected: List[str]) -> List[str]:
    if block_name in collected:
        return collected
    collected.append(block_name)
    realization_path = get_realization_path(block_name=block_name,realization_name=realization_name,check_exist=True,take_def=True)
    realization_data = json.loads(load_file(path=realization_path))

    if "inline_block" not in realization_data:
        return collected

    for inline in realization_data["inline_block"]:
        if not isinstance(inline, dict):
            raise ValueError(f"inline_block must be an object in {realization_path}")

        if "block_name" not in inline:
            raise ValueError(f"inline_block must contain block_name in {realization_path}")

        sub_block_name = inline["block_name"]
        sub_realization_name = inline.get("realization_name", realization_name)
        collect_block_names(block_name=sub_block_name,realization_name=sub_realization_name,collected=collected)
    return collected

 

def collect_assets(realization_name: str) -> None:
    raw_site_data = load_file(path=str(Path(JSON_DIR) / f"{realization_name}.json"))
    site_data = json.loads(raw_site_data)
    bl_name = get_block_name(realization_name=realization_name)
    site_blocks =  collect_block_names(block_name=bl_name,realization_name=realization_name,collected=[])
    css_parts = []
    js_parts = []
    for block_name in site_blocks:
        css_file = Path(BLOCKS_DIR) / block_name / BASE_CSS
        js_file = Path(BLOCKS_DIR) / block_name / BASE_JS
        if css_file.exists():
            css_parts.append(f"\n/* ===== {block_name} ===== */\n" + css_file.read_text(encoding="utf-8").strip())

        if js_file.exists():
            js_parts.append(f"\n/* ===== {block_name} ===== */\n" + js_file.read_text(encoding="utf-8").strip())

    if css_parts:
        Path(FILE_OUT_CSS).write_text("\n\n".join(css_parts) + "\n", encoding="utf-8")
        print(f"[OK] generated {FILE_OUT_CSS}")

    if js_parts:
        Path(FILE_OUT_JS).write_text("\n\n".join(js_parts) + "\n", encoding="utf-8")
        print(f"[OK] generated {FILE_OUT_JS}")

def clean(realization_name: str) -> None:
    removed_any = False

    # 1. remove temporary framework assets
    for tmp_path in [Path(FILE_OUT_CSS), Path(FILE_OUT_JS)]:
        if tmp_path.exists():
            tmp_path.unlink()
            print(f"[OK] removed {tmp_path}")
            removed_any = True

    # 2. remove realization jsons (except default_* and test_*)
    for block_dir in Path(BLOCKS_DIR).iterdir():
        if not block_dir.is_dir():
            continue

        realization_dir = block_dir / REALIZATION_DIR
        if not realization_dir.exists():
            continue

        for json_file in realization_dir.glob("*.json"):
            name = json_file.name
            if name.startswith("default_") or name.startswith("test_"):
                continue

            json_file.unlink()
            print(f"[OK] removed {json_file}")
            removed_any = True

#    # 3. remove realization-specific HTML
#    html_path = Path(SITES_DIR) / f"{realization_name}.html"
#    if html_path.exists():
#        html_path.unlink()
#        print(f"[OK] removed {html_path}")
#        removed_any = True
#
#    if not removed_any:
#        print(f"[OK] nothing to clean for realization '{realization_name}'")
#
