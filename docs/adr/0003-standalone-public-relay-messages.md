# ADR 0003: standalone public relay messages are the first signal surface

- Status: accepted
- Date: 2026-08-14
- Source review updated: 2026-08-17

## Context

The original Phase 0 definition treated configured public feeds and supported
site APIs as the primary signal surface. The product owner clarified the radio
metaphor: Cyber Space Radio should listen for public messages cast into an open
network without a particular human, group, conversation, or website as their
apparent target - "shouts in the dark."

Internet packets still have technical destinations. The product therefore
cannot listen to an addressless global ether. Public relay and event-stream
protocols provide the closest technically real surface: an author publishes a
public event to relay infrastructure and any subscriber permitted by that
infrastructure may receive it.

## Decision

The first use case is read-only listening to explicitly approved public
relay/event streams for standalone public plaintext messages.

A candidate is standalone only when protocol structure shows that it is not:

- a reply or thread continuation;
- a quote or repost;
- a direct message or recipient-tagged message;
- a group, room, channel, or community message; or
- private or access-controlled content.

This structural classifier runs before semantic matching and persistence. The
station does not publish, reply, react, follow, contact an author, or modify a
relay. Phase 0A will compare Nostr public text notes with AT Protocol Jetstream.
The exact review set is Jetstream v2 US East, `relay.damus.io`, and `nos.lol`.
All three are approved-disabled for a bounded local-client evaluation. Nostr is
the preferred first probe because kind-1 public notes are the closer protocol
fit. The Nostr probe connects to both approved relays concurrently and treats a
verified event ID as one candidate regardless of how many relays delivered it.
Incomplete relay policies remain visible operational caveats. See the
[Phase 0A source review](../phase-0/PHASE_0A_SOURCE_REVIEW.md).

A later aggregate-only Nostr size probe sets a cross-platform accepted-body
limit of 16,384 UTF-8 bytes. The decoded message body is measured before
normalization. A larger body is a separate `Oversized` resource-safety result,
not spam, and is discarded before Junk, waterfall display, matching,
notification, or persistence. A separate owner decision caps the complete
assembled incoming Nostr event message at 65,536 UTF-8 bytes, regardless of
WebSocket fragmentation, and enforces it before JSON event-field parsing where
the platform permits. Both limits use aggregate-only `Oversized` reasons. See the
[Nostr message-size sample](../phase-0/PHASE_0A_NOSTR_SIZE_SAMPLE.md).

The output policy is hybrid. Every structurally standalone shout may appear in
a bounded, short-lived, in-memory waterfall and contribute to
non-identifying aggregate activity. Only a shout that also matches an enabled
topic watch passes through privacy projection into a durable record or report.
Unmatched waterfall content has no disk, log, export, backup, notification,
browser-storage, or federation path. Mode changes do not retroactively persist
volatile items.

For topic matches, the durable record contains the full public message text in
authenticated encrypted form for seven days by default, plus minimal source and
match evidence. A later decision also permits an explicit local Keep on one
valid waterfall item and opt-in non-expiring future matches per topic, within a
hard local capacity. Author profiles and inferred identity are excluded. Any
protocol public key required for signature verification remains inside the
encrypted record and is not enriched.

Encryption unlock is manual. Every launch is stopped and locked, and listening
cannot begin until the local operator enters the passphrase. STOP LISTENING
closes source activity, clears the volatile waterfall, and locks durable
message text again without deleting its ciphertext.

There is no passphrase recovery, escrow, or bypass. If the passphrase is lost,
the ciphertext remains unreadable. The only reset path explicitly purges the
old encrypted records and wrapped key before initialising a new station key.

Topic matching is precision-first. A matcher version must demonstrate at least
85% precision and 60% recall on the held-out corpus before it may create
durable records or reports. Discovery mode remains available when a matcher has
not yet passed this gate.

## Consequences

Positive:

- gives "shouts in the dark" a concrete, testable protocol meaning;
- filters conversations and addressed communication without guessing intent
  from prose;
- makes a read-only station feasible using public subscription interfaces; and
- differentiates the product from ordinary website keyword monitoring.

Negative:

- there is no single global relay stream, so coverage is always partial and
  source-dependent;
- public streams may contain high-volume spam and automated events;
- protocols represent replies and recipients differently, requiring an
  explicit classifier per adapter;
- persistent stream connections expose some connection metadata to relay
  operators; and
- Harken's fit for long-lived WebSocket streams is unproven.

## Required validation

Before production implementation, Phase 0A must use synthetic fixtures and a
bounded, content-minimising, read-only sample to measure volume, standalone
proportion, noise, resource cost, disconnect/reconnect behaviour, and adapter
fit. The completed Nostr size probe informs the body ceiling but does not
replace that cross-source usefulness comparison. No source is enabled without
a complete approved-source register row.

## Alternatives rejected

- **Arbitrary public website monitoring:** useful as a secondary adapter but
  not the clarified product concept.
- **Packet interception or whole-Internet listening:** neither technically
  available to an ordinary station nor within scope.
- **Replies and public conversations:** publicly visible, but aimed at a known
  context and therefore not standalone shouts.
- **Direct messages:** addressed and potentially private; always excluded.
