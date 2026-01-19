import argparse

from generator.core.cli_core import merge, split, collect_assets as build_assets, render_block, clean
from generator.core.validate_json import main as validate


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ptpartners-cli",
        description="PT Partners site generator CLI",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # ---- merge
    merge_p = subparsers.add_parser("merge", help="Merge realizations into site json")
    merge_p.add_argument("realization", help="Realization name (e.g. consular_ua)")

    # ---- split
    split_p = subparsers.add_parser("split", help="Split site json into realizations")
    split_p.add_argument("realization", help="Realization name")

    # ---- build
    build_p = subparsers.add_parser("build", help="Build site assets and render blocks")
    build_p.add_argument("realization", help="Realization name")

    # ---- validate
    subparsers.add_parser("validate", help="Validate realization json files")

    # ---- clean
    clean_p = subparsers.add_parser("clean", help="Clean generated artifacts")
    clean_p.add_argument("realization", help="Realization name")

    args = parser.parse_args()

    # ---- dispatch
    if args.command == "merge":
        merge(args.realization)

    elif args.command == "split":
        split(args.realization)

    elif args.command == "build":
        build_assets(args.realization)
        render_block(args.realization)

    elif args.command == "validate":
        validate()

    elif args.command == "clean":
        clean(args.realization)


if __name__ == "__main__":
    main()
