# Phase 0A source comparison report

Evidence dates: **2026-08-17 to 2026-08-18**

Source/transport sub-gate: **PASSED**

Matcher v2 metric sub-gate: **PASSED**

Overall Phase 0A gate: **PENDING PROJECT-OWNER LABEL APPROVAL**

## Decision

The bounded comparison now demonstrates that both approved source families can
deliver standalone public shouts to the local-only client with the declared
privacy and resource bounds:

- Nostr event IDs and BIP-340 signatures are verified before classification;
- Jetstream v2 messages are decoded through their XRPC JSON envelope;
- received message bodies, identifiers, account keys, tags, and records are
  never printed or persisted; and
- STOP closes all workers and disables retries.

The source/transport sub-gate therefore passes. Frozen Matcher v2 subsequently
passed its fresh held-out metric gate at 87.50% precision and 100% recall on
both source structures. This still does **not** authorize routine listening or
Phase 1 implementation: its synthetic labels remain provisionally owned. The
overall Phase 0A gate waits for explicit project-owner approval or correction
of the frozen label sheet.

All reviewed sources remain `approved-disabled` outside explicitly authorized,
bounded evidence runs.

## Scope and privacy controls

The comparison client is
[`tools/phase0a/phase0a_compare.py`](../../tools/phase0a/phase0a_compare.py).
It opens one direct, read-only WebSocket connection per selected endpoint, uses
no credentials, publishes nothing, contacts no message author, and sends no
data to project-operated infrastructure. The public project-contact URI is
included only in the Jetstream upgrade header and is not written to evidence.

The client outputs aggregate counts, byte distributions, timings, safe error
categories, and resource measurements. Process-local hashes used for Nostr
deduplication and conservative repeat/burst counts are discarded at exit.

Enforced bounds were:

- 60 seconds wall time and at most 60 seconds of replay;
- at most 300 event messages per source;
- Nostr subscription `limit` 100;
- 65,536 bytes per assembled Nostr message before JSON parsing;
- 16,384 UTF-8 bytes per decoded message body;
- one connection per source, bounded reconnect backoff, and immediate STOP;
  and
- no intake work queue in this synchronous evidence client. The production
  adapter still requires the approved 100-event queue and overflow tests.

The primary aggregate is
[`live-all-2026-08-17.json`](../../tools/phase0a/evidence/live-all-2026-08-17.json).
The first failed end-to-end attempt is retained as
[`live-all-envelope-failure-2026-08-17.json`](../../tools/phase0a/evidence/live-all-envelope-failure-2026-08-17.json),
and the independent fresh Jetstream case is
[`live-jetstream-fresh-2026-08-17.json`](../../tools/phase0a/evidence/live-jetstream-fresh-2026-08-17.json).

## Diagnostic repair and end-to-end rerun

The first authorized all-source run connected successfully but classified all
300 Jetstream deliveries as `not_commit`. A one-second diagnostic probe recorded
only field names, runtime types, and protocol discriminators. It recorded no
field values other than the public protocol discriminator strings, no text, and
no identifiers.

The semantic checkpoints were:

| Checkpoint | Expected | Observed | Verdict |
|---|---|---|---|
| WebSocket intake | JSON text messages | 300 bounded JSON messages | Correct |
| JSON parse | Dictionary envelope | Dictionary with `$type` and `payload` | Correct |
| XRPC normalization | Commit payload supplied to classifier | Wrapper supplied directly | First wrong |
| Commit classification | `#commit` discriminator in payload | Outer discriminator was `message` | Downstream failure |

Jetstream v2 framed every observed event as an outer
`{"$type":"message","payload":...}` object; the nested payload carried the
`network.bsky.jetstream.subscribeEvents#commit` discriminator and commit fields.
The classifier had implemented the nested Lexicon object but omitted the XRPC
message-envelope normalization.

The narrow repair unwraps only an outer `$type` equal to `message`, requires a
dictionary payload, then applies the existing commit-shape and standalone rules.
A missing or non-object payload fails closed as `xrpc_envelope`. Direct decoded
commit fixtures remain supported.

The original 60-second all-source invocation was rerun after the repair and
completed successfully. Fifteen focused adapter/privacy tests, eight corpus
tests, the complete root suite, and an independent one-second live Jetstream
case also pass. The fresh case again accepted 103 standalone posts from the
first 300 bounded deliveries without recording content or identifiers.

## Primary all-source result

The repaired primary run lasted 60.031 seconds. A missing counter means zero.

### Nostr

| Measure | `relay.damus.io` | `nos.lol` | Combined/deduplicated |
|---|---:|---:|---:|
| Event messages | 105 | 110 | 215 deliveries |
| Recomputed-ID valid | 105 | 110 | 97 unique |
| BIP-340 signature valid | 105 | 110 | 215 deliveries |
| Standalone | 68 deliveries | 107 deliveries | 72 unique |
| Addressed/conversational | 37 | 3 | 25 unique by subtraction |
| Cross-relay overlap, valid | - | - | 28 unique events |
| Cross-relay overlap, standalone | - | - | 27 unique events |
| High-confidence relationship/gossip yield | 0 | 0 | 1 unique |
| Broad interpersonal yield | 0 | 0 | 2 unique |

The combined standalone bodies averaged 251.1 bytes, with a 195-byte median
and 1,387-byte maximum. Twelve of 72 unique standalone events were flagged by
conservative mechanical indicators: six exact-body repeats, five publisher
bursts, and one URL-heavy body. These flags are not content judgments.

Both Nostr endpoints completed the planned disconnect/reconnect. `nos.lol`
also encountered one content-free TLS error and recovered through the bounded
retry path. All 215 recomputed-ID-valid deliveries had valid BIP-340 signatures.

### Jetstream v2

| Measure | Result |
|---|---:|
| Event messages | 300 |
| Valid post events | 269 |
| Standalone unique | 103 |
| Addressed/conversational | 166 |
| Invalid/non-post | 31 |
| Replies rejected | 143 |
| Recipient mentions rejected | 6 |
| Quote posts rejected | 17 |
| Empty posts rejected | 14 |
| Other shape rejections | 17 |
| High-confidence relationship/gossip yield | 2 |
| Broad interpersonal yield | 5 |
| Mean / median / maximum body | 135.7 / 110 / 588 bytes |
| Mean / maximum accepted envelope | 1,019.8 / 3,096 bytes |
| Inbound application bytes | 276,796 |

Jetstream reached the conservative 300-event intake cap in 0.391 seconds at an
observed connected-time rate of about 767 events/second. It therefore stopped
before the planned five-second reconnect. This is a consequence of the local
cap, not a reconnect failure. The shared reconnect state machine is covered by
the Nostr live results; a production Jetstream adapter still needs explicit
backpressure, sampling, and reconnect testing without weakening the intake
ceiling.

Jetstream supplies operator-decoded records and the evidence client does not
independently verify repository signatures. That trust distinction remains a
source attribute and must be visible in product/source documentation.

### STOP and resource cost

All three workers exited. Reported STOP close latency was 0 ms for each source.
Peak traced Python heap was 510,905 bytes, CPU time was 0.234 seconds, and three
worker threads were used. Traced heap excludes the interpreter, TLS/native
allocations, and operating-system buffers, so it is a lower-bound comparison
measure rather than whole-process RSS.

## Signature evidence

Nostr validation uses pinned `coincurve` 21.0.0 backed by `libsecp256k1`.
Signature failure occurs before standalone classification or aggregation. All
19 official BIP-340 vectors matched their expected result. The earlier bounded
signature probe verified 178 of 178 recomputed-ID-valid deliveries, and this
all-source run verified 215 of 215.

The reproducible metadata is in
[`signature-verification-2026-08-17.json`](../../tools/phase0a/evidence/signature-verification-2026-08-17.json).
Historical evidence files that report signature verification unavailable remain
unchanged as truthful records of those earlier runs.

## Matcher evidence and remaining gate

The 286-record Matcher v2 corpus applies the repaired XRPC envelope path for
Jetstream and the verified event path for Nostr. Its newly authored held-out
split was evaluated only after the matcher freeze:

| Metric | Required | Nostr | Jetstream | Overall | Result |
|---|---:|---:|---:|---:|---|
| Precision | at least 85% | 87.50% | 87.50% | 87.50% | Pass |
| Recall | at least 60% | 100.00% | 100.00% | 100.00% | Pass |
| Explicit owner label approval | Required | Outstanding | Outstanding | Outstanding | Pending |

The first held-out result preserves five non-personal false-positive concepts
per source and has no false negatives. The matcher was not changed after that
result. Full method, hashes, and the approval statement are in the
[Matcher v2 report](PHASE_0A_MATCHER_V2_REPORT.md).

The overall Phase 0A gate therefore remains **PENDING OWNER LABEL APPROVAL**.
Durable topic-match persistence and reporting stay disabled. Ephemeral
discovery may continue only within the already approved bounded
prototype/evidence rules.

To close Phase 0A, the project owner must approve the frozen label sheet
unchanged. A correction invalidates the evaluation and requires a new matcher
or corpus version and a new held-out result. Source limits, contact exposure,
aggregate privacy, signature checks, immediate STOP, and approved-disabled
defaults remain mandatory.

Phase 0B independently remains blocked on physical Android lifecycle, battery,
notification, STOP, and packaging evidence.

## Verification and primary references

Current local verification includes:

- 18 passing source-adapter, signature, matcher, boundary, privacy, and
  envelope tests;
- 8 passing historical corpus tests and 7 passing Matcher v2 corpus tests;
- 7 passing prototype/record-management tests;
- all 19 official BIP-340 vectors matching expectations;
- successful repaired 60-second all-source and fresh one-second Jetstream live
  runs; and
- no raw content, identifiers, public keys, tags, records, signatures, or
  operator-contact value in aggregate evidence.

Protocol and endpoint interpretation uses primary sources:

- [Nostr NIP-01 basic protocol and event serialization](https://github.com/nostr-protocol/nips/blob/master/01.md)
- [Nostr NIP-10 reply and thread tags](https://github.com/nostr-protocol/nips/blob/master/10.md)
- [Jetstream v2 client specification](https://github.com/bluesky-social/jetstream/blob/main/specs/client.md)
- [Jetstream v2 subscription Lexicon](https://github.com/bluesky-social/jetstream/blob/main/lexicons/network/bsky/jetstream/subscribeEvents.json)
- [AT Protocol post Lexicon](https://github.com/bluesky-social/atproto/blob/main/lexicons/app/bsky/feed/post.json)
- [Bluesky developer guidelines](https://bsky.network/docs/developer-guidelines/)
