# ADR 0004: independent Windows and Android stations

- Status: Android target accepted; .NET MAUI probe foundation proposed; physical evidence pending
- Date: 2026-08-14

## Context

The product must work on Windows 11 and Android. An Android-only remote control
would fail whenever the desktop is unavailable, while making both devices silently
depend on one shared service would contradict the local-first and deletable
product boundary.

Mobile operating systems also do not offer the same background execution model
as Windows. Android long-running work normally uses a user-visible foreground
service and is subject to version-specific restrictions. iOS normally suspends
apps after they leave the foreground and provides scheduled or event-driven
background opportunities rather than an unrestricted permanent connection.

Primary platform references:

- [Android background services](https://developer.android.com/develop/background-work/services)
- [Android foreground-service restrictions](https://developer.android.com/develop/background-work/services/fgs/changes)
- [Apple background-task strategies](https://developer.apple.com/documentation/backgroundtasks/choosing-background-strategies-for-your-app)
- [Apple networking and background guidance](https://developer.apple.com/documentation/technotes/tn3151-choosing-the-right-networking-api)

## Decision

Build Windows and Android as independently operable stations. Each installation
owns and can manage its own:

- approved sources, cursor/replay state, classifier, matcher, and hybrid mode;
- manual passphrase, local content key, encrypted records, seven-day ordinary
  expiry, explicit Keep modes, and hard local capacity;
- exact deletion, source deletion, purge/reset, and STOP LISTENING state; and
- truthful health, last-proven-activity time, and coverage-gap history.

Neither station requires the other to configure, unlock, discover, tune,
listen, persist a match, expire, delete, stop, or reset.

Android reports what the operating system has actually permitted. It must
distinguish foreground Listening, background-limited, offline, locked, stopped,
and degraded states. Because a suspended or removed process cannot report live,
`Coverage gap / previously suspended` is derived retrospectively on resume from
an unclosed session and stale last-proven activity. It must not imply continuous
background coverage when execution was suspended.

After the operator explicitly presses Start, Android may continue listening
off-screen through a visible ongoing foreground service. Its notification
shows the actual state, last proven source activity, and STOP without exposing
message text. STOP terminates the service, removes the notification, clears
volatile previews, discards usable content keys, and prevents automatic
restart. A device reboot or process restart remains stopped and locked.

A durable topic match may raise one generic local `New signal found`
notification. It contains no message, source, author, score, explanation,
event reference, watch name, or permalink. Opening it requires local unlock.
Email, webhooks, hosted alerts, and remote push payloads remain disabled in
Phase 1.

The Phase 0B desktop probe and architecture review selected Android 13/API 33
as the proposed minimum, API 36 as the target, a bounded user-started
`dataSync` foreground service, and .NET 10 MAUI as the next shared-core/UI
foundation to probe. [ADR 0006](0006-dotnet-maui-probe-foundation.md) records
that choice. Physical-device evidence is still absent, so the Phase 0B gate and
production foundation remain unaccepted. iPhone is deferred until Android
evidence and local product value are accepted.

## Optional pairing boundary

Owner-controlled pairing may be considered after independent stations work. It
could coordinate watch versions, deduplicate summaries, show device health,
and provide an authenticated `STOP ALL MY DEVICES` action.

Pairing is explicit and removable. By default it does not synchronise raw
message text, passphrases, usable content keys, or historical plaintext. Its
identity, encryption, revocation, deletion, outage, and stop semantics require
a separate decision and verification gate. Losing or deleting either station
must not disable the other.

## Consequences

Positive:

- either device remains useful on its own;
- a desktop may later improve coverage during honest phone suspension gaps;
- pairing can add coordination without becoming custody of the local archive;
  and
- the UI can make platform limitations visible rather than inventing an
  always-on promise.

Negative:

- Phase 1 is larger than the earlier Windows-only estimate;
- mobile background, battery, notification, encryption, and packaging evidence
  must be gathered on physical devices;
- shared semantics require cross-platform fixtures and parity tests; and
- Harken is no longer a complete foundation decision by itself.
