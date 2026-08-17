# Project charter

## Vision

Cyber Space Radio is a local-first listening console that receives public,
standalone text messages from explicitly approved relay/event streams, checks
them against an operator-defined idea, records only likely matches with stable
source evidence, and discards unrelated material.

The product has two independently operable station classes: Windows 11 desktop
and Android. Each can perform the complete listening lifecycle using its own
local encrypted state even when the other is absent or offline. iPhone is
deferred until the Android lifecycle evidence and local value are accepted.

The radio language is a product metaphor. The product does not receive radio
waves, intercept network traffic, or listen to private communications.

## Problem

Some public networks carry top-level messages that are not addressed to a
person, group, conversation, or particular website audience. These
"shouts in the dark" are surrounded by replies, automated traffic, spam, and
ordinary material. Existing social timelines optimise for accounts and
engagement rather than quiet, explainable listening.

Cyber Space Radio should answer one question:

> Has a standalone public message sufficiently close to the idea I am
> listening for appeared on an approved relay stream, and what stable event
> evidence identifies it?

## Approved first use case

Listen read-only to explicitly approved public relay/event streams for public
plaintext messages that are not replies, quotes, reposts, direct messages,
named-recipient messages, or group/channel messages. Apply the local watch only
after this structural classification when topic filtering is enabled.

The approved output policy is hybrid. Discovery mode shows a bounded,
in-memory waterfall of recent standalone shouts plus aggregate activity. Tuned
mode keeps that ephemeral awareness but creates durable, reportable records
only for shouts that match an enabled operator-authored topic watch. Unmatched
message content is never written to disk, logs, exports, backups, or reports.

A durable topic match contains the full public message text encrypted locally
for seven days by default, plus the approved source, stable event reference,
timestamps, score, matcher version, and explanation. An explicit message Keep
or keep-enabled topic removes automatic expiry, subject to the hard local
capacity. It does not retain an author profile or infer a real-world identity.
A protocol public key may be retained only when required as verifiable event
evidence and remains encrypted at rest.

The operator may begin in discovery mode, add and refine watches as patterns
emerge, run quietly in tuned mode, or stop listening completely if the stream
is not useful. Switching modes does not retroactively persist earlier
unmatched shouts.

The first release observes; it never publishes, replies, reacts, follows,
contacts an author, or changes a relay. Nostr public text-note events and AT
Protocol Jetstream are the approved Phase 0A comparison families. Exact
endpoints still require source-register review before any connection. Phase 1
will use the source family or bounded combination justified by the spike rather
than assuming that greater volume is better.

The public source is the server; Cyber Space Radio is a direct local client.
There is no project backend in Phase 1. Message content, event identifiers,
sources, watches, matches, reports, and listening history do not leave the
device for project-operated infrastructure. The proposed .NET MAUI application
uses native local UI on both platforms and has no remotely reachable browser
server or WebView data store.

## Product principles

1. **Public and approved:** use only sources explicitly enabled by the operator.
2. **Local relevance:** score and explain matches on the node whenever possible.
3. **Precision first:** silence is better than an inbox full of weak matches.
4. **Source, not identity:** link to the public entry without resolving or
   inferring a person behind it.
5. **Minimum record:** retain only what is required to review a match.
6. **Bounded by design:** connections, event rates, replay windows, memory,
   disk, queues, and retention have hard limits.
7. **Courtesy is functional:** identify the operator, honour limits, and remove
   a source promptly when asked.
8. **Stop and delete are distinct:** stop halts activity; deletion is a separate
   deliberate action.
9. **No backend:** project-operated infrastructure never receives listening
   content or listening metadata in Phase 1.
10. **Consent before federation:** nodes exist only because their operators
   installed and configured them.
11. **No hidden intelligence:** show why text matched and make uncertainty clear.

## Primary user

### Independent researcher/operator

The primary user has a small set of approved public relay streams and a rare
idea or question to monitor. They need to:

- define the idea and alternative phrasings;
- exclude common false-positive patterns;
- see whether listening is active and when sources last succeeded;
- understand why a signal matched;
- open the original public entry;
- dismiss or preserve a useful signal;
- delete one record, one source's records, or all local records; and
- stop activity immediately without accidentally erasing evidence.

### Other stakeholders

- **Source owner:** expects conservative polling, an operator contact,
  attribution, and prompt removal on request.
- **Future node operator:** explicitly installs a node, selects peers, controls
  its keys, and can leave the network.
- **Mobile operator:** needs truthful foreground/background state, bounded
  battery and bandwidth use, full local encryption, and no dependency on a
  desktop station.
- **Maintainer:** needs deterministic tests, bounded behaviour, inspectable
  configuration, and evidence-based release gates.

Authors whose public entries match are not investigative targets or product
users. The software must not infer identity, affiliation, intent, or belief.

## Vocabulary

| Term | Meaning |
|---|---|
| Watch | An operator-authored idea, its alternative phrasings, exclusions, and threshold. |
| Starter topic | A bundled, editable local template that helps create a watch; it is not selected by default and is not a remote subscription or editorial label. |
| Standalone message | Public text with no protocol evidence that it targets a recipient, group, reply thread, quote, or repost. |
| Candidate | A standalone message received from an approved source before local relevance filtering. |
| Signal | A candidate whose text crossed the watch threshold. |
| Noise | A candidate that did not match. Its body is not retained. |
| Oversized | A complete incoming event envelope or decoded message body above its local safety limit; it is discarded before further content processing and is not classified as spam. |
| Live waterfall | A bounded, volatile view of recent standalone shouts; it is not a record and disappears on expiry, restart, or stop. |
| Junk drawer | A bounded, volatile view of valid events suppressed by conservative spam rules; it is not durable storage and excludes malformed or invalid events. |
| Discovery mode | Shows the live waterfall and aggregate activity without creating durable records for unmatched shouts. |
| Tuned mode | Persists and reports only shouts that cross an enabled topic-watch threshold. |
| Source | An approved relay, event stream, feed, or supported API plus its subscription and operating policy. |
| Station | One local Cyber Space Radio installation. |
| Node | A future station enrolled in a consent-only federation. |
| Match score | Relevance evidence about text, not a score about a person. |
| Stop listening | Close local source connections/polling and stop outbound reporting. |
| Stop network | A future control-plane action that ends operating leases for enrolled nodes. |

## Phase 0 scope

- Define the implementation-foundation criteria and the Phase 0A/0B evidence
  needed to select it.
- Define the local-only product, user, terminology, and non-goals.
- Define watches, exclusions, precision-first matching, and explanations.
- Define the structural classifier that separates standalone messages from
  replies, mentions, groups, reposts, and direct messages.
- Define the approved-source boundary and source register.
- Define minimum signal records, retention, deletion, and purge.
- Design equivalent Windows and Android operator experiences and all primary
  foreground, background, locked, stopped, degraded, and suspended states.
- Define the matcher evaluation corpus and Phase 1 acceptance evidence.
- Produce a sequenced roadmap and implementation backlog.
- Preserve federation as a reviewed future design, not executable software.

## Explicit non-goals

- Listening to the whole Internet.
- Crawling, link following, source discovery, browser scraping, or packet
  interception.
- Private, paywalled, authenticated, or access-controlled sources unless a
  later adapter is explicitly authorised and documented.
- Identity resolution, deanonymisation, person scoring, profiling, targeting,
  contact discovery, or automated outreach.
- Decisions affecting a person's access, reputation, opportunities, or safety.
- Self-installation, self-propagation, stranger enrollment, remote rules,
  peer-supplied fetch targets, or arbitrary code execution.
- Public hosting, multi-tenancy, or operational federation in Phase 0 or Phase
  1. Phase 0B covers only a bounded phone feasibility spike; the standalone
  phone station itself is a Phase 1 product.
- Claims of literal zero resource usage or instant global failure knowledge.
- A claim that software design alone provides legal clearance.
- Publishing, replying, reacting, following, or contacting a message author.

## Phase 1 functional requirements

| ID | Requirement |
|---|---|
| FR-01 | The operator can create, pause, resume, edit, and delete a watch. |
| FR-02 | A watch contains idea phrases, exclusions, and a visible threshold. |
| FR-03 | Only sources present in the approved-source register can run. |
| FR-04 | A source failure cannot stop other sources in the same scan. |
| FR-05 | Candidates are normalised and deduplicated before local matching. |
| FR-06 | Each signal shows its source provenance, original link, observed time, and retention mode. Topic matches show every matching watch with its score and plain-language explanation; a manually kept non-match shows `Kept manually`. |
| FR-07 | Noise, excluded candidates, duplicates, malformed entries, and oversized entries are not persisted as content. |
| FR-08 | Full public message text is stored only for topic-matched signals or an explicit local `Keep`, encrypted at rest, and expires after seven days unless deliberately kept; author profiles and inferred identity remain off. |
| FR-09 | The operator can delete one complete signal, remove one source's provenance from all signals, delete expired signals, or purge all local data. Source-provenance deletion deletes a signal only when no other observed source remains. |
| FR-09A | Removing a source stops its connection but retains historical provenance until the operator separately deletes that source's data. |
| FR-10 | STOP LISTENING prevents new polling and outbound reporting and shows a truthful stopped state. |
| FR-11 | Source polling honours source-specific intervals, timeouts, conditional requests, and retry limits. |
| FR-12 | Incoming content cannot add a source, watch, peer, command, or fetch target. |
| FR-13 | Relay candidates must pass protocol validation and standalone-message classification before relevance matching or persistence. |
| FR-14 | Replies, quotes, reposts, direct messages, recipient-tagged events, and group/channel events are excluded by structure, not guessed from prose. |
| FR-15 | Streaming adapters enforce approved endpoints, event kinds, replay windows, reconnect backoff, event-rate ceilings, and bounded queues. |
| FR-16 | Discovery mode shows a bounded in-memory waterfall and aggregate activity for standalone shouts. No unmatched item persists without an explicit local `Keep`. |
| FR-17 | Tuned mode automatically persists and reports only topic-matched shouts; an explicit local `Keep` may persist one valid waterfall item in either mode. Changing modes alone cannot retroactively persist volatile content. |
| FR-18 | STOP LISTENING closes source activity and clears volatile waterfall/Junk content while leaving deliberately persisted matches and kept messages untouched. |
| FR-19 | Plaintext matched-message content cannot appear in SQLite pages, journals/WAL, temporary files, logs, exports, backups, crash reports, or browser storage. |
| FR-20 | Every launch begins stopped and locked; a manual passphrase unlock is required before listening can start or persisted message text can be viewed. |
| FR-21 | STOP LISTENING closes connections, prevents reconnects, clears volatile previews, discards usable in-memory content keys, and leaves only encrypted persisted records. |
| FR-22 | There is no passphrase recovery or decryption bypass; a lost-passphrase reset requires explicit ciphertext purge before a new station key is created. |
| FR-23 | Windows and Android installations each support the complete local lifecycle independently: configure, unlock, discover, tune, listen, persist matches, expire, delete, stop, and reset. |
| FR-24 | Mobile status distinguishes Listening, background-limited, offline, locked, stopped, and degraded from a retrospective `Coverage gap / previously suspended` state recorded after execution resumes. It never claims to report live while the OS has suspended or removed the process. |
| FR-25 | Optional pairing cannot be required for either station to operate and cannot silently copy raw messages, keys, passphrases, sources, or watches. |
| FR-26 | After an explicit Start, Android may continue off-screen only through an operator-visible foreground service. Its ongoing notification shows state and STOP; STOP terminates the service and prevents automatic restart. |
| FR-27 | Android may issue a generic local `New signal found` notification for a durable topic match. It contains no message text, source, author, score, explanation, or stable event reference, and opening it requires local unlock. |
| FR-28 | No project-operated infrastructure receives message content, event identifiers, source history, watch terms, matches, reports, author evidence, or listening state; all Phase 1 listening traffic flows directly between the local station and an operator-enabled public source. |
| FR-29 | Nostr Start and reconnect request no more than the preceding 60 seconds; repeated events are deduplicated locally, and a longer interruption is reported as a coverage gap without deeper backfill. |
| FR-30 | Every deduplicated Nostr shout shows `Damus`, `nos.lol`, or `Both`; delivery through the second relay updates the existing item's provenance without adding activity or creating another signal. |
| FR-31 | Opening a Nostr signal renders it locally without external requests. An optional `Open externally` action uses an operator-configured HTTPS viewer only after confirmation and sends only a safely encoded stable event reference. |
| FR-32 | External Nostr viewing defaults to disabled with no configured viewer on installation and reset; the action remains absent until enabled deliberately in local Settings. |
| FR-33 | Conservatively identified spam/flood events are suppressed before the waterfall and matcher. While blocked they increment only a non-identifying `Noise blocked` counter and cannot produce persistence or notifications. |
| FR-34 | The volatile Junk drawer holds at most 50 valid spam-suppressed events or five minutes, whichever is smaller, and clears on STOP, restart, expiry, eviction, or `Clear Junk`. Invalid or malformed events never enter it. |
| FR-35 | `Restore once` moves one verified Junk event into the waterfall under a session-only exact-event override and runs the normal matcher without creating a permanent spam rule. |
| FR-36 | A topic definition persists until paused or deleted. `Keep future matches`, off by default, makes only subsequent matches non-expiring; applying it to existing signals requires a separate previewed confirmation. |
| FR-37 | `Keep` on one valid message adds manual protection against automatic expiry and capacity eviction. Removing that manual reason starts a new seven-day expiry only when no other retention reason remains. Explicit deletion, purge, reset, and uninstall remain authoritative. |
| FR-38 | Each device independently enforces a configurable 100 MiB default hard capacity over all application-owned durable data and transaction headroom, with warnings at 80% and 95%. |
| FR-39 | At capacity, expiry and oldest-unkept pruning run first; kept data is never silently evicted. If protected data fills the quota, durable saving stops truthfully while bounded volatile listening continues. |
| FR-40 | Lowering capacity previews pruning and is rejected when kept data plus required headroom cannot fit without deleting protected records. |
| FR-41 | Confirmed source-data deletion removes sole-source Kept signals after separately warning and counting them; multi-source Kept signals survive under their remaining provenance. Keep protects only against automatic expiry and eviction. |
| FR-42 | The live waterfall retains at most the newest 100 valid standalone shouts and no item longer than ten minutes. The first limit reached evicts the oldest unkept item; a successfully Kept item has already moved to encrypted durable storage. |
| FR-43 | A collapsed waterfall card shows at most 280 user-perceived Unicode characters without splitting a grapheme; expanding reveals the complete accepted message locally and performs no external request. |
| FR-44 | A decoded public-message body is accepted only when it is at most 16,384 UTF-8 bytes. A larger body increments only a non-identifying `Oversized` counter and is discarded before normalization, spam classification, Junk, waterfall display, matching, notification, or persistence. |
| FR-45 | An assembled incoming Nostr event-envelope message is accepted only when it is at most 65,536 UTF-8 bytes. A larger envelope increments only the aggregate `Oversized` envelope reason and is rejected at the transport boundary before JSON event-field parsing where the platform permits. Fragmentation cannot bypass the limit. |
| FR-46 | Before first Start, the station asks what the operator wants to listen for using an unselected, multi-select starter-topic catalogue that includes relationships/dating, gossip/drama, friendship/family, other broad interests, and a custom topic. Selections create editable local draft watches; `Skip and explore` starts Discovery with no active watch. |
| FR-47 | Topic browsing and selection cause no source request or listening-data egress. An unvalidated starter-template version is visibly preview-only and cannot automatically persist or notify until it passes the accepted matcher gate. |
| FR-48 | The operator can create a manual topic during onboarding or later from Watches. A skippable, replayable local tutorial explains the idea statement, alternative phrasings, exclusions, threshold/breadth, preview evidence, retention, and the distinction between saving a draft and enabling it. |
| FR-49 | Manual-topic preview uses bundled synthetic fixtures and may use current waterfall items only in memory. Typed topics, examples, exclusions, labels, and preview decisions remain local; deleting the watch or resetting the station removes them within that scope. |
| FR-50 | Signals from every watch appear in one unified inbox with `All topics` as the default and local topic/source/state filters. One deduplicated shout is one row, one unique-signal count, one notification, and one encrypted message copy even when several watches match; all matching watch decisions remain inspectable. |
| FR-51 | A signal owns a set of retention reasons. Manual Keep and every keep-enabled matching topic independently protect the one signal; it remains non-expiring while any reason remains. Removing the final reason after confirmation starts a fresh seven-day expiry. |
| FR-52 | Enabling or disabling `Keep future matches` affects future matches only. Applying or removing that topic's protection on existing signals requires a separate item/byte preview and confirmation and cannot remove protection supplied by another reason. |
| FR-53 | Deleting a topic previews other-topic survivors, manually kept survivors, ordinary deletions, protected deletions, and estimated bytes separately. Confirmation removes that topic's definition, match decisions, and retention reasons transactionally; cancellation or failure changes nothing. |
| FR-54 | A signal surviving topic deletion keeps all other matches and retention reasons. Final-reason removal starts a fresh seven-day expiry when another match remains; a manual-only survivor becomes `Kept manually`; a signal with no remaining match or retention reason is deleted. |
| FR-55 | Every unlocked Signals session begins at `All topics`, newest first by initial observed time with a deterministic tie-breaker. Filter, sort, and scroll state may survive only within that unlocked session and clears on lock, STOP, restart, or reset without durable/browser storage. |
| FR-56 | A durable signal starts `New` and becomes `Reviewed` only after its unlocked local inspector renders successfully. Row display, filtering, deletion preview, or tapping a locked notification does not review it; multi-topic signals have one shared review state. |
| FR-57 | `Mark as new` clears the review timestamp without re-notifying, recounting, reordering, rematching, or changing retention. Review state is device-local metadata, survives restart, never leaves the station, and is removed with the signal. |
| FR-58 | `Mark visible as reviewed` previews the exact count of currently New signals in the complete filtered result and, after confirmation, atomically marks only that snapshotted set. Later arrivals remain New; bodies are not opened/decrypted and no other signal behaviour changes. |
| FR-59 | A local signal has an opaque random ID and deduplicates only on protocol identity/version, never identical text. Nostr uses verified event ID; Jetstream uses AT URI plus CID for a post version and retains the AT URI as its upstream-deletion key. |
| FR-60 | An authenticated Jetstream delete for an approved post collection immediately and idempotently removes every local version of that AT URI, including Kept content, leaving only a content-free audit and aggregate local notice. Invalid, unauthenticated, wrong-collection, and unapproved-source deletes remove nothing. |
| FR-61 | Only a validated watch version may automatically persist or notify. Bundled and custom promotion evidence freezes the definition, matcher, authorised corpus, labels, and development/held-out split; records per-source precision/recall and approval; and is invalidated by any input change. Draft and preview-only watches may still highlight volatile Discovery items and permit an explicit one-item Keep. |

## Success measures

The matcher values are owner-approved gates. Windows resource budgets remain
proposed; phone budgets and the combined product estimate remain pending Phase
0B physical-device evidence.

- At least 85% precision and 60% recall on a held-out, labelled corpus of at
  least 200 candidates with at least 50 positive examples.
- Every persisted signal has a random local signal ID, protocol-derived
  deduplication key and source-object key, approved source ID set, observed
  time, derived retention state, and complete retention-reason set. Topic
  matches also have a match explanation and validation-evidence version. A
  public URL is included only when the protocol supplies or safely derives one.
- Zero ignored candidate bodies persisted in functional tests.
- Zero unmatched waterfall content written to the database, files, logs,
  exports, backups, or reports without an explicit tested `Keep` action.
- A known plaintext sentinel from a matched message is absent from every
  at-rest artifact while the unlocked UI can recover the exact message.
- Startup and automatic restart remain locked and stopped until a manual local
  unlock succeeds.
- A lost-passphrase reset cannot recover any prior message and leaves no old
  ciphertext or wrapped key in active storage.
- Exact, by-source, expiry, and purge deletion pass end to end.
- A stopped station has no live source connection, issues no polling or report
  requests, and does not reconnect.
- Both Windows and Android pass the full lifecycle independently, and Android
  never reports active listening during a proven OS-suspension gap.
- Shared fixtures produce equivalent classification, match, persistence,
  expiry, deletion, and STOP decisions on both platforms.
- A 500-candidate local evaluation completes in under five seconds on the
  agreed reference machine, excluding source network time.
- Phase 1 steady-state memory stays below 250 MiB and local application data
  below 100 MiB under the seven-day reference fixture.
- Every enabled source has a complete, current source-register row.
