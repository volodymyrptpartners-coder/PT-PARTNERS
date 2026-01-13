#!/usr/bin/env python3
import sys
import json
from pathlib import Path

IN_FILE = Path("sites/site_ua.json")
BLOCKS_DIR = Path("blocks")

def die(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def split_realization(infile:str,realization_name:str)->None:
    with open(infile, "r", encoding="utf-8") as f:
        data = json.load(f)

    for block_name, block_data in data["blocks"].items():
        realization_dir = BLOCKS_DIR / block_name / "realization"
        realization_dir.mkdir(parents=True, exist_ok=True)

        out_file = realization_dir / f"{realization_name}.json"
        out_file.write_text(
            json.dumps(
                block_data["realization"],
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8",
        )
        print(f"OK: wrote {out_file}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        die("usage: split_realizations.py <site_path> <realization_name>")
    site_path = sys.argv[1]
    realization_name = sys.argv[2]
    print(f"site_path\t\t{site_path}  \nrealization_name\t{realization_name}")

    split_realization(infile=site_path,realization_name=realization_name) 
