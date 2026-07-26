from __future__ import annotations
from pathlib import Path
import typer
from typing import List, Dict
from generator.core.cli_core3 import main, get_sites
from generator.m404 import generate_404

app = typer.Typer(
    name="sitegen",
    help=(
        "🚀 SiteGen — block-based static site generator\n\n"
        "A deterministic build system for multi-language websites.\n\n"
        "Each site is defined as a JSON block graph and rendered into static HTML.\n"
    ),
    add_completion=True,
    rich_markup_mode="rich",
)

BASE = Path("./")
JSON_DIRECTORY = BASE / "json_backbone"
BLOCK_DIRECTORY = BASE / "blocks"
SITES_DIRECTORY = BASE / "sites"


def complete_site(incomplete: str) -> List[str]:
    sites = [k["site_name"] for k in get_sites()]
    return [site for site in sites if site.startswith(incomplete)]


def complete_lang(ctx: typer.Context, incomplete: str) -> List[str]:
    site = ctx.params.get("site")

    langs = [k["lang"] for k in get_sites() if k["site_name"] == site]
    if not langs:
        return langs
    return [lang for lang in langs if lang.startswith(incomplete)]


@app.command(help="List available sites")
def sites() -> None:
    result: Dict[str, List[str]] = {}
    for item in get_sites():
        if item["site_name"] not in result:
            result[item["site_name"]] = []
        result[item["site_name"]].append(item["lang"])

    for site_name, langs in result.items():
        print(f"{str(site_name).ljust(30)} {langs}")


@app.command(help="Validate all blocks and build final static HTML site")
def build(
    site: str = typer.Argument(..., autocompletion=complete_site),
    lang: str = typer.Argument(..., autocompletion=complete_lang),
) -> None:
    main(JSON_DIRECTORY, BLOCK_DIRECTORY, SITES_DIRECTORY, site, lang)
    print("Building ...")
    generate_404()


@app.command(
    help=("Full rebuild of all sites.\nRuns full pipeline for each site:\n  clean → split → validate → build\nUseful for CI/CD or full regeneration.")
)
def regenerate() -> None:
    print("Regenerating...")
    msg = ""
    for item in get_sites():
        site_name = item["site_name"]
        lang = item["lang"]
        main(JSON_DIRECTORY, BLOCK_DIRECTORY, SITES_DIRECTORY, site_name, lang)
        msg += f"Site: {str(site_name).ljust(30)} {lang} regenerated.\n"
    print(msg)
    generate_404()


if __name__ == "__main__":
    app()
