"Convention file and functions"

from pathlib import Path
from typing import List, Any

import json
from jinja2 import Environment, FileSystemLoader, StrictUndefined


BLOCKS_DIR = "blocks"
REALIZATION_DIR = "realization"


FILE_OUT_CSS = "site.css"
FILE_OUT_JS = "site.js"

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
    site_path = Path(f"sites/{realization_name}.json")
    if check_exist and not site_path.exists():
        raise ValueError(f"{str(site_path)} not exists!")
    return str(site_path)

def get_json_schema_path(block_name:str)->str:
    return str(Path(BLOCKS_DIR) / block_name / 'schema.json')



def get_block_names() -> List[str]:
    result = []
    for block_dir in Path(BLOCKS_DIR).iterdir():
        result.append(block_dir.name)
    return result

def get_realization_jsons(block_name:str)->List[str]:
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
    realization_path = str(Path(BLOCKS_DIR) / block_name / REALIZATION_DIR / f"{realization_name}.json")
    if check_exist:
        if not Path(realization_path).exists() and not take_def:
            raise ValueError(f"{realization_path!r} not found!")

        lang = get_language_by_realization_name(realization_name=realization_name)
        realization_path_default = str(Path(BLOCKS_DIR) / block_name / REALIZATION_DIR / f"default_{lang}.json")
        if not Path(realization_path_default).exists():
            raise ValueError(f"{realization_path!r} not found! and {realization_path_default!r} not found!")
        realization_path = realization_path_default
    return realization_path


def merge(realization_name: str) -> str:
    result = copy.deepcopy(CORE_SITE_JSON)
    for block_name in get_block_names():
        realization_path = get_realization_path(block_name=block_name, realization_name=realization_name)
        if Path(realization_path).exists():
            with open(realization_path, "r", encoding="utf-8") as f:
                result["blocks"][block_name] = {"realization": json.load(f)}  # type: ignore

    raw_result = json.dumps(result, ensure_ascii=False, indent=2)
    return raw_result


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
    with open(path, mode="r", encoding="utf-8") as f:
        data = f.read()
    return data


def load_json(path: Path) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError as excp:
        raise ValueError(f"file not found: {path}") from excp
    except json.JSONDecodeError as excp:
        raise ValueError(f"invalid JSON in {path}: {excp}") from excp

    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object in {path}")
    return data





def render(block_name: str, realization_name: str, include_css: bool = False, include_js: bool = False) -> str:
    inline_block = {}
    realization_path = get_realization_path(block_name=block_name, realization_name=realization_name, check_exist=True, take_def=True)
    if include_css:
        if not Path(FILE_OUT_CSS).exists():
            raise ValueError(f"{FILE_OUT_CSS} file is not found")
        inline_block["include_css"] = load_file(path=FILE_OUT_CSS)

    if include_js:
        if not Path(FILE_OUT_JS).exists():
            raise ValueError(f"{FILE_OUT_JS} file is not found")
        inline_block["include_js"] = load_file(path=FILE_OUT_JS)

    template_path = Path(BLOCKS_DIR) / block_name / BASE_J2
    if not template_path.exists():
        raise ValueError(f"template not found: {template_path}")

    realization_data = load_json(Path(realization_path))

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
