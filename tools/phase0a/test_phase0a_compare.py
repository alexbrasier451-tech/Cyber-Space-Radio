from __future__ import annotations

import csv
import hashlib
import json
import unittest
from pathlib import Path

from coincurve import PrivateKey

from phase0a_compare import (
    BODY_LIMIT_BYTES,
    NOSTR_ENVELOPE_LIMIT_BYTES,
    ContentMetrics,
    NostrAdapter,
    NostrCombined,
    ReceivedMessage,
    SourceStats,
    WebSocketConnection,
    bounded_json,
    classify_jetstream_event,
    classify_nostr_event,
    obvious_content_noise_flags,
    relationship_topic_match,
    run_comparison,
    verify_schnorr_signature,
)


def nostr_event(content: str = "a public standalone note", tags=None) -> dict:
    tags = [] if tags is None else tags
    private_key = PrivateKey(bytes.fromhex("01" * 32))
    event = {
        "pubkey": private_key.public_key_xonly.format().hex(),
        "created_at": 1_700_000_000,
        "kind": 1,
        "tags": tags,
        "content": content,
    }
    canonical = json.dumps(
        [
            0,
            event["pubkey"],
            event["created_at"],
            event["kind"],
            event["tags"],
            event["content"],
        ],
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    event["id"] = hashlib.sha256(canonical).hexdigest()
    event["sig"] = private_key.sign_schnorr(
        bytes.fromhex(event["id"]), aux_randomness=bytes(32)
    ).hex()
    return event


def jetstream_post(record_overrides=None) -> dict:
    record = {
        "$type": "app.bsky.feed.post",
        "text": "a public standalone post",
        "createdAt": "2026-08-17T12:00:00Z",
    }
    record.update(record_overrides or {})
    return {
        "$type": "network.bsky.jetstream.subscribeEvents#commit",
        "seq": 123,
        "did": "did:plc:testfixture",
        "time": "2026-08-17T12:00:01Z",
        "rev": "3fixture",
        "operation": "create",
        "collection": "app.bsky.feed.post",
        "rkey": "fixture",
        "record": record,
        "cid": "fixture-cid",
    }


def jetstream_message(record_overrides=None) -> dict:
    return {"$type": "message", "payload": jetstream_post(record_overrides)}


class ClassificationTests(unittest.TestCase):
    def test_nostr_recalculates_id_and_accepts_standalone(self) -> None:
        result = classify_nostr_event(nostr_event())
        self.assertTrue(result.valid_shape)
        self.assertTrue(result.valid_event_id)
        self.assertTrue(result.valid_signature)
        self.assertTrue(result.standalone)

    def test_nostr_rejects_addressed_tags_structurally(self) -> None:
        for marker in ("e", "p", "q"):
            with self.subTest(marker=marker):
                result = classify_nostr_event(nostr_event(tags=[[marker, "fixture"]]))
                self.assertTrue(result.valid_event_id)
                self.assertTrue(result.valid_signature)
                self.assertFalse(result.standalone)

    def test_nostr_rejects_invalid_signature_before_classification(self) -> None:
        event = nostr_event()
        event["sig"] = "00" * 64
        result = classify_nostr_event(event)
        self.assertTrue(result.valid_event_id)
        self.assertTrue(result.valid_shape)
        self.assertFalse(result.valid_signature)
        self.assertFalse(result.standalone)

        combined = NostrCombined()
        adapter = NostrAdapter("fixture", "wss://example.test", combined)
        stats = SourceStats("fixture", "nostr")
        payload = json.dumps(["EVENT", "fixture-sub", event]).encode("utf-8")
        adapter.handle_message(
            ReceivedMessage(payload, 1, False, len(payload)), stats, 0.1
        )
        self.assertEqual(stats.counters["invalid_schnorr_signature"], 1)
        self.assertEqual(stats.counters["standalone_deliveries"], 0)
        self.assertEqual(combined.aggregate()["unique_standalone"], 0)

    def test_nostr_invalid_id_is_rejected(self) -> None:
        event = nostr_event()
        event["id"] = "00" * 32
        result = classify_nostr_event(event)
        self.assertFalse(result.valid_event_id)
        self.assertFalse(result.valid_signature)

    def test_authoritative_bip340_verification_vectors(self) -> None:
        vector_path = Path(__file__).parent / "testdata" / "bip340_test_vectors.csv"
        with vector_path.open(newline="", encoding="utf-8") as handle:
            vectors = list(csv.DictReader(handle))
        self.assertEqual(len(vectors), 19)
        for vector in vectors:
            with self.subTest(index=vector["index"], comment=vector["comment"]):
                actual = verify_schnorr_signature(
                    bytes.fromhex(vector["public key"]),
                    bytes.fromhex(vector["signature"]),
                    bytes.fromhex(vector["message"]),
                )
                self.assertEqual(actual, vector["verification result"] == "TRUE")

    def test_body_limit_uses_utf8_bytes(self) -> None:
        for byte_count in (BODY_LIMIT_BYTES - 1, BODY_LIMIT_BYTES):
            with self.subTest(byte_count=byte_count):
                accepted = classify_nostr_event(nostr_event("x" * byte_count))
                self.assertFalse(accepted.body_oversized)
                self.assertTrue(accepted.valid_event_id)

        rejected = classify_nostr_event(nostr_event("x" * (BODY_LIMIT_BYTES + 1)))
        self.assertTrue(rejected.body_oversized)

        multibyte_accepted = classify_nostr_event(
            nostr_event("\u00e9" * (BODY_LIMIT_BYTES // 2))
        )
        multibyte_rejected = classify_nostr_event(
            nostr_event("\u00e9" * (BODY_LIMIT_BYTES // 2) + "x")
        )
        self.assertFalse(multibyte_accepted.body_oversized)
        self.assertTrue(multibyte_accepted.valid_event_id)
        self.assertTrue(multibyte_rejected.body_oversized)

    def test_jetstream_accepts_standalone_post(self) -> None:
        result = classify_jetstream_event(jetstream_post())
        self.assertTrue(result.valid_shape)
        self.assertTrue(result.standalone)

    def test_jetstream_accepts_xrpc_message_envelope(self) -> None:
        result = classify_jetstream_event(jetstream_message())
        self.assertTrue(result.valid_shape)
        self.assertTrue(result.standalone)

    def test_jetstream_rejects_invalid_xrpc_message_envelope(self) -> None:
        result = classify_jetstream_event({"$type": "message", "payload": None})
        self.assertFalse(result.valid_shape)
        self.assertEqual(result.reason, "xrpc_envelope")

    def test_jetstream_rejects_reply_mention_and_quote(self) -> None:
        cases = [
            {"reply": {"root": {}, "parent": {}}},
            {
                "facets": [
                    {
                        "features": [
                            {"$type": "app.bsky.richtext.facet#mention", "did": "did:x"}
                        ]
                    }
                ]
            },
            {"embed": {"$type": "app.bsky.embed.record", "record": {}}},
            {
                "embed": {
                    "$type": "app.bsky.embed.recordWithMedia",
                    "record": {},
                }
            },
        ]
        for overrides in cases:
            with self.subTest(overrides=overrides):
                result = classify_jetstream_event(jetstream_message(overrides))
                self.assertTrue(result.valid_shape)
                self.assertFalse(result.standalone)


class BoundsAndPrivacyTests(unittest.TestCase):
    def test_relationship_matcher_v2_accepts_contextual_human_phrasing(self) -> None:
        examples = (
            "My partner and I agreed to listen to each other.",
            "I was dumped by someone I trusted.",
            "He asked me out for dinner and I said yes.",
            "A friend says the pair kissed after everyone left.",
            "Their romance began during a delayed train journey.",
            "He is hiding texts from the person he lives with.",
            "Fresh gossip says two friends are secretly together.",
        )
        for example in examples:
            with self.subTest(example=example):
                self.assertTrue(relationship_topic_match(example))

    def test_relationship_matcher_v2_rejects_non_human_word_senses(self) -> None:
        examples = (
            "The relationship between temperature and pressure is linear.",
            "Radiometric dating can estimate the age of rocks.",
            "The radio drama uses footsteps to create distance.",
            "Please crush the empty cans before recycling.",
            "The player was cheating during the chess match.",
            "A gossip protocol shares membership between cluster nodes.",
            "The asteroid breakup produced several fragments.",
            "The romance novel won a publishing award.",
        )
        for example in examples:
            with self.subTest(example=example):
                self.assertFalse(relationship_topic_match(example))

    def test_relationship_matcher_v2_suppresses_obvious_junk_first(self) -> None:
        junk = "dating dating dating dating dating dating dating dating dating dating"
        self.assertEqual(obvious_content_noise_flags(junk), {"mechanical_token_repeat"})
        self.assertFalse(relationship_topic_match(junk))

        metrics = ContentMetrics()
        metrics.observe(junk, author_key="fixture", event_time=1.0, envelope_size=90)
        aggregate = metrics.aggregate()
        self.assertEqual(
            aggregate["lexical_yield_counts"][
                "relationship_or_gossip_high_confidence"
            ],
            0,
        )
        self.assertEqual(
            aggregate["conservative_structural_noise"]["events_flagged"], 1
        )

    def test_jetstream_fails_closed_without_published_operator_contact(self) -> None:
        with self.assertRaisesRegex(ValueError, "operator-contact"):
            run_comparison(1.0, None, "jetstream", None)

    def test_json_envelope_boundary(self) -> None:
        base = b'{"ok":true}'
        accepted = base + b" " * (NOSTR_ENVELOPE_LIMIT_BYTES - len(base))
        rejected = accepted + b" "
        self.assertEqual(bounded_json(accepted, NOSTR_ENVELOPE_LIMIT_BYTES)[1], None)
        self.assertEqual(
            bounded_json(rejected, NOSTR_ENVELOPE_LIMIT_BYTES)[1], "oversized"
        )

    def test_aggregate_metrics_do_not_contain_content_or_keys(self) -> None:
        content = "SENTINEL_PRIVATE_BODY gossip"
        key = "SENTINEL_PUBLIC_KEY"
        metrics = ContentMetrics()
        metrics.observe(content, author_key=key, event_time=1.0, envelope_size=200)
        output = json.dumps(metrics.aggregate())
        self.assertNotIn(content, output)
        self.assertNotIn(key, output)
        self.assertNotIn("SENTINEL_PRIVATE_BODY", output)

    def test_combined_nostr_overlap_counts_without_output_ids(self) -> None:
        event = nostr_event("SENTINEL_BODY")
        combined = NostrCombined()
        for source in ("a", "b"):
            combined.observe(
                source_id=source,
                event_id=event["id"],
                standalone=True,
                content=event["content"],
                author_key=event["pubkey"],
                created_at=event["created_at"],
                envelope_size=250,
            )
        aggregate = combined.aggregate()
        self.assertEqual(aggregate["unique_standalone"], 1)
        self.assertEqual(aggregate["overlap_standalone"], 1)
        output = json.dumps(aggregate)
        self.assertNotIn(event["id"], output)
        self.assertNotIn(event["content"], output)

    def test_client_frame_send_masks_payload(self) -> None:
        class FakeSocket:
            def __init__(self) -> None:
                self.sent = b""

            def sendall(self, value: bytes) -> None:
                self.sent += value

        connection = WebSocketConnection(
            "wss://example.test",
            stop_event=__import__("threading").Event(),
            max_message_bytes=64,
        )
        fake = FakeSocket()
        connection.sock = fake  # type: ignore[assignment]
        connection.send_text("fixture")
        self.assertTrue(fake.sent[1] & 0x80)
        length = fake.sent[1] & 0x7F
        mask = fake.sent[2:6]
        payload = fake.sent[6 : 6 + length]
        decoded = bytes(value ^ mask[index % 4] for index, value in enumerate(payload))
        self.assertEqual(decoded, b"fixture")


if __name__ == "__main__":
    unittest.main()
