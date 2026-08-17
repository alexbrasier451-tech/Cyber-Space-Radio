# Phase 1 requirement traceability matrix

Status: **planned targets; no Phase 1 implementation evidence claimed**
Updated: 2026-08-17

This matrix gives every functional requirement in
[`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) an explicit automation target and,
where an operator interaction is involved, a UI acceptance target. The IDs are
stable planning handles. A row passes only when the implemented test is green
and the applicable platform evidence is attached to a test report.

| Requirement | Planned automated evidence | Planned UI acceptance evidence |
|---|---|---|
| FR-01 | `P1-WATCH-001` watch lifecycle/state transitions | `UI-WATCH-001` create/edit/pause/resume/delete |
| FR-02 | `P1-WATCH-002` watch schema and threshold bounds | `UI-WATCH-002` ideas/exclusions/threshold visible |
| FR-03 | `P1-SOURCE-001` allowlist fail-closed connection gate | `UI-SOURCE-001` disabled/unapproved source state |
| FR-04 | `P1-SOURCE-002` per-source failure isolation | `UI-NOW-001` one degraded source, others active |
| FR-05 | `P1-PIPE-001` normalization and protocol-key dedup | — |
| FR-06 | `P1-SIGNAL-001` durable projection/provenance/matches | `UI-SIGNAL-001` inspector fields and explanations |
| FR-07 | `P1-PIPE-002` rejected-content durable-sentinel scan | `UI-NOW-002` aggregate reject counters only |
| FR-08 | `P1-STORE-001` encrypted selective persistence/expiry | `UI-DATA-001` retention and Keep state |
| FR-09 | `P1-DELETE-001` exact/source/expired/purge scopes | `UI-DELETE-001` scoped previews and confirmation |
| FR-09A | `P1-SOURCE-003` remove source without deleting history | `UI-SOURCE-002` separate remove/data-delete actions |
| FR-10 | `P1-STOP-001` outbound gate and stopped-state proof | `UI-STOP-001` STOP state and explicit resume |
| FR-11 | `P1-SOURCE-004` intervals/timeouts/retry/conditional rules | `UI-SOURCE-003` limits and degraded status |
| FR-12 | `P1-ABUSE-001` hostile-content configuration isolation | — |
| FR-13 | `P1-PIPE-003` envelope/signature/classifier ordering | — |
| FR-14 | `P1-CLASS-001` structural addressed-event rejection corpus | — |
| FR-15 | `P1-STREAM-001` filter/replay/backoff/rate/queue bounds | `UI-NOW-003` rate/drop/gap status |
| FR-16 | `P1-DISCOVERY-001` volatile-only waterfall/activity | `UI-DISCOVERY-001` waterfall and explicit Keep |
| FR-17 | `P1-TUNED-001` validated-match persistence gate | `UI-MODE-001` Discovery/Tuned behaviour |
| FR-18 | `P1-STOP-002` volatile clear/durable preservation | `UI-STOP-002` post-STOP retained/cleared views |
| FR-19 | `P1-CRYPTO-001` plaintext sentinel artefact scan | — |
| FR-20 | `P1-CRYPTO-002` locked startup/manual unlock gate | `UI-LOCK-001` launch and unlock journey |
| FR-21 | `P1-STOP-003` connection/retry/key teardown | `UI-STOP-003` locked post-STOP inspector |
| FR-22 | `P1-CRYPTO-003` loss/reset purge-before-new-key | `UI-RESET-001` destructive reset wording/scope |
| FR-23 | `P1-PARITY-001` independent end-to-end station suites | `UI-PARITY-001` Windows/Android complete journeys |
| FR-24 | `P1-ANDROID-001` proven-state lifecycle transitions | `UI-ANDROID-001` truthful lifecycle labels |
| FR-25 | `P1-PAIR-001` operation with absent/offline peer | `UI-PAIR-001` pairing optionality |
| FR-26 | `P1-ANDROID-002` explicit-start foreground service/STOP | `UI-ANDROID-002` ongoing notification and STOP |
| FR-27 | `P1-NOTIFY-001` generic local notification projection | `UI-NOTIFY-001` lock-screen and unlock path |
| FR-28 | `P1-EGRESS-001` capture proves no project-backend traffic | `UI-PRIVACY-001` no account/backend disclosure |
| FR-29 | `P1-NOSTR-001` 60-second replay/dedup/gap behaviour | `UI-NOW-004` coverage-gap display |
| FR-30 | `P1-NOSTR-002` cross-relay event-ID/provenance merge | `UI-SIGNAL-002` Damus/nos.lol/Both badge update |
| FR-31 | `P1-VIEWER-001` local-open zero-egress and safe external URL | `UI-VIEWER-001` confirmed external open |
| FR-32 | `P1-VIEWER-002` install/reset disabled/null default | `UI-VIEWER-002` action absent until configured |
| FR-33 | `P1-SPAM-001` conservative pre-match suppression | `UI-NOW-005` Noise blocked counter |
| FR-34 | `P1-JUNK-001` 50-item/five-minute volatile bounds | `UI-JUNK-001` drawer/clear/expiry |
| FR-35 | `P1-JUNK-002` exact-event one-session restore | `UI-JUNK-002` Restore once result |
| FR-36 | `P1-KEEP-001` topic definition/future-Keep lifecycle | `UI-WATCH-003` future-only control and preview |
| FR-37 | `P1-KEEP-002` manual reason/fresh-expiry transitions | `UI-SIGNAL-003` Keep/remove protection |
| FR-38 | `P1-CAPACITY-001` 100 MiB accounting/warnings | `UI-STORAGE-001` usage, limit, 80/95% warnings |
| FR-39 | `P1-CAPACITY-002` pruning/protected-full behaviour | `UI-STORAGE-002` truthful not-saved state |
| FR-40 | `P1-CAPACITY-003` lower-limit preflight/rejection | `UI-STORAGE-003` pruning preview and refusal |
| FR-41 | `P1-DELETE-002` source-delete protected/multi-source cases | `UI-DELETE-002` named protected-count warning |
| FR-42 | `P1-WATERFALL-001` 100-item/ten-minute eviction | `UI-DISCOVERY-002` bounded list and Keep handoff |
| FR-43 | `P1-WATERFALL-002` Unicode 280-grapheme projection | `UI-DISCOVERY-003` safe local expand/collapse |
| FR-44 | `P1-LIMIT-001` 16,383/16,384/16,385-byte bodies | `UI-NOW-006` content-free Oversized count |
| FR-45 | `P1-LIMIT-002` fragmented 65,535/65,536/65,537 envelopes | `UI-NOW-007` envelope reject reason only |
| FR-46 | `P1-ONBOARD-001` no-preselect draft/skip state | `UI-ONBOARD-001` required topic screen/routes |
| FR-47 | `P1-ONBOARD-002` zero-egress and preview-only gate | `UI-ONBOARD-002` validation badges and disabled autosave |
| FR-48 | `P1-ONBOARD-003` tutorial state/replay/skip | `UI-ONBOARD-003` four-step tutorial and Enable separation |
| FR-49 | `P1-VALIDATE-001` local preview/config deletion scope | `UI-VALIDATE-001` synthetic/volatile preview evidence |
| FR-50 | `P1-INBOX-001` one record/count/notice with N decisions | `UI-INBOX-001` unified filters and multi-match inspector |
| FR-51 | `P1-KEEP-003` independent retention-reason set | `UI-SIGNAL-004` all protection reasons visible |
| FR-52 | `P1-KEEP-004` future-only and bulk-reason transactions | `UI-WATCH-004` existing-item preview/confirmation |
| FR-53 | `P1-DELETE-003` transactional topic-deletion plan | `UI-DELETE-003` four disjoint counts/bytes |
| FR-54 | `P1-DELETE-004` survivor/orphan/fresh-expiry outcomes | `UI-SIGNAL-005` surviving state after topic delete |
| FR-55 | `P1-INBOX-002` default/sort/session-state clearing | `UI-INBOX-002` All topics/newest-first reset |
| FR-56 | `P1-REVIEW-001` inspection-only Reviewed transition | `UI-REVIEW-001` New/Reviewed shared state |
| FR-57 | `P1-REVIEW-002` Mark-as-new isolation/persistence | `UI-REVIEW-002` reversible review action |
| FR-58 | `P1-REVIEW-003` atomic filtered snapshot update | `UI-REVIEW-003` count preview/concurrency case |
| FR-59 | `P1-IDENTITY-001` protocol-key identity and same-text separation | — |
| FR-60 | `P1-DELETE-005` authenticated upstream-delete precedence | `UI-DELETE-004` content-free kept-item removal notice |
| FR-61 | `P1-VALIDATE-002` frozen evidence/promotion invalidation | `UI-VALIDATE-002` preview-only/promotion/edit states |

The watch-promotion row requires the exact frozen watch version to pass the
held-out corpus gate before automatic persistence or notification; any edit
must revoke that promotion.
