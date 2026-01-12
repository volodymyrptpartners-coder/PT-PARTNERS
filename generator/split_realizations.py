#!/usr/bin/env python3

import json
from pathlib import Path

IN_FILE = Path("sites/site_ua.json")
BLOCKS_DIR = Path("blocks")

with open(IN_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

for block_name, block_data in data["blocks"].items():
    realization_dir = BLOCKS_DIR / block_name / "realization"
    realization_dir.mkdir(parents=True, exist_ok=True)

    out_file = realization_dir / "ua.json"
    out_file.write_text(
        json.dumps(block_data["realization"], ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"OK: wrote {out_file}")

