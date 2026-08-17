# ADR 0005: local-only direct-source architecture

- Status: accepted
- Date: 2026-08-17

## Context

Cyber Space Radio is a listener in the product sense, not a hosted ingestion
service. The public source already operates the server. A station is a client
that opens an outbound connection, receives public events, evaluates them, and
keeps any selected record on the user's own device.

Treating the product as if it operated a central collector created unnecessary
privacy, policy, operations, deletion, and breach assumptions. It also conflicted
with the requirement that Windows and Android work independently and remain
fully deletable by their owner.

## Decision

Phase 1 has no Cyber Space Radio backend.

```text
public Nostr relay or Jetstream
  -> direct encrypted outbound connection from the station
  -> bounded local memory and structural classification
  -> local topic matching
  -> discard unmatched content on waterfall expiry
  -> encrypt and retain matched content on that device only
```

Project-operated infrastructure must not receive, relay, proxy, store, log,
infer, or decrypt:

- public message content or event identifiers;
- configured source history;
- watch phrases, exclusions, match results, or reports;
- author keys or other source evidence; or
- listening state or device-to-device health.

Phase 1 therefore has no user account, cloud database, ingestion endpoint,
hosted alert, remote push payload, listening telemetry, content-bearing crash
report, cross-user node reporting, federation, or project-operated sync.
Notifications and reports are generated locally. The emergency control stops
and locks the current device; there is no global network to stop.

Windows may provisionally use a FastAPI/Jinja process for its installed UI. If
retained, it binds only to loopback, accepts no LAN or Internet connections, and
is part of the local application rather than a remote service. Android uses a
local application runtime and visible foreground service where permitted.

Software distribution, generic update delivery, and support may exist later,
but they must be separated from listening data. Any diagnostics are opt-in and
structurally incapable of including content, event IDs, watch terms, source
history, or decrypted storage. App data included in OS backup must already be
encrypted, and backup behaviour must be disclosed and tested.

Signal review uses the local retained record. The app performs no automatic
profile lookup, link preview, media fetch, or external-viewer request. An
operator may configure an HTTPS Nostr viewer and explicitly confirm
`Open externally`; that separate browser action contains only a safely encoded
event reference and visibly discloses the third-party destination. New and
reset stations have no viewer configured and expose no external action until
the operator deliberately enables one in local Settings.

## Responsibility boundary

The relay or stream operator controls its public service and connection logs.
The local operator selects the sources and purposes and controls the station's
records. Cyber Space Radio processes only separate publisher data it actually
receives, such as a support email or store transaction; it does not receive the
listening corpus.

Private household use and professional use may have different legal treatment.
The application documents that distinction without claiming that local design
grants every user legal clearance.

## Consequences

Positive:

- removes central custody and central message-breach exposure;
- makes deletion and passphrase control genuinely device-local;
- allows each Windows and Android installation to operate independently;
- makes Nostr's ordinary public, read-only client model viable for the bounded
  Phase 0A evaluation; and
- prevents a server dependency from becoming a hidden product requirement.

Negative:

- there is no automatic cross-device history, deduplication, remote support, or
  global kill switch;
- source operators still see ordinary connection metadata such as the device's
  public IP address and connection timing;
- device loss and local backup behaviour become the owner's principal custody
  risks; and
- any future pairing, sync, backend, hosted reporting, or federation feature
  must be designed and reviewed as a new data flow.

## Verification

Phase 1 release tests must demonstrate:

- an outbound allowlist containing only enabled public sources and separately
  documented update infrastructure;
- no listening-data egress under normal, error, crash, notification, export,
  backup, stop, purge, and upgrade paths;
- loopback-only binding for any Windows local UI process;
- no remote-push dependency for Android match notifications;
- ciphertext-only durable storage and backup artefacts; and
- complete local stop, expiry, exact deletion, purge, and uninstall behaviour.
