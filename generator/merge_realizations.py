#!/usr/bin/env python3

import json
from pathlib import Path

LANG = "ua"
BLOCKS_DIR = Path("blocks")
OUT_FILE = Path(f"sites/site_{LANG}.json")

result = {
    "meta": {
        "lang": LANG,
    },
    "blocks": {}
}

for block_dir in BLOCKS_DIR.iterdir():
    realization = block_dir / "realization" / "consular_ua.json"
    if realization.exists():
        with open(realization, "r", encoding="utf-8") as f:
            result["blocks"][block_dir.name] = {
                "realization": json.load(f)
            }

OUT_FILE.write_text(
    json.dumps(result, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print(f"OK: merged into {OUT_FILE}")

