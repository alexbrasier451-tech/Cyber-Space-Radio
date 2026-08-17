# Phase 0: definition and readiness

Status: **definition owner-approved; evidence gates open; Phase 1 blocked**

Prepared: 2026-08-14

Updated: 2026-08-17
Implementation base decision: **do not fork Harken for production; .NET 10
MAUI is the proposed cross-platform probe foundation, but Phase 0A and physical
Phase 0B evidence must pass before production implementation**

Phase 0 turns the Cyber Space Radio idea into an implementation-ready product
definition. It does not deploy a service, broaden data collection, or enable
federation.

## Decision summary

- Do not create a production fork of
  [Harken](https://github.com/VladUZH/harken). Retain its reviewed commit
  [`d0710a427dbbe712594ef3a6c25112e1d14cc027`](https://github.com/VladUZH/harken/commit/d0710a427dbbe712594ef3a6c25112e1d14cc027)
  only as a research reference unless code is deliberately reused later.
- Use a greenfield .NET 10 MAUI solution for the next Windows/Android probe;
  accept it for production only after the physical Phase 0B gate passes.
- Keep the current scripts as a Phase 0 requirements spike and regression
  reference.
- Use a shared native MAUI information architecture with explicit Windows and
  Android lifecycle/security shells. No localhost browser server, WebView
  store, or project backend is part of the proposed production foundation.
- Start with explicitly approved public relay/event streams and listen only for
  standalone public text messages: no reply, quote, repost, direct recipient,
  or group target. Perform relevance filtering locally.
- Treat RSS/Atom and supported APIs as secondary adapters and fixtures, not the
  defining Phase 1 signal surface.
- Use a hybrid output policy: show a bounded, ephemeral live waterfall and
  aggregate activity for standalone shouts, but persist and report only shouts
  that match an enabled topic watch or that the local operator explicitly
  chooses to Keep. This lets the operator explore first, tune later, preserve a
  particular discovery, or stop if the stream is not useful.
- Ask `What would you like to listen for?` before first Start. Offer unselected,
  editable starter topics—including relationships/dating, gossip/drama, and
  friendship/family—alongside custom creation and `Skip and explore`. A local,
  skippable tutorial teaches manual topics, alternatives, exclusions, breadth,
  and preview evidence without starting the listener or sending topic text away.
- Put all durable signals in one locally filterable inbox. A shout that matches
  several topics appears once with multiple topic chips and per-watch
  explanations; it creates one unique-signal count, notification, and encrypted
  message copy.
- Open each unlocked inbox at `All topics`, newest first by initial observation.
  Filters and scroll survive only within that unlocked session and clear on
  lock, STOP, restart, or reset, so a stale view cannot hide retained signals.
- New signals become `Reviewed` only after their unlocked local inspector
  renders. `Mark as new` reverses that local metadata without another alert or
  any change to order, matching, Keep, or expiry.
- `Mark visible as reviewed` previews and confirms the exact set of New signals
  in the complete current filtered result; later arrivals remain New and no
  message body is opened or decrypted by the batch action.
- Manual Keep and every keep-enabled matching topic contribute independent
  protection reasons to that one signal. It remains non-expiring while any
  reason remains; confirmed removal of the final reason starts a fresh
  seven-day expiry.
- Deleting a topic previews survivors and deletions separately. Signals still
  matched by another topic or protected by manual Keep survive without the
  deleted topic's decision/reason; records left with neither are deleted, with
  protected deletions called out separately before confirmation.
- Compare Nostr public text-note streams with AT Protocol Jetstream during the
  bounded Phase 0A spike. Select the production Phase 1 source from measured
  standalone-message yield, noise, operating cost, and adapter fit.
- The 2026-08-17 source review approves-disabled Jetstream v2 US East,
  `relay.damus.io`, and `nos.lol` for the bounded local-client comparison.
  Nostr is the preferred first probe; incomplete relay terms remain recorded
  operational caveats rather than blockers.
- An aggregate-only Nostr size probe observed 340 within-run-deduplicated
  standalone messages: approximately 297 UTF-8 bytes on average, 195-byte
  medians, a sub-800-byte 95th percentile, and a 4,585-byte maximum. Phase 1
  therefore accepts message bodies through 16,384 UTF-8 bytes and discards
  larger bodies under a separate non-identifying `Oversized` count, not spam.
  Independently, an assembled incoming Nostr event message is capped at 65,536
  UTF-8 bytes so wrappers and tags cannot bypass the body boundary.
- Operate with no Cyber Space Radio backend: each installation connects
  directly to its sources, performs all listening work locally, and never sends
  messages, event identifiers, watch phrases, matches, or history to us.
- Retain full public text only for topic-matched shouts or an explicit local
  Keep, encrypted locally. Ordinary matches expire after seven days; kept
  messages and future matches from a keep-enabled topic do not auto-expire.
  Enforce an adjustable 100 MiB default hard capacity per device, never silently
  evicting kept data. Keep minimal source/event evidence and exclude profiles
  and inferred identity.
- Require a manual passphrase after every launch. Startup is stopped and
  locked; listening cannot begin while locked; STOP LISTENING closes source
  activity and removes the usable content key from process memory.
- Provide no recovery key, escrow, hint, or bypass. A lost passphrase means
  retained records cannot be decrypted; the operator may explicitly purge the
  ciphertext and initialise a new key.
- Use a precision-first durable-match gate: precision >= 0.85 and recall >=
  0.60 on the held-out corpus. The live waterfall carries broader discovery
  without weakening the persisted-signal threshold.
- Make Windows 11 and Android installations independently capable stations. Each
  owns its sources, passphrase, matcher, encrypted store, retention, deletion,
  and STOP state. Pairing is optional and cannot be required for operation.
- On Android, an explicit Start may continue listening off-screen through a
  visible ongoing foreground-service notification. STOP terminates that
  service, prevents restart, clears volatile previews, and locks saved text.
- A topic match may trigger a generic local `New signal found` notification.
  It contains no message, source, author, score, or explanation; reviewing the
  signal requires a fresh local unlock. Email and webhooks remain disabled.
- Use `Cyber Space Radio` as the product name and `Public-source listening
  console` as its factual subtitle in product surfaces and release material.
- Treat a signal as matched public text, not as a person or a claim about the
  author's identity, intent, or beliefs.
- Keep federation disabled until the local product proves useful and the
  separate federation laboratory gate passes.

## Documents

1. [Project charter](PROJECT_CHARTER.md) - purpose, users, scope, non-goals,
   requirements, success measures, and vocabulary.
2. [Technical foundation](TECHNICAL_FOUNDATION.md) - codebase choice,
   architecture, data contracts, and adoption strategy.
3. [UX and UI concept](UX_UI_CONCEPT.md) - information architecture, screens,
   flows, states, interaction rules, and visual direction.
4. [Data and source policy](DATA_AND_SOURCE_POLICY.md) - source approval,
   courtesy, minimisation, retention, attribution, and deletion.
5. [Roadmap](ROADMAP.md) - staged delivery from local station to a possible
   invite-only federation.
6. [Project plan](PROJECT_PLAN.md) - work packages, milestones, ownership,
   estimates, dependencies, and Phase 1 backlog.
7. [Verification plan](VERIFICATION_PLAN.md) - product, matcher, safety,
   resource, and UI evidence.
8. [Risk and decision log](RISK_DECISION_LOG.md) - current risks, accepted
   decisions, and decisions still requiring an owner.
9. [Phase 0A source review](PHASE_0A_SOURCE_REVIEW.md) - current endpoints,
   policies, limits, qualification results, and Nostr operating caveats.
10. [Phase 0A Nostr message-size sample](PHASE_0A_NOSTR_SIZE_SAMPLE.md) -
    aggregate live evidence and the accepted 16 KiB body limit.
11. [Phase 0A source comparison report](PHASE_0A_COMPARISON_REPORT.md) - bounded
    repaired Nostr/Jetstream evidence, passed source/transport sub-gate, and
    the remaining matcher-quality blocker.
12. [Phase 0A matcher report](PHASE_0A_MATCHER_REPORT.md) - frozen synthetic
    corpus, held-out precision/recall evidence, and the failed quality gate.
13. [Reviewed Phase 0A source register](phase-0a-reviewed-sources.csv) - exact
    approved-disabled endpoint rows from the review.
14. [Approved-source register template](templates/approved-source-register.csv)
    - evidence required before a source can be enabled.
15. [ADR 0005: local-only direct-source architecture](../adr/0005-local-only-direct-source-architecture.md)
    - the no-backend data-flow and responsibility boundary.
16. [Phase 0B foundation report](PHASE_0B_FOUNDATION_REPORT.md) - environment,
    Windows primitive probe, .NET MAUI recommendation, revised estimate, and
    failed physical-device gate.
17. [Phase 1 requirement traceability matrix](PHASE_1_TRACEABILITY_MATRIX.md)
    - planned automated and UI evidence for every functional requirement.

Supporting documents already in the repository:

- [Current prototype guide](../../README.md)
- [Consent-only federation design](../../FEDERATION_DESIGN.md)
- [UK release-gate research](../../LEGAL_RELEASE_GATE.md)
- [ADR 0001: Harken foundation](../adr/0001-harken-foundation.md)
- [ADR 0002: local-first before federation](../adr/0002-local-first-before-federation.md)
- [ADR 0003: standalone public relay messages](../adr/0003-standalone-public-relay-messages.md)
- [ADR 0004: independent Windows and Android stations](../adr/0004-independent-desktop-mobile-stations.md)
- [ADR 0006: .NET MAUI probe foundation](../adr/0006-dotnet-maui-probe-foundation.md)
- [Phase 0 documentation validator](../../tools/validate_phase0_docs.py)

## Phase 0 exit gate

The initial use case, local-only boundary, source set, body limit, and quality
thresholds are owner-approved. The completed size probe did not enable a source
for routine operation; all three reviewed endpoints remain approved-disabled
outside an explicit bounded Phase 0A run. The Phase 0B desktop primitive probe
passed, rejected Harken as the production base, and proposed .NET 10 MAUI for
the next probe, but its physical Android and packaging gate failed. Production
implementation remains blocked on the Phase 0A matcher precision/label gate and
the Phase 0B physical-device gate. The cross-source source/transport sub-gate
has passed. No codebase fork, backend, federation, or public marketplace
release is part of this gate.
