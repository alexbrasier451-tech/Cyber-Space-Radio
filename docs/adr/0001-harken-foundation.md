# ADR 0001: provisionally use Harken as the Windows foundation

- Status: superseded for production by the proposed .NET MAUI probe foundation in ADR 0006
- Date: 2026-08-14

## Context

Cyber Space Radio needs public-source adapters, normalisation, deduplication,
local persistence, a web console, CLI, retention, operations, and tests before
its distinctive local semantic listening or future federation can be useful.

The current repository is an uncommitted RSS/Atom proof of concept. A greenfield
application would repeat general social-listening infrastructure.

## Decision

**Outcome recorded 2026-08-17:** do not create the production Harken fork.
Phase 0B found that retaining Harken for Windows would duplicate the shared
state, source, storage, cryptography, and STOP core on Android while preserving
little of this product's hard path. Continue to use Harken only as a read-only
product/reference source. [ADR 0006](0006-dotnet-maui-probe-foundation.md)
selects .NET MAUI for the next physical-device probe; that proposal has not yet
passed the production-foundation gate.

The original provisional decision follows for history.

If Phase 0A and Phase 0B retain Harken, create a history-preserving fork of
[Harken](https://github.com/VladUZH/harken). Initially pin the fork to commit
`d0710a427dbbe712594ef3a6c25112e1d14cc027` and retain the MIT notice.

Keep the current prototype as a requirements and regression archive. Port its
minimum-record, explainable-match, retention, deletion, courtesy, and
federation-boundary requirements into the fork.

Before creating the production fork, run the bounded Phase 0A spike defined by
ADR 0003. Confirm that continuous relay adapters, standalone-message
classification, backpressure, and reconnect control fit Harken cleanly. If
they do not, supersede this ADR with a new foundation decision.

The independent phone-station requirement in ADR 0004 makes Harken
insufficient as the complete product foundation. Phase 0B must prove mobile
lifecycle behaviour and decide whether Harken is retained behind a portable
shared core, paired with a platform-native implementation governed by one
behavioural contract, or replaced by a cross-platform foundation. Do not create
the production fork until both spikes are complete.

## Consequences

Positive:

- avoids rebuilding source adapters, storage, dashboard, CLI, auth, alerts,
  metrics, backup, and operational tooling;
- stays in Python and matches the current development environment;
- preserves an upstream path for general listening features; and
- reaches local product validation earlier.

These benefits apply only if Harken survives the Phase 0A and Phase 0B gates.

Negative:

- Harken is young, pre-1.0, and must be treated as untrusted until audited;
- its default record model is less minimal than Cyber Space Radio requires;
- upstream merging becomes harder as privacy and federation boundaries diverge;
  and
- dependencies need a downstream lock and review policy.
- it does not supply a standalone phone runtime, mobile lifecycle integration,
  or physical-device evidence.

## Alternatives rejected

- **Continue the prototype:** too little structure for the planned product and
  would grow into a framework accidentally.
- **Greenfield FastAPI application:** maximum control but repeats most of
  Harken's working substrate without reducing the hard semantic or federation
  risks.
- **Start from a peer-to-peer social network:** solves distribution before the
  local listening product and carries a much larger, less relevant codebase.
