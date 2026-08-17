# Data and source policy

## Boundary

A station may contact only endpoints present in its local approved-source
register. Content, peers, federation messages, redirects, and search results
cannot create or modify source configuration.

Phase 0A compares Nostr public text-note subscriptions with AT Protocol
Jetstream. Phase 1 adopts one family or a deliberately bounded combination only
after the comparison report. RSS/Atom remains available for deterministic
fixtures and later adapters. Each endpoint is enabled separately after its
source row is complete.

The current qualification result is in
[`PHASE_0A_SOURCE_REVIEW.md`](PHASE_0A_SOURCE_REVIEW.md), with exact rows in
[`phase-0a-reviewed-sources.csv`](phase-0a-reviewed-sources.csv). Jetstream v2
US East, `relay.damus.io`, and `nos.lol` are approved-disabled for a bounded
local-client trial. The missing or ineffective Nostr relay policy documents are
recorded caveats, not blockers for that trial.

## No-backend boundary

Phase 1 is an installed local client, not a hosted monitoring service:

- each Windows or Android station connects directly to an operator-enabled
  public source;
- source events, watch phrases, match decisions, identifiers, and listening
  history never pass through project-operated infrastructure;
- classification, matching, notifications, encryption, retention, reporting,
  and deletion happen on the device;
- there is no Cyber Space Radio account, ingestion API, proxy, telemetry
  pipeline, cloud database, hosted alert, remote push payload, or cross-user
  reporting service; and
- Windows may use a loopback-only UI process if the selected foundation needs
  one, but it must bind only to the local device and is not a remote backend.

Any feature that weakens this boundary, including content-bearing crash reports,
cloud sync, device pairing, remote control, federation, or a project-operated
relay, requires a new architecture decision and privacy review before work.

Bundled starter topics are static application assets. Browsing, selecting, or
editing one creates only local watch configuration and makes no source,
analytics, search, model, or project-server request. No topic is preselected,
and `Skip and explore` creates no active watch. Manually typed ideas,
alternative phrasings, exclusions, tutorial progress, and fixture labels remain
local and follow watch deletion and station-reset scope.

### Watch validation and promotion

Every watch definition and matcher version has a local validation state:
`draft`, `preview-only`, or `validated`. Only `validated` may automatically
persist or notify. Discovery highlighting and an explicit one-item `Keep`
remain available for draft and preview-only watches.

- A bundled starter-template version may ship as validated only with a
  versioned evaluation package: immutable watch-definition hash, corpus and
  label versions, predeclared development/held-out split, at least 200
  authorised examples including 50 positives, per-source results, precision,
  recall, timestamp, software version, and project-owner approval.
- A custom watch, or any edit to a validated starter, begins preview-only. The
  local operator owns its labels and may promote that exact frozen version only
  after the same held-out `>= 0.85` precision and `>= 0.60` recall gate passes.
- The promotion wizard accepts bundled synthetic/licensed fixtures and
  examples the operator deliberately authors or labels. Any saved example text
  is encrypted as watch configuration, never telemetry, and is deleted with
  the watch or station reset. Merely viewing a waterfall item never adds it to
  the corpus.
- Tuning happens only on the development split. The held-out split remains
  concealed until the operator freezes the watch version and runs the gate.
  Changing phrases, exclusions, threshold, labels, corpus, or matcher
  invalidates the evidence version and returns the watch to preview-only.
- The signal records the exact watch, matcher, and validation-evidence versions
  responsible for persistence so a result can be reproduced and withdrawn.

Signals-inbox filter, sort, and scroll state is volatile UI state. It may remain
in memory during one unlocked session but is never written to the database,
browser storage, files, logs, exports, backups, analytics, or crash reports.
Lock, STOP, restart, and reset clear it.

## Source approval

Every source row must identify:

- stable source ID and display name;
- exact relay, stream, feed, or supported API endpoint;
- protocol, connection mode, permitted event types, and subscription filter;
- source owner and source-owner contact route when published; otherwise record
  that no usable source-owner route was found and require explicit local risk
  acceptance;
- the separate project-operator contact route and its verified publication
  state;
- licence or terms URL and the permitted use relied upon; when a public
  protocol endpoint publishes neither, record that absence, the public access
  basis, advertised limits, and the owner's explicit risk acceptance;
- authentication method, if any;
- minimum polling interval and published quota;
- whether conditional requests or cursors are supported;
- replay/backfill window, reconnect policy, event-rate ceiling, and queue cap;
- permitted retained fields;
- attribution requirement;
- approval owner and date;
- next review date; and
- candidate, blocked-policy, approved-disabled, enabled, paused, removed, or
  expired status.

The repository includes
[`templates/approved-source-register.csv`](templates/approved-source-register.csv)
as the operational template.

The Cyber Space Radio operator route is recorded separately in the repository
[contact file](../../CONTACT.md). A local file is not evidence of public
publication. Each reviewed row therefore records both the contact URI and one
of these states: `recorded-not-published`, `published-unverified`, or
`published-and-client-exposed`. A live Jetstream trial requires the final state,
including a reachable public page, a mailbox receipt check, and client
handshake exposure. A source owner's support address never satisfies this
project-operator requirement.

The publication target is the public repository's `main`-branch
[`CONTACT.md`](https://github.com/alexbrasier451-tech/Cyber-Space-Radio/blob/main/CONTACT.md).
After a push, verification must use the unauthenticated raw-file URL and match
the exact mailto route; the Git push result alone does not advance contact
status.

## Courtesy rules

- Where the protocol supports it, use an honest product identifier with the
  separately recorded project-operator contact. Do not configure it as
  published until its public page and mailbox route have been verified.
- Default continuous polling to no faster than 15 minutes and obey any stricter
  source limit.
- Use ETag, Last-Modified, cursors, and backoff when supported.
- For persistent streams, request only approved event types, use a bounded
  replay window, apply reconnect backoff, and stop intake before a queue grows
  beyond its configured ceiling.
- Cap timeouts, retries, pages, items, and response bytes.
- Honour `429`, `Retry-After`, access revocation, and direct opt-out requests.
- Do not bypass a login, paywall, CAPTCHA, robots exclusion, rate limit, or
  technical control.
- Do not follow entry links or redirects to an unapproved origin.
- Opening a signal never fetches its links, media, author profile, relay context,
  or an external Nostr viewer. A configured viewer may receive only a safely
  encoded stable event reference after an explicit operator action and warning;
  never append message text, watch terms, scores, or local history.
- One source failure must not increase pressure on that source or other sources.
- Remove or pause a source immediately when approval expires or its owner asks.
- Missing terms never authorise bypassing controls, hosted collection,
  republishing, resale, or continued access after refusal.
- Phase 0A may open one read-only connection to each of the two approved Nostr
  relays concurrently. A verified event ID seen on both relays is one candidate:
  deduplicate it before aggregate counting, waterfall display, topic matching,
  notification, or persistence.
- A deduplicated Nostr candidate keeps a set of approved source IDs that
  delivered it. The UI renders that set as `Damus`, `nos.lol`, or `Both`; a
  later duplicate updates provenance without incrementing activity or creating
  another signal. Unmatched provenance expires with its waterfall item.
- On explicit Start or reconnect, request at most the preceding 60 seconds from
  each Nostr relay. Deduplicate replayed events against local volatile and
  retained event IDs. Never extend the window to fill a longer outage; record
  and display the resulting coverage gap instead.

## Data lifecycle

```text
receive candidate event from approved endpoint
  -> reject an assembled incoming Nostr event envelope over 65,536 UTF-8 bytes
  -> validate protocol envelope/signature when the protocol supports it
  -> classify standalone versus addressed/conversational event
  -> discard replies, quotes, reposts, direct/recipient/group messages
  -> reject a decoded content body over 16,384 UTF-8 bytes as Oversized
  -> normalise in memory
  -> deduplicate
  -> suppress conservatively identified spam/flood events
  -> update non-identifying aggregate activity
  -> place standalone content in a bounded volatile waterfall
  -> apply exclusions and relevance locally
  -> expire unmatched waterfall content without persistence
  -> privacy-project and persist a topic match or one explicit local Keep
  -> expire or delete
```

### Volatile discovery data

- The live waterfall exists only in process memory and has both an age limit
  and an item-count limit.
- Its collapsed UI projects at most 280 user-perceived Unicode characters from
  the same in-memory item. Expansion reads the complete accepted message from
  that item and creates no extra copy, persistence, log, or network request.
- The owner-approved Phase 1 limits are the most recent 100 standalone shouts
  and a maximum age of ten minutes; the first limit reached evicts the oldest
  unkept item.
- It is not written to SQLite, files, logs, browser storage, exports, backups,
  crash reports, notifications, or federation messages.
- Restart, STOP LISTENING, expiry, or `Clear waterfall` removes it immediately.
- Aggregate counters may outlive individual previews only when they contain no
  message text, event ID, author key, source address, or other identifying data.
- Obvious spam is suppressed before the waterfall and matching stages. The
  `Noise blocked` counter may increment, but blocked content, event IDs, and
  author keys are not persisted.
- A body over the accepted size limit increments only the non-identifying
  `Oversized` counter and is discarded before the waterfall or matching stages.
- Switching from discovery to tuned mode cannot persist older waterfall items.

### Oversized safety boundary

- Accept an assembled incoming Nostr WebSocket text message carrying an event
  envelope only when it is at most 65,536 UTF-8 bytes, including the protocol
  wrapper, subscription ID, event fields, signatures, and tags. Enforce this at
  the transport boundary before JSON parsing where the platform permits;
  otherwise measure and discard immediately before parsing event fields.
- Measure the decoded public-message body as UTF-8 before normalization,
  truncation, spam classification, Junk, waterfall display, matching, or
  persistence.
- Accept at most 16,384 body bytes. A 65,537-byte envelope or 16,385-byte body
  is `Oversized` and is discarded. Fragmentation does not bypass the envelope
  limit: measure the complete assembled WebSocket message.
- `Oversized` is a resource-safety result, not a spam opinion. It increments a
  separate aggregate count with an aggregate-only `envelope` or `body` reason,
  containing no content, event ID, public key, author, subscription ID, tags,
  or source address.
- Oversized content has no Junk, restore, notification, durable-store, log,
  export, backup, crash-report, external-viewer, or federation path.
- A transport that closes an over-limit connection must apply the ordinary
  reconnect backoff and must not enter a tight retry loop. Phase 1 must still
  impose and verify bounded tag counts/depth, queues, and parser work within
  the accepted envelope.

### Conservative spam boundary

- Spam suppression runs only on protocol-valid, within-size events and uses
  exact/near-exact repetition, extreme per-key bursts, and mechanically
  repetitive payloads. Thresholds are versioned and tested against labelled
  fixtures.
- It does not classify political views, unpopular opinions, vocabulary, topic,
  sentiment, identity, or relay choice as spam.
- Relay-level spam labels may be displayed as evidence but do not silently add
  an identity blacklist or override the local versioned rules.
- While blocked, an event cannot create a match, notification, durable signal,
  profile, or automatic permanent rule. Only the explicit exact-event
  `Restore once` path below may return a valid event to normal processing.
- Valid events suppressed only by the spam rules enter the volatile Junk drawer
  described below. Invalid signatures, malformed envelopes, structurally
  excluded conversations, and `Oversized` inputs are discarded and cannot be
  restored.

### Volatile Junk drawer

- Hold at most the newest 50 valid spam-suppressed events or five minutes of
  events, whichever limit removes an item first.
- Keep entries and their event IDs entirely in process memory. They have no
  database, file, log, browser-storage, export, backup, notification, external
  viewer, or federation path.
- Show the versioned structural/repetition reason for each decision and the
  relay provenance badge.
- `Restore once` applies a session-only override for that exact verified event,
  moves it into the live waterfall, and runs the normal local matcher. It may
  become a durable signal only if it independently satisfies the enabled watch.
- Restore never creates a permanent author, content, relay, or identity rule.
  A later different event is evaluated normally.
- STOP LISTENING, application restart, five-minute expiry, capacity eviction,
  or `Clear Junk` removes the volatile entries immediately. The aggregate
  `Noise blocked` count contains no restorable content.

### Default persisted fields

These fields apply only to durable topic matches or explicitly kept messages:

- protocol and the set of approved source IDs that delivered the event;
- stable protocol event ID/reference;
- public entry URL when supplied or safely derived;
- full public message text encrypted at rest;
- source title when present;
- published and observed timestamps;
- local review state and nullable reviewed timestamp;
- zero or more watch-match decisions, each containing its watch ID, relevance
  score, explanation, matcher version, and validation-evidence version;
- a random local signal ID, protocol-derived deduplication key, and stable
  source-object key for upstream deletion; and
- derived retention mode (`expiring` or `kept`), zero or more retention reasons
  with kind, optional watch ID, and decision time, plus nullable expiry time.

### Default excluded fields

- author profile fields, display name, avatar, biography, follower counts, or
  other profile enrichment;
- unmatched post body, summary, or message text after volatile expiry;
- profile link, avatar, follower counts, or inferred demographics;
- client IP, cookies, request headers, or source credentials;
- identity-resolution output;
- raw embeddings shared outside the local station; and
- any private or access-controlled material.
- unmatched standalone-message content and event identifiers after their
  volatile waterfall entry expires.

Full public message text is stored only after a topic match or an explicit local
`Keep` action on a valid waterfall item. Ordinary automatic matches expire after
seven days. Kept messages and future matches from a keep-enabled topic have no
automatic expiry and remain subject to the hard local storage capacity and
explicit deletion controls below. Author/profile storage remains off. A
protocol public key is not a person identity and may be retained only when
required to verify the event; it must be encrypted and must not be enriched or
resolved. Message text and author evidence are never sent through the future
federation protocol.

Content fingerprints are permitted only as bounded spam or near-duplicate
features. They are not durable signal identity and cannot merge two distinct
protocol events with identical text. Nostr deduplicates on the verified event
ID; Jetstream deduplicates a post version on AT URI plus CID and uses the AT URI
as its upstream-deletion key.

Review state is metadata on the one local signal, not per-topic activity. It is
created as `New`, becomes `Reviewed` only after successful unlocked local
inspection, and returns to `New` when the operator explicitly chooses `Mark as
new`. It never changes expiry, Keep, matching, notification delivery, ordering,
or source activity and has no egress path. Exact deletion, orphan deletion,
purge, reset, and uninstall remove it with the signal.

`Mark visible as reviewed` operates on a locally computed snapshot of unique
signal IDs matching the current filters. Its preview contains filters and an
aggregate count, not message content. Confirmation atomically updates only the
snapshotted New records; later arrivals remain New. The batch action does not
decrypt bodies or affect source traffic, notifications, matches, retention,
ordering, or expiry.

### Android match notifications

- Only a durable topic match may trigger the generic local `New signal found`
  notification; waterfall items and aggregate activity cannot trigger it.
- The notification contains no message text, source, author, score,
  explanation, event reference, watch name, or permalink.
- Opening it requires local passphrase unlock before any persisted plaintext or
  source evidence is shown.
- Phase 1 sends no email, webhook, hosted alert, or remote push payload.

### External Nostr viewer

- The complete retained message is readable inside an unlocked local station;
  an external viewer is optional and never required.
- Every new installation and reset starts with external viewing disabled and no
  viewer URL. Until the operator explicitly configures one in local Settings,
  the UI exposes no `Open externally` action.
- The viewer base is a local operator setting, not supplied by a relay event or
  message link. It must use HTTPS and accept only a safely encoded stable Nostr
  event reference.
- `Open externally` requires an explicit tap and a confirmation naming the
  destination and connection-metadata exposure.
- There is no automatic redirect, link preview, prefetch, profile enrichment,
  cookie forwarding, or viewer request during list or inspector rendering.
- The station does not claim deletion control over browser history or data
  subsequently handled by the selected external viewer.

## Encryption at rest

- Durably retained message text and any required author verification key are
  encrypted before they reach SQLite or another durable store.
- Use a maintained authenticated-encryption construction with a versioned
  envelope, unique nonces, integrity failure handling, and documented key
  rotation. Do not invent a cryptographic algorithm.
- Plaintext is confined to bounded process memory while matching or while an
  authorised local operator views an unlocked record.
- SQLite journals/WAL, temporary files, logs, browser storage, exports, crash
  reports, and backups must not receive plaintext message content.
- Backups contain ciphertext only and follow the record's expiring or kept
  lifecycle; the station does not claim to erase offline media it cannot reach.
- The passphrase is never stored. A maintained, reviewed memory-hard password
  KDF derives a key-encryption key from the manually entered passphrase and a
  stored random salt. That key unwraps a random content-encryption key; the
  durable store contains only the wrapped form.
- Every launch and automatic restart begins stopped and locked. No source
  connection may start and no saved message text may be viewed until manual
  local unlock succeeds.
- STOP LISTENING closes source activity, prevents reconnects, clears the
  volatile waterfall, and makes a best-effort removal of usable plaintext keys
  and content from process memory. Persisted records remain ciphertext.
- The application never places the passphrase or an unwrapped content key in
  configuration, command-line arguments, environment variables, logs, crash
  reports, browser storage, or backups.
- Key rotation rewraps the content key without rewriting message plaintext.
  Rotation requires the current passphrase or an already unlocked session.

### Passphrase loss and reset

- There is no recovery key, escrow copy, passphrase hint, administrator bypass,
  OS-vault fallback, or maintainer backdoor.
- Losing the passphrase makes the retained ciphertext permanently unreadable.
- The reset flow cannot decrypt or migrate old records. It first stops and
  locks the station, previews the amount of ciphertext to be removed, requires
  an explicit `PURGE AND RESET KEY` confirmation, deletes the encrypted records
  and wrapped content key, and only then creates a new key and passphrase.
- Public source configuration may be retained only if it contains no secret or
  encrypted field. Encrypted watches, credentials, and other content tied to
  the lost key are purged with the records.
- Backups containing the old ciphertext remain unreadable and follow their
  documented expiry/deletion policy; reset does not claim to alter offline
  media that is outside the station's control.

## Retention

- Watch/topic definitions remain encrypted local configuration until the
  operator pauses or deletes them; they do not expire merely because no message
  matched recently.
- Ordinary automatic topic matches default to seven-day expiry.
- `Keep` on a valid waterfall item or durable signal changes that exact message
  by adding a manual retention reason, removes automatic expiry while that or
  another reason remains, and records the local decision time.
- Keeping a waterfall item moves it out of the volatile 100-item/ten-minute set
  only after the encrypted durable write succeeds. A failed Keep leaves it
  volatile and subject to the ordinary waterfall limits.
- `Keep future matches` is off by default per topic. When enabled, only future
  matches add a topic retention reason; existing signals change only through a
  separate previewed and confirmed bulk action. Disabling it is likewise
  future-only unless the operator separately previews and confirms removal of
  that topic's reasons from existing signals.
- Manual Keep and every keep-enabled topic that matched a signal are independent
  reasons on the same record. Removing one never defeats another. Removing the
  final reason after confirmation sets a new seven-day expiry from the removal
  time; it does not reuse an old or already elapsed deadline.
- Kept status protects against expiry and capacity eviction, but not an explicit
  exact delete, confirmed source-data deletion, full purge, passphrase-reset
  purge, or uninstall.
- Expiry is attached when an ordinary signal is created.
- Changing the default does not silently lengthen existing records.
- An expiry job runs at startup and at least daily while active.
- Metrics may retain non-identifying aggregate counts after content deletion.
- Backups and replicas must have documented deletion behaviour before use.

## Local storage capacity

- Each Windows and Android station has an independent hard capacity setting for
  application-owned durable data, including the encrypted database, indexes,
  journals/WAL, durable audits, and transaction headroom.
- The initial default is **100 MiB per device**. The operator may change it in
  local Settings, subject to preflight validation against current protected
  usage and available device space.
- Show warnings at 80% and 95%. The UI shows used bytes, configured capacity,
  kept bytes/items, ordinary bytes/items, and the oldest ordinary signal.
- Before refusing a durable write, delete expired records and then the oldest
  unkept ordinary signals until sufficient bounded transaction headroom exists.
- Never automatically delete a signal with any retention reason. If protected
  records consume the available capacity, enter `Storage full`: continue
  bounded listening, waterfall, Junk, and matching in memory, but do not claim
  that new signals were saved.
- A failed `Keep` or automatic save remains visibly `Not saved - storage full`
  while its volatile item exists. The operator must delete data or increase the
  capacity before retrying.
- Lowering the capacity previews required pruning. It cannot silently delete
  kept records; reject the new limit if protected data plus required headroom
  cannot fit.
- Capacity enforcement must fail closed before a write rather than knowingly
  exceeding the configured limit.

## Deletion

Supported scopes:

1. one exact signal ID, protocol event ID, or public entry URL;
2. one source's provenance from all local signals;
3. all expired signals;
4. one watch definition plus its match decisions and topic-retention reasons;
   and
5. complete local content purge.

Source-provenance deletion removes that source ID from every matching signal.
A signal observed only through that source is deleted completely. A signal also
observed through another approved source remains, with its provenance badge and
source-ID set updated; for example, `Both` becomes `nos.lol` when Damus
provenance is deleted. This is not a second copy of the message: one logical
signal has a set of independent delivery observations.

This confirmed action is authoritative over Keep. Its preview separately shows
ordinary sole-source deletions, Kept sole-source deletions, and multi-source
records that will remain. If any Kept signal would be deleted, confirmation must
name the source and state the protected-item count; cancellation changes
nothing. A Kept `Both` signal remains Kept under its surviving provenance.

Topic deletion first produces a local preview with four disjoint counts and
estimated bytes:

- signals that remain because at least one other watch still matches;
- signals that remain because a manual Keep still applies, even if no other
  watch matches;
- ordinary signals left with neither a match nor a retention reason and
  therefore deleted; and
- protected signals whose only remaining justification is the deleting topic's
  retention reason and therefore require a separate protected-item warning.

After confirmation, one transaction deletes the watch definition, its
`SignalDecision` entries, and its topic retention reasons. A surviving signal
keeps its other decisions and reasons. If removal of that topic was the final
retention reason but another watch still matches, the signal begins a fresh
seven-day expiry. A manually kept signal with no remaining watch becomes
`Kept manually`. A signal left with neither a match decision nor a retention
reason is deleted completely. Confirmation names the topic and separately
states the protected-signal count; cancellation and transaction failure leave
the watch and signals unchanged.

Deletion must be idempotent, previewable for bulk scopes, and tested end to end.
A deletion audit contains scope, time, operator, result count, and software
version, but no deleted content.

Removing a source stops its connection and future replay first. Existing signal
provenance remains unchanged unless the operator separately chooses
`Delete this source's data`. Exact signal deletion always removes the complete
signal regardless of provenance, and full purge removes every local signal.

An authenticated upstream source deletion is a different scope from the
operator's `Delete this source's data` action. For Jetstream, a delete commit
for an approved `app.bsky.feed.post` AT URI immediately and idempotently removes
all local versions keyed to that URI, including Kept records, their ciphertext,
match decisions, review state, and retention reasons. It does not wait for an
interactive preview because continuing to retain source-deleted content would
break the source contract. The station records only a content-free deletion
audit and shows an after-the-fact count such as `1 kept item removed by source`;
it never preserves deleted text for the warning. Malformed, unauthenticated,
wrong-collection, or unapproved-source delete messages fail closed and remove
nothing.

## Future federation

Only compact signal digests and direct health observations may leave a station.
No title, author, body, full source URL, raw idea, IP address, or source
credential is federated. See [the federation design](../../FEDERATION_DESIGN.md).
