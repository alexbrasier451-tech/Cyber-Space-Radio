# Phase 0B foundation report

- **Evidence date:** 17 August 2026
- **Gate result:** **FAIL - Phase 1 must not start**
- **Foundation recommendation:** replace Harken as the production foundation
  with a .NET 10 MAUI application containing one shared C# behavioural core and
  small platform-specific Windows and Android lifecycle shells.
- **Evidence honesty:** this machine can compile and publish an ordinary .NET 8
  Windows console application. It cannot currently build a .NET MAUI,
  Android, APK/AAB, or MSIX application, and no Android device or emulator was
  available. No workload, SDK, emulator, or dependency was installed during
  this review.

The architecture can be selected provisionally, but the Phase 0B gate cannot
pass until the Android lifecycle, notification STOP, encryption/store,
resource, and packaging claims run on physical hardware.

## 1. Governing contracts reviewed

The recommendation preserves these existing decisions and requirements:

- Windows 11 and Android are complete, independent stations. Neither is a
  remote control for the other (`ADR 0004`, `FR-23`).
- Phase 1 has no Cyber Space Radio backend. Each station connects directly to
  its approved sources and keeps listening data locally (`ADR 0005`, `FR-28`).
- Every launch starts stopped and locked. Manual passphrase unlock is required
  before listening or viewing retained plaintext (`FR-20`).
- STOP closes source activity, prevents reconnect, clears volatile content,
  discards usable content keys, and leaves deliberately persisted ciphertext
  intact (`FR-18`, `FR-21`, `FR-26`).
- Android off-screen listening begins only after an explicit foreground user
  action and runs only with a visible foreground-service notice containing a
  STOP action (`FR-26`).
- Windows and Android must classify, match, persist, expire, delete, stop, and
  reset identically against shared fixtures.
- Plaintext retained-message content may not appear in SQLite pages,
  journals/WAL, temporary files, logs, exports, backups, crash reports, or
  browser storage (`FR-19`).
- Nostr event messages have a 65,536-byte assembled-envelope ceiling and a
  16,384-byte decoded-body ceiling, with bounded queues and reconnect.

One clarification is needed in the existing UX contract: an Android process
cannot update its UI while the operating system has actually suspended or
removed it. `OS suspended` is therefore retrospective evidence recorded on
the next execution opportunity from an unclosed session and a last-proven-
activity gap. It must not be presented as a live state emitted by a process
that was not running.

## 2. Actual machine capability

The reproducible read-only probe is
[`tools/phase0b/probe-environment.ps1`](../../tools/phase0b/probe-environment.ps1).

| Capability | Observed evidence | Consequence |
|---|---|---|
| Host OS | x64, runtime build `10.0.26200.0`; registry display version `25H2`, build `26200.9168`, Professional | Suitable Windows 11-class host for later desktop work. The legacy registry product-name string is not used as evidence. |
| Visual Studio | Community 2022 `17.9.34728.123`; MSBuild `17.9.8.16306`; Managed Desktop workload | Can build ordinary managed desktop code, but is behind the proposed production foundation. |
| .NET | SDK `8.0.204`, runtime `8.0.4`; no installed workloads; no MAUI template | Enough for a bounded BCL probe only. .NET 8 reaches end of support on 10 November 2026 and is not the recommended new baseline. |
| .NET 10 / MAUI | Not installed; `Microsoft.Maui.Sdk` and `Microsoft.Android.Sdk.Windows` packs absent | Production shared UI and Android targets cannot be built here. |
| Java / Android tools | No Java/Javac, Gradle, Android SDK, `sdkmanager`, `avdmanager`, `adb`, or emulator on `PATH`; normal Android SDK/Studio paths absent | No Android project can be compiled, installed, inspected, or lifecycle-tested. |
| Android target | No AVDs can be listed because the emulator is absent; Windows reported no connected `AndroidUsbDeviceClass` device | There is no physical-device or emulator evidence. |
| Windows packaging | Windows SDK directories and `makeappx`/`signtool` absent from `PATH` | No signed MSIX evidence exists. |
| Alternative stacks | Flutter/Dart, Rust/Cargo, Node/npm, CMake/Ninja, Docker, and WSL absent | None offers a presently installed shortcut around the mobile evidence gap. |

[Microsoft's current support table](https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core)
lists .NET 10 as the active LTS release through November 2028; .NET 8 is in its
maintenance phase through November 2026. .NET 10 MAUI supports Android and
Windows from one project while retaining direct access to platform APIs:
[MAUI overview](https://learn.microsoft.com/en-us/dotnet/maui/what-is-maui?view=net-maui-10.0),
[supported platforms](https://learn.microsoft.com/en-us/dotnet/maui/supported-platforms?view=net-maui-10.0).

## 3. Bounded probe performed

The smallest safe probe that the installed SDK could support is in
[`tools/phase0b/FoundationProbe`](../../tools/phase0b/FoundationProbe/).
It uses only the .NET 8 base class library, opens only a loopback TCP socket,
and uses synthetic non-secret content.

Commands run:

```powershell
dotnet run --project .\tools\phase0b\FoundationProbe\FoundationProbe.csproj -c Release
dotnet publish .\tools\phase0b\FoundationProbe\FoundationProbe.csproj `
  -c Release -r win-x64 --self-contained false `
  -o .\tools\phase0b\FoundationProbe\publish
.\tools\phase0b\FoundationProbe\publish\FoundationProbe.exe
```

Both source-run and published executable returned exit code 0. The generated
[`probe-evidence.json`](../../tools/phase0b/FoundationProbe/probe-evidence.json)
records all checks as passing:

- wrong synthetic passphrase fails authenticated unwrap;
- the synthetic plaintext sentinel is absent from the temporary durable JSON
  record;
- AES-GCM encrypted record round-trip succeeds;
- modified ciphertext fails authentication;
- a loopback-only WebSocket text message completes;
- STOP cancellation ends a pending WebSocket receive and closes the socket;
- launch begins stopped and locked;
- STOP returns to stopped and locked with reconnect forbidden; and
- simulated unclean restart remains stopped and locked and records a coverage
  gap rather than resuming.

This is evidence that the installed .NET runtime exposes the required primitive
shapes. It is **not** evidence for production KDF parameters, SQLite/WAL
behaviour, DPAPI, Android Keystore, TLS/public WebSockets, MAUI, foreground
services, notifications, process death, OS suspension, battery use, Android
backup, APK/AAB, or MSIX.

## 4. Foundation evaluation

| Foundation | Shared behaviour/UI | Native Android lifecycle | Windows packaging | Main risk | Result |
|---|---:|---:|---:|---|---|
| Harken/Python on Windows plus separate Android app | Low | Separate implementation | Existing web process, not app packaging | Two cores, two stores, two crypto stacks, and parity drift | Reject as production base |
| .NET 10 MAUI | High | Platform code available inside one multi-targeted project | WinUI 3/MSIX supported | MAUI and native crypto/store packaging still require a spike | **Recommend** |
| Kotlin/Compose Multiplatform | Medium-high | Excellent | JVM/desktop and Windows key integration require extra work | Windows packaging and DPAPI bridge become second-class | Reserve alternative |
| Flutter | High UI sharing | Requires native service/plugin work | Supported but plugin-heavy | Secure store, foreground service, and encrypted SQLite depend heavily on plugins | Reserve alternative |
| Rust core plus native WinUI/Android UIs | High domain sharing, low UI sharing | Excellent after JNI/FFI work | Strong | Highest FFI, packaging, and team cost for a small project | Reject for Phase 1 |

### Harken decision

**Replace Harken as the production codebase.** Do not create the proposed
history-preserving production fork.

Harken remains useful as a read-only product reference and a source of general
social-listening ideas, but its value is concentrated in Python polling
adapters, a FastAPI dashboard, account/server operations, plaintext mention
storage, exports, hosted alerts, and brand-monitoring analysis. Cyber Space
Radio's first source is a long-lived direct Nostr WebSocket, its UI must be a
native independent phone station as well as Windows, and its critical work is a
shared structural classifier, state reducer, encrypted vault, and STOP
lifecycle. Retaining Harken would preserve relatively little of the hard path
while requiring separate Python and mobile implementations of the most
sensitive behaviour.

The current Harken README still describes a Python/FastAPI/SQLite local brand-
monitoring product and does not advertise an Android runtime or Nostr relay
adapter: [Harken repository](https://github.com/VladUZH/harken). None of its
code was copied by this Phase 0B work.

### Recommended solution shape

Use a .NET 10 MAUI solution with these boundaries:

```text
CyberSpaceRadio.Domain
  immutable contracts, standalone classifier, state reducer, retention,
  deletion plans, quota policy, matcher interfaces

CyberSpaceRadio.Application
  station orchestration, bounded source sessions, privacy projection,
  use cases and generation-scoped STOP cancellation

CyberSpaceRadio.Infrastructure
  direct ClientWebSocket Nostr adapter, encrypted-blob SQLite vault,
  cryptographic envelopes, platform-neutral clocks and persistence ports

CyberSpaceRadio.App
  shared MAUI XAML navigation and view models
  Platforms/Windows: app lifecycle, DPAPI device binding, MSIX concerns
  Platforms/Android: foreground service, notification channels/actions,
                     Keystore device binding, backup rules, lifecycle evidence

CyberSpaceRadio.Contracts.Tests
  shared fixtures and parity tests run against both platform targets
```

There is no FastAPI process, loopback browser server, WebView/Blazor store, or
project backend. MAUI's multi-targeting allows shared UI and business logic
while platform-specific files invoke the real Android and Windows APIs where
needed. [Microsoft documents this platform-code pattern](https://learn.microsoft.com/en-us/dotnet/maui/platform-integration/invoke-platform-code?view=net-maui-10.0).

## 5. Direct WebSocket architecture

The shared source port should be implemented with the .NET
`System.Net.WebSockets.ClientWebSocket` API. The station, not a project server,
opens one outbound `wss://` connection to each enabled approved relay.

Required implementation rules:

1. Resolve endpoints only from the local approved-source register. Received
   text, tags, redirects, or relay notices cannot create another destination.
2. Use ordinary platform certificate and hostname validation. No trust-all
   callback is permitted.
3. Read fragments into one bounded assembler. Abort an assembled message above
   65,536 UTF-8 bytes before JSON event-field processing where the API permits.
4. Validate protocol envelope/signature and standalone structure, then enforce
   the 16,384-byte decoded-body boundary.
5. Send accepted work through a fixed-capacity channel. Overflow discards or
   applies source backpressure according to the adapter contract; it never
   creates an unbounded task collection.
6. Give every listening session a generation and root cancellation token.
   Reconnect attempts must re-check that generation, `Unlocked`, and
   `ListeningRequested` before opening a socket.
7. STOP first commits durable stopped intent, then cancels the generation,
   closes/aborts sockets after a short bounded graceful-close window, clears
   volatile queues, and zeroes usable content-key buffers.
8. Reconnect uses capped exponential backoff and the defined 60-second replay
   request. It never silently deep-backfills a coverage gap.

The local probe demonstrates a WebSocket-shaped round trip and cancellation
over loopback. Public TLS, relay fragmentation, Android networking, Doze, and
network-switch behaviour remain unproven.

## 6. Encrypted local store and key handling

### Store recommendation

Use ordinary SQLite as a transaction/index container, but put all listening
data into application-encrypted authenticated blobs **before SQLite sees it**.
This is the mandatory privacy boundary on both platforms.

A minimal physical schema can contain:

```text
vault_items(
  row_id random UUID primary key,
  object_kind small non-content discriminator,
  expires_at nullable UTC integer,
  dedupe_tag keyed HMAC blob,
  crypto_version integer,
  nonce blob,
  ciphertext blob,
  authentication_tag blob
)
```

Source URLs, relay IDs, protocol event references, watch text, match
explanations, message text, public keys, and review/retention detail belong
inside encrypted objects. A keyed HMAC of the canonical event identity enables
deduplication without persisting the identity. Derive independent encryption
and index keys from one random station master key with versioned HKDF labels.

Use AES-256-GCM with a fresh 96-bit nonce and 128-bit tag for every envelope;
bind object ID, object kind, and schema/key version as associated data. The
application must serialize directly to memory, encrypt, and then bind only
ciphertext to SQLite. Sensitive strings never enter SQL, migrations, query
logs, exception messages, or telemetry.

Whole-database SQLCipher can be considered later as an extra layer, but it is
not the initial dependency. The previously common
`SQLitePCLRaw.bundle_e_sqlcipher` package is deprecated by its maintainer, and
Zetetic's supported current .NET/MAUI binaries are commercial:
[SQLitePCLRaw encryption options](https://github.com/ericsink/SQLitePCL.raw/wiki/SQLite-encryption-options-for-use-with-SQLitePCLRaw),
[SQLCipher for .NET](https://www.zetetic.net/sqlcipher/sqlcipher-for-dotnet/).
The encrypted-object design avoids silently selecting an unsupported native
bundle and is sufficient only after the SQLite/WAL/temp sentinel test passes on
both platforms.

### Key hierarchy and manual unlock

1. First setup generates a random 256-bit station master key.
2. A versioned password KDF derives a passphrase wrapping key from a random
   salt. For the dependency-minimal first implementation, use built-in
   PBKDF2-HMAC-SHA-256, calibrated per platform to an interactive unlock budget
   with a floor of 600,000 iterations. The 210,000 iterations in the small
   console probe are intentionally **not** production parameters.
3. AES-GCM wraps the station master key with the passphrase key.
4. A separate device-bound key wraps that passphrase envelope: Android
   Keystore on Android and user-scoped DPAPI/DataProtectionProvider on Windows.
   The device layer is a second factor, not an automatic-unlock bypass.
5. Unlock requires both the device-bound unwrap and a freshly entered manual
   passphrase. No passphrase, derived passphrase key, station master key, or
   content subkey is stored in arguments, environment, settings, logs, browser
   storage, crash reports, or backups.
6. STOP and app background lock zero byte buffers with
   `CryptographicOperations.ZeroMemory`, release crypto services, and prevent
   new decrypt operations. Managed UI strings cannot be proven zeroable, so
   their lifetime and scope must be kept minimal and excluded from every
   durable/diagnostic path.
7. Lost-passphrase or lost-device-key recovery has one route: transactionally
   purge encrypted objects and wrapped keys, verify removal, then create a new
   station. There is no escrow or bypass.

Android Keystore can keep key material non-exportable and, where supported,
hardware-bound:
[Android Keystore](https://developer.android.com/privacy-and-security/keystore).
Windows DPAPI normally binds protected data to the same user and computer:
[CryptProtectData](https://learn.microsoft.com/en-us/windows/win32/api/dpapi/nf-dpapi-cryptprotectdata),
[WinUI data protection](https://learn.microsoft.com/en-us/windows/uwp/security/data-protection).

Android backup rules must exclude the device-bound key and disclose that a
copied ciphertext vault is deliberately unrecoverable on another device. This
is consistent with the accepted no-recovery contract, but it requires an
explicit UX statement and restore test.

## 7. Truthful state model

A single status enum cannot represent the product honestly. Persist only
operator intent and minimal session evidence; derive the display from
orthogonal dimensions.

| Dimension | Values |
|---|---|
| Security | `Locked`, `Unlocking`, `Unlocked`, `Locking`, `ResetRequired` |
| Operator intent | `Stopped`, `StartRequested`, `StopRequested` |
| Runtime proof | `Inactive`, `Starting`, `Connecting`, `Receiving`, `Backoff`, `Offline`, `Degraded`, `BackgroundLimited`, `StorageFull` |
| Android host proof | `NoService`, `ForegroundServiceStarting`, `ForegroundServiceVisible`, `ForegroundServiceStopping` |
| Coverage | last successful connection/read time, per-source status, nullable open/closed coverage-gap interval |

Display labels are derived:

- **Stopped / Locked:** the mandatory launch, restart, reboot, post-STOP, and
  unclean-recovery state. No reconnect is permitted.
- **Ready / Unlocked:** manual unlock succeeded, but the operator has not
  pressed Start. No network request occurs.
- **Starting:** Start was pressed in a visible UI and platform service/source
  creation is incomplete.
- **Listening:** intent is active, keys are unlocked, the source loop is alive,
  and on Android the foreground service is confirmed visible. Show last-proven
  source activity separately; intent alone never produces this label.
- **Degraded:** at least one enabled source is healthy and another is failing,
  or bounded processing/storage has reduced coverage.
- **Offline:** no enabled source is currently reachable or platform network is
  unavailable.
- **Background limited:** Android has denied notification visibility, reached
  its foreground-service time allowance, entered a restricted battery state,
  or otherwise cannot support the requested off-screen session.
- **Coverage gap / previously OS-suspended:** generated after execution resumes
  when an earlier session lacked a clean close and last-proven activity is
  stale. The process cannot claim to have reported live while suspended.
- **Stopping:** STOP is in progress. Do not display Stopped until durable intent
  is stopped, sockets cannot reconnect, volatile content is cleared, and keys
  are locked.
- **Storage full:** volatile bounded listening may remain active, but the UI
  must state that durable matches are not being saved.

### STOP ordering

1. Commit `Stopped` intent and a new session generation in a small durable
   transaction.
2. Cancel the previous generation token so late source callbacks cannot save,
   notify, or reconnect.
3. Stop reconnect timers and close direct WebSockets; abort after a bounded
   graceful-close timeout.
4. Clear waterfall, Junk, candidate queues, in-flight plaintext, and pending
   match notifications.
5. Zero usable keys and set Security to `Locked`.
6. On Android, remove the foreground notification and call `stopSelfResult`;
   the service returns `START_NOT_STICKY`.
7. Record only the content-free session end. A crash at any later step restarts
   from the already committed stopped-and-locked state.

## 8. Android operating model

### Version choice

- **Minimum supported version:** Android 13, API 33.
- **Compile and target version:** Android 16, API 36.

API 33 is the smallest recommended support surface because the product's
contract depends directly on Android 13's foreground-service Task Manager and
runtime notification permission. A lower minimum expands the lifecycle matrix
without adding evidence or product value yet. Google Play requires new apps
and updates to target API 36 from 31 August 2026:
[current target-API requirements](https://support.google.com/googleplay/android-developer/answer/11926878?hl=en-AU).

### Foreground-service type and limits

Use a user-started `dataSync` foreground service for the first bounded probe.
Receiving a configured network event stream is closer to documented data fetch
and transfer than to any other defined type. It is **not** an unlimited
always-on mechanism.

For apps targeting Android 15 or later, `dataSync` foreground services receive
at most six background hours in a rolling 24-hour period across the app; the
timer resets when the user brings the app to the foreground. The timeout must
call `stopSelf()` within seconds:
[foreground-service timeout rules](https://developer.android.com/develop/background-work/services/fgs/timeout).
The app must therefore describe Android listening as a bounded, user-started
session and transition to `Background limited` with a coverage gap when the OS
ends that allowance.

Do not declare `remoteMessaging`: Android defines it for continuity of the
user's messaging between devices, which is not this product. Do not assume
`specialUse`: its free-form use case is reviewed during Play submission. The
defined service types and review rule are documented here:
[foreground-service types](https://developer.android.com/develop/background-work/services/fgs/service-types).
If a later Play review accepts `specialUse`, treat that as new evidence rather
than retroactively changing this report.

### Lifecycle rules

- Start only from a visible activity after explicit user action; call
  `startForegroundService()` and promote the service promptly.
- Require Android 13 notification permission before offering off-screen mode.
  If denied, allow only visible-activity listening or stay
  `Background limited`. Android otherwise shows the service only in Task
  Manager, not the notification drawer, which fails this product's visible
  ongoing-notification promise:
  [notification permission](https://developer.android.com/develop/ui/compose/notifications/notification-permission).
- The ongoing notice contains generic state, last-proven activity, Open, and a
  prominent internal STOP action. It contains no signal content or watch/source
  identifier.
- Use an explicit, non-exported service and immutable application-scoped
  `PendingIntent` actions.
- Return `START_NOT_STICKY`. Register no boot receiver, alarm, WorkManager job,
  push handler, or scheduler capable of starting listening.
- A notification STOP runs the same generation-scoped STOP path as the UI. It
  must remove the notice, terminate the service, close sockets, lock keys, and
  prevent restart.
- Android 13's Task Manager Stop removes the entire app from memory and the
  foreground-service notification. On next launch, report an interruption gap
  but remain stopped and locked:
  [user-initiated foreground-service stopping](https://developer.android.com/develop/background-work/services/fgs/handle-user-stopping).
- Device reboot, package update, process death, swipe-away, network change,
  battery restriction, Doze, and forced foreground-service timeout all require
  physical tests. None may silently resume listening.

## 9. Packaging plan

### Windows 11

- Build the shared MAUI application for `net10.0-windows` and x64 first.
- Produce a signed MSIX. Keep signing keys outside the repository and CI logs.
- Verify first install, upgrade, downgrade rejection, STOP during update,
  encrypted data preservation on upgrade, reset, uninstall, and residual app
  data.
- Add ARM64 only after x64 lifecycle and encryption evidence passes.

Microsoft's MAUI packaging path produces signed MSIX packages and requires a
trusted certificate:
[Windows MAUI publishing](https://learn.microsoft.com/en-us/dotnet/maui/windows/deployment/publish-cli?view=net-maui-10.0).
The Phase 0B console executable is not MSIX evidence.

### Android

- Produce a signed APK for bounded device testing and an AAB for a later Play
  submission.
- Keep upload/signing keys outside the repository; document Play App Signing
  separately if Play is selected.
- Verify clean install, upgrade, Task Manager Stop, application data clear,
  uninstall, backup exclusion, and reinstall on physical API 33 and API 36
  devices.

MAUI supports APK and AAB output:
[Android MAUI publishing](https://learn.microsoft.com/en-us/dotnet/maui/android/deployment/?view=net-maui-10.0).
Distribution choice remains relevant because Play must review the foreground-
service declaration. Architecture must not assume approval.

## 10. Revised estimate

### Complete Phase 0B evidence

After the required tooling and physical devices are available: **8-12 focused
days**, plus elapsed battery/session measurement time.

| Evidence package | Focused effort |
|---|---:|
| Install/pin .NET 10, MAUI, JDK 21, Android API 33/36 and Windows packaging tools; record lock | 1-2 days |
| Minimal MAUI shared-core/state and direct WebSocket probe | 1-2 days |
| Android foreground service, notification STOP, timeout and restart probe | 2-3 days |
| Encrypted SQLite-blob, DPAPI/Keystore, backup and sentinel probe | 2-3 days |
| APK/AAB/MSIX build plus physical lifecycle/resource report | 2-3 days |

### Combined Phase 1

The earlier 41-58-day Windows/Harken range is superseded. For the current 62
functional requirements, two independent station targets, native Android
lifecycle, encrypted local vault, shared UI, packaging, and full evidence, use
**88-129 focused engineering days**:

| Work package | Estimate |
|---|---:|
| Repository, pinned toolchain, MAUI shell and CI fixtures | 5-7 days |
| Shared contracts, state reducer and parity harness | 8-12 days |
| Nostr WebSocket, limits, classification, dedupe and provenance | 9-13 days |
| Encrypted vault, keys, retention, capacity and deletion transactions | 12-18 days |
| Matching, spam/Junk, waterfall and topic lifecycle | 10-14 days |
| Shared Windows/Android operator UI and accessibility | 14-20 days |
| Android service, notification, lock/background and coverage gaps | 8-12 days |
| Windows MSIX and Android APK/AAB packaging/upgrade/uninstall | 5-8 days |
| Security, no-egress, corpus, parity, lifecycle and resource evidence | 14-20 days |
| Operator documentation and release-gate evidence | 3-5 days |

For one experienced engineer this is roughly 18-26 focused weeks. Two engineers
with one integration owner can shorten elapsed time to roughly 12-17 weeks, but
source/core changes, store migrations, STOP integration, and final evidence
remain serial gates. Store-vendor licensing, Play review, legal review, and
device procurement latency are outside the engineering range.

## 11. Smallest next evidence procedure

Do not begin product implementation. Close the evidence gap in this order:

1. Install and pin the current patched .NET 10 SDK/MAUI workload, JDK 21,
   Android SDK platform/build-tools 33 and 36, platform-tools/`adb`, one API 33
   emulator, one API 36 emulator, and the Windows SDK/MSIX tools. Record exact
   versions and hashes where available.
2. Provide at least one physical Android 16/API 36 device and preferably a
   second physical API 33 device. Emulator results may support fixtures/layout,
   but cannot satisfy lifecycle, notification, battery, thermal, lock-screen,
   or suspension evidence.
3. Build a minimal MAUI probe, not the full product: one shared state reducer,
   one synthetic encrypted object, one direct WebSocket to a controlled local
   test endpoint, one Android `dataSync` service, and one Windows app target.
4. Prove clean launch is stopped/locked, wrong passphrase fails, manual unlock
   is required, explicit Start creates the visible Android service, and no
   source request exists before both unlock and Start.
5. Exercise Home, screen off, device lock, Doze, network loss/switch, process
   kill, swipe-away, Task Manager Stop, reboot, package update, notification
   denial, notification STOP, and forced `dataSync` timeout. Use Android's
   documented compatibility flag and shortened timeout for the timeout case.
6. After every termination case, prove no service, socket, alarm, job, or
   reconnect survives and the next launch is stopped/locked with an honest
   coverage gap.
7. Persist a unique synthetic plaintext sentinel, STOP, and inspect the app
   database, WAL/journal, temp/cache, preferences, logcat, Android backup
   extraction, Windows files, crash output, and package upgrade artefacts.
   Only encrypted bytes may contain the record. Repeat tamper, wrong-
   passphrase, no-recovery reset, expiry, exact delete, and purge.
8. Measure memory, storage, bytes transferred, reconnect count, thermal state,
   and battery over a natural off-screen session. Separately force the Android
   15+ timeout; do not wait six hours merely to test the callback.
9. Produce signed test APK and MSIX artefacts, an unsigned/signed AAB as
   appropriate for the selected distribution process, and install/upgrade/
   uninstall evidence.
10. Update the foundation ADR only after the physical report is green. If MAUI
    cannot meet service, encryption, or packaging behaviour without weakening
    the contract, reopen the reserved alternatives rather than compensating in
    the UI.

## 12. Phase 0B gate matrix

| Gate requirement | Evidence | Result |
|---|---|---:|
| Windows and Android independently complete the full lifecycle | Design only; .NET console primitive probe on Windows; no Android build | **Fail** |
| Truthful phone foreground/background/suspended/offline/locked/stopped/degraded state | Proposed reducer only; no OS evidence | **Fail** |
| Ongoing Android notification exposes state and STOP | Android SDK/device absent | **Fail** |
| Notification STOP terminates service and prevents restart | Cancellation works in loopback console; no Android service | **Fail** |
| Encryption/source/retention/deletion guarantees survive mobile constraints | AES-GCM envelope primitive green; no SQLite/WAL, Keystore, backup, deletion, or mobile evidence | **Fail** |
| Direct WebSockets are bounded and stoppable | Loopback round-trip/cancellation green; no TLS relay or Android evidence | Partial |
| APK/AAB and signed MSIX packaging work | No required workloads/SDK/signing tools | **Fail** |
| Physical battery/bandwidth/memory/storage/thermal budgets exist | No physical device | **Fail** |
| Production foundation accepted before implementation | .NET 10 MAUI recommendation is provisional pending the failed evidence above | **Fail** |

**Decision:** Phase 0B does not pass. The project may accept .NET 10 MAUI as
the foundation to probe and may supersede the provisional Harken decision, but
it must not claim the Android station, production encrypted store, package, or
Phase 1 start gate as proven.
