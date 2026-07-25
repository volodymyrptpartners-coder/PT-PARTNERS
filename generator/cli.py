from __future__ import annotations
from pathlib import Path
import typer
from typing import List
from generator.core.cli_core3 import main, SITES, LANGS
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
    return [site for site in SITES if site.startswith(incomplete)]


def complete_lang(incomplete: str) -> List[str]:
    return [lang for lang in LANGS if lang.startswith(incomplete)]


@app.command(help="List available sites")
def sites():
    for site_name in SITES:
        for lang in LANGS:
            print(f"{str(site_name).ljust(30)} ({lang})")


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
    for site_name in SITES:
        for lang in LANGS:
            main(JSON_DIRECTORY, BLOCK_DIRECTORY, SITES_DIRECTORY, site_name, lang)
            msg += f"Site: {str(site_name).ljust(30)} {lang} regenerated.\n"
    print(msg)
    generate_404()


if __name__ == "__main__":
    app()
