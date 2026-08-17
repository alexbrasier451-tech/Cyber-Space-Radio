"""Validate Phase 0 documentation invariants with the Python standard library."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
PHASE0 = ROOT / "docs" / "phase-0"
SOURCE_REGISTER = PHASE0 / "phase-0a-reviewed-sources.csv"
SOURCE_TEMPLATE = PHASE0 / "templates" / "approved-source-register.csv"
CHARTER = PHASE0 / "PROJECT_CHARTER.md"
TRACEABILITY = PHASE0 / "PHASE_1_TRACEABILITY_MATRIX.md"
CONTACT = ROOT / "CONTACT.md"
PROJECT_CONTACT = "mailto:cyberspaceradio@proton.me"
PROJECT_CONTACT_PAGE = (
    "https://github.com/alexbrasier451-tech/Cyber-Space-Radio/blob/main/CONTACT.md"
)

REQUIRED_SOURCE_COLUMNS = {
    "source_id",
    "endpoint",
    "owner_contact",
    "project_operator_contact",
    "project_operator_contact_status",
    "replay_window_seconds",
    "reconnect_policy",
    "max_events_per_minute",
    "queue_cap",
    "retained_fields",
    "status",
}


def validate_csv(path: Path, *, reviewed: bool) -> tuple[int, int]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
        columns = list(rows[0].keys()) if rows else list(csv.DictReader(handle).fieldnames or [])

    missing = REQUIRED_SOURCE_COLUMNS.difference(columns)
    if missing:
        raise AssertionError(f"{path}: missing columns {sorted(missing)}")
    if any(None in row for row in rows):
        raise AssertionError(f"{path}: row has more values than the header")
    if any(any(value is None for value in row.values()) for row in rows):
        raise AssertionError(f"{path}: row has fewer values than the header")

    ids = [row["source_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise AssertionError(f"{path}: source_id values are not unique")
    for row in rows:
        if not row["reconnect_policy"].strip() or not row["queue_cap"].strip():
            raise AssertionError(f"{path}: {row['source_id']} lacks reconnect/queue bounds")
        if reviewed and row["status"] != "approved-disabled":
            raise AssertionError(f"{path}: reviewed source {row['source_id']} is not approved-disabled")
        if reviewed and row["project_operator_contact"] != PROJECT_CONTACT:
            raise AssertionError(
                f"{path}: reviewed source {row['source_id']} lacks the recorded project contact"
            )
        if reviewed and row["project_operator_contact_status"] != "published-and-client-exposed":
            raise AssertionError(
                f"{path}: reviewed source {row['source_id']} lacks the verified project-contact state"
            )
        if row["owner_contact"] and row["owner_contact"] == row["project_operator_contact"]:
            raise AssertionError(
                f"{path}: {row['source_id']} conflates source-owner and project-operator contacts"
            )
    return len(columns), len(rows)


def validate_links() -> int:
    broken: list[str] = []
    checked = 0
    link_pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    for markdown in ROOT.rglob("*.md"):
        text = markdown.read_text(encoding="utf-8")
        for raw_target in link_pattern.findall(text):
            target = raw_target.strip().strip("<>").split("#", 1)[0]
            if not target or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE):
                continue
            checked += 1
            resolved = (markdown.parent / unquote(target)).resolve()
            if not resolved.exists():
                broken.append(f"{markdown.relative_to(ROOT)} -> {target}")
    if broken:
        raise AssertionError("broken local links:\n" + "\n".join(broken))
    return checked


def validate_traceability() -> int:
    requirement_pattern = re.compile(r"^\| (FR-\d+(?:A)?) \|", re.MULTILINE)
    requirements = requirement_pattern.findall(CHARTER.read_text(encoding="utf-8"))
    mapped = requirement_pattern.findall(TRACEABILITY.read_text(encoding="utf-8"))
    if len(requirements) != len(set(requirements)):
        raise AssertionError("PROJECT_CHARTER.md contains duplicate functional requirement IDs")
    if len(mapped) != len(set(mapped)):
        raise AssertionError("PHASE_1_TRACEABILITY_MATRIX.md contains duplicate requirement IDs")
    if set(requirements) != set(mapped):
        missing = sorted(set(requirements).difference(mapped))
        extra = sorted(set(mapped).difference(requirements))
        raise AssertionError(f"traceability mismatch: missing={missing}, extra={extra}")
    return len(requirements)


def validate_json_fences() -> int:
    count = 0
    fence_pattern = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL | re.IGNORECASE)
    for markdown in ROOT.rglob("*.md"):
        for payload in fence_pattern.findall(markdown.read_text(encoding="utf-8")):
            json.loads(payload)
            count += 1
    return count


def validate_project_contact() -> str:
    text = CONTACT.read_text(encoding="utf-8")
    if PROJECT_CONTACT not in text:
        raise AssertionError("CONTACT.md lacks the registered project contact")
    if PROJECT_CONTACT_PAGE not in text:
        raise AssertionError("CONTACT.md lacks the intended public contact page")
    if "Published, anonymously reachable, mailbox-verified, and client-exposed." not in text:
        raise AssertionError("CONTACT.md does not record the completed contact gate")
    if "published-and-client-exposed" not in text:
        raise AssertionError("CONTACT.md lacks the verified source-register state")
    return PROJECT_CONTACT


def main() -> int:
    try:
        reviewed_columns, reviewed_rows = validate_csv(SOURCE_REGISTER, reviewed=True)
        template_columns, template_rows = validate_csv(SOURCE_TEMPLATE, reviewed=False)
        links = validate_links()
        requirements = validate_traceability()
        json_fences = validate_json_fences()
        project_contact = validate_project_contact()
    except (AssertionError, csv.Error, json.JSONDecodeError, OSError) as exc:
        print(f"Phase 0 documentation validation FAILED: {exc}", file=sys.stderr)
        return 1

    print(
        "Phase 0 documentation validation passed: "
        f"reviewed CSV {reviewed_rows}x{reviewed_columns}, "
        f"template CSV {template_rows}x{template_columns}, "
        f"{requirements} requirements mapped, {links} local links, "
        f"{json_fences} JSON fences, project contact {project_contact} "
        "published, mailbox-verified, and client-exposed."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
