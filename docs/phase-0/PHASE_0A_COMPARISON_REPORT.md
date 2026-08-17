# Phase 0A source comparison report

Evidence date: **2026-08-17**
Gate status: **NOT PASSED — limited Nostr evidence only**

## Decision

The approved Nostr trial is technically reachable and inexpensive in this
bounded sample, but it did not produce evidence of useful relationship/gossip
signal. Jetstream was not contacted because the project has not supplied the
honest, already-published operator contact required by the approved source
review. The requested cross-source comparison is therefore incomplete and the
Phase 0A gate remains red.

This is a limitation decision, not a conclusion that either source is unusable.
No production Phase 1 source integration should start from this evidence.

## Scope and privacy controls

The reusable spike is
[`tools/phase0a/phase0a_compare.py`](../../tools/phase0a/phase0a_compare.py).
It uses one direct read-only WebSocket connection per selected endpoint, no
credentials, no publishing operation, no author contact, and no project-hosted
collector. The two Nostr relays are sampled concurrently and deduplicated in
memory by recalculated event ID.

The collector neither prints nor persists received bodies, event IDs, public
keys, tags, payloads, or matched terms. Its output contains aggregate counts,
distributions, timings, safe error categories, and resource measurements only.
Content and author hashes used for mechanical repeat/burst counters are
process-local and are discarded at exit.

Enforced bounds were:

- 60 seconds wall time and 60 seconds of replay;
- at most 300 event messages per source;
- Nostr subscription `limit` 100;
- 65,536 bytes per assembled Nostr WebSocket message before JSON parsing;
- 16,384 UTF-8 bytes per decoded body before classification;
- one connection per relay, one planned reconnect, and bounded backoff after an
  unexpected close.

This small evidence client processes each received message synchronously and
does not create an intake work queue. The approved source contract's 100-event
queue cap therefore had nothing to fill in this run; it remains a production
adapter requirement and still needs explicit overflow/backpressure tests.

The client validates Nostr envelope shape and recalculates the NIP-01 event ID.
It **does not verify BIP-340/Schnorr signatures**: no maintained verifier is
available in the bundled runtime. Accordingly, the evidence calls these events
“recomputed-ID valid,” never cryptographically verified, and reports the
signature-verified count as zero. Production signature validation remains a
hard requirement.

The aggregate-only evidence is
[`live-nostr-2026-08-17.json`](../../tools/phase0a/evidence/live-nostr-2026-08-17.json).
An earlier five-second connectivity smoke result is retained separately as
[`smoke-nostr-2026-08-17.json`](../../tools/phase0a/evidence/smoke-nostr-2026-08-17.json).

## Live Nostr result

The primary run lasted 60.016 seconds. A missing counter in the JSON means zero.

| Measure | `relay.damus.io` | `nos.lol` | Combined/deduplicated |
|---|---:|---:|---:|
| Data messages received | 148 | 88 | 236 deliveries |
| Event messages | 129 | 86 | 215 deliveries |
| Shape-valid and recomputed-ID-valid | 129 | 86 | 113 unique |
| Standalone | 80 deliveries | 85 deliveries | 82 unique |
| Addressed/conversational | 49 | 1 | 31 unique by subtraction |
| Oversized envelopes | 17 | 0 | 17 deliveries |
| Oversized decoded bodies | 0 | 0 | 0 |
| Event rate while connected | 2.259/s | 1.440/s | 1.883 unique valid/s wall-clock |
| Inbound application bytes | 2,144,007 | 54,527 | 2,198,534 |
| Approx. inbound rate | 37,552 B/s | 913 B/s | 36,632 B/s wall-clock |

The application-byte estimate is measured after TLS decryption and includes
HTTP upgrade and WebSocket framing; it excludes TCP, IP, and TLS framing. The
Damus total is dominated by 17 messages rejected at the 64 KiB assembled-message
boundary.

Across 215 recomputed-ID-valid deliveries, local deduplication removed 102
repeat deliveries (47.4%). Twenty-seven of 113 unique valid events appeared on
both relays (23.9% cross-relay overlap). Across the standalone subset, 83 of 165
deliveries were repeats (50.3%), and 27 of 82 unique standalone events appeared
on both relays (32.9%). The larger delivery-repeat count includes replayed
events after reconnect as well as cross-relay duplication.

### Body size, signal, and conservative noise

The following figures cover the 82 unique standalone notes after deduplication:

| Measure | Result |
|---|---:|
| Mean body | 247.4 bytes |
| Median body | 195 bytes |
| 90th / 95th percentile | 489 / 541 bytes |
| Maximum body | 861 bytes |
| Mean assembled envelope | 666.8 bytes |
| Maximum accepted assembled envelope | 1,232 bytes |
| High-confidence relationship/gossip lexical yield | 0 / 82 (0%) |
| Broad interpersonal lexical yield | 0 / 82 (0%) |
| Conservatively mechanically flagged | 18 / 82 (22.0%) |

The 18 mechanically flagged events comprised 12 exact-body repeats across
distinct event IDs, five publisher bursts, and one symbol-heavy body. These are
deliberately conservative structural indicators, not a claim that an event is
spam, abusive, false, or unwanted. The zero lexical yield is also not a
population estimate; it says only that this short unlabelled sample supplies no
positive usefulness evidence for the intended topic.

### Reconnect, STOP, and resource cost

Both relays completed the single planned disconnect and reconnect: two
successful connections and one successful planned reconnection per relay.
Each later produced one content-free `closed` error category. Damus also had
one later rejected handshake; the bounded client did not bypass the rejection
or add parallel connections. The run ended before persistent recovery from
those late events could be established.

STOP closed both workers in approximately 16 ms, with no stop timeout. Peak
traced Python heap was 363,556 bytes, CPU time was 0.219 seconds, and two worker
threads were used. Traced heap excludes the Python interpreter, TLS/native
allocations, and operating-system buffers, so it is a lower-bound comparison
measure rather than whole-process RSS.

Measured class-source complexity was 217 nonblank lines for the shared bounded
WebSocket client, 74 for the Nostr adapter, and 66 for the Jetstream adapter.
These counts exclude classifiers and tests. The Jetstream figure is an
implementation estimate only because no live Jetstream handshake or event was
allowed in this run.

## Jetstream evidence gap

The approved source review requires Cyber Space Radio to publish an honest
project operator contact before a Jetstream live trial. No such contact was
provided, and Bluesky's own support address cannot stand in for the project's.
The collector now fails closed when `jetstream` or `all` is selected without an
explicit `--operator-contact`; the value is exposed in the handshake but is not
included in aggregate output.

Consequently, Jetstream has **no live received/valid/standalone counts, size
distribution, bandwidth, event rate, lexical yield, noise count, reconnect
result, or resource result** in this evidence package. Static fixture coverage
does exercise the current v2 commit shape and structural exclusions for replies,
mentions, and quote posts, but fixtures cannot substitute for the live
comparison.

## Gate assessment and required closure

Phase 0A does not pass because:

1. the approved Nostr-versus-Jetstream live comparison is incomplete;
2. the Nostr-only sample produced zero intended-topic lexical hits, so it does
   not demonstrate a useful signal floor; and
3. Nostr signatures were not independently verified.

To close the gate:

1. publish and supply an honest project operator contact, then run the same
   bounded aggregate-only comparison with `--sources all`;
2. add a maintained BIP-340/Schnorr verifier and make signature failure a
   pre-classification rejection, with valid, invalid, and boundary fixtures;
3. compare source usefulness on the pre-declared labelled corpus rather than
   interpreting this unlabelled lexical sample as precision/recall evidence;
4. repeat the unexpected-close test long enough to establish bounded recovery,
   while preserving the one-connection-per-source and immediate-STOP rules; and
5. keep every source disabled after testing until the complete Phase 0A and 0B
   gates pass.

## Verification and primary references

The focused suite has 12 passing fixtures covering event-ID recalculation,
standalone structural exclusions, signature non-claims, the exact
16,383/16,384/16,385-byte body boundary including a multibyte case, the 64 KiB
envelope boundary, deduplication without identifier output, aggregate privacy,
masked client frames, Jetstream exclusions, and fail-closed operator-contact
handling. Both Python modules also compile successfully.

Protocol and endpoint interpretation uses primary sources:

- [Nostr NIP-01 basic protocol and event serialization](https://github.com/nostr-protocol/nips/blob/master/01.md)
- [Nostr NIP-10 reply and thread tags](https://github.com/nostr-protocol/nips/blob/master/10.md)
- [Jetstream v2 client specification](https://github.com/bluesky-social/jetstream/blob/main/specs/client.md)
- [Jetstream v2 subscription Lexicon](https://github.com/bluesky-social/jetstream/blob/main/lexicons/network/bsky/jetstream/subscribeEvents.json)
- [AT Protocol post Lexicon](https://github.com/bluesky-social/atproto/blob/main/lexicons/app/bsky/feed/post.json)
- [Bluesky developer guidelines](https://bsky.network/docs/developer-guidelines/)
