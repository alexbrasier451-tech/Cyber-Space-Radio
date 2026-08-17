# Phase 0A source review

Review date: **2026-08-17**

Scope: **endpoint, policy, local-client architecture, and bounded size evidence**
Live message collection performed: **yes - aggregate-only Nostr size sample; no message body retained**

## Outcome

Approve `relay.damus.io` and `nos.lol` as disabled Nostr candidates for a
bounded, read-only, local-client Phase 0A evaluation. Keep Bluesky's current
Jetstream v2 US East endpoint approved-disabled as the comparison source.
The Nostr evaluation connects to both approved relays simultaneously, using one
read-only connection per relay and deduplicating identical event IDs locally
before activity counting, waterfall display, matching, or persistence. Each
deduplicated item keeps a local set of the relays that delivered it and shows a
small provenance badge: `Damus`, `nos.lol`, or `Both`. A later duplicate updates
the existing item's provenance instead of creating another shout.

This revision follows confirmation that Cyber Space Radio has no hosted
collection service: each installed station connects directly to a public
source, filters in local memory, stores only encrypted local matches, and sends
no listening data to the project. The incomplete relay policies remain recorded
operational caveats, but they do not block a standard low-rate local Nostr
client evaluation.

This resolves which endpoints are under review and supplies a bounded Nostr
body-size measurement. It does not pass the full Phase 0A cross-source
usefulness gate and does not change the repository-wide legal no-go for public
operation.

## Method

- Checked current primary protocol and operator documentation.
- Retrieved live Nostr NIP-11 documents over HTTPS with
  `Accept: application/nostr+json`.
- The initial source-policy review recorded only endpoint metadata, published
  limits, contacts, and policy references. It did not open a WebSocket event
  subscription.
- After separate owner approval, ran two bounded, direct, read-only Nostr
  observations totalling 360 seconds per relay. The sampler measured content
  sizes in memory and emitted aggregate counts only; it did not print, retain,
  or write message bodies, event IDs, public keys, tags, or relay payloads. See
  the [Nostr message-size sample](PHASE_0A_NOSTR_SIZE_SAMPLE.md).
- Applied the local-client source requirements in `DATA_AND_SOURCE_POLICY.md`.
  Public technical access is not a general licence to republish or operate a
  hosted collector, but an unauthenticated public subscription interface may be
  evaluated locally within its advertised limits when the missing policy is
  recorded and no content is sent onward.

NIP-11 makes relay terms and contact fields optional, so a relay can conform to
the protocol while still failing this project's stricter approval gate. See the
[NIP-11 relay-information specification](https://github.com/nostr-protocol/nips/blob/master/11.md).

## Selected AT Protocol endpoint

| Field | Reviewed value |
|---|---|
| Source ID | `phase0a-at-jetstream-us-east-v2` |
| Endpoint | `wss://jetstream.us-east.bsky.network/xrpc/network.bsky.jetstream.subscribeEvents?collections=app.bsky.feed.post&kinds=commit` |
| Source operator | Bluesky Social PBC |
| Source-owner contact | `mailto:support@bsky.app` |
| Cyber Space Radio operator contact | `mailto:cyberspaceradio@proton.me` |
| Project-contact publication state | `published-and-client-exposed` |
| Intended public contact page | `https://github.com/alexbrasier451-tech/Cyber-Space-Radio/blob/main/CONTACT.md` |
| Authentication | None for live tail |
| Server-side filter | One collection: `app.bsky.feed.post`; event kind: `commit` |
| Cursor | Monotonic `seq`; inclusive replay; delivery is at least once |
| Published filter limits | Up to 100 collections and 10,000 DIDs per subscription |
| Local Phase 0A limits | 60-second replay cap, 300 events/minute intake cap, 100-event queue, exponential reconnect backoff from 2 to 60 seconds with jitter, immediate stop |
| Status | Approved-disabled for routine operation; contact prerequisite cleared for the explicitly authorised bounded Phase 0A comparison |

Bluesky's current documentation says new projects should use v2 and lists the
US East and US West public instances. It also says no authentication is needed,
explains the server-side collection/kind filters, and documents cursor and
duplicate semantics. The older `jetstream1`/`jetstream2` `/subscribe` interface
is a compatibility endpoint and is no longer the right default. See
[Jetstream public endpoints and limits](https://bsky.network/docs/jetstream/).

The classifier accepts only create/update post records with non-empty text and
then excludes:

- records with a `reply` reference;
- records whose rich-text facets name a recipient;
- quote-post embeds using `app.bsky.embed.record` or
  `app.bsky.embed.recordWithMedia`;
- deletion events as candidates, while authenticated delete commits for the
  approved post collection immediately remove all retained versions of their
  AT URI, including Kept records, under the content-free audit rule; and
- non-post collections, already excluded by the server-side filter.

The canonical post schema defines `reply`, rich-text facets, and record embeds;
see the
[official `app.bsky.feed.post` Lexicon](https://github.com/bluesky-social/atproto/blob/main/lexicons/app/bsky/feed/post.json).

### Policy findings

- Bluesky's developer guidelines prohibit spam, require current public contact
  information, deletion handling, report handling where applicable, and
  reasonable security measures. Cyber Space Radio remains read-only and
  provides local deletion. The project owner has supplied
  `cyberspaceradio@proton.me`, now published in the project
  [contact file](../../CONTACT.md). On 2026-08-17 the raw GitHub file was
  fetched without authentication and matched the exact mailto route. The
  client's synthetic upgrade test also exposed the exact contact header once
  without logging or persistence. The project operator then confirmed an
  independent mailbox receive/reply test passed on 2026-08-17. No message
  content or non-project address was recorded. The composite contact gate is
  therefore complete for the bounded trial.
  See the [Bluesky Developer Guidelines](https://bsky.network/docs/developer-guidelines/).
- The source owner's `support@bsky.app` address is not the project operator's
  contact. The source register now stores it separately from
  `mailto:cyberspaceradio@proton.me`. The receive/reply and client-exposure
  checks are now complete. The Jetstream row remains approved-disabled for
  routine operation, but the explicitly authorised bounded Phase 0A comparison
  may run with the exact contact URI.
- The Network Services Privacy Notice says public posts are public, but also
  says the service may collect IP address, device/network, and usage data and
  may transfer information internationally. The station must disclose that
  connection-metadata exposure. See the
  [AT Protocol Network Services Privacy Notice](https://bsky.social/about/support/network-services-privacy-policy).
- The public endpoint documentation does not publish an events-per-minute
  quota. The trial therefore applies its own 300-events/minute ceiling, drops
  excess work locally, backs off on closure, and does not open extra
  connections to compensate.

## Nostr candidate review

| Endpoint | Live NIP-11 result | Terms/contact result | Decision |
|---|---|---|---|
| `wss://relay.damus.io` | Reachable; kind-1/NIP-11 capable; `max_limit=500`, `max_subscriptions=200`, `max_message_length=1000000` | Contact `jb55@jb55.com`; no terms or privacy URL in NIP-11 and no relay-specific policy found | Exact candidate; **approved-disabled** for bounded local-client evaluation |
| `wss://nos.lol` | Reachable; kind-1/NIP-11 capable; `max_limit=500`, `max_subscriptions=20`, `max_message_length=131072` | No contact URI; advertised terms URL resolves to an empty topic page rather than operative relay terms | Exact candidate; **approved-disabled** for bounded local-client evaluation |
| `wss://nostr.mom` | Reachable; same operator key as `nos.lol`; stricter spam/nudity-filter description | Advertised terms URL likewise contains no operative terms; no contact URI | Not selected; adds little operator diversity |
| `wss://relay.primal.net` | Reachable; kind-1/NIP-11 capable; `max_limit=500`, `max_subscriptions=20` | `contact` is only `primal.net`; no terms/privacy URL | Not selected; policy evidence incomplete |
| `wss://relay.snort.social` | Reachable; NIP-1/NIP-11; high published subscription limit | No operator contact or terms/privacy URL | Not selected; policy evidence incomplete |
| `wss://nostr.wine` | Reachable; clear limits, contact, terms, and privacy link | Requires payment before action; published admission fee is 18,888,000 msats | Policy is inspectable, but no purchase is authorised and it is not a free-public comparator |
| `wss://relay.nostr.band` | NIP-11 HTTPS request timed out after 20 seconds | Not evaluated further | Not selected on this review |

The exact Nostr event filter is kind `1` with an owner-approved 60-second replay
window on explicit Start and reconnect, and a local `limit` no greater than 100
even where the relay advertises 500. A longer interruption is shown as a
coverage gap; it never expands into a historical crawl. The local client
accepts at most 16,384 UTF-8 bytes in the decoded event `content` field. A
larger body is counted only as `Oversized` and discarded before normalization,
spam classification, Junk, waterfall display, matching, or persistence. The
complete assembled incoming event-envelope message is independently capped at
65,536 UTF-8 bytes, regardless of WebSocket fragmentation, and rejected before
JSON event-field parsing where the platform permits.
The trial uses one connection to each approved Nostr relay, no publishing key,
no NIP-42 authentication, no historical crawl, a 300-events/minute local intake
ceiling and 100-event queue per relay, and exponential reconnect backoff from
2 to 60 seconds with jitter. Queue overflow drops work and increments only a
non-identifying aggregate counter; it never opens another connection. STOP
disables all retry timers. The station deduplicates
by verified Nostr event ID before an event can affect user-visible activity or
matching. NIP-01 defines kind `1` as a short text note;
NIP-10 defines reply/root markers. The local classifier additionally rejects
recipient tags, quotes, repost structures, and group/channel structures before
topic matching. See [NIP-01](https://github.com/nostr-protocol/nips/blob/master/01.md)
and [NIP-10](https://github.com/nostr-protocol/nips/blob/master/10.md).

## What is actually available

There are plenty of technically open Nostr relays, but operator and policy
quality varies sharply. The reviewed free relays expose useful protocol limits
yet usually omit a usable privacy policy or terms document. That uncertainty
would be material for a hosted collector, republisher, or project-operated
service. It is a smaller operational risk for this user-directed local client,
which performs the ordinary public subscription operation, retains data only
on the user's device, and can be disconnected immediately.

Nostr is the closer conceptual fit for standalone "shouts in the dark" and is
viable for bounded engineering probes. Jetstream remains a useful,
better-documented comparison source. The first Nostr-only comparison run is
documented in the
[Phase 0A comparison report](PHASE_0A_COMPARISON_REPORT.md); it did not establish
source usefulness or a cross-source recommendation.

## Live Nostr body-size evidence

The two owner-authorized observations produced 340 within-run-deduplicated
standalone observations. Their weighted mean body size was approximately 297
UTF-8 bytes; both runs had a 195-byte median and a 95th percentile below 800
bytes. The observed maximum was 4,585 bytes. Five observations were over 1 KiB,
one was over 4 KiB, and none was over 8 KiB or 16 KiB.

Only five messages matched the deliberately broad English
relationship/gossip or interpersonal vocabulary. They averaged approximately
596 bytes and had a 745-byte maximum. That subset is too sparse to estimate the
topic's population distribution, but it provides no evidence that this focus
needs unusually large messages. The evidence supports a 16,384-byte local body
limit while leaving the topic question to the labelled-corpus and full Phase
0A comparison gates. The sampler recalculated event IDs but did not independently
verify Schnorr signatures; production validation remains mandatory.

## Gate and next actions

1. Keep every reviewed row disabled until the operator starts the bounded test.
2. Run synthetic and handshake tests before opening any event subscription.
3. Treat both aggregate-only Nostr runs as limited evidence, not a passed
   source gate. Publicly publish and verify the recorded project operator
   contact before any Jetstream run, add maintained Schnorr verification
   before accepting Nostr candidates, and then run the bounded cross-source
   comparison against the predeclared labelled corpus.
4. Treat missing Nostr terms/contact information as a visible caveat: stop on
   access denial or operator request, never bypass controls, and re-review any
   material NIP-11 or endpoint change.
5. Verify by egress tests that message content, event identifiers, watch terms,
   and listening history never reach project-operated infrastructure.
6. Do not begin production Phase 1 implementation until the protocol-valid
   Phase 0A evidence
   gate and the separate Phase 0B Android foundation gate pass.
