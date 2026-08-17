# Roadmap

The roadmap is gate-driven. Later phases are not promises; each begins only when
the preceding product, safety, and evidence gate passes.

## Phase 0 - Definition and readiness

**Goal:** turn the idea into an implementation-ready local product.

Deliverables:

- codebase decision and adoption strategy;
- product charter and vocabulary;
- UI concept and complete state inventory;
- technical and data contracts;
- source approval template;
- verification plan and quality thresholds;
- risk and decision log; and
- ordered Phase 1 backlog.

Gate:

- owner approves the primary use case, initial source families, product
  boundary, provisional foundation direction, phone scope, UI direction,
  record schema, and quality measures;
- no blocking decision remains; and
- nothing has been deployed or federated.

## Phase 0A - Relay suitability spike

**Goal:** confirm that approved public streams contain a useful, technically
identifiable class of standalone messages before committing the production
source architecture.

The 2026-08-17 source review qualifies Jetstream v2 US East,
`relay.damus.io`, and `nos.lol` as approved-disabled candidates for a bounded
local-client comparison. Nostr is the preferred first probe because public
kind-1 notes are the closer fit for standalone "shouts in the dark"; Jetstream
remains the documented comparison source. The Nostr probe uses both approved
relays concurrently and deduplicates their overlap locally by event ID.

An aggregate-only Nostr body-size probe is complete: 340
within-run-deduplicated standalone observations supported a 16,384-byte UTF-8
message-body ceiling. A separate defensive decision caps the assembled incoming
Nostr event message at 65,536 UTF-8 bytes. It did not measure the complete
usefulness/noise question and does not replace the cross-source gate below.

**2026-08-17 result: SOURCE/TRANSPORT PASSED; OVERALL PHASE 0A NOT PASSED.** The
[comparison report](PHASE_0A_COMPARISON_REPORT.md) records a repaired compliant
60-second all-source run: 97 unique valid Nostr events, 72 unique standalone
Nostr shouts, 215/215 valid Nostr signatures, and 103 standalone Jetstream
posts from its first 300 bounded deliveries. The public-contact gate, STOP,
privacy, source bounds, and adapter compatibility checks passed. Jetstream's
XRPC envelope mismatch was diagnosed at the normalization boundary, repaired,
and confirmed by the original end-to-end rerun plus a fresh live case. The
overall gate remains red because held-out matcher precision is 57.14% against
the required 85%, and corpus-label approval remains outstanding.

Deliverables:

- synthetic fixtures for standalone notes, replies, mentions, quotes, reposts,
  groups, direct messages, malformed events, and duplicates;
- bounded read-only adapters for both approved comparison families: Nostr
  public text notes and AT Protocol Jetstream posts;
- a short-lived, content-minimising sample report covering message volume,
  standalone proportion, spam/noise, reconnect behaviour, and resource cost;
- the completed aggregate Nostr size report and a cross-source implementation
  of the 16,384-byte body gate, plus a 65,536-byte Nostr envelope gate, with a
  distinct `Oversized` counter;
- a recommendation confirming or revising the Harken adapter strategy;
- a source recommendation based on standalone yield, topic-match yield,
  duplication, spam/noise, connection stability, bandwidth, memory, and
  implementation complexity; and
- no publishing credentials, reactions, replies, following, or author contact.

Gate:

- standalone classification is deterministic for the selected protocol;
- the source is useful enough to justify Phase 1 and can be operated within
  approved limits; and
- each live source has an approved local source row, bounded operating limits,
  and recorded policy caveats; and
- the relay-adapter and classifier fit is measured for use by the Phase 0B
  production-foundation decision.

## Phase 0B - Mobile foundation and background feasibility

**Goal:** select an architecture that supports independent Windows 11 and
Android stations without making false continuous-listening claims.

**2026-08-17 result: FAIL.** The
[foundation report](PHASE_0B_FOUNDATION_REPORT.md) recommends a greenfield .NET
10 MAUI solution for the next probe and rejects Harken as the production base.
A .NET 8 Windows console probe passed ten synthetic crypto, locked-start,
WebSocket cancellation, STOP, and restart checks. This host has no MAUI/Android
toolchain, emulator, attached Android device, or Windows MSIX tools, so none of
the mandatory physical lifecycle/resource/packaging evidence exists. The
architecture recommendation is provisional and Phase 1 remains blocked.

Deliverables:

- selected minimum supported Android version and the accepted explicit-Start,
  visible-foreground-service operating mode;
- one shared behavioural contract for source gating, classification, matching,
  hybrid output, encryption, retention, deletion, and STOP;
- native foreground/background probes on physical devices, including
  suspension, restart, reconnect, notification, and locked-device behaviour;
- measured battery, bandwidth, memory, storage, and reconnect cost;
- a recorded decision between a portable shared core, platform-native cores,
  or a replacement cross-platform foundation;
- revised Phase 1 estimates and packaging plan; and
- an updated production-foundation ADR.

Gate:

- Windows and Android stations can each complete the local lifecycle without the
  other;
- the phone reports foreground, background-limited, OS-suspended, offline,
  locked, stopped, and degraded states truthfully;
- the Android ongoing notification exposes current state and STOP, and service
  termination is proven after STOP;
- mobile constraints do not weaken encryption, source approval, STOP,
  retention, or deletion guarantees; and
- the production foundation is accepted before implementation begins.

## Phase 1 - Local listening station

**Goal:** useful, bounded, independently operable Windows 11 and Android stations
built on the confirmed application foundation.

Deliverables:

- confirmed desktop/mobile foundation, shared behavioural contract, dependency
  pins, attribution, and platform packaging;
- approved-source registry and outbound request gate;
- approved relay/event adapter, signature/envelope validation, standalone
  classifier, 65,536-byte Nostr envelope gate, 16,384-byte decoded-body gate,
  bounded replay, and reconnect control;
- watches, alternatives, exclusions, and lexical-v1 matcher;
- privacy projection before persistence;
- authenticated local encryption for full durable message text, key
  handling, manual startup unlock, fail-closed locked/stopped restart, lock on
  STOP, no-recovery purge/reset, rotation, and plaintext-leak tests;
- explicit message Keep, per-topic `Keep future matches`, and independent
  retention-reason sets for multi-topic signals, and independent 100 MiB default
  hard capacity with protected-item and storage-full behaviour;
- listening desk, one unified locally filterable signal inbox with multi-topic
  deduplication, reversible local New/Reviewed state, and watch/source
  management;
- first-run multi-select topic catalogue with relationships/dating,
  gossip/drama, friendship/family, other starter templates, custom topics, and
  `Skip and explore`, plus a skippable/replayable local manual-topic tutorial;
- discovery/tuned modes, a bounded volatile waterfall, non-identifying activity
  and `Oversized` counters, a bounded volatile Junk drawer with exact-event
  restore, and proof that unmatched, oversized, or junk content has no durable
  output path;
- STOP LISTENING with proven outbound closure;
- exact, source, expiry, and purge deletion plus transactional topic deletion
  that preserves multi-topic/manual-Keep survivors and previews protected
  orphans separately;
- conditional polling where applicable plus bounded stream replay, queues,
  reconnects, and retries;
- labelled matcher corpus and regression suite; and
- operator documentation and separate desktop/mobile resource measurements.

Gate:

- all Phase 1 requirements and tests pass on fixtures and a small approved test
  source set;
- accepted precision/recall, deletion, and stop targets plus approved resource
  targets are met; and
- ignored content is not persisted.

Optional owner-controlled pairing remains outside the Phase 1 gate. It may be
considered later for watch-version coordination, deduplicated summaries,
device health, and a `STOP ALL MY DEVICES` control, but neither station may
depend on it.

## Phase 2 - Signal quality and source governance

**Goal:** improve relevance and coverage without weakening the source boundary.

Candidate deliverables:

- optional local embedding matcher, adopted only if the evaluation corpus shows
  material improvement over lexical-v1;
- per-watch tuning and richer explanations;
- approved supported-API adapters, added one at a time;
- source-policy review reminders and opt-out workflow;
- local audit summaries and reproducible evaluation reports; and
- expanded fault, parser, and resource tests.

Gate:

- every adapter has documented terms, limits, fixtures, and failure behaviour;
- local embeddings improve agreed measures within resource budgets; and
- no hosted model or notification channel is enabled silently.

## Phase 3 - Consent-only federation laboratory

**Goal:** test whether several known operators benefit from sharing minimal
digests and health evidence.

Candidate deliverables:

- three to five statically configured laboratory nodes;
- TLS 1.3 with mutual certificate authentication and per-node identity;
- compact local-origin match digests only;
- direct, observer-specific health states;
- replay protection, bounded queues, key rotation, and revocation;
- fail-closed operating leases and one-touch STOP NETWORK; and
- partition, deletion, recovery, and resource-bound evidence.

Excluded:

- discovery, dynamic enrollment, rebroadcast, raw content, peer-supplied URLs,
  remote rules, code execution, or self-propagation.

Gate: every proof requirement in `FEDERATION_DESIGN.md` passes in an isolated
environment with real certificates.

## Phase 4 - Invite-only operational pilot

**Goal:** determine whether the laboratory has sustainable real-world value.

Conditions:

- named operators and jurisdictions;
- approved operating and source model;
- rights, deletion, incident, key, and opt-out procedures;
- monitored, documented resource ceilings; and
- small, fixed membership.

Gate: every applicable release item has named evidence and an accountable
owner.

## Phase 5 - Public release decision

Public operation is not presumed. Proceed only if product value, source
permissions, privacy evidence, security testing, operational ownership, and
applicable review justify it. A decision to remain local or invite-only is a
valid outcome.
