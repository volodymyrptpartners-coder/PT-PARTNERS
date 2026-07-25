from __future__ import annotations
from pathlib import Path
from typing import List, Any, Dict, Tuple, Iterator, Literal
import copy
import json
from jinja2 import Environment, FileSystemLoader, StrictUndefined, Template
from generator.core.validate_json import SchemaValidator

LANGS = ["ua", "ru"]
Lang = Literal["ua", "ru"]


SITES = ["consular", "auto_registration", "karta_pobutu_CUKR"]
ContentType = Literal[
    "consular",
    "common",
    "shared",
]


class Content:
    def __init__(self) -> None:
        self._kwargs: Dict[str, Any]

    def setup_fields(self, **kwargs: Dict[str, Any]) -> None:
        self.__dict__["_kwargs"] = kwargs
        for key, value in self._kwargs.items():
            self.__dict__[key] = self._value_instantiation(value)

        self._setup_extra_fields()

    def _setup_extra_fields(self) -> None:
        pass

    def _value_instantiation(self, value: Any) -> Any:
        if isinstance(value, list):
            value_list = []
            for item in value:
                value_list.append(self._value_instantiation(item))
            return value_list
        if isinstance(value, dict):
            content = Content()
            content.setup_fields(**value)
            return content
        return value

    def __str__(self) -> str:
        new_dict = self._kwargs.copy()
        return json.dumps(new_dict, indent=4, ensure_ascii=False)

    def __setattr__(self, attr: str, value: Any) -> None:
        raise AttributeError("Cannot modify attributes of a frozen object")

    def has_attr(self, attr: str) -> bool:
        return hasattr(self, attr)

    def items(self) -> Iterator[Tuple[str, Any]]:
        for key in self._kwargs.keys():
            yield key, self.__dict__[key]

    def get_content_dict(self) -> Dict[str, Any]:
        return copy.deepcopy(self._kwargs)


class Block(Content):
    def __init__(self) -> None:
        self.inline_blocks: List[str]
        self.splited: bool
        self.block_name: str
        self.content_type: ContentType
        self.content_lang: Lang
        self.content: Content

        self.__dict__["inline_blocks"] = []
        self.__dict__["splited"] = False

    def _setup_extra_fields(self) -> None:
        reserved = ["inline_blocks", "splited", "block_name", "content_type", "content_lang", "content"]
        for key in reserved:
            if key not in self.__dict__:
                msg = f"Dictionary is not following format! Key {key!r} not found!"
                raise KeyError(msg)


class Site:
    def __init__(self, site_name: str, lang: Lang, root_name: str) -> None:
        self._blocks: List[Block] = []
        self.site_name = site_name
        self.lang = lang
        self._root_name = root_name

    @property
    def root_name(self) -> str:
        return self._root_name

    @property
    def blocks(self) -> Iterator[Block]:
        for block in self._blocks:
            yield block

    def setup_blocks(self, all_blocks: List[Block]) -> None:
        langs = ["common", self.lang]
        same_lang_blocks = [b for b in all_blocks if b.content_lang in langs]

        content_type = ["common", "shared", self.site_name]
        same_site_blocks = [b for b in same_lang_blocks if b.content_type in content_type]

        self._blocks = self._sort_order_by_dependecies(self.root_name, same_site_blocks)

    def _sort_order_by_dependecies(self, root_name: str, blocks: List[Block]) -> List[Block]:
        graph = {b.block_name: b.inline_blocks for b in blocks}
        visited = set()
        temp = set()
        result = []

        def dfs(node: str) -> None:
            if node in temp:
                raise ValueError(f"Cycle detected at {node}")
            if node in visited:
                return
            temp.add(node)
            for dep in graph.get(node, []):
                if dep in graph:  # ігноруємо відсутні
                    dfs(node=dep)
            temp.remove(node)
            visited.add(node)
            result.append(node)

        dfs(root_name)
        name_to_block = {b.block_name: b for b in blocks}
        return [name_to_block[name] for name in result]


class Backbone:
    def __init__(self, json_dir: Path, block_dir: Path) -> None:
        self.json_dir = json_dir
        self.block_dir = block_dir

    def collect_blocks(self) -> List[Block]:
        block_list = []
        for json_file in Path(self.json_dir).glob("*.json"):
            raw_json_data = json_file.read_text(encoding="utf-8")
            json_data = json.loads(raw_json_data)
            if not isinstance(json_data, list):
                msg = f"Expected Block list, got: {type(json_data)}, {json_data}"
                raise ValueError(msg)

            for block_dict in json_data:
                if not isinstance(block_dict, dict):
                    msg = f"Expected Block dictionary, got: {type(block_dict)}, {block_dict}"
                    raise ValueError(msg)

                block = Block()
                block.setup_fields(**block_dict)
                block_list.append(block)
        return block_list


class Jinja2Parser:
    def __init__(self, site: Site, block_dir: Path) -> None:
        self.site = site
        self.block_dir = block_dir
        self.blocks_dict: Dict[str, str] = {}
        self.text_css: str = ""
        self.text_js: str = ""

    def _validate_block(self, block: Block) -> None:
        schema_path = self.block_dir / block.block_name / "content.schema"
        sc = SchemaValidator(3)
        sc.verify_json_by_path(schema_path, block.content.get_content_dict())
        print(f"Validate {schema_path}.")

    def _load_assets(self, block: Block) -> None:
        css_file = self.block_dir / block.block_name / "base.css"
        if css_file.exists():
            self.text_css += "\n" + css_file.read_text(encoding="utf-8")
        js_file = self.block_dir / block.block_name / "base.js"
        if js_file.exists():
            self.text_js += "\n" + js_file.read_text(encoding="utf-8")

    def _get_template(self, block: Block) -> Template:
        env = Environment(
            loader=FileSystemLoader(str(self.block_dir)),
            undefined=StrictUndefined,
            autoescape=False,
        )
        env.globals["raise"] = RuntimeError
        template_path = Path(block.block_name) / "base.j2"
        return env.get_template(str(template_path))

    def parse_block(self, block: Block) -> None:
        self._validate_block(block)

        print(f"Parse block: {block.block_name!r} ...", end="")
        template = self._get_template(block)
        self._load_assets(block)

        template_dictionary = {
            "content": block.content,
            "site_name": self.site.site_name,
            "inline_blocks": self.blocks_dict.copy(),
            "text_css": self.text_css,
            "text_js": self.text_js,
        }
        result = template.render(**template_dictionary)

        self.blocks_dict.update(self.split_content(block.block_name, result))
        print(" [OK]")

    def split_content(self, block_name: str, data: str) -> Dict[str, str]:
        splited_data = data.split("<!-- SPLIT -->")
        if len(splited_data) == 1:
            return {block_name: data}
        result = {}
        for number, part in enumerate(splited_data):
            result[f"{block_name}_part{number + 1}"] = part
        return result

    def parse_site(self) -> str:
        for block in self.site.blocks:
            self.parse_block(block)
        return self.blocks_dict[self.site.root_name]


ROOT_LIST = [
    "header_block",
    "header_icons",
    "cookie_consent_v2",
    "site_top_panel_block",
    "hero_block",
    "hero2_block",
    "site_txt_block",
    "path_way_block",
    "team_block",
    "office_block",
    "accordion_container",
    "contacts_block",
    "contact_fab_block",
    "site_footer_block",
    "hero_txt1_block",
    "tiktok_block",
    "google_staff",
    "aa_entrypoint",
]
ROOT_NAME = ROOT_LIST[-1]


def main(
    json_directory: Path,
    block_directory: Path,
    sites_directory: Path,
    site_name: str,
    lang: str,
) -> None:
    if lang not in LANGS:
        msg = f"Language {lang} is not supported!"
        raise ValueError(msg)

    if site_name not in SITES:
        msg = f"Site {site_name} is not supported!"
        raise ValueError(msg)

    backcone = Backbone(json_directory, block_directory)
    blocks = backcone.collect_blocks()

    site = Site(site_name, lang, root_name=ROOT_NAME)  # type: ignore
    site.setup_blocks(blocks)

    parser = Jinja2Parser(site=site, block_dir=block_directory)
    file_content = parser.parse_site()

    site_file = sites_directory / f"{site_name}_{lang}.html"
    site_file.write_text(file_content)


#
# if __name__ == "__main__":  # pragma: no cover
#    base = Path("./")
#    json_directory = base / "new_backbone"
#    block_directory = base / "blocks"
#    sites_directory = base / "sites"
#
#    import sys
#
#    print(sys.argv)
#    if len(sys.argv) == 3:
#        name = sys.argv[1]
#        lang = sys.argv[2]
#        main(json_directory, block_directory, sites_directory, name, lang)
#    else:
#        print("Example: python3 generator/core/cli_core3.py consular ua")
