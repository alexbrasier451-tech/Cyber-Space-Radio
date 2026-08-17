"""Generate the frozen synthetic Phase 0A relationship/gossip corpus.

All fixture prose in this file was written for this project.  Nothing is copied
from a live Nostr relay, Jetstream, a social-network account, or a private
message.  Generation is deterministic and uses no network access or randomness.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


CORPUS_VERSION = "relationship-gossip-synthetic-v1"
SCHEMA = "cyber-space-radio/phase0a-matcher-corpus/1"
SOURCE_FAMILIES = ("nostr", "jetstream")
LICENSE = "CC0-1.0"


MATCHED_POSITIVES = [
    "I am dating someone new and feel hopeful about it.",
    "My boyfriend and I finally talked through the awkward silence.",
    "Her girlfriend planned a thoughtful surprise for the weekend.",
    "My husband remembered the tiny detail that mattered to me.",
    "His wife asked for more honesty about their plans.",
    "The breakup was painful, but I am starting to recover.",
    "They are discussing divorce after months of living apart.",
    "Our marriage feels stronger after that difficult conversation.",
    "I admitted my crush and learned the feeling was mutual.",
    "She discovered cheating and is deciding what comes next.",
    "He confessed an affair and asked whether trust can be rebuilt.",
    "There is gossip that two friends have quietly started seeing each other.",
    "A rumour about their secret engagement is spreading among friends.",
    "The rumor says the former partners may be together again.",
    "The friendship drama began when both people liked the same person.",
    "That situationship ended when they wanted different levels of commitment.",
    "Their relationship became long-distance after one of them moved.",
    "Several relationships in our friend group changed this summer.",
    "Dating after a long break has been unexpectedly nerve-racking.",
    "My boyfriend wants us to meet each other's families soon.",
    "Her girlfriend said she needs space before making a decision.",
    "My husband and I scheduled a quiet evening to reconnect.",
    "His wife feels ignored whenever work takes over the weekend.",
    "We handled the breakup kindly and returned each other's things.",
    "The divorce conversation became calmer once they wrote down priorities.",
    "They postponed the marriage ceremony after a serious disagreement.",
    "I still have a crush on the neighbour who always makes me laugh.",
    "A friend suspects cheating because the explanations keep changing.",
    "The affair became public and caused a painful argument at home.",
    "Fresh gossip suggests the two exes were seen holding hands again.",
    "The latest rumour is that they reconciled during the holiday.",
    "Their drama is really about jealousy and unspoken expectations.",
]


UNMATCHED_POSITIVES = [
    "My partner and I agreed to spend more time listening to each other.",
    "Her fiancé cancelled the wedding and moved out this morning.",
    "I was dumped by someone I trusted and I cannot stop thinking about it.",
    "The two exes have quietly started seeing one another again.",
    "They separated after years of arguing about money and trust.",
    "Someone whispered that two colleagues are secretly a couple.",
    "He asked me out for dinner and I said yes.",
    "She proposed during our walk and her partner accepted.",
    "My sweetheart has stopped replying since our disagreement.",
    "They called off the wedding after one person changed their mind.",
    "A friend says the pair kissed after everyone else left.",
    "I learned my ex has been seeing my closest friend.",
    "Their romance began during a delayed train journey.",
    "The couple are trying again after spending a month apart.",
    "He is hiding texts from the person he lives with.",
    "People keep whispering that the neighbours have reunited.",
]


NEAR_MISS_NEGATIVES = [
    "The relationship between temperature and pressure is nearly linear.",
    "These database relationships need indexes before the migration.",
    "Customer relationship software is included in the quarterly budget.",
    "Carbon dating placed the wooden sample in the twelfth century.",
    "Radiometric dating can estimate the age of certain rocks.",
    "The archive is dating each manuscript by its paper and ink.",
    "The drama course meets in the theatre every Wednesday.",
    "That historical drama won an award for costume design.",
    "The radio drama uses footsteps to create a sense of distance.",
    "The chef described the sauce as a marriage of citrus and spice.",
    "Please crush the empty cans before putting them in recycling.",
    "The orange crush drink is stored on the second shelf.",
    "The player was caught cheating during the online chess match.",
    "Cheating on an examination can lead to disqualification.",
    "The committee called the procurement failure an affair of state.",
    "A gossip protocol shares membership data between cluster nodes.",
    "The distributed gossip algorithm converged after six rounds.",
    "Engineers model rumor spreading to understand network propagation.",
    "The asteroid breakup produced several smaller fragments.",
    "Careful teams husband scarce resources during a long emergency.",
]


PLAIN_NEGATIVES = [
    "The library will close early while the heating system is repaired.",
    "A bright meteor crossed the northern sky just before dawn.",
    "I baked bread with rosemary and left it to cool by the window.",
    "The bus route changes next Monday because the bridge is closed.",
    "Our garden produced more tomatoes than expected this year.",
    "The new keyboard is quieter and easier to use at night.",
    "Clouds covered the hills before the afternoon rain arrived.",
    "A local museum opened an exhibition about early navigation.",
    "The software update reduced startup time on my old laptop.",
    "We counted three owls during the walk through the woods.",
    "Café tables were moved indoors when the wind became stronger.",
    "The recipe needs two lemons, fresh mint, and plenty of ice.",
    "My bicycle tyre was flat, so I took the train instead.",
    "The lecture explains how glaciers shape valleys over time.",
    "A small repair stopped the tap from dripping overnight.",
    "The community orchestra rehearses every second Saturday.",
]


STRUCTURAL_EXCLUSIONS = [
    ("reply", "My boyfriend replied and asked me to call him tonight."),
    ("recipient", "Gossip for you: our two friends are apparently dating."),
    ("quote", "This quoted breakup story should not become a new shout."),
    ("repost", "A repost repeats somebody else's marriage announcement."),
    ("direct", "This direct note discusses a private affair with its recipient."),
    ("group", "The group thread is full of drama about yesterday's argument."),
    ("reply", "I answered their dating question inside the existing thread."),
    ("recipient", "I tagged one person to ask about their relationship advice."),
]


SPAM_NEGATIVES = [
    "dating dating dating dating dating dating dating dating dating dating",
    "gossip gossip gossip gossip gossip gossip gossip gossip gossip gossip",
    "relationship!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",
    "drama https://spam.invalid/a https://spam.invalid/b https://spam.invalid/c",
]


DUPLICATE_NEGATIVES = [
    ("matched-positive-001", MATCHED_POSITIVES[0]),
    ("matched-positive-002", MATCHED_POSITIVES[1]),
    ("matched-positive-003", MATCHED_POSITIVES[2]),
    ("matched-positive-004", MATCHED_POSITIVES[3]),
]


AMBIGUOUS = [
    "Our relationship changed after the move.",
    "That drama was something nobody expected.",
    "I heard a rumour, but there is no context or confirmation.",
    "We are dating the samples now, if that is what they meant.",
]


BOUNDARIES = [
    ("ascii-below", "x" * 16_383, 16_383),
    ("ascii-exact", "x" * 16_384, 16_384),
    ("ascii-above", "x" * 16_385, 16_385),
    ("unicode-below", "é" * 8_191 + "x", 16_383),
    ("unicode-exact", "é" * 8_192, 16_384),
    ("unicode-above", "é" * 8_192 + "x", 16_385),
]


def _split(local_index: int) -> str:
    """The predeclared split: odd category index -> dev, even -> held-out."""

    return "development" if local_index % 2 == 1 else "held_out"


def _record(
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
    protocol_identity = duplicate_of or concept_id
    return {
        "schema": SCHEMA,
        "corpus_version": CORPUS_VERSION,
        "id": f"syn-v1-{concept_id}-{source}",
        "concept_id": concept_id,
        "source_family": source,
        "split": _split(local_index),
        "label": label,
        "label_status": "provisional_product_team",
        "label_owner": "Cyber Space Radio product team",
        "owner_approved": False,
        "rationale": rationale,
        "event_class": event_class,
        "protocol_identity": f"{source}:{protocol_identity}",
        "duplicate_of": (
            f"syn-v1-{duplicate_of}-{source}" if duplicate_of is not None else None
        ),
        "expected_utf8_bytes": (
            expected_utf8_bytes
            if expected_utf8_bytes is not None
            else len(text.encode("utf-8"))
        ),
        "text": text,
        "provenance": "project-created synthetic fixture; no live content",
        "license": LICENSE,
    }


def build_records() -> list[dict[str, Any]]:
    definitions: list[dict[str, Any]] = []

    for index, text in enumerate(MATCHED_POSITIVES, 1):
        definitions.append(
            dict(
                category="matched-positive",
                local_index=index,
                text=text,
                label="relevant",
                rationale="Clear relationship or gossip meaning with an existing lexical-v1 term.",
            )
        )
    for index, text in enumerate(UNMATCHED_POSITIVES, 1):
        definitions.append(
            dict(
                category="unmatched-positive",
                local_index=index,
                text=text,
                label="relevant",
                rationale="Clear relationship or gossip meaning expressed without a lexical-v1 term.",
            )
        )
    for index, text in enumerate(NEAR_MISS_NEGATIVES, 1):
        definitions.append(
            dict(
                category="near-miss",
                local_index=index,
                text=text,
                label="not_relevant",
                rationale="Contains a lexical-v1 term in a non-interpersonal sense.",
            )
        )
    for index, text in enumerate(PLAIN_NEGATIVES, 1):
        definitions.append(
            dict(
                category="plain-negative",
                local_index=index,
                text=text,
                label="not_relevant",
                rationale="Clear non-relationship and non-gossip subject.",
            )
        )
    for index, (event_class, text) in enumerate(STRUCTURAL_EXCLUSIONS, 1):
        definitions.append(
            dict(
                category="structural-exclusion",
                local_index=index,
                text=text,
                label="not_relevant",
                rationale="Addressed, conversational, quoted, reposted, direct, or group event; not a standalone shout.",
                event_class=event_class,
            )
        )
    for index, text in enumerate(SPAM_NEGATIVES, 1):
        definitions.append(
            dict(
                category="spam",
                local_index=index,
                text=text,
                label="not_relevant",
                rationale="Mechanically obvious spam/noise containing a lexical-v1 term.",
            )
        )
    for index, (duplicate_of, text) in enumerate(DUPLICATE_NEGATIVES, 1):
        definitions.append(
            dict(
                category="duplicate",
                local_index=index,
                text=text,
                label="not_relevant",
                rationale="Repeated protocol identity must be suppressed before a second match decision.",
                event_class="duplicate",
                duplicate_of=duplicate_of,
            )
        )
    for index, text in enumerate(AMBIGUOUS, 1):
        definitions.append(
            dict(
                category="ambiguous",
                local_index=index,
                text=text,
                label="ambiguous",
                rationale="Insufficient context for a reliable clear label; excluded from precision/recall.",
            )
        )
    for index, (boundary_name, text, size) in enumerate(BOUNDARIES, 1):
        definitions.append(
            dict(
                category="body-boundary",
                local_index=index,
                text=text,
                label="not_relevant",
                rationale=f"Synthetic {boundary_name} UTF-8 body-size boundary fixture.",
                event_class="standalone",
                expected_utf8_bytes=size,
            )
        )

    records: list[dict[str, Any]] = []
    for definition in definitions:
        for source in SOURCE_FAMILIES:
            records.append(_record(source=source, **definition))
    return records


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_corpus(output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    corpus_path = output_dir / "corpus.jsonl"
    manifest_path = output_dir / "manifest.json"
    records = build_records()
    corpus_bytes = "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
        for record in records
    ).encode("utf-8")
    corpus_path.write_bytes(corpus_bytes)

    generator_path = Path(__file__).resolve()
    evaluator_path = output_dir / "evaluate_corpus.py"
    matcher_path = output_dir.parent / "phase0a_compare.py"
    manifest = {
        "schema": "cyber-space-radio/phase0a-matcher-corpus-manifest/1",
        "corpus_version": CORPUS_VERSION,
        "matcher_version": "phase0a-relationship-terms-v1",
        "created_date": "2026-08-17",
        "generation": "deterministic; no randomness; no network access",
        "split_rule": "Within each category, odd one-based concept index is development and even is held_out; each concept is rendered once per source family.",
        "held_out_tuning": "prohibited; no matcher changes were made during corpus evaluation",
        "label_status": "provisional_product_team; explicit project-owner approval outstanding",
        "license": LICENSE,
        "provenance": "All text is project-created synthetic fixture prose; no live event content was read, copied, or persisted.",
        "counts": {
            "records": len(records),
            "concepts": len(records) // len(SOURCE_FAMILIES),
            "source_families": list(SOURCE_FAMILIES),
            "development_records": sum(r["split"] == "development" for r in records),
            "held_out_records": sum(r["split"] == "held_out" for r in records),
            "clear_relevant_records": sum(r["label"] == "relevant" for r in records),
            "ambiguous_records": sum(r["label"] == "ambiguous" for r in records),
        },
        "sha256": {
            "corpus.jsonl": hashlib.sha256(corpus_bytes).hexdigest(),
            "generate_corpus.py": _sha256(generator_path),
            "evaluate_corpus.py": _sha256(evaluator_path),
            "../phase0a_compare.py": _sha256(matcher_path),
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return corpus_path, manifest_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir", type=Path, default=Path(__file__).resolve().parent
    )
    args = parser.parse_args()
    corpus_path, manifest_path = write_corpus(args.output_dir.resolve())
    print(corpus_path)
    print(manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
