# Consent-only federation design

## Boundary

Cyber Space Radio may federate only among nodes whose operators explicitly
install them and whose identities and exact addresses are present in local
configuration. A node never discovers, enrolls, installs, forwards to, or
configures another node. Received data can never trigger a fetch, process
launch, configuration change, or external action.

This is the safe interpretation of “grow like fungus”: independently operated
sites can opt into the same protocol. It is not self-propagation.

The first implementation should support at most 32 peers. Every node directly
checks every configured peer. This makes loss observations simple and honest,
but costs O(N²) requests and is not intended for Internet-scale membership.

## What leaves a node

Filtering happens locally. Ignored, addressed/conversational, excluded,
duplicate, and malformed source
entries never enter federation. A recorded match becomes a compact digest:

```json
{
  "protocol": "csr-federation/1",
  "origin": "node-london-1",
  "boot_id": "random-uuid-per-start",
  "sequence": 184,
  "event_id": "sha256-of-public-entry-identity",
  "observed_at": "2026-08-14T00:05:22Z",
  "source_id": "sha256-of-canonical-approved-source",
  "idea_id": "sha256-of-normalized-local-rule",
  "score_basis_points": 7500
}
```

Raw post text, titles, author names, full URLs, query tokens, request headers,
client IP addresses, browsing history, and local matching rules remain local.
Authentication proves only which node made a report; displays must say “node A
reported” rather than treating the report as independently verified fact.

## Membership and loss reports

Nodes exchange a small authenticated heartbeat every 30 seconds, with bounded
jitter. Reachability uses the local monotonic clock:

```text
unknown -> healthy      after one authenticated exchange
healthy -> suspect      after two failures or 75 seconds without success
suspect -> unavailable  after four failures and 150 seconds without success
unavailable -> recovering after one success
recovering -> healthy   after a second consecutive success
```

States are observer-specific. A partition means “London cannot reach Leeds,”
not “Leeds is dead.” Indirect reports are retained only as another node’s
opinion and cannot override direct evidence. Stale observations expire after
ten minutes.

The protocol never rebroadcasts a received report. Each node sends only its own
heartbeats and its own locally produced match digests. This prevents loops and
amplification while ensuring every configured surviving node independently
notices a missing peer.

## Encryption and identity

“Deep encryption” means established defense in depth, not custom cryptography:

1. TLS 1.3 encrypts transport.
2. Mutual TLS requires both sides to present operator-issued certificates.
3. Each configured `node_id` is pinned to its certificate identity or SHA-256
   fingerprint. There is no federation-wide shared password.
4. Envelopes contain a protocol version, node ID, random boot ID, strictly
   increasing sequence, issued time, expiry, and random message ID.
5. A bounded replay cache rejects duplicates and stale or far-future messages.
6. Persistent records use operating-system or deployment-platform encryption
   at rest. Private keys belong in that platform's secret store, never in the
   repository or ordinary configuration.
7. Certificates and keys have short validity, documented rotation, and an
   operator-controlled revocation path.

Use Python's `ssl` module or a TLS-terminating platform for transport. Use a
maintained implementation such as `cryptography` if end-to-end Ed25519
signatures are added; do not implement primitives locally. Certificate and
hostname validation must never be disabled.

## One-touch emergency stop

Every node needs a short-lived operating lease issued by a separate
operator-controlled control plane. A lease identifies the federation,
generation, node, issue time, expiry time, and whether operation is enabled.
It is authenticated independently of peer traffic.

The red **STOP NETWORK** control performs these actions:

1. increments the control-plane generation and marks the federation disabled;
2. stops issuing or renewing active leases;
3. pushes the disabled state to reachable nodes;
4. records an operator audit event.

Upon a disabled or expired lease, a node closes its federation listener, stops
source stream connections, polling, reconnects, and outbound reporting, clears
volatile queues, and exits cleanly.
It does not delete logs or evidence. A peer cannot issue, renew, or cancel a
lease. Restarting a process cannot bypass the stop because it still lacks an
active lease.

Disconnected nodes stop when their existing lease expires. A 60-second lease
with renewal every 20 seconds gives a maximum disconnected shutdown delay of
about one minute. Shorter leases make the system more sensitive to harmless
control-plane outages. A fail-closed lease cannot provide both zero delay and
partition tolerance.

Re-enabling requires a deliberate operator action that creates a newer active
generation. A stale enable message can never override a later stop generation.

## Resource bounds

Zero resource use is impossible. A node must hold code, certificates, its peer
allowlist, replay state, and health timers. The target is small and bounded:

- at most 32 static peers;
- at most eight concurrent inbound requests;
- request and response bodies no larger than 64 KiB;
- at most 64 digests per batch;
- replay cache capped at 2,048 message IDs;
- received digest ring capped at 1,024 entries;
- report queue capped at 512 events;
- connection and read timeout of five seconds;
- no raw content cache on federated nodes;
- no retries without a capped exponential backoff.

If state is corrupt, local monitoring may continue, but federation fails closed
until the operator repairs it. No node invents a new identity or sequence to
hide lost records.

## Control plane and reporting

An optional configured sink receives only these typed events:

- `match_originated`
- `peer_suspect`
- `peer_unavailable`
- `peer_recovered`
- `replication_gap`
- aggregated `authentication_failure`
- `emergency_stop`

The sink response body is ignored. It cannot return commands, configuration,
peer addresses, rules, or URLs. Nodes contact only approved source, peer, control-plane,
and sink endpoints written in local operator configuration.

## Required proof before Internet deployment

- Unknown, expired, revoked, and wrong-node certificates are rejected.
- Changed, replayed, stale, future, duplicate-key, malformed, and oversized
  envelopes are rejected without amplification.
- Received strings cannot create log lines, HTML, shell input, code, peer
  membership, fetches, or configuration changes.
- Rate, connection, queue, replay, retention, and disk limits remain bounded
  under load.
- In a three-node test, stopping one node causes both survivors to report their
  own loss observation, and recovery requires two direct successes.
- A network partition displays contradictory observer evidence rather than a
  false global-death claim.
- Pressing STOP makes reachable nodes dormant immediately and isolated nodes
  dormant no later than lease expiry; restart does not bypass it.
- Federation payloads contain no public post body, author, raw rule, client IP,
  credential, or full source URL.
- No network message can add peers, change rules, launch code, or request an
  arbitrary URL.

The network-facing federation and control plane should not be enabled until
these checks pass with real certificates in the intended hosting environment.
