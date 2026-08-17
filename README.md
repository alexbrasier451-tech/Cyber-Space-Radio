# Cyber Space Radio

**Public-source listening console**

Project operator contact: [`cyberspaceradio@proton.me`](CONTACT.md).
Do not send listened-to messages, station data, or credentials to this address.

The Phase 0 definition and evidence package is indexed at
[`docs/phase-0/README.md`](docs/phase-0/README.md). Do not create the proposed
Harken production fork. The Phase 0B review recommends a greenfield .NET 10
MAUI foundation for the next cross-platform probe, but physical Android and
packaging evidence is still missing, so Phase 1 is blocked. This repository's
scripts remain a local requirements prototype.

The approved first product use case is narrower than this RSS prototype:
listen read-only to explicitly approved public relay/event streams for
standalone messages that are not replies, direct messages, group messages, or
named-recipient messages. See
[`ADR 0003`](docs/adr/0003-standalone-public-relay-messages.md). RSS/Atom
remains useful for fixtures and later adapters, but it is not the defining
signal surface.

The selected operating model is hybrid: a bounded in-memory waterfall exposes
recent standalone shouts during discovery, while topic-matched shouts are
persisted automatically and one valid preview may be persisted only through an
explicit local `Keep`. Other unmatched previews disappear on expiry, restart,
or STOP LISTENING.

First run asks what the operator wants to hear, offering editable starter-topic
cards—including relationships, dating, gossip, drama, friendship, and family—
plus manual topic creation and a `Skip and explore` route. A skippable local
tutorial explains alternative phrasings, exclusions, breadth, and previewing;
choosing or editing a topic does not start listening or send it anywhere.
Signals from every topic share one local inbox with topic/source/state filters.
A shout matching several topics appears once with all matching topic labels,
not as duplicated messages or notifications.
Each unlocked session opens that inbox at `All topics`, newest first. Filter and
scroll state is memory-only for the session and clears on lock, STOP, restart,
or reset.
A signal is marked `Reviewed` only after its unlocked local inspector opens;
`Mark as new` reverses that state without affecting notification history,
matching, Keep, or expiry.
An explicit `Mark visible as reviewed` action previews the exact filtered count
and updates that snapshot only, leaving later arrivals New.
Manual Keep and each keep-enabled matching topic independently protect that one
signal from expiry. Removing one reason preserves the others; removing the last
after confirmation starts a new seven-day expiry.
Deleting a topic similarly preserves a signal when another topic or manual Keep
still justifies it, and previews resulting ordinary and protected deletions
before removing orphaned records.

An aggregate-only live Nostr sample supports a 16,384-byte UTF-8 message-body
ceiling for the future product. Larger bodies are discarded under a separate
non-identifying `Oversized` count before spam handling, display, matching, or
persistence. Complete assembled incoming Nostr event messages are separately
capped at 65,536 UTF-8 bytes, regardless of WebSocket fragmentation, to bound
wrapper and tag overhead before event-field parsing. See the
[`Phase 0A Nostr size report`](docs/phase-0/PHASE_0A_NOSTR_SIZE_SAMPLE.md).

A repaired bounded all-source comparison now verifies Nostr BIP-340 signatures
and correctly decodes Jetstream v2's XRPC message envelope. The primary run
observed 72 unique standalone Nostr shouts and 103 standalone Jetstream posts;
all 215 valid-ID Nostr deliveries had valid signatures. Jetstream reached the
conservative 300-event cap in under 0.4 seconds, demonstrating why the future
adapter needs explicit sampling and backpressure. See the
[`Phase 0A comparison report`](docs/phase-0/PHASE_0A_COMPARISON_REPORT.md).

The source/transport sub-gate passes, but the frozen 220-record synthetic
relationship/gossip corpus still fails the 85% precision gate at 57.14%
(recall 66.67%). Durable topic matching remains disabled. See the
[`Phase 0A matcher report`](docs/phase-0/PHASE_0A_MATCHER_REPORT.md).

For the future product, ordinary topic-matched records keep the full public
message text in an encrypted local store for seven days, together with minimal
source and match evidence. Explicitly kept messages and future matches from a
keep-enabled topic remain until an explicit deletion action, subject to the
100 MiB default hard per-device capacity. Author profiles and inferred identity
remain excluded.
The station starts stopped and locked after every launch. Listening requires a
manual passphrase unlock; STOP LISTENING closes source activity and locks the
saved messages again.
There is no passphrase recovery or escrow. Losing it makes existing encrypted
records permanently unreadable; the only reset path purges their ciphertext
and creates a new station key.

Durable topic matching is precision-first: the Phase 1 acceptance corpus must
reach at least 85% precision and 60% recall. Broader, non-persistent discovery
remains available through the live waterfall.

The target product now includes independently operable Windows 11 and Android
stations. Each device can listen, match, encrypt, retain, delete, and stop using
its own local state. Optional owner-controlled pairing may later improve
coverage and coordination, but neither device depends on the other.

Cyber Space Radio has no remote backend in Phase 1. Each station connects
directly to a public Nostr relay or other approved stream and performs
classification, matching, notification, retention, reporting, and deletion on
that device. Message content, event identifiers, source history, watch phrases,
matches, and reports are never sent to project-operated infrastructure. The
proposed .NET MAUI foundation uses native local UI and does not add a localhost
web process or hosted service.

> **Pre-release status: Phase 1 product implementation must not start; only
> bounded evidence closure and prototype/document work may proceed.** Public
> marketplace distribution still needs the applicable
> local-client checks, while any hosted collection, content-bearing pairing, or
> federation remains blocked by the separate UK review in
> [`LEGAL_RELEASE_GATE.md`](LEGAL_RELEASE_GATE.md). This is not a legal-clearance
> claim.

This is a small public-feed monitor: “pirate radio of the Internet” as a
metaphor, not an RF receiver or packet interceptor. It checks only RSS/Atom
feeds you deliberately configure, scores public entries against an idea, and
records the relevant ones. Unrelated entries are counted and discarded.

Each accepted JSON Lines record contains:

- the originating feed and entry URLs;
- the feed title and any author name publicly supplied by the feed;
- the public title, summary, and publication time;
- the idea that matched and its lexical coverage score;
- a fingerprint used to prevent duplicate recordings.

It does not deanonymize authors, inspect private traffic, or equate an IP
address with a person. A source URL identifies a public post, not necessarily
the human behind it.

## Use it

Copy `feeds.example.txt` to `feeds.txt`, add public RSS/Atom URLs, then run:

```powershell
py .\internet_signal_monitor.py `
  --idea "decentralized community network" `
  --feeds-file .\feeds.txt `
  --log .\matches.jsonl
```

Use `--idea` more than once to monitor several related formulations. Use an
exclusion when a recurring ordinary topic produces false positives:

```powershell
py .\internet_signal_monitor.py `
  --idea "decentralized community network" `
  --exclude "commercial networking event" `
  --feed "https://example.org/public-feed.xml"
```

One pass is the default. Continuous polling is deliberately conservative and
requires an operator contact that feed owners can see:

```powershell
py .\internet_signal_monitor.py `
  --idea "decentralized community network" `
  --feeds-file .\feeds.txt `
  --interval 1800 `
  --contact "mailto:operator@example.org"
```

The minimum interval is 15 minutes. Sources may impose stricter terms, opt-out
requirements, or rate limits; follow them and remove a feed immediately when
asked. There is no crawling, link following, feed discovery, or background
service installation.

Records expire after seven days by default. `--retention-days` changes that
period. Author names and summaries are not stored unless `--store-content` is
deliberately supplied.

## Delete records or uninstall

Delete records for one exact public entry or one feed:

```powershell
py .\manage_records.py delete-url "https://example.org/post/123"
py .\manage_records.py delete-feed "https://example.org/feed.xml"
```

Delete the complete local record file:

```powershell
py .\manage_records.py purge --yes
```

The program creates no Windows service, scheduled task, startup entry, browser
extension, or hidden data directory. Stop the running terminal and delete this
project folder to uninstall it. The emergency network stop described below is
intentionally separate from record deletion.

## What “similar” means here

The included matcher is deterministic and local: after removing common words,
it calculates how many terms from an idea appear in a post. The default 0.6
threshold means at least 60% of the meaningful idea terms must appear, with at
least two terms matching for multi-word ideas. This is transparent and needs no
cloud service, but it does not understand intent or synonyms. Adjust
`--min-score` or supply several `--idea` phrasings for better coverage.

The tool observes configured public feeds; it cannot listen to the entire
Internet. Platforms without RSS/Atom require their supported public API and
permission model rather than scraping or traffic interception.

## Federation boundary

The consent-only node protocol, encrypted transport, outage semantics,
resource limits, and fail-closed one-touch emergency stop are specified in
[`FEDERATION_DESIGN.md`](FEDERATION_DESIGN.md). Network federation is not
enabled by this prototype: certificates, control-plane hosting, and real
deployment topology must be supplied and verified first. In particular, nodes
never self-install, discover strangers, or accept remote configuration.
