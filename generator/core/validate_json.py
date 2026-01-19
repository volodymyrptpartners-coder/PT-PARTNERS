import json
import sys
from typing import Any
from typing import List
from pathlib import Path
from jsonschema import Draft202012Validator
from jsonschema import RefResolver
from generator.core.cli_core import get_block_names, get_json_schema_path, get_realization_jsons


def die(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def get_ref() -> RefResolver:
    schema = load_json("generator/inline_block.schema.json")
    return RefResolver(base_uri="generator/", referrer=schema)


def load_json(path: str) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            result = json.load(f)
    except FileNotFoundError:
        die(f"file not found: {path}")
    except json.JSONDecodeError as e:
        die(f"invalid JSON in {path}: {e}")
    return result


def count_json_lines(node: Any) -> int:
    if isinstance(node, dict):
        if not node:
            return 1
        return 2 + sum(count_json_lines(v) for v in node.values())
    if isinstance(node, list):
        if not node:
            return 1
        return 2 + sum(count_json_lines(v) for v in node)
    return 1


def json_path_to_line(data: Any, target_path: List[Any]) -> int:
    found = None

    def walk(node: Any, current_path: Any, line: int) -> int:
        nonlocal found

        if found is not None:
            return line

        # full match
        if current_path == target_path:
            found = line
            return line
        if isinstance(node, dict):
            line += 1  # {
            for key, value in node.items():
                line = walk(value, current_path + [key], line)
                if found is not None:
                    return line
            line += 1  # }
            return line
        if isinstance(node, list):
            line += 1  # [
            for i, value in enumerate(node):
                line = walk(value, current_path + [i], line)
                if found is not None:
                    return line
            line += 1  # ]
            return line
        # scalar
        return line + 1

    walk(data, [], 0)
    if found is None:
        raise KeyError("Path not found")
    return found


def print_context(
    lines: List[str],
    error_line: int,
    before: int = 2,
    after: int = 2,
) -> None:
    """
    Print context around a line, similar to grep -n -A/-B.
    error_line is 0-based.
    """

    start = max(0, error_line - before)
    end = min(len(lines), error_line + after + 1)

    for i in range(start, end):
        marker = ">" if i == error_line else " "
        lineno = i + 1  # human-readable
        content = lines[i].rstrip()

        print(f"{marker} {lineno:4d} | {content}", file=sys.stderr)


def verify_json(schema_path: str, data_path: str, context_lines: int = 4) -> bool:
    schema = load_json(schema_path)
    validator = Draft202012Validator(schema, resolver=get_ref())

    file_path = Path(data_path)
    lines = file_path.read_text(encoding="utf-8").splitlines()
    data = load_json(path=data_path)

    for err in validator.iter_errors(data):
        print("Error found!")

        base_path = list(err.absolute_path)
        path_for_line = base_path.copy()

        # --- SPECIAL HANDLING FOR additionalProperties ---
        if err.validator == "additionalProperties":
            extra_key = None

            # 1. Preferred: params.additionalProperties
            params = getattr(err, "params", None)
            if isinstance(params, dict):
                extras = params.get("additionalProperties")
                if isinstance(extras, (list, tuple)) and extras:
                    extra_key = extras[0]

            # 2. Fallback: parse from error message
            if extra_key is None and isinstance(err.message, str):
                import re

                m = re.search(r"\('([^']+)' was unexpected\)", err.message)
                if m:
                    extra_key = m.group(1)

            if extra_key is not None:
                path_for_line.append(extra_key)

        key = path_for_line[-1] if path_for_line else None

        print(f"\n❌ {data_path}", file=sys.stderr)

        if path_for_line:
            print("\nProblem at:", file=sys.stderr, end="")
            print(".".join(str(p) for p in path_for_line), file=sys.stderr)

            try:
                error_line = json_path_to_line(data, path_for_line)
            except Exception:
                error_line = None

            if error_line is not None:
                print("\nContext:", file=sys.stderr)
                print_context(lines, error_line, before=context_lines, after=context_lines)

        print("\nWhat to do:\t", file=sys.stderr, end="")

        if err.validator == "type":
            expected = err.validator_value
            print(f"Replace this value with a {expected}.", file=sys.stderr)
            if key:
                print("\nExample:\t", file=sys.stderr, end="")
                print(f'"{key}": "<{expected}>"', file=sys.stderr)
        else:
            print(f"\nValidator type  {err.validator!r}", file=sys.stderr)
            print("Fix this value according to the expected format.", file=sys.stderr)

        return False

    return True


def main() -> None:
    for block_name in get_block_names():
        schema_path = get_json_schema_path(block_name=block_name)

        for data_path in get_realization_jsons(block_name=block_name):
            correct = verify_json(schema_path=schema_path, data_path=data_path)
            if not correct:
                print(f"[ERROR] validated {data_path}")
                raise ValueError("Json is invalid!")
            print(f"[OK] validated {data_path}")
    print("All realizations are valid")


if __name__ == "__main__":
    main()
