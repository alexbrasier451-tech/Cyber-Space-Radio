# Phase 0B foundation probes

This directory contains the smallest locally runnable evidence that the
installed .NET SDK can support the proposed shared-core primitives. It does not
contact an external endpoint and does not claim Android or production proof.

## Run

```powershell
dotnet run --project .\tools\phase0b\FoundationProbe\FoundationProbe.csproj
```

The probe:

- begins and recovers in a stopped-and-locked state;
- exercises a synthetic passphrase-derived key envelope and AES-GCM record;
- verifies that its plaintext sentinel is absent from the temporary durable
  record and that tampering fails authentication;
- sends one text message over a loopback-only WebSocket and proves cancellation
  of a pending receive; and
- verifies that STOP removes reconnect permission.

It writes `FoundationProbe/probe-evidence.json`. The synthetic test passphrase
and message are not secrets. The temporary encrypted record is deleted before
the process exits.

This evidence does **not** validate Android foreground services, notifications,
Keystore behavior, OS suspension, physical-device battery or bandwidth, native
encrypted SQLite, MAUI UI, APK/AAB/MSIX packaging, or public-relay TLS.
