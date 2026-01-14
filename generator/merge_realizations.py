#!/usr/bin/env python3
import sys
import json
from pathlib import Path

BLOCKS_DIR = Path("blocks")


def die(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def merge_realization(realization_name: str) -> None:
    result = {
        "meta": {
            "realization_name": realization_name,
        },
        "blocks": {},
    }

    OUT_FILE = Path(f"sites/{realization_name}.json")
    for block_dir in BLOCKS_DIR.iterdir():
        realization = block_dir / "realization" / f"{realization_name}.json"
        if realization.exists():
            with open(realization, "r", encoding="utf-8") as f:
                result["blocks"][block_dir.name] = {"realization": json.load(f)} # type: ignore

    raw_string = json.dumps(result, ensure_ascii=False, indent=2)
    OUT_FILE.write_text(raw_string, encoding="utf-8")
    print(f"OK: merged into {OUT_FILE}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        die("usage: merge_realizations.py <realization_name>")
    realization_name = sys.argv[1]
    print(f"realization_name\t{realization_name}")
    merge_realization(realization_name=realization_name)
