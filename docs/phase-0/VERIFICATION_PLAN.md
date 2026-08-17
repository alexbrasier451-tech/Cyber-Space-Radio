# Verification plan

## Purpose

Phase 1 is complete only when the original user journey works end to end and
the product's boundaries are demonstrated, not merely documented.

## Traceability

Every functional requirement in `PROJECT_CHARTER.md` must map to at least one
automated test and, where a human interaction is involved, one UI acceptance
case. Test reports record the application commit, fixture version, matcher
version, operating system/version, device model, and reference machine.

The requirement-level targets are enumerated in the
[Phase 1 traceability matrix](PHASE_1_TRACEABILITY_MATRIX.md). They are planned
test IDs, not claims that Phase 1 tests already exist. A requirement is not
complete until its mapped automation passes and each applicable UI case has
recorded evidence on the target platform.

## Matcher evaluation

### Corpus

- At least 200 candidates covering both Nostr and AT Protocol event structures,
  plus synthetic variants of every structural event class.
- At least 50 known-positive examples.
- Known negatives include replies, recipient-tagged notes, group/channel
  messages, direct messages, quotes, reposts, common near-misses, ambiguous
  language, spam, duplicates, markup, and exclusion phrases.
- Resource fixtures include ASCII and multibyte Unicode bodies immediately
  below, exactly at, and immediately above the 16,384-byte boundary.
- Transport fixtures include single-frame and fragmented Nostr event envelopes
  immediately below, exactly at, and immediately above 65,536 UTF-8 bytes,
  including a small body surrounded by an excessive tag array.
- Labels are `relevant`, `not relevant`, or `ambiguous`, with a short rationale.
- Split before tuning into development and held-out sets.
- Corpus text is synthetic, licensed, or stored with documented permission.
- Each evaluated watch version freezes its definition hash, matcher version,
  corpus/label versions, and split before the held-out run. Editing any input
  invalidates the result and returns the watch to preview-only.
- The evidence package records label owner and approval, per-source results,
  timestamp, software version, and exact metric calculation. Bundled topics are
  approved by the project owner; a custom topic is labelled and promoted only
  by its local operator.

### Measures

- Precision is the primary gate.
- Recall, false positives per 100 candidates, and false negatives are reported.
- Results are shown per watch and source, not only as one aggregate.
- The Phase 0A comparison reports standalone yield, topic-match yield,
  duplication, spam/noise, event rate, bandwidth, memory, reconnect behaviour,
  and adapter complexity separately for Nostr and Jetstream.
- Accepted initial gate: precision >= 0.85 and recall >= 0.60 on the held-out
  set.
- A matcher that misses the precision gate cannot create durable records or
  reports even if its recall is high. Recall remains visible and must meet its
  floor; the volatile waterfall provides broader discovery without lowering
  the persistence gate.
- A local embedding model is adopted only if it improves agreed measures over
  the accepted deterministic matcher without breaking resource or explanation
  requirements.

## Functional evidence

| Area | Required cases |
|---|---|
| Sources | Approved endpoint succeeds; absent/expired/paused source cannot connect or fetch; source failure is isolated. |
| Streaming | Approved event filter, signature/envelope validation, one connection per approved Nostr relay, exactly bounded 60-second Start/reconnect replay, no deeper outage backfill, per-relay event-rate cap and queue cap, disconnect, reconnect backoff, truthful coverage gaps, cursor recovery, and cross-relay event-ID deduplication before any visible or durable output. |
| Polling | Where applicable: minimum interval, conditional request, timeout, redirect, retry, `429`, and item/byte/page limits. |
| Parsing | RSS, Atom, malformed XML, invalid UTF-8, hostile markup, bounded envelopes/tags, and duplicate fields. |
| Incoming envelope | Accept assembled Nostr event messages of 65,535 and 65,536 UTF-8 bytes; reject 65,537 bytes before JSON event-field parsing where supported. A fragmented message uses its assembled size. Transport closure backs off without a tight reconnect loop. Only the aggregate `Oversized` envelope reason changes. |
| Oversized body | Measure the decoded body before normalization. Accept 16,383- and 16,384-byte ASCII and multibyte UTF-8 fixtures; reject 16,385 bytes. Rejection increments only `Oversized`, exposes no content, and cannot reach spam, Junk, waterfall, matching, notification, or persistence. |
| Standalone classification | Top-level public note accepted; reply, quote, repost, direct/recipient/group event rejected before relevance matching. |
| Matching | Positive, negative, ambiguous, exclusion, alternate phrasing, threshold boundary, and matcher version. |
| Unified signal inbox | Each unlock defaults to `All topics`, newest first by initial `observed_at` with stable-ID tie-break; single- and multi-topic filters; combined topic/source/state filters; clear filters; chip overflow and accessibility. Filters/scroll survive current-session navigation but clear on lock, STOP, restart, and reset with no durable/browser artefact. A fixture matching three watches produces one row, count, notification, ciphertext copy, and three decisions; later provenance/matches do not reorder it. |
| Review state | New signal begins `New`; row display, filtering, deletion preview, and locked notification tap do not change it; successful unlocked inspector render marks the one multi-topic signal `Reviewed`; restart preserves it independently per device. `Mark as new` reverses it with no notification, count, order, match, Keep, expiry, network, or duplicate-record effect; deletion removes it. |
| Batch review | `Mark visible as reviewed` counts all unique New signals in the complete filtered result, not only the rendered page; zero disables it. Confirm updates exactly the previewed ID snapshot atomically; cancellation/failure changes nothing; concurrent later arrivals remain New. No message decryption or notification, matching, order, Keep, expiry, or network side effect occurs. |
| Persistence | Full text only for validated topic matches or explicit Keep; authenticated encryption before durable storage; no profiles; random local signal ID; protocol-identity deduplication rather than content-identity merging; seven-day ordinary expiry; non-expiring kept message/topic modes. |
| Keep lifecycle | Add/remove manual Keep; one and several topic reasons; manual plus topic reasons; future-only topic on/off changes; previewed application/removal on existing records; intermediate reason removal remains kept; final reason removal starts a fresh seven-day expiry; STOP/restart survival; explicit delete, purge, reset, and uninstall. |
| Storage capacity | Independent 100 MiB default per device; total durable-byte accounting including WAL/headroom; 80%/95% warnings; expired then oldest-unkept pruning; no kept eviction; truthful storage-full mode; rejected over-small capacity; volatile operation continues without false saved claims. |
| Encryption | Manual unlock, wrong passphrase, throttling, tampered ciphertext, unique nonce, restart, lock on STOP, rotation, expiry, backup, no-recovery passphrase loss, purge/reset, and unavailable-key cases. |
| Hybrid output | Waterfall is fixed-count and fixed-age; unmatched content never reaches disk, logs, browser storage, exports, backups, reports, or federation; mode changes are not retroactive. |
| Waterfall limits | The 101st item evicts the oldest unkept item; an item expires at ten minutes even below capacity; simultaneous age/count pressure is deterministic; successful Keep moves the item durably before volatile removal; failed Keep leaves it subject to both limits. |
| Waterfall preview | ASCII, emoji, combining marks, right-to-left text, line breaks, markup-like text, and exactly 279/280/281-grapheme fixtures render safely. Collapse never exceeds 280 user-perceived characters or splits a grapheme; Expand uses the same local item and causes zero network requests. |
| Stop | In-flight completion policy; no new requests after stop; restart stays stopped until resume. |
| Deletion | Exact ID/URL, source provenance, watch, expiry, purge, idempotency, preview counts, and failure recovery. Source deletion separately counts/warns for sole-source Kept signals, removes them only after named confirmation, and preserves multi-source Kept signals under their remaining provenance; exact deletion removes the whole signal. An authenticated Jetstream delete removes all local versions of its AT URI immediately even when Kept, leaves only a content-free audit/count, and cannot be forged across collection or source boundaries. Topic deletion separately counts other-topic survivors, manual-Keep survivors, ordinary deletions, and protected deletions; atomically removes only that topic's configuration/decisions/reasons; starts fresh expiry after final-reason removal when another match survives; and fully deletes records left with neither match nor reason. |
| UI | First run, empty, new signal, degraded, stopped, offline, expired detail, and delete confirmation. |
| Topic onboarding | No topic is preselected. Multi-select starter cards include relationships/dating, gossip/drama, and friendship/family. `Skip and explore` creates no watch; selected cards create editable local drafts; selection causes zero network requests and does not start listening. |
| Manual-topic tutorial | Create during onboarding and from Watches; complete and skip the four steps; replay from Help; verify idea, alternatives, exclusions, breadth, threshold, preview explanation, Save draft, and separate Enable. Synthetic and volatile previews leave no durable content copy. |
| Watch promotion | New and edited watches are preview-only; evidence package contains frozen definition/corpus/split/version/label owner; held-out gate controls automatic persistence and notification; a passing version can be promoted; every edit invalidates it; deliberately saved labelled examples are encrypted and follow watch deletion/reset. |
| Mobile lifecycle | Explicit Start, visible ongoing foreground-service notification, off-screen listening, notification STOP, background-permitted, background-limited, locked-device, process termination, restart, network change, and bounded catch-up. Suspension/process-removal is reported retrospectively as a coverage gap after execution resumes; the app never claims it emitted a live state while not running. Status must match proven execution rather than operator intent. |
| Cross-platform parity | The same fixtures produce the same structural classification, match decision, persistence decision, expiry, deletion result, and STOP result on Windows and Android. |
| Match notification | Exactly one generic local notice for a durable topic match; none for waterfall/noise; no sensitive fields; tap opens locked Signals; no email, webhook, or remote push. |
| No-backend egress | Capture outbound traffic during normal, error, crash, notification, export, backup, update, STOP, purge, and uninstall paths; prove that listening data reaches only enabled public sources and never project-operated infrastructure. Verify any Windows local UI binds to loopback only. |
| Relay provenance | A one-relay event shows that relay's badge; the same verified event arriving later from the second relay updates the existing item to `Both` without incrementing activity, repeating a match notification, or creating a second durable record. |
| External Nostr viewing | Fresh installation and reset default to disabled/null. Opening list and inspector views produces no external request. With no configured viewer, no external action is offered. A confirmed action opens exactly the configured HTTPS origin with only the encoded event reference; cancellation, malformed configuration, message URLs, and redirects fail closed. |
| Spam suppression | Protocol-valid, within-size exact/near-repeat, burst, and mechanically repetitive fixtures are suppressed before waterfall/matching and increment only `Noise blocked`; legitimate repeated phrasing and controversial content remain visible. While blocked, events cannot persist, notify, or create a permanent identity rule. |
| Volatile Junk | Only valid spam-suppressed events enter; maximum 50 and five-minute expiry both enforce; capacity, expiry, Clear, STOP, and restart remove content. No durable or external artefact exists. `Restore once` re-enters waterfall/matching for that exact event only and creates no permanent rule. |

## Safety and abuse evidence

- A relay event, feed entry, title, author, URL, tag, or markup cannot add a
  source, watch, subscription, or outbound destination.
- No content string becomes HTML, a shell command, a template instruction, a
  log line, or a fetch target.
- Redirects cannot escape the approved endpoint policy.
- Credentials, cookies, query tokens, and request headers never enter logs,
  exports, match explanations, or federated digests.
- A unique plaintext sentinel from a matched message is absent from the main
  database, journal/WAL, temporary files, logs, browser storage, exports,
  backups, crash reports, and federated output.
- Ciphertext modification fails closed and never returns partial plaintext.
- Passphrases and usable unwrapped keys are absent from configuration,
  arguments, environment, database, journals/WAL, logs, crash reports, browser
  storage, exports, and backups.
- A locked station cannot connect, poll, reconnect, view saved plaintext, or
  enter Listening state.
- A suspended or background-limited phone cannot present itself as actively
  listening; the most recent proven source activity and any coverage gap remain
  visible after resume.
- Android off-screen listening cannot begin without explicit Start and an
  ongoing notification. Notification STOP terminates the service; process
  restart, device reboot, alarms, and schedulers do not silently resume it.
- Match notifications contain only the approved generic wording and a local
  route. Message text, source, author, score, explanation, event ID, watch name,
  and permalink are absent from notification records and lock-screen history.
- Network captures contain no project destination carrying message text, event
  identifiers, author evidence, watch terms, source history, matches, reports,
  or listening state. Generic update traffic is separately allowlisted and
  independent of listening state.
- No recovery artifact or bypass can decrypt a record. Lost-passphrase reset
  purges ciphertext and the wrapped key before creating a new key, and the new
  key cannot decrypt any retained old backup.
- Incoming data cannot trigger outreach, webhooks, code, peer changes, or
  arbitrary network requests.
- Nostr signal text, tags, and relay metadata cannot configure or invoke an
  external viewer. No viewer request occurs before an explicit confirmed action,
  and its URL contains no message text, watch term, score, or local history.
- Parsing and matching remain bounded under malformed, adversarial, or very
  repetitive content.
- Spam decisions are explainable from versioned structural/repetition evidence,
  not an author's identity, opinion, political position, sentiment, or relay.
- A plaintext sentinel from a Junk item is absent from databases, files, logs,
  browser storage, exports, backups, crash reports, notifications, and external
  requests before and after expiry, Clear, STOP, and restart.
- A plaintext sentinel from a 16,385-byte `Oversized` item is absent from Junk,
  waterfall, matcher traces, databases, files, logs, browser storage, exports,
  backups, crash reports, notifications, and external requests. Only the
  non-identifying `Oversized` count changes; `Noise blocked` does not.
- A sentinel in a 65,537-byte envelope, including a tag-heavy envelope whose
  body remains below 16,384 bytes, is never exposed to event-field processing
  where the transport permits early rejection and is absent from every content
  output. Only the aggregate `Oversized: envelope` reason changes.
- Stop and delete operations are authenticated when account mode is enabled and
  protected against cross-site request forgery.

## Resource budgets

Proposed Windows reference budgets for Phase 1:

- 500-candidate local evaluation under five seconds, excluding network time;
- steady-state process memory below 250 MiB;
- default seven-day application data below 100 MiB for the reference fixture;
- maximum source response 5 MiB unless a lower source-specific limit applies;
- maximum accepted decoded public-message body 16,384 UTF-8 bytes, independent
  of stricter frame, envelope, tag, or source-specific limits;
- maximum accepted assembled incoming Nostr event message 65,536 UTF-8 bytes,
  independent of its WebSocket fragmentation;
- maximum 500 candidates per polling scan and a configurable per-minute stream
  event ceiling in the first release;
- no unbounded queue, retry, thread, record, or log collection;
- a stopped process performs zero scheduled outbound requests;
- the durable store, indexes, WAL/journals, audits, and reserved transaction
  headroom remain within the configured capacity under ordinary, keep, pruning,
  failed-write, crash-recovery, and capacity-change cases; and
- the volatile waterfall contains at most 100 items, retains no item longer
  than ten minutes, and is empty after restart or STOP LISTENING.

Budgets are ceilings, not targets. The test report records actual values.
Phase 0B must establish separate phone budgets for foreground and background
operation on physical devices, covering battery use, data transfer, memory,
storage, thermal behaviour, reconnect frequency, and OS-enforced execution
limits. The Windows budgets must not be copied to phone without measurement.

## UI and accessibility evidence

- Keyboard-only completion of first run, review, stop, resume, and deletion.
- Keyboard, touch, and screen-reader completion of topic selection and the
  create-your-own tutorial, including skip, back, validation errors, and Help
  replay.
- WCAG 2.2 AA automated checks plus manual focus, error, zoom, contrast, and
  reduced-motion review.
- Layout verified at 360, 736, and 1024 CSS pixels.
- Windows 11 and Android are verified separately. An emulator may support
  layout and fixture tests but cannot replace physical-
  device lifecycle, notification, lock-screen, battery, or suspension evidence.
- Status never relies on colour alone.
- Signal score always includes visible explanation and source.
- Destructive actions state exact scope and do not combine stop with deletion.

## Phase 1 end-to-end decision case

The gate case runs independently from a clean installation on Windows 11 and
on Android, using synthetic plus approved test sources:

1. configure operator contact, approved endpoints, event kinds, structural
   exclusions, and bounded replay;
2. launch and prove the station is stopped and locked;
3. unlock with the manual passphrase, create a watch with positives, negatives,
   and exclusions, then start listening;
4. ingest a mixed fixture containing one top-level true match plus noise,
   duplicate, exclusion, reply, mention, quote, repost, group message, direct
   message, malformed event, 16,385-byte body, and 65,537-byte envelope; prove
   the last two increment only their aggregate `Oversized` reasons and never
   appear in Junk;
5. show standalone activity in the volatile waterfall, then show exactly one
   source-attributed topic-matched signal with explanation in the durable inbox;
6. stop listening and prove the stream closes, no reconnect occurs, no further
   outbound request is issued, the waterfall clears, and saved text locks;
7. prove unmatched waterfall content expired without any durable copy;
8. unlock the matched signal again, recover its exact text with the correct
   key, and prove a wrong key or modified ciphertext fails closed;
9. search every at-rest artifact for the plaintext sentinel and find none;
10. delete the signal and prove it is absent from UI, store, export, and backup
   policy scope; and
11. create a second encrypted fixture, simulate a lost passphrase, prove there
    is no recovery path, complete `PURGE AND RESET KEY`, and prove the new key
    cannot decrypt the old ciphertext; and
12. repeat the complete case while the other device is absent or offline, then
    prove the result does not depend on pairing; and
13. rerun the full upstream and downstream test suites.

Any red step returns the product to implementation. A component test cannot
replace this integrated gate.
