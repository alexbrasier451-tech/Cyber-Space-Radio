# Phase 0A Nostr message-size sample

Sample date: **2026-08-17**

Purpose: **choose a bounded Phase 1 message-body limit**

Sources: **`wss://relay.damus.io` and `wss://nos.lol`**
Message bodies retained, printed, or written: **no**

## Outcome

Adopt a maximum accepted message-body size of **16,384 UTF-8 bytes**. Measure
the decoded Nostr event `content` field before normalization, waterfall display,
spam classification, topic matching, or persistence.

An event over the limit is classified as `Oversized`, increments a separate
non-identifying aggregate counter, and is discarded. It is not labelled spam
and never enters the waterfall, volatile Junk drawer, matcher, notification
path, durable store, logs, exports, backups, crash reports, or external viewer.

The limit is deliberately above every body observed in this sample. It also
leaves room for longer personal narratives while remaining far below the
reviewed relays' published maxima.

After reviewing the difference between body size and transport size, the owner
also accepted a **65,536 UTF-8 byte maximum for the complete assembled incoming
Nostr event-envelope message**, including wrapper, signature, fields, and tags.
This is a defensive engineering boundary rather than a measurement result: the
sample did not retain per-envelope sizes. A larger envelope contributes only an
aggregate `Oversized: envelope` reason and is rejected before JSON event-field
parsing where the platform permits. WebSocket fragmentation does not reset the
limit.

## Method

Two sequential, aggregate-only observations were made with one direct read-only
WebSocket connection to each approved Nostr relay:

| Run | Duration | Initial replay | Maximum intake |
|---|---:|---:|---:|
| A | 60 seconds | 60 seconds | 300 event messages per relay |
| B | 300 seconds | 60 seconds | 1,500 event messages per relay, equivalent to the approved 300/minute ceiling |

For both runs, the sampler:

- requested public kind-1 events only;
- recalculated and checked each Nostr event ID from its canonical serialized
  fields;
- rejected events carrying `e`, `p`, or `q` tags from the standalone set;
- deduplicated relay overlap by event ID within each run;
- measured `content` as UTF-8 bytes and Unicode code points in memory;
- applied a high-confidence English relationship/gossip vocabulary and a
  separately reported broader interpersonal vocabulary; and
- emitted aggregate counts and size distributions only.

The sampler did not perform independent Schnorr signature verification. That is
still required of the production adapter. Event IDs, bodies, public keys, tags,
and relay payloads existed only in process memory and were discarded when each
sampler process exited.

## Relay observations

| Run | Relay | Event messages | Event-ID valid | Structurally standalone |
|---|---|---:|---:|---:|
| A | Damus | 113 | 112 | 80 |
| A | nos.lol | 91 | 90 | 90 |
| B | Damus | 213 | 213 | 135 |
| B | nos.lol | 160 | 160 | 159 |

Run A contained 152 unique event-ID-valid events, 120 unique standalone events,
and 50 events observed through both relays. Run B contained 299 unique
event-ID-valid events, 220 unique standalone events, and 74 events observed
through both relays.

The combined summary therefore covers 340 within-run-deduplicated standalone
observations. Cross-run event IDs were intentionally not retained, so the
combined figure should be treated as an approximate sample count rather than a
permanent corpus identifier set.

## Message-size results

| Measure | Run A | Run B | Combined interpretation |
|---|---:|---:|---|
| Standalone count | 120 | 220 | 340 within-run-deduplicated observations |
| Mean UTF-8 body | 322.3 B | 283.2 B | approximately 297 B, weighted from rounded run means |
| Median UTF-8 body | 195 B | 195 B | 195 B in both runs |
| 75th percentile | 393 B | 295 B | below 400 B in both runs |
| 90th percentile | 629 B | 593 B | below 630 B in both runs |
| 95th percentile | 751 B | 791 B | below 800 B in both runs |
| 99th percentile | 1,471 B | 1,211 B | below 1.5 KiB in both runs |
| Maximum | 4,585 B | 2,144 B | 4,585 B observed maximum |
| Over 1 KiB | 2 | 3 | 5, approximately 1.5% |
| Over 4 KiB | 1 | 0 | 1, approximately 0.3% |
| Over 8 KiB | 0 | 0 | none |
| Over 16 KiB | 0 | 0 | none |

A 4 KiB limit would already have rejected one otherwise structurally valid
observation. An 8 KiB limit accepted everything observed. The selected 16 KiB
limit provides a further safety margin for longer legitimate narratives without
accepting the relays' much larger maximum bodies.

## Relationship and gossip subset

The high-confidence vocabulary included explicit terms such as relationship,
dating, boyfriend/girlfriend, husband/wife, breakup, divorce, marriage, crush,
cheating, affair, gossip, rumour, drama, and situationship. The broader
interpersonal vocabulary additionally included love, romance, friendship,
family, parents, siblings, children, and couples.

- Run A found one high-confidence `gossip` hit at 666 UTF-8 bytes.
- Run B found no high-confidence hit.
- Run B found four broader interpersonal hits averaging 579 bytes, with a
  745-byte maximum.
- The five specifically identified examples across the observations averaged
  approximately 596 bytes and all remained below 1 KiB.

This subset is too small and too English-specific to establish a reliable
relationship/gossip population average. It does show no evidence that the
proposed focus requires unusually large messages. Before matcher acceptance,
the project still needs a labelled relationship/gossip corpus containing real
or synthetic long-form, multilingual, slang, false-positive, and adversarial
cases.

## Limits of this evidence

- This was a short time slice from two relays, not a representative census of
  Nostr.
- The keyword subsets measure lexical indicators, not the author's actual topic
  or intent.
- No profile enrichment, language detection, semantic model, historical crawl,
  or content retention was used.
- The sample does not compare usefulness with Jetstream and does not satisfy the
  complete Phase 0A cross-source suitability gate.
- The 16 KiB limit must be re-evaluated if a later source family or labelled
  relationship/gossip corpus shows a legitimate need for larger bodies.
