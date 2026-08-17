from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent


def _load_local_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


generate_corpus = _load_local_module(
    "phase0a_generate_corpus_v2", HERE / "generate_corpus.py"
)
evaluate_corpus = _load_local_module(
    "phase0a_evaluate_corpus_v2", HERE / "evaluate_corpus.py"
)
evaluate = evaluate_corpus.evaluate
load_and_verify = evaluate_corpus.load_and_verify


class MatcherV2CorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.records, cls.manifest = load_and_verify(
            HERE / "corpus.jsonl", HERE / "manifest.json"
        )

    def test_corpus_meets_minimums_and_keeps_sources_balanced(self) -> None:
        self.assertGreaterEqual(len(self.records), 200)
        self.assertEqual(len(self.records) % 2, 0)
        per_source = {
            source: sum(record["source_family"] == source for record in self.records)
            for source in ("nostr", "jetstream")
        }
        self.assertEqual(per_source["nostr"], per_source["jetstream"])
        self.assertGreaterEqual(
            sum(record["label"] == "relevant" for record in self.records), 50
        )

    def test_only_v1_development_and_fresh_v2_held_out_are_combined(self) -> None:
        development = [r for r in self.records if r["split"] == "development"]
        held_out = [r for r in self.records if r["split"] == "held_out"]
        self.assertTrue(development)
        self.assertTrue(held_out)
        self.assertTrue(all(record["id"].startswith("syn-v1-") for record in development))
        self.assertTrue(all(record["id"].startswith("syn-v2-") for record in held_out))
        self.assertTrue(self.manifest["matcher_frozen_before_held_out_authoring"])
        self.assertEqual(
            self.manifest["matcher_frozen_sha256"], generate_corpus.MATCHER_SHA256
        )

    def test_all_labels_are_synthetic_and_await_owner_approval(self) -> None:
        self.assertTrue(all(not record["owner_approved"] for record in self.records))
        self.assertTrue(all("no live content" in record["provenance"] for record in self.records))
        self.assertTrue(all(record["license"] == "CC0-1.0" for record in self.records))

    def test_review_sheet_has_one_row_per_concept(self) -> None:
        rows = list(
            csv.DictReader(
                io.StringIO(
                    (HERE / "owner_label_review.csv")
                    .read_text(encoding="utf-8-sig")
                )
            )
        )
        self.assertEqual(len(rows), len({r["concept_id"] for r in self.records}))
        self.assertTrue(all(not row["owner_decision"] for row in rows))

    def test_utf8_boundaries_are_exact(self) -> None:
        boundaries = [
            record
            for record in self.records
            if record["concept_id"].startswith("fresh-body-boundary-")
        ]
        self.assertEqual(len(boundaries), 12)
        self.assertEqual(
            sorted({record["expected_utf8_bytes"] for record in boundaries}),
            [16_383, 16_384, 16_385],
        )

    def test_generator_rebuilds_corpus_and_review_sheet_byte_identically(self) -> None:
        records = generate_corpus.build_records()
        self.assertEqual(
            generate_corpus._jsonl_bytes(records),
            (HERE / "corpus.jsonl").read_bytes(),
        )
        self.assertEqual(
            generate_corpus._review_csv_bytes(records),
            (HERE / "owner_label_review.csv").read_bytes(),
        )

    def test_evaluation_never_claims_owner_approval(self) -> None:
        result = evaluate(self.records, self.manifest)
        held_out = result["metrics"]["held_out"]
        for source in ("nostr", "jetstream"):
            self.assertEqual(
                (
                    held_out[source]["tp"],
                    held_out[source]["fp"],
                    held_out[source]["tn"],
                    held_out[source]["fn"],
                ),
                (35, 5, 44, 0),
            )
            self.assertEqual(held_out[source]["precision"], 0.875)
            self.assertEqual(held_out[source]["recall"], 1.0)
        self.assertTrue(result["gate"]["metric_gate_passed"])
        self.assertFalse(result["labels"]["project_owner_approval"])
        self.assertFalse(result["gate"]["phase0a_matcher_gate_passed"])
        self.assertEqual(
            hashlib.sha256((HERE.parent / "phase0a_compare.py").read_bytes()).hexdigest(),
            generate_corpus.MATCHER_SHA256,
        )


if __name__ == "__main__":
    unittest.main()
