# Phase 0A aggregate comparison tool

`phase0a_compare.py` makes one direct, unauthenticated, read-only WebSocket
connection to each selected approved comparison source. It samples for at most
60 seconds and processes at most 300 event messages per source. The two approved
Nostr relays run concurrently and are deduplicated in memory.

The tool never publishes or contacts an author. Received bodies, identifiers,
keys, tags, and payloads are never printed or written. JSON output contains only
aggregate counts, distributions, timing, bandwidth estimates, and resource
measurements. Safe error categories intentionally omit exception text.

The spike recalculates each Nostr event ID and then verifies its BIP-340
Schnorr signature before it can be classified, counted as standalone, or
passed to the in-memory aggregate. Invalid IDs and signatures fail closed.
The verifier is `coincurve==21.0.0`, maintained Python bindings to Bitcoin
Core's `libsecp256k1`, pinned for the Windows CPython 3.12 evidence runtime.

This order implements the [NIP-01 event and signature contract](https://github.com/nostr-protocol/nips/blob/master/01.md).
The verifier seam is tested against all 19 official
[BIP-340 verification vectors](https://github.com/bitcoin/bips/blob/200f9b26fe0a2f235a2af8b30c4be9f12f6bc9cb/bip-0340/test-vectors.csv).
The checked-in vector copy has SHA-256
`01c8cabba63b4c9b2f44c975902990086a4fe56eee9d265b187d1e2c1d98ccfb`.

Jetstream v2's `xrpc.v1.json` wire path wraps each Lexicon event in an outer
`{"$type":"message","payload":...}` envelope. The adapter requires and unwraps
that envelope before applying commit, post-shape, reply, recipient, quote, and
body-size rules. A malformed message envelope fails closed.

## Create the reproducible evidence environment

From this directory with 64-bit CPython 3.12 on Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install `
  --require-hashes `
  -r .\requirements-win-py312.lock
```

The lock permits only the `coincurve 21.0.0` CPython 3.12 Windows x64 wheel,
whose SHA-256 is
`5dd7b66b83b143f3ad3861a68fc0279167a0bae44fe3931547400b7a200e90b1`.
The virtual environment and pip download cache are ignored locally rather than
committed.

## Run fixtures

From this directory after creating the evidence environment:

```powershell
.\.venv\Scripts\python.exe -m unittest -v test_phase0a_compare.py
```

## Run the approved Nostr trial

```powershell
.\.venv\Scripts\python.exe phase0a_compare.py `
  --sources nostr `
  --duration 60 `
  --reconnect-after 5 `
  --output evidence/live-nostr.json
```

Jetstream remains approved-disabled for routine operation. The project's
[public operator contact](../../CONTACT.md) has passed publication,
receive/reply, and client-exposure checks, so an explicitly authorized bounded
trial passes that URI in the WebSocket handshake. The value is never printed or
written to aggregate evidence:

```powershell
.\.venv\Scripts\python.exe phase0a_compare.py `
  --sources all `
  --operator-contact mailto:cyberspaceradio@proton.me `
  --duration 60 `
  --output evidence/live-all.json
```

Omitting `--operator-contact` makes `--sources jetstream` and `--sources all`
fail closed.

`--reconnect-after 0` disables the single planned reconnect. The client still
uses bounded exponential backoff after an unexpected close. Run the live path
only while the reviewed source rows remain approved and current.
