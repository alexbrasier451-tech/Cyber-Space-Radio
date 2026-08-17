from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import generate_corpus  # noqa: E402
from evaluate_corpus import evaluate, load_and_verify, lexical_match  # noqa: E402


class CorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.records, cls.manifest = load_and_verify(
            HERE / "corpus.jsonl", HERE / "manifest.json"
        )

    def test_frozen_corpus_meets_minimums_and_has_equal_sources_and_splits(self) -> None:
        self.assertEqual(len(self.records), 220)
        self.assertEqual(len({record["concept_id"] for record in self.records}), 110)
        self.assertEqual(
            {source: sum(r["source_family"] == source for r in self.records) for source in ("nostr", "jetstream")},
            {"nostr": 110, "jetstream": 110},
        )
        self.assertEqual(
            {split: sum(r["split"] == split for r in self.records) for split in ("development", "held_out")},
            {"development": 110, "held_out": 110},
        )
        self.assertEqual(sum(r["label"] == "relevant" for r in self.records), 96)

    def test_all_content_is_declared_synthetic_and_provisional(self) -> None:
        self.assertTrue(all(r["license"] == "CC0-1.0" for r in self.records))
        self.assertTrue(all("no live content" in r["provenance"] for r in self.records))
        self.assertTrue(all(not r["owner_approved"] for r in self.records))
        self.assertEqual(self.manifest["label_status"], "provisional_product_team; explicit project-owner approval outstanding")

    def test_existing_lexical_semantics_are_exact_token_matches(self) -> None:
        self.assertTrue(lexical_match("GOSSIP about nothing"))
        self.assertFalse(lexical_match("gossiping about nothing"))
        self.assertTrue(lexical_match("Unicode punctuation—dating—still tokenizes."))

    def test_utf8_body_boundaries_are_exact(self) -> None:
        boundaries = [r for r in self.records if r["concept_id"].startswith("body-boundary-")]
        self.assertEqual(len(boundaries), 12)
        self.assertEqual(
            sorted({r["expected_utf8_bytes"] for r in boundaries}),
            [16_383, 16_384, 16_385],
        )
        for record in boundaries:
            self.assertEqual(len(record["text"].encode("utf-8")), record["expected_utf8_bytes"])

    def test_duplicates_reuse_protocol_identity_within_each_source(self) -> None:
        by_id = {record["id"]: record for record in self.records}
        duplicates = [record for record in self.records if record["duplicate_of"]]
        self.assertEqual(len(duplicates), 8)
        for duplicate in duplicates:
            original = by_id[duplicate["duplicate_of"]]
            self.assertEqual(duplicate["protocol_identity"], original["protocol_identity"])
            self.assertEqual(duplicate["text"], original["text"])

    def test_evaluation_is_reproducible_and_gate_fails_honestly(self) -> None:
        result = evaluate(self.records, self.manifest)
        held_out = result["metrics"]["held_out"]["overall"]
        self.assertEqual((held_out["tp"], held_out["fp"], held_out["tn"], held_out["fn"]), (32, 24, 34, 16))
        self.assertEqual(held_out["precision"], 0.571429)
        self.assertEqual(held_out["recall"], 0.666667)
        self.assertFalse(result["gate"]["metric_gate_passed"])
        self.assertFalse(result["gate"]["label_approval_passed"])

    def test_structural_duplicates_and_oversized_cases_are_filtered(self) -> None:
        result = evaluate(self.records, self.manifest)
        held_out = result["metrics"]["held_out"]["overall"]
        self.assertEqual(held_out["structurally_excluded"], 8)
        self.assertEqual(held_out["duplicates_excluded"], 4)
        self.assertEqual(held_out["oversized_excluded"], 2)

    def test_generator_rebuild_is_byte_identical(self) -> None:
        expected = (HERE / "corpus.jsonl").read_bytes()
        records = generate_corpus.build_records()
        rebuilt = "".join(
            json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
            for record in records
        ).encode("utf-8")
        self.assertEqual(rebuilt, expected)


if __name__ == "__main__":
    unittest.main()
