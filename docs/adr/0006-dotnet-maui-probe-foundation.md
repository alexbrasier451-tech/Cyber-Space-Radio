# ADR 0006: use .NET MAUI as the cross-platform probe foundation

- Status: proposed for the Phase 0B physical spike; production acceptance pending
- Date: 2026-08-17

## Context

Cyber Space Radio must provide complete, independently operable Windows 11 and
Android stations without a project backend. The difficult shared behaviour is
the source gate, protocol classification, matcher, encrypted vault, retention,
deletion, bounded reconnect, truthful state reducer, and generation-scoped
STOP. Android additionally requires a native foreground service, ongoing
notification, platform key binding, and lifecycle evidence.

The Phase 0B environment and primitive results are recorded in the
[foundation report](../phase-0/PHASE_0B_FOUNDATION_REPORT.md). The current host
can run an ordinary .NET 8 console probe, but has no .NET MAUI/Android workload,
JDK, Android SDK, emulator, attached Android device, or Windows MSIX tools. The
probe passed ten synthetic AES-GCM, locked-start, WebSocket cancellation, STOP,
and fail-closed restart checks. It did not build an Android or packaged Windows
application.

Harken is a useful Python/FastAPI social-listening reference, but retaining it
for Windows would require a separate Android core and duplicate the sensitive
state, storage, cryptography, source, and STOP behaviour. Its existing polling,
dashboard, account, export, alert, and brand-monitoring features do not cover
most of this product's hard path.

## Decision

Do not create a production Harken fork. Use a greenfield .NET 10 MAUI solution
as the foundation for the next bounded Phase 0B probe:

- shared C# domain, application, source, cryptographic-envelope, and storage
  contracts;
- shared MAUI navigation/view models and native controls;
- Windows-specific lifecycle, DPAPI/DataProtectionProvider, and MSIX work;
- Android-specific foreground service, notification action, Keystore, backup,
  and process-lifecycle work; and
- one shared fixture/parity suite across both targets.

Target Android API 36 with Android 13/API 33 as the initial minimum. Treat
off-screen listening as a bounded, explicitly started `dataSync` foreground
service, not an always-on promise. The state model records operator intent,
runtime proof, Android service proof, and coverage separately.

This decision selects what to probe; it does **not** accept the production
foundation or authorise Phase 1. Acceptance requires the physical-device,
encrypted-store, lifecycle, resource, notification-STOP, APK/AAB, and MSIX
evidence listed in the report. If MAUI cannot meet those gates without
weakening the contract, reopen the reserved alternatives.

## Consequences

Positive:

- one language and solution can own the behavioural core and parity fixtures;
- MAUI supports Windows and Android while allowing direct platform API access;
- no FastAPI, localhost browser service, WebView store, or project backend is
  required; and
- platform-specific lifecycle/security code remains explicit rather than
  hidden behind a least-common-denominator abstraction.

Negative:

- the current workstation needs a pinned .NET 10/MAUI, Android, Java, and
  Windows packaging toolchain before it can build the probe;
- physical API 33 and API 36 hardware evidence is still missing;
- MAUI service, notification, encrypted SQLite-blob, upgrade, and packaging
  behaviour remain unproven; and
- the greenfield estimate is larger than the former Windows-only Harken range.

## Alternatives

- **Harken plus a separate Android app:** rejected for production because it
  creates two sensitive cores and high parity risk.
- **Kotlin/Compose Multiplatform:** reserve alternative if MAUI fails; strong on
  Android but adds Windows key/packaging work.
- **Flutter:** reserve alternative if MAUI fails; native service, secure store,
  and encrypted SQLite would be plugin-heavy.
- **Rust core with native UIs:** rejected for Phase 1 because FFI and two UI
  stacks add disproportionate cost.
