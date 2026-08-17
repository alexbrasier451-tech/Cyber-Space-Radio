# ADR 0002: prove the local station before federation

- Status: accepted
- Date: 2026-08-14

## Context

The long-term concept includes several consent-based nodes sharing match
digests and health evidence. That network adds identity, key management,
partitions, replay defence, deletion propagation, resource limits, and an
emergency operating lease before it adds user value.

## Decision

Phase 1 and Phase 2 contain no federation runtime. They build and validate a
useful local public-source listening station first.

Federation work begins only in an isolated Phase 3 laboratory after:

- local relevance quality is measured;
- source approval, retention, stop, and deletion work end to end;
- the exact federated digest is stable and contains no raw content;
- multiple named operators confirm a real need; and
- the proof requirements in `FEDERATION_DESIGN.md` are funded and owned.

## Consequences

- The project can demonstrate value without operating a distributed system.
- Privacy and deletion contracts are defined before replication.
- The UI may reserve conceptual space for network health, but the navigation is
  hidden until Phase 3.
- Any implementation that introduces peer discovery, enrollment, or network
  messages before the Phase 3 gate violates this decision.
