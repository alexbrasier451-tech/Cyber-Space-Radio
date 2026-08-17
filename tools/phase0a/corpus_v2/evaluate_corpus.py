"""Evaluate frozen Matcher v2 without exposing or retaining live content."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from coincurve import PrivateKey


HERE = Path(__file__).resolve().parent
PHASE0A_DIR = HERE.parent
sys.path.insert(0, str(PHASE0A_DIR))

from phase0a_compare import (  # noqa: E402
    RELATIONSHIP_MATCHER_VERSION,
    classify_jetstream_event,
    classify_nostr_event,
    relationship_topic_match,
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_and_verify(
    corpus_path: Path, manifest_path: Path
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    frozen_paths = {
        "corpus.jsonl": corpus_path,
        "owner_label_review.csv": HERE / "owner_label_review.csv",
        "generate_corpus.py": HERE / "generate_corpus.py",
        "evaluate_corpus.py": HERE / "evaluate_corpus.py",
        "../phase0a_compare.py": PHASE0A_DIR / "phase0a_compare.py",
        "../corpus/corpus.jsonl": PHASE0A_DIR / "corpus" / "corpus.jsonl",
    }
    for name, path in frozen_paths.items():
        actual_hash = sha256_file(path)
        expected_hash = manifest["sha256"][name]
        if actual_hash != expected_hash:
            raise ValueError(
                f"frozen input hash mismatch for {name}: "
                f"expected {expected_hash}, got {actual_hash}"
            )
    matcher_hash = manifest["matcher_frozen_sha256"]
    if matcher_hash != manifest["sha256"]["../phase0a_compare.py"]:
        raise ValueError("manifest matcher freeze does not match frozen input hash")
    if RELATIONSHIP_MATCHER_VERSION != manifest["matcher_version"]:
        raise ValueError("runtime matcher version does not match manifest")
    records = [
        json.loads(line)
        for line in corpus_path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    return records, manifest


def _identity_seed(value: str) -> int:
    return int(hashlib.sha256(value.encode("utf-8")).hexdigest()[:8], 16)


def _nostr_event(record: dict[str, Any]) -> dict[str, Any]:
    identity = record["protocol_identity"]
    private_key = PrivateKey(bytes.fromhex("01" * 32))
    pubkey = private_key.public_key_xonly.format().hex()
    created_at = 1_700_000_000 + _identity_seed(identity) % 10_000_000
    event_class = record["event_class"]
    kind = 1
    tags: list[list[str]] = []
    if event_class == "reply":
        tags = [["e", "11" * 32]]
    elif event_class == "recipient":
        tags = [["p", "22" * 32]]
    elif event_class == "quote":
        tags = [["q", "33" * 32]]
    elif event_class == "repost":
        kind = 6
    elif event_class == "direct":
        kind = 4
    elif event_class == "group":
        kind = 42
    event = {
        "pubkey": pubkey,
        "created_at": created_at,
        "kind": kind,
        "tags": tags,
        "content": record["text"],
    }
    canonical = json.dumps(
        [0, pubkey, created_at, kind, tags, record["text"]],
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    event["id"] = hashlib.sha256(canonical).hexdigest()
    event["sig"] = private_key.sign_schnorr(
        bytes.fromhex(event["id"]), aux_randomness=bytes(32)
    ).hex()
    return event


def _jetstream_event(record: dict[str, Any]) -> dict[str, Any]:
    identity = record["protocol_identity"]
    event_class = record["event_class"]
    body: dict[str, Any] = {
        "$type": "app.bsky.feed.post",
        "text": record["text"],
        "createdAt": "2026-08-18T12:00:00Z",
    }
    collection = "app.bsky.feed.post"
    if event_class == "reply":
        body["reply"] = {"root": {}, "parent": {}}
    elif event_class in {"recipient", "direct", "group"}:
        body["facets"] = [
            {
                "features": [
                    {
                        "$type": "app.bsky.richtext.facet#mention",
                        "did": "did:plc:fixture",
                    }
                ]
            }
        ]
    elif event_class == "quote":
        body["embed"] = {"$type": "app.bsky.embed.record", "record": {}}
    elif event_class == "repost":
        collection = "app.bsky.feed.repost"
    payload = {
        "$type": "network.bsky.jetstream.subscribeEvents#commit",
        "seq": _identity_seed(identity),
        "did": "did:plc:syntheticfixture",
        "time": "2026-08-18T12:00:01Z",
        "rev": "synthetic-v2",
        "operation": "create",
        "collection": collection,
        "rkey": identity.split(":", 1)[1],
        "record": body,
        "cid": hashlib.sha256(identity.encode("utf-8")).hexdigest(),
    }
    return {"$type": "message", "payload": payload}


def _classify(record: dict[str, Any]) -> tuple[bool, bool, bool, str]:
    if record["source_family"] == "nostr":
        result = classify_nostr_event(_nostr_event(record))
        valid = result.valid_shape and result.valid_event_id and result.valid_signature
        return valid, result.body_oversized, result.standalone, (
            "standalone" if result.standalone else "structural_or_invalid"
        )
    result = classify_jetstream_event(_jetstream_event(record))
    return result.valid_shape, result.body_oversized, result.standalone, (
        "standalone" if result.standalone else result.reason or "structural_or_invalid"
    )


def _empty_metrics() -> collections.Counter[str]:
    return collections.Counter(
        tp=0,
        fp=0,
        tn=0,
        fn=0,
        ambiguous_excluded=0,
        structurally_excluded=0,
        oversized_excluded=0,
        duplicates_excluded=0,
        evaluated=0,
        total=0,
    )


def _finish(counter: collections.Counter[str]) -> dict[str, Any]:
    tp, fp, fn = counter["tp"], counter["fp"], counter["fn"]
    predicted_positive = tp + fp
    known_positive = tp + fn
    precision = tp / predicted_positive if predicted_positive else None
    recall = tp / known_positive if known_positive else None
    output: dict[str, Any] = dict(counter)
    output.update(
        {
            "precision": round(precision, 6) if precision is not None else None,
            "recall": round(recall, 6) if recall is not None else None,
            "false_positives_per_100_candidates": (
                round(fp * 100 / counter["evaluated"], 3)
                if counter["evaluated"]
                else None
            ),
        }
    )
    return output


def validate_corpus(records: list[dict[str, Any]]) -> dict[str, Any]:
    ids = [record["id"] for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("corpus IDs are not unique")
    if len(records) < 200:
        raise ValueError("corpus has fewer than 200 records")
    if sum(record["label"] == "relevant" for record in records) < 50:
        raise ValueError("corpus has fewer than 50 clear positives")
    if {record["source_family"] for record in records} != {"nostr", "jetstream"}:
        raise ValueError("both source families are required")
    if {record["split"] for record in records} != {"development", "held_out"}:
        raise ValueError("development and held-out splits are required")
    for record in records:
        if record["label"] not in {"relevant", "not_relevant", "ambiguous"}:
            raise ValueError(f"invalid label in {record['id']}")
        if record["split"] == "held_out" and not record["id"].startswith("syn-v2-"):
            raise ValueError(f"held-out record is not a fresh v2 fixture: {record['id']}")
        if len(record["text"].encode("utf-8")) != record["expected_utf8_bytes"]:
            raise ValueError(f"UTF-8 size mismatch in {record['id']}")
        if "no live content" not in record["provenance"]:
            raise ValueError(f"non-synthetic provenance in {record['id']}")
    return {
        "records": len(records),
        "unique_concepts": len({record["concept_id"] for record in records}),
        "clear_relevant_records": sum(
            record["label"] == "relevant" for record in records
        ),
        "ambiguous_records": sum(
            record["label"] == "ambiguous" for record in records
        ),
        "per_source": dict(
            sorted(
                collections.Counter(
                    record["source_family"] for record in records
                ).items()
            )
        ),
        "per_split": dict(
            sorted(
                collections.Counter(record["split"] for record in records).items()
            )
        ),
    }


def evaluate(records: list[dict[str, Any]], manifest: dict[str, Any]) -> dict[str, Any]:
    validation = validate_corpus(records)
    buckets: dict[tuple[str, str], collections.Counter[str]] = {
        (split, source): _empty_metrics()
        for split in ("development", "held_out")
        for source in ("nostr", "jetstream", "overall")
    }
    seen_identities: dict[str, set[str]] = collections.defaultdict(set)
    outcomes: list[dict[str, Any]] = []

    for record in records:
        source = record["source_family"]
        split = record["split"]
        valid, oversized, standalone, classifier_reason = _classify(record)
        duplicate = record["protocol_identity"] in seen_identities[source]
        seen_identities[source].add(record["protocol_identity"])
        eligible = valid and not oversized and standalone and not duplicate
        predicted = eligible and relationship_topic_match(record["text"])
        outcomes.append(
            {
                "id": record["id"],
                "source_family": source,
                "split": split,
                "label": record["label"],
                "predicted_relevant": predicted,
                "eligible": eligible,
                "duplicate": duplicate,
                "classifier_reason": classifier_reason,
                "body_oversized": oversized,
            }
        )
        for bucket_source in (source, "overall"):
            counter = buckets[(split, bucket_source)]
            counter["total"] += 1
            if record["label"] == "ambiguous":
                counter["ambiguous_excluded"] += 1
                continue
            counter["evaluated"] += 1
            if oversized:
                counter["oversized_excluded"] += 1
            elif duplicate:
                counter["duplicates_excluded"] += 1
            elif not standalone or not valid:
                counter["structurally_excluded"] += 1
            positive = record["label"] == "relevant"
            if positive and predicted:
                counter["tp"] += 1
            elif not positive and predicted:
                counter["fp"] += 1
            elif positive:
                counter["fn"] += 1
            else:
                counter["tn"] += 1

    metrics = {
        split: {
            source: _finish(buckets[(split, source)])
            for source in ("nostr", "jetstream", "overall")
        }
        for split in ("development", "held_out")
    }
    held_out_sources = [metrics["held_out"][source] for source in ("nostr", "jetstream", "overall")]
    metric_gate_passed = all(
        item["precision"] is not None
        and item["recall"] is not None
        and item["precision"] >= 0.85
        and item["recall"] >= 0.60
        for item in held_out_sources
    )
    false_positive_ids = [
        outcome["id"]
        for outcome in outcomes
        if outcome["split"] == "held_out"
        and outcome["label"] == "not_relevant"
        and outcome["predicted_relevant"]
    ]
    false_negative_ids = [
        outcome["id"]
        for outcome in outcomes
        if outcome["split"] == "held_out"
        and outcome["label"] == "relevant"
        and not outcome["predicted_relevant"]
    ]
    return {
        "schema": "cyber-space-radio/phase0a-matcher-evaluation/2",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "corpus_version": manifest["corpus_version"],
        "matcher_version": manifest["matcher_version"],
        "frozen_sha256": manifest["sha256"],
        "corpus_validation": validation,
        "method": {
            "matcher": "frozen production v2 contextual phrase matcher with conservative junk suppression",
            "pipeline_order": "protocol validation, body limit, standalone classification, protocol-identity deduplication, junk suppression, then topic match",
            "development_data": "v1 development split only",
            "held_out_first_evaluation": True,
            "held_out_used_for_tuning": False,
            "ambiguous_labels": "excluded from precision and recall",
            "precision_gate": 0.85,
            "recall_gate": 0.60,
            "live_content_read_or_persisted": False,
        },
        "labels": {
            "status": "provisional_project_owner_review",
            "project_owner_approval": False,
            "approval_outstanding": True,
        },
        "metrics": metrics,
        "held_out_error_ids": {
            "false_positives": false_positive_ids,
            "false_negatives": false_negative_ids,
            "note": "Synthetic fixture IDs only; no source text or live identifiers.",
        },
        "gate": {
            "metric_gate_passed": metric_gate_passed,
            "label_approval_passed": False,
            "phase0a_matcher_gate_passed": False,
            "result": "PENDING_OWNER_APPROVAL" if metric_gate_passed else "FAIL",
            "reasons": [
                (
                    "held-out metric thresholds passed"
                    if metric_gate_passed
                    else "one or more held-out metric thresholds failed"
                ),
                "explicit project-owner approval of provisional labels remains outstanding",
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=HERE / "corpus.jsonl")
    parser.add_argument("--manifest", type=Path, default=HERE / "manifest.json")
    parser.add_argument(
        "--output", type=Path, default=HERE / "evidence" / "evaluation.json"
    )
    args = parser.parse_args()
    records, manifest = load_and_verify(args.corpus, args.manifest)
    result = evaluate(records, manifest)
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0 if result["gate"]["phase0a_matcher_gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
