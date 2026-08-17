"""Generate the frozen Matcher v2 corpus and owner-review sheet.

The development records are the already-seen v1 development split. The
held-out records below were written only after the Matcher v2 implementation
was frozen. Generation is deterministic and performs no network access.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any


CORPUS_VERSION = "relationship-gossip-synthetic-v2"
MATCHER_VERSION = "relationship-gossip-context-v2"
MATCHER_SHA256 = "8c16b632ecf04e52dcdaa9ba124526c8d0f22bdd46c60ef1554d517f790f4757"
SCHEMA = "cyber-space-radio/phase0a-matcher-corpus/2"
SOURCE_FAMILIES = ("nostr", "jetstream")
LICENSE = "CC0-1.0"


FRESH_POSITIVES = [
    "My girlfriend and I are planning a quiet weekend together.",
    "Her fiancé apologised and they agreed to start again slowly.",
    "After the divorce, we finally spoke without arguing.",
    "Their wedding is back on after a long conversation.",
    "I have started dating someone who makes me laugh.",
    "My ex called to ask whether we could try again.",
    "A quiet situationship turned serious when they discussed commitment.",
    "The breakup still hurts, although each day is becoming easier.",
    "He admitted an affair and told his partner the truth.",
    "My wife wants us to spend more time together.",
    "Her husband moved out after another argument about trust.",
    "A colleague says two friends are secretly a couple.",
    "Rumours say she and her old partner have reconciled.",
    "There is gossip about him dating a neighbour.",
    "Their drama started when jealousy took over the friendship.",
    "I have a crush on someone from my evening class.",
    "She cheated on her partner and now regrets it.",
    "Our relationship improved after we stopped avoiding the problem.",
    "The pair reunited after spending the summer apart.",
    "He asked her out, and she happily agreed.",
    "They started seeing one another after years of friendship.",
    "The friends kissed when everyone else had gone home.",
    "My partner surprised me with breakfast and a handwritten note.",
    "She was dumped by the person she trusted most.",
    "They separated because neither person felt heard.",
    "Their romance grew from a long and patient friendship.",
    "He is hiding his texts and she suspects something is wrong.",
    "She proposed during the walk and her partner accepted.",
    "They called off their wedding after changing their plans.",
    "The neighbours are secretly together, according to two friends.",
    "Two colleagues started seeing one another after the conference.",
    "My sweetheart left a message asking me to come home.",
    "People whisper that the couple have reunited.",
    "Her engagement ended when they could not agree about the future.",
    "I think my boyfriend is planning a surprise for our anniversary.",
]


FRESH_NEAR_MISS_NEGATIVES = [
    "The relationship between voltage and current is shown on the graph.",
    "Entity relationships are documented in the database diagram.",
    "Archaeological dating placed the fossil in an earlier period.",
    "The stone building is dating from the late seventeenth century.",
    "The drama class rehearses in the hall on Thursday.",
    "A television drama won the award for sound editing.",
    "The sculpture is a marriage of glass and reclaimed wood.",
    "Crush the garlic before adding it to the warm oil.",
    "The referee found the player cheating during the game.",
    "The minister called the leak an affair of state.",
    "A gossip algorithm distributes membership updates to every node.",
    "The paper compares two models of rumor propagation.",
    "The band breakup left the label with an unfinished album.",
    "Teams must husband scarce resources during the exercise.",
    "The romance film opens in cinemas next Friday.",
    "The wedding venue published a revised price list.",
    "The divorce statute was amended by parliament last year.",
    "A dating app released its quarterly earnings report.",
    "The current affairs bulletin starts at nine o'clock.",
    "The marriage licence office closes at four this afternoon.",
]


FRESH_PLAIN_NEGATIVES = [
    "A fox crossed the empty road just before sunrise.",
    "The printer needs a new black cartridge before Monday.",
    "Fresh basil grows well beside the kitchen window.",
    "The train was delayed while engineers checked the signal.",
    "We measured the room before ordering the new shelves.",
    "A short walk helped clear my head after a busy morning.",
    "The community pool reopens after maintenance next week.",
    "Rainwater collected in the barrel behind the greenhouse.",
    "The documentary explains how migrating birds navigate.",
    "Three parcels arrived together at the reception desk.",
]


FRESH_STRUCTURAL_EXCLUSIONS = [
    ("reply", "My boyfriend replied with an apology this morning."),
    ("recipient", "For you: gossip says our neighbours are dating."),
    ("quote", "This quoted divorce announcement is not a new shout."),
    ("repost", "A repost repeats their wedding announcement."),
    ("direct", "This direct message discusses a private breakup."),
    ("group", "The group thread contains relationship advice."),
]


FRESH_SPAM_NEGATIVES = [
    "romance romance romance romance romance romance romance romance romance romance",
    "wedding!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",
    "dating https://junk.invalid/a https://junk.invalid/b https://junk.invalid/c",
    "gossip gossip gossip gossip gossip gossip gossip gossip gossip gossip",
]


FRESH_DUPLICATE_NEGATIVES = [
    ("fresh-positive-001", FRESH_POSITIVES[0]),
    ("fresh-positive-002", FRESH_POSITIVES[1]),
    ("fresh-positive-003", FRESH_POSITIVES[2]),
]


FRESH_AMBIGUOUS = [
    "Things between us are different now.",
    "Apparently those two have news, but nobody knows what it is.",
    "That relationship changed everything.",
    "There is some drama nearby, although the subject is unclear.",
]


FRESH_BOUNDARIES = [
    ("ascii-below", "x" * 16_383, 16_383),
    ("ascii-exact", "x" * 16_384, 16_384),
    ("ascii-above", "x" * 16_385, 16_385),
    ("unicode-below", "é" * 8_191 + "x", 16_383),
    ("unicode-exact", "é" * 8_192, 16_384),
    ("unicode-above", "é" * 8_192 + "x", 16_385),
]


def _v1_corpus_path() -> Path:
    return Path(__file__).resolve().parent.parent / "corpus" / "corpus.jsonl"


def _development_records() -> list[dict[str, Any]]:
    records = [
        json.loads(line)
        for line in _v1_corpus_path().read_text(encoding="utf-8").splitlines()
    ]
    development = [record for record in records if record["split"] == "development"]
    for record in development:
        record["schema"] = SCHEMA
        record["corpus_version"] = CORPUS_VERSION
        record["label_status"] = "provisional_project_owner_review"
        record["owner_approved"] = False
        record["provenance"] = (
            "project-created synthetic v1 development fixture; no live content"
        )
    return development


def _held_out_record(
    *,
    source: str,
    category: str,
    local_index: int,
    text: str,
    label: str,
    rationale: str,
    event_class: str = "standalone",
    duplicate_of: str | None = None,
    expected_utf8_bytes: int | None = None,
) -> dict[str, Any]:
    concept_id = f"{category}-{local_index:03d}"
    identity = duplicate_of or concept_id
    return {
        "schema": SCHEMA,
        "corpus_version": CORPUS_VERSION,
        "id": f"syn-v2-{concept_id}-{source}",
        "concept_id": concept_id,
        "source_family": source,
        "split": "held_out",
        "label": label,
        "label_status": "provisional_project_owner_review",
        "label_owner": "Cyber Space Radio project owner",
        "owner_approved": False,
        "rationale": rationale,
        "event_class": event_class,
        "protocol_identity": f"{source}:v2:{identity}",
        "duplicate_of": (
            f"syn-v2-{duplicate_of}-{source}" if duplicate_of is not None else None
        ),
        "expected_utf8_bytes": (
            expected_utf8_bytes
            if expected_utf8_bytes is not None
            else len(text.encode("utf-8"))
        ),
        "text": text,
        "provenance": "project-created synthetic v2 held-out fixture; no live content",
        "license": LICENSE,
    }


def _held_out_records() -> list[dict[str, Any]]:
    definitions: list[dict[str, Any]] = []
    categories = (
        (
            "fresh-positive",
            FRESH_POSITIVES,
            "relevant",
            "Clear human relationship, dating, or interpersonal gossip meaning.",
        ),
        (
            "fresh-near-miss",
            FRESH_NEAR_MISS_NEGATIVES,
            "not_relevant",
            "Relationship vocabulary is used in a non-interpersonal sense.",
        ),
        (
            "fresh-plain-negative",
            FRESH_PLAIN_NEGATIVES,
            "not_relevant",
            "Clear unrelated subject.",
        ),
    )
    for category, examples, label, rationale in categories:
        for index, example in enumerate(examples, 1):
            definitions.append(
                dict(
                    category=category,
                    local_index=index,
                    text=example,
                    label=label,
                    rationale=rationale,
                )
            )
    for index, (event_class, text) in enumerate(FRESH_STRUCTURAL_EXCLUSIONS, 1):
        definitions.append(
            dict(
                category="fresh-structural-exclusion",
                local_index=index,
                text=text,
                label="not_relevant",
                rationale="Addressed, conversational, quoted, reposted, direct, or group event.",
                event_class=event_class,
            )
        )
    for index, text in enumerate(FRESH_SPAM_NEGATIVES, 1):
        definitions.append(
            dict(
                category="fresh-spam",
                local_index=index,
                text=text,
                label="not_relevant",
                rationale="Mechanically obvious junk must be suppressed before matching.",
            )
        )
    for index, (duplicate_of, text) in enumerate(FRESH_DUPLICATE_NEGATIVES, 1):
        definitions.append(
            dict(
                category="fresh-duplicate",
                local_index=index,
                text=text,
                label="not_relevant",
                rationale="Repeated protocol identity must not create another match.",
                event_class="duplicate",
                duplicate_of=duplicate_of,
            )
        )
    for index, text in enumerate(FRESH_AMBIGUOUS, 1):
        definitions.append(
            dict(
                category="fresh-ambiguous",
                local_index=index,
                text=text,
                label="ambiguous",
                rationale="Insufficient context for a reliable clear label.",
            )
        )
    for index, (name, text, size) in enumerate(FRESH_BOUNDARIES, 1):
        definitions.append(
            dict(
                category="fresh-body-boundary",
                local_index=index,
                text=text,
                label="not_relevant",
                rationale=f"Synthetic {name} UTF-8 body-size boundary fixture.",
                expected_utf8_bytes=size,
            )
        )

    return [
        _held_out_record(source=source, **definition)
        for definition in definitions
        for source in SOURCE_FAMILIES
    ]


def build_records() -> list[dict[str, Any]]:
    return _development_records() + _held_out_records()


def _jsonl_bytes(records: list[dict[str, Any]]) -> bytes:
    return "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
        for record in records
    ).encode("utf-8")


def _review_csv_bytes(records: list[dict[str, Any]]) -> bytes:
    concepts: dict[str, dict[str, Any]] = {}
    for record in records:
        concepts.setdefault(record["concept_id"], record)
    output = io.StringIO(newline="")
    fields = (
        "concept_id",
        "split",
        "label",
        "event_class",
        "text",
        "rationale",
        "owner_decision",
    )
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for record in concepts.values():
        writer.writerow(
            {
                field: record.get(field, "")
                for field in fields
                if field != "owner_decision"
            }
            | {"owner_decision": ""}
        )
    return output.getvalue().encode("utf-8-sig")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_corpus(output_dir: Path) -> tuple[Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    corpus_path = output_dir / "corpus.jsonl"
    manifest_path = output_dir / "manifest.json"
    review_path = output_dir / "owner_label_review.csv"
    records = build_records()
    corpus_bytes = _jsonl_bytes(records)
    review_bytes = _review_csv_bytes(records)
    corpus_path.write_bytes(corpus_bytes)
    review_path.write_bytes(review_bytes)

    generator_path = Path(__file__).resolve()
    evaluator_path = output_dir / "evaluate_corpus.py"
    matcher_path = output_dir.parent / "phase0a_compare.py"
    source_corpus_path = output_dir.parent / "corpus" / "corpus.jsonl"
    matcher_hash = _sha256(matcher_path)
    if matcher_hash != MATCHER_SHA256:
        raise ValueError("Matcher v2 changed after its declared freeze")
    manifest = {
        "schema": "cyber-space-radio/phase0a-matcher-corpus-manifest/2",
        "corpus_version": CORPUS_VERSION,
        "matcher_version": MATCHER_VERSION,
        "matcher_frozen_sha256": MATCHER_SHA256,
        "matcher_frozen_before_held_out_authoring": True,
        "created_date": "2026-08-18",
        "generation": "deterministic; no randomness; no network access",
        "split_rule": (
            "Development is the v1 development split used for tuning; held_out is "
            "newly authored v2 material first evaluated only after Matcher v2 freeze."
        ),
        "held_out_tuning": "prohibited; preserve the first evaluation without matcher changes",
        "label_status": "provisional_project_owner_review; explicit approval outstanding",
        "license": LICENSE,
        "provenance": "Project-created synthetic fixtures only; no live content.",
        "counts": {
            "records": len(records),
            "concepts": len({record["concept_id"] for record in records}),
            "source_families": list(SOURCE_FAMILIES),
            "development_records": sum(
                record["split"] == "development" for record in records
            ),
            "held_out_records": sum(record["split"] == "held_out" for record in records),
            "clear_relevant_records": sum(
                record["label"] == "relevant" for record in records
            ),
            "ambiguous_records": sum(
                record["label"] == "ambiguous" for record in records
            ),
        },
        "sha256": {
            "corpus.jsonl": hashlib.sha256(corpus_bytes).hexdigest(),
            "owner_label_review.csv": hashlib.sha256(review_bytes).hexdigest(),
            "generate_corpus.py": _sha256(generator_path),
            "evaluate_corpus.py": _sha256(evaluator_path),
            "../phase0a_compare.py": matcher_hash,
            "../corpus/corpus.jsonl": _sha256(source_corpus_path),
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return corpus_path, manifest_path, review_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir", type=Path, default=Path(__file__).resolve().parent
    )
    args = parser.parse_args()
    for path in write_corpus(args.output_dir.resolve()):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
