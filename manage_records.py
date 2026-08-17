"""Delete exact Cyber Space Radio records without touching other files."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Callable


def rewrite_records(log_path: Path, keep: Callable[[dict[str, object]], bool]) -> int:
    if not log_path.exists():
        return 0

    records: list[dict[str, object]] = []
    removed = 0
    with log_path.open("r", encoding="utf-8") as log:
        for line_number, line in enumerate(log, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise SystemExit(f"Invalid record at {log_path}:{line_number}") from error
            if keep(record):
                records.append(record)
            else:
                removed += 1

    if not removed:
        return 0

    temporary_name = ""
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            newline="\n",
            delete=False,
            dir=log_path.parent,
            prefix=f".{log_path.name}.",
            suffix=".tmp",
        ) as temporary:
            temporary_name = temporary.name
            for record in records:
                temporary.write(
                    json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
                )
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_name, log_path)
    finally:
        if temporary_name and os.path.exists(temporary_name):
            os.unlink(temporary_name)
    return removed


def source_value(record: dict[str, object], key: str) -> str:
    source = record.get("source")
    if not isinstance(source, dict):
        return ""
    value = source.get(key)
    return value if isinstance(value, str) else ""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, default=Path("matches.jsonl"))
    commands = parser.add_subparsers(dest="command", required=True)

    delete_url = commands.add_parser("delete-url", help="Delete one exact entry URL")
    delete_url.add_argument("url")

    delete_feed = commands.add_parser("delete-feed", help="Delete one exact feed")
    delete_feed.add_argument("url")

    purge = commands.add_parser("purge", help="Delete the entire record file")
    purge.add_argument("--yes", action="store_true", help="Confirm complete deletion")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.command == "purge":
        if not args.yes:
            raise SystemExit("Refusing to purge without --yes.")
        if args.log.exists():
            args.log.unlink()
            print(f"Deleted {args.log.resolve()}")
        else:
            print("No record file exists.")
        return

    key = "entry_url" if args.command == "delete-url" else "feed_url"
    removed = rewrite_records(args.log, lambda record: source_value(record, key) != args.url)
    print(f"Deleted {removed} matching record(s).")


if __name__ == "__main__":
    main()
