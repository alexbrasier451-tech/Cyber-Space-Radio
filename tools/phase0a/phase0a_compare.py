"""Bounded, aggregate-only Phase 0A Nostr/Jetstream comparison.

The live path deliberately has no content-output API. Received message bodies,
event identifiers, public keys, tags, and source payloads exist only in memory
for validation and aggregate calculation. The JSON result contains counts,
size distributions, timing, resource measurements, and implementation metadata.

This spike implements a small RFC 6455 client with the Python standard library
so that its dependency and adapter cost are visible. It is evidence tooling,
not the production streaming implementation.
"""

from __future__ import annotations

import argparse
import base64
import collections
import dataclasses
import hashlib
import inspect
import json
import math
import os
import re
import socket
import ssl
import statistics
import struct
import sys
import threading
import time
import tracemalloc
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import coincurve
from coincurve import PublicKeyXOnly


NOSTR_ENVELOPE_LIMIT_BYTES = 65_536
BODY_LIMIT_BYTES = 16_384
MAX_EVENTS_PER_SOURCE = 300
MAX_DURATION_SECONDS = 60.0
NOSTR_REPLAY_SECONDS = 60
NOSTR_RELAY_LIMIT = 100
SOCKET_TIMEOUT_SECONDS = 0.25
HANDSHAKE_LIMIT_BYTES = 16_384
MAX_TAGS = 100
MAX_TAG_ITEMS = 20
MAX_TAG_ITEM_BYTES = 2_048

SOURCES = {
    "nostr_damus": "wss://relay.damus.io",
    "nostr_nos_lol": "wss://nos.lol",
    "jetstream_v2_us_east": (
        "wss://jetstream.us-east.bsky.network/xrpc/"
        "network.bsky.jetstream.subscribeEvents"
    ),
}

# The tool emits only category counts, never the matched terms or source text.
RELATIONSHIP_TERMS = frozenset(
    {
        "relationship",
        "relationships",
        "dating",
        "boyfriend",
        "girlfriend",
        "husband",
        "wife",
        "breakup",
        "divorce",
        "marriage",
        "crush",
        "cheating",
        "affair",
        "gossip",
        "rumour",
        "rumor",
        "drama",
        "situationship",
    }
)
INTERPERSONAL_TERMS = RELATIONSHIP_TERMS | frozenset(
    {
        "love",
        "romance",
        "friend",
        "friends",
        "friendship",
        "family",
        "parent",
        "parents",
        "sibling",
        "siblings",
        "child",
        "children",
        "couple",
        "couples",
    }
)
TOKEN_RE = re.compile(r"[\w']+", re.UNICODE)
URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)
HEX_RE = re.compile(r"^[0-9a-f]+$")


class SafeWebSocketError(Exception):
    """A deliberately content-free WebSocket failure."""

    def __init__(self, category: str):
        super().__init__(category)
        self.category = category


class StopRequested(Exception):
    pass


class ConnectionClosed(Exception):
    pass


@dataclass(frozen=True)
class ReceivedMessage:
    payload: bytes | None
    opcode: int
    oversized: bool
    size_bytes: int


def _percentile(values: list[int], fraction: float) -> int | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, math.ceil(fraction * len(ordered)) - 1)
    return ordered[index]


def size_summary(values: list[int]) -> dict[str, int | float | None]:
    if not values:
        return {
            "count": 0,
            "mean_bytes": None,
            "median_bytes": None,
            "p75_bytes": None,
            "p90_bytes": None,
            "p95_bytes": None,
            "p99_bytes": None,
            "max_bytes": None,
        }
    return {
        "count": len(values),
        "mean_bytes": round(statistics.fmean(values), 1),
        "median_bytes": _percentile(values, 0.50),
        "p75_bytes": _percentile(values, 0.75),
        "p90_bytes": _percentile(values, 0.90),
        "p95_bytes": _percentile(values, 0.95),
        "p99_bytes": _percentile(values, 0.99),
        "max_bytes": max(values),
    }


def _safe_error_category(error: BaseException) -> str:
    if isinstance(error, SafeWebSocketError):
        return error.category
    if isinstance(error, socket.gaierror):
        return "dns"
    if isinstance(error, (ssl.SSLError, ssl.CertificateError)):
        return "tls"
    if isinstance(error, (TimeoutError, socket.timeout)):
        return "timeout"
    if isinstance(error, ConnectionClosed):
        return "closed"
    if isinstance(error, OSError):
        return "socket"
    return "other"


class WebSocketConnection:
    """Minimal bounded RFC 6455 client for approved WSS endpoints only."""

    def __init__(
        self,
        url: str,
        *,
        stop_event: threading.Event,
        max_message_bytes: int,
        subprotocol: str | None = None,
        operator_contact: str | None = None,
    ) -> None:
        self.url = url
        self.stop_event = stop_event
        self.max_message_bytes = max_message_bytes
        self.subprotocol = subprotocol
        self.operator_contact = operator_contact
        self.sock: ssl.SSLSocket | None = None
        self._read_buffer = bytearray()
        self.inbound_wire_bytes = 0
        self.outbound_wire_bytes = 0
        self._message_opcode: int | None = None
        self._message_parts: list[bytes] = []
        self._message_size = 0
        self._message_oversized = False

    def connect(self) -> None:
        parsed = urlsplit(self.url)
        if parsed.scheme != "wss" or not parsed.hostname:
            raise SafeWebSocketError("endpoint_not_approved_shape")
        host = parsed.hostname
        port = parsed.port or 443
        try:
            raw = socket.create_connection((host, port), timeout=10.0)
            context = ssl.create_default_context()
            self.sock = context.wrap_socket(raw, server_hostname=host)
            self.sock.settimeout(SOCKET_TIMEOUT_SECONDS)
        except BaseException:
            if "raw" in locals():
                raw.close()
            raise

        key = base64.b64encode(os.urandom(16)).decode("ascii")
        target = parsed.path or "/"
        if parsed.query:
            target += "?" + parsed.query
        host_header = host if port == 443 else f"{host}:{port}"
        headers = [
            f"GET {target} HTTP/1.1",
            f"Host: {host_header}",
            "Upgrade: websocket",
            "Connection: Upgrade",
            f"Sec-WebSocket-Key: {key}",
            "Sec-WebSocket-Version: 13",
            "User-Agent: CyberSpaceRadio-Phase0A/0.1",
        ]
        if self.subprotocol:
            headers.append(f"Sec-WebSocket-Protocol: {self.subprotocol}")
        if self.operator_contact:
            headers.append(f"X-Cyber-Space-Radio-Operator-Contact: {self.operator_contact}")
        request = ("\r\n".join(headers) + "\r\n\r\n").encode("ascii")
        self._send_raw(request)
        response = self._read_http_headers()
        status, response_headers = _parse_http_upgrade(response)
        if status != 101:
            raise SafeWebSocketError("handshake_rejected")
        expected = base64.b64encode(
            hashlib.sha1(
                (key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode("ascii")
            ).digest()
        ).decode("ascii")
        if response_headers.get("sec-websocket-accept") != expected:
            raise SafeWebSocketError("handshake_accept_invalid")
        if response_headers.get("upgrade", "").casefold() != "websocket":
            raise SafeWebSocketError("handshake_upgrade_invalid")
        if "upgrade" not in response_headers.get("connection", "").casefold():
            raise SafeWebSocketError("handshake_connection_invalid")
        selected = response_headers.get("sec-websocket-protocol")
        if selected and selected != self.subprotocol:
            raise SafeWebSocketError("handshake_subprotocol_invalid")

    def _read_http_headers(self) -> bytes:
        data = bytearray()
        while b"\r\n\r\n" not in data:
            if len(data) >= HANDSHAKE_LIMIT_BYTES:
                raise SafeWebSocketError("handshake_oversized")
            data.extend(self._recv_socket(min(4096, HANDSHAKE_LIMIT_BYTES - len(data))))
        head, remainder = bytes(data).split(b"\r\n\r\n", 1)
        if remainder:
            self._read_buffer.extend(remainder)
        return head

    def _recv_socket(self, limit: int) -> bytes:
        if self.stop_event.is_set():
            raise StopRequested
        assert self.sock is not None
        try:
            chunk = self.sock.recv(limit)
        except socket.timeout:
            if self.stop_event.is_set():
                raise StopRequested
            return b""
        if not chunk:
            raise ConnectionClosed
        self.inbound_wire_bytes += len(chunk)
        return chunk

    def _recv_some(self, limit: int) -> bytes:
        if self._read_buffer:
            size = min(limit, len(self._read_buffer))
            chunk = bytes(self._read_buffer[:size])
            del self._read_buffer[:size]
            return chunk
        return self._recv_socket(limit)

    def _read_exact(self, length: int) -> bytes:
        parts: list[bytes] = []
        remaining = length
        while remaining:
            chunk = self._recv_some(remaining)
            if not chunk:
                continue
            parts.append(chunk)
            remaining -= len(chunk)
        return b"".join(parts)

    def _discard_exact(self, length: int) -> None:
        remaining = length
        while remaining:
            chunk = self._recv_some(min(remaining, 16_384))
            if chunk:
                remaining -= len(chunk)

    def _send_raw(self, payload: bytes) -> None:
        if self.sock is None:
            raise SafeWebSocketError("not_connected")
        self.sock.sendall(payload)
        self.outbound_wire_bytes += len(payload)

    def send_text(self, text: str) -> None:
        self._send_frame(0x1, text.encode("utf-8"))

    def _send_frame(self, opcode: int, payload: bytes) -> None:
        mask = os.urandom(4)
        length = len(payload)
        if length < 126:
            header = bytes((0x80 | opcode, 0x80 | length))
        elif length <= 0xFFFF:
            header = bytes((0x80 | opcode, 0x80 | 126)) + struct.pack("!H", length)
        else:
            header = bytes((0x80 | opcode, 0x80 | 127)) + struct.pack("!Q", length)
        masked = bytes(value ^ mask[index % 4] for index, value in enumerate(payload))
        self._send_raw(header + mask + masked)

    def recv_message(self) -> ReceivedMessage | None:
        header = self._read_exact(2)
        first, second = header
        fin = bool(first & 0x80)
        if first & 0x70:
            raise SafeWebSocketError("unsupported_rsv")
        opcode = first & 0x0F
        if second & 0x80:
            raise SafeWebSocketError("masked_server_frame")
        length = second & 0x7F
        if length == 126:
            length = struct.unpack("!H", self._read_exact(2))[0]
        elif length == 127:
            length = struct.unpack("!Q", self._read_exact(8))[0]
            if length & (1 << 63):
                raise SafeWebSocketError("invalid_frame_length")

        if opcode >= 0x8:
            if not fin or length > 125:
                raise SafeWebSocketError("invalid_control_frame")
            payload = self._read_exact(length)
            if opcode == 0x8:
                raise ConnectionClosed
            if opcode == 0x9:
                self._send_frame(0xA, payload)
            return None

        if opcode in (0x1, 0x2):
            if self._message_opcode is not None:
                raise SafeWebSocketError("interleaved_data_frames")
            self._message_opcode = opcode
            self._message_parts = []
            self._message_size = 0
            self._message_oversized = False
        elif opcode == 0x0:
            if self._message_opcode is None:
                raise SafeWebSocketError("unexpected_continuation")
        else:
            self._discard_exact(length)
            raise SafeWebSocketError("unsupported_opcode")

        self._message_size += length
        if self._message_size > self.max_message_bytes:
            self._message_oversized = True
        if self._message_oversized:
            self._discard_exact(length)
        else:
            self._message_parts.append(self._read_exact(length))

        if not fin:
            return None
        message = ReceivedMessage(
            payload=None if self._message_oversized else b"".join(self._message_parts),
            opcode=self._message_opcode or opcode,
            oversized=self._message_oversized,
            size_bytes=self._message_size,
        )
        self._message_opcode = None
        self._message_parts = []
        self._message_size = 0
        self._message_oversized = False
        return message

    def close(self) -> None:
        sock = self.sock
        self.sock = None
        if sock is None:
            return
        try:
            self.sock = sock
            self._send_frame(0x8, struct.pack("!H", 1000))
        except BaseException:
            pass
        finally:
            self.sock = None
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            sock.close()


def _parse_http_upgrade(response: bytes) -> tuple[int, dict[str, str]]:
    try:
        lines = response.decode("iso-8859-1").split("\r\n")
        status_parts = lines[0].split(" ", 2)
        status = int(status_parts[1])
    except (UnicodeDecodeError, IndexError, ValueError) as error:
        raise SafeWebSocketError("handshake_malformed") from error
    headers: dict[str, str] = {}
    for line in lines[1:]:
        if not line:
            continue
        if ":" not in line:
            raise SafeWebSocketError("handshake_malformed")
        name, value = line.split(":", 1)
        headers[name.strip().casefold()] = value.strip()
    return status, headers


def bounded_json(payload: bytes, limit: int) -> tuple[Any | None, str | None]:
    if len(payload) > limit:
        return None, "oversized"
    try:
        text = payload.decode("utf-8", errors="strict")
        return json.loads(text), None
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, "malformed"


def _is_hex(value: Any, length: int) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and HEX_RE.fullmatch(value) is not None
    )


def _bounded_nostr_tags(tags: Any) -> bool:
    if not isinstance(tags, list) or len(tags) > MAX_TAGS:
        return False
    for tag in tags:
        if not isinstance(tag, list) or len(tag) > MAX_TAG_ITEMS:
            return False
        for value in tag:
            if not isinstance(value, str) or len(value.encode("utf-8")) > MAX_TAG_ITEM_BYTES:
                return False
    return True


@dataclass(frozen=True)
class NostrResult:
    valid_shape: bool
    valid_event_id: bool
    standalone: bool
    body_oversized: bool
    valid_signature: bool = False
    event_id: str | None = None
    content: str | None = None
    author_key: str | None = None
    created_at: int | None = None


def verify_schnorr_signature(
    public_key: bytes, signature: bytes, message: bytes
) -> bool:
    """Verify a BIP-340 signature with libsecp256k1 via coincurve.

    Malformed public keys and signatures fail closed. This wrapper is also the
    seam exercised against the authoritative BIP-340 verification vectors.
    """

    try:
        return PublicKeyXOnly(public_key).verify(signature, message)
    except ValueError:
        return False


def classify_nostr_event(event: Any) -> NostrResult:
    if not isinstance(event, dict):
        return NostrResult(False, False, False, False)
    event_id = event.get("id")
    pubkey = event.get("pubkey")
    created_at = event.get("created_at")
    kind = event.get("kind")
    tags = event.get("tags")
    content = event.get("content")
    sig = event.get("sig")
    shape_valid = (
        _is_hex(event_id, 64)
        and _is_hex(pubkey, 64)
        and isinstance(created_at, int)
        and not isinstance(created_at, bool)
        and isinstance(kind, int)
        and not isinstance(kind, bool)
        and _bounded_nostr_tags(tags)
        and isinstance(content, str)
        and _is_hex(sig, 128)
    )
    if not shape_valid:
        return NostrResult(False, False, False, False)
    body_size = len(content.encode("utf-8"))
    if body_size > BODY_LIMIT_BYTES:
        return NostrResult(True, False, False, True)
    canonical = json.dumps(
        [0, pubkey, created_at, kind, tags, content],
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    calculated = hashlib.sha256(canonical).hexdigest()
    valid_event_id = calculated == event_id
    if not valid_event_id:
        return NostrResult(True, False, False, False)
    valid_signature = verify_schnorr_signature(
        bytes.fromhex(pubkey), bytes.fromhex(sig), bytes.fromhex(event_id)
    )
    if not valid_signature:
        return NostrResult(True, True, False, False, False)
    addressed_tags = {"e", "p", "q"}
    standalone = kind == 1 and not any(
        tag and tag[0].casefold() in addressed_tags for tag in tags
    )
    return NostrResult(
        True,
        True,
        standalone,
        False,
        True,
        event_id=event_id,
        content=content,
        author_key=pubkey,
        created_at=created_at,
    )


@dataclass(frozen=True)
class JetstreamResult:
    valid_shape: bool
    standalone: bool
    body_oversized: bool
    sequence: int | None = None
    content: str | None = None
    author_key: str | None = None
    created_at_seconds: float | None = None
    reason: str | None = None


def _facet_has_mention(facets: Any) -> bool:
    if not isinstance(facets, list):
        return False
    for facet in facets:
        if not isinstance(facet, dict):
            continue
        features = facet.get("features")
        if not isinstance(features, list):
            continue
        for feature in features:
            if isinstance(feature, dict) and str(feature.get("$type", "")).endswith(
                "#mention"
            ):
                return True
    return False


def _deprecated_entity_has_mention(entities: Any) -> bool:
    return isinstance(entities, list) and any(
        isinstance(entity, dict) and entity.get("type") == "mention"
        for entity in entities
    )


def _parse_datetime_seconds(value: Any) -> float | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def classify_jetstream_event(message: Any) -> JetstreamResult:
    if not isinstance(message, dict):
        return JetstreamResult(False, False, False)
    if message.get("$type") == "message":
        payload = message.get("payload")
        if not isinstance(payload, dict):
            return JetstreamResult(False, False, False, reason="xrpc_envelope")
        message = payload
    type_name = message.get("$type")
    if not isinstance(type_name, str) or not type_name.endswith("#commit"):
        return JetstreamResult(False, False, False, reason="not_commit")
    sequence = message.get("seq")
    did = message.get("did")
    operation = message.get("operation")
    collection = message.get("collection")
    rkey = message.get("rkey")
    record = message.get("record")
    shape_valid = (
        isinstance(sequence, int)
        and not isinstance(sequence, bool)
        and isinstance(did, str)
        and did.startswith("did:")
        and operation in {"create", "update"}
        and collection == "app.bsky.feed.post"
        and isinstance(rkey, str)
        and isinstance(record, dict)
    )
    if not shape_valid:
        return JetstreamResult(False, False, False, reason="shape")
    content = record.get("text")
    if not isinstance(content, str) or not content.strip():
        return JetstreamResult(False, False, False, reason="empty")
    if len(content.encode("utf-8")) > BODY_LIMIT_BYTES:
        return JetstreamResult(True, False, True, sequence=sequence)
    if "reply" in record:
        return JetstreamResult(
            True, False, False, sequence=sequence, reason="reply"
        )
    if _facet_has_mention(record.get("facets")) or _deprecated_entity_has_mention(
        record.get("entities")
    ):
        return JetstreamResult(
            True, False, False, sequence=sequence, reason="recipient"
        )
    embed = record.get("embed")
    if isinstance(embed, dict) and embed.get("$type") in {
        "app.bsky.embed.record",
        "app.bsky.embed.recordWithMedia",
    }:
        return JetstreamResult(
            True, False, False, sequence=sequence, reason="quote"
        )
    created = _parse_datetime_seconds(record.get("createdAt"))
    return JetstreamResult(
        True,
        True,
        False,
        sequence=sequence,
        content=content,
        author_key=did,
        created_at_seconds=created,
    )


@dataclass
class ContentMetrics:
    body_sizes: list[int] = field(default_factory=list)
    envelope_sizes: list[int] = field(default_factory=list)
    relationship_yield: int = 0
    interpersonal_yield: int = 0
    structurally_flagged_events: int = 0
    structural_flag_counts: collections.Counter[str] = field(
        default_factory=collections.Counter
    )
    _body_hashes: set[bytes] = field(default_factory=set)
    _author_times: dict[bytes, collections.deque[float]] = field(default_factory=dict)

    def observe(
        self,
        content: str,
        *,
        author_key: str,
        event_time: float | None,
        envelope_size: int,
    ) -> None:
        body = content.encode("utf-8")
        self.body_sizes.append(len(body))
        self.envelope_sizes.append(envelope_size)
        normalized = content.casefold()
        terms = set(TOKEN_RE.findall(normalized))
        if terms & RELATIONSHIP_TERMS:
            self.relationship_yield += 1
        if terms & INTERPERSONAL_TERMS:
            self.interpersonal_yield += 1

        flags: set[str] = set()
        body_hash = hashlib.sha256(body).digest()
        if body_hash in self._body_hashes:
            flags.add("exact_body_repeat")
        self._body_hashes.add(body_hash)
        if re.search(r"(.)\1{19,}", normalized, re.DOTALL):
            flags.add("long_character_run")
        token_list = TOKEN_RE.findall(normalized)
        if len(token_list) >= 8:
            most_common = collections.Counter(token_list).most_common(1)[0][1]
            if most_common / len(token_list) >= 0.80:
                flags.add("mechanical_token_repeat")
        urls = URL_RE.findall(content)
        if len(urls) >= 3 and sum(map(len, urls)) >= max(1, int(len(content) * 0.60)):
            flags.add("url_heavy")
        if len(content) >= 32:
            alphanumeric = sum(character.isalnum() for character in content)
            if alphanumeric / len(content) <= 0.15:
                flags.add("symbol_heavy")

        author_hash = hashlib.sha256(author_key.encode("utf-8")).digest()
        timestamp = event_time if event_time is not None else time.time()
        recent = self._author_times.setdefault(author_hash, collections.deque())
        cutoff = timestamp - 10.0
        while recent and recent[0] < cutoff:
            recent.popleft()
        recent.append(timestamp)
        if len(recent) > 8:
            flags.add("publisher_burst")

        if flags:
            self.structurally_flagged_events += 1
            self.structural_flag_counts.update(flags)

    def aggregate(self) -> dict[str, Any]:
        return {
            "body_sizes": size_summary(self.body_sizes),
            "envelope_sizes": size_summary(self.envelope_sizes),
            "lexical_yield_counts": {
                "relationship_or_gossip_high_confidence": self.relationship_yield,
                "interpersonal_broad": self.interpersonal_yield,
            },
            "conservative_structural_noise": {
                "events_flagged": self.structurally_flagged_events,
                "flag_incidence": dict(sorted(self.structural_flag_counts.items())),
                "interpretation": "mechanical indicators only; not a content judgement",
            },
        }


@dataclass
class SourceStats:
    source_id: str
    family: str
    counters: collections.Counter[str] = field(default_factory=collections.Counter)
    errors: collections.Counter[str] = field(default_factory=collections.Counter)
    connection_seconds: float = 0.0
    first_connected_after_seconds: float | None = None
    last_event_after_seconds: float | None = None
    stop_close_latency_ms: float | None = None
    inbound_wire_bytes: int = 0
    outbound_wire_bytes: int = 0
    content: ContentMetrics = field(default_factory=ContentMetrics)

    def aggregate(self, wall_seconds: float) -> dict[str, Any]:
        event_count = self.counters["event_messages"]
        rate_basis = self.connection_seconds or wall_seconds
        return {
            "family": self.family,
            "counts": dict(sorted(self.counters.items())),
            "safe_error_categories": dict(sorted(self.errors.items())),
            "timing": {
                "connection_seconds": round(self.connection_seconds, 3),
                "first_connected_after_seconds": (
                    None
                    if self.first_connected_after_seconds is None
                    else round(self.first_connected_after_seconds, 3)
                ),
                "last_event_after_seconds": (
                    None
                    if self.last_event_after_seconds is None
                    else round(self.last_event_after_seconds, 3)
                ),
                "event_messages_per_second": round(event_count / rate_basis, 3),
                "stop_close_latency_ms": (
                    None
                    if self.stop_close_latency_ms is None
                    else round(self.stop_close_latency_ms, 3)
                ),
            },
            "approximate_bandwidth": {
                "inbound_wire_bytes": self.inbound_wire_bytes,
                "outbound_wire_bytes": self.outbound_wire_bytes,
                "inbound_bytes_per_second": round(
                    self.inbound_wire_bytes / max(rate_basis, 0.001), 1
                ),
            },
            **self.content.aggregate(),
        }


class NostrCombined:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._valid_sources: dict[str, set[str]] = {}
        self._standalone_sources: dict[str, set[str]] = {}
        self.content = ContentMetrics()
        self.classification_disagreements = 0

    def observe(
        self,
        *,
        source_id: str,
        event_id: str,
        standalone: bool,
        content: str | None,
        author_key: str | None,
        created_at: int | None,
        envelope_size: int,
    ) -> tuple[bool, bool]:
        with self._lock:
            valid_sources = self._valid_sources.setdefault(event_id, set())
            valid_duplicate = bool(valid_sources)
            valid_sources.add(source_id)
            standalone_duplicate = False
            if standalone:
                standalone_sources = self._standalone_sources.setdefault(event_id, set())
                standalone_duplicate = bool(standalone_sources)
                standalone_sources.add(source_id)
                if not standalone_duplicate:
                    assert content is not None and author_key is not None
                    self.content.observe(
                        content,
                        author_key=author_key,
                        event_time=float(created_at) if created_at is not None else None,
                        envelope_size=envelope_size,
                    )
            elif event_id in self._standalone_sources:
                self.classification_disagreements += 1
            return valid_duplicate, standalone_duplicate

    def aggregate(self) -> dict[str, Any]:
        with self._lock:
            overlap_valid = sum(len(sources) > 1 for sources in self._valid_sources.values())
            overlap_standalone = sum(
                len(sources) > 1 for sources in self._standalone_sources.values()
            )
            return {
                "unique_recomputed_id_valid": len(self._valid_sources),
                "unique_standalone": len(self._standalone_sources),
                "overlap_recomputed_id_valid": overlap_valid,
                "overlap_standalone": overlap_standalone,
                "classification_disagreements": self.classification_disagreements,
                **self.content.aggregate(),
            }


class BaseAdapter:
    family = "base"
    max_message_bytes = NOSTR_ENVELOPE_LIMIT_BYTES
    subprotocol: str | None = None

    def __init__(self, source_id: str, endpoint: str) -> None:
        self.source_id = source_id
        self.endpoint = endpoint
        self.operator_contact: str | None = None

    def url_for_connection(self) -> str:
        return self.endpoint

    def on_connected(self, connection: WebSocketConnection) -> None:
        del connection

    def handle_message(
        self, message: ReceivedMessage, stats: SourceStats, elapsed: float
    ) -> None:
        raise NotImplementedError


class NostrAdapter(BaseAdapter):
    family = "nostr"

    def __init__(self, source_id: str, endpoint: str, combined: NostrCombined) -> None:
        super().__init__(source_id, endpoint)
        self.combined = combined

    def on_connected(self, connection: WebSocketConnection) -> None:
        subscription_id = base64.urlsafe_b64encode(os.urandom(9)).decode("ascii")
        request = [
            "REQ",
            subscription_id,
            {
                "kinds": [1],
                "since": int(time.time()) - NOSTR_REPLAY_SECONDS,
                "limit": NOSTR_RELAY_LIMIT,
            },
        ]
        connection.send_text(json.dumps(request, separators=(",", ":")))

    def handle_message(
        self, message: ReceivedMessage, stats: SourceStats, elapsed: float
    ) -> None:
        stats.counters["data_messages_received"] += 1
        if message.oversized:
            stats.counters["oversized_envelopes"] += 1
            return
        assert message.payload is not None
        decoded, error = bounded_json(message.payload, NOSTR_ENVELOPE_LIMIT_BYTES)
        if error:
            stats.counters[f"{error}_envelopes"] += 1
            return
        if not (
            isinstance(decoded, list)
            and len(decoded) >= 1
            and isinstance(decoded[0], str)
        ):
            stats.counters["malformed_envelopes"] += 1
            return
        if decoded[0] != "EVENT":
            stats.counters["control_messages"] += 1
            return
        stats.counters["event_messages"] += 1
        stats.last_event_after_seconds = elapsed
        if len(decoded) != 3:
            stats.counters["malformed_events"] += 1
            return
        result = classify_nostr_event(decoded[2])
        if result.body_oversized:
            stats.counters["oversized_bodies"] += 1
            return
        if not result.valid_shape:
            stats.counters["invalid_event_shape"] += 1
            return
        stats.counters["valid_event_shape"] += 1
        if not result.valid_event_id:
            stats.counters["invalid_event_id"] += 1
            return
        stats.counters["recomputed_id_valid"] += 1
        if not result.valid_signature:
            stats.counters["invalid_schnorr_signature"] += 1
            return
        stats.counters["schnorr_signature_valid"] += 1
        if result.standalone:
            stats.counters["standalone_deliveries"] += 1
        else:
            stats.counters["structurally_addressed_or_conversational"] += 1
        assert result.event_id is not None
        valid_duplicate, standalone_duplicate = self.combined.observe(
            source_id=self.source_id,
            event_id=result.event_id,
            standalone=result.standalone,
            content=result.content,
            author_key=result.author_key,
            created_at=result.created_at,
            envelope_size=message.size_bytes,
        )
        if valid_duplicate:
            stats.counters["duplicate_valid_deliveries"] += 1
        if standalone_duplicate:
            stats.counters["duplicate_standalone_deliveries"] += 1


class JetstreamAdapter(BaseAdapter):
    family = "jetstream"
    subprotocol = "xrpc.v1.json"

    def __init__(self, source_id: str, endpoint: str, operator_contact: str) -> None:
        super().__init__(source_id, endpoint)
        self.operator_contact = operator_contact
        self._seen_sequences: set[int] = set()

    def url_for_connection(self) -> str:
        parsed = urlsplit(self.endpoint)
        query = parse_qsl(parsed.query, keep_blank_values=True)
        query.extend(
            [
                ("collections", "app.bsky.feed.post"),
                ("kinds", "commit"),
                ("cursor", str(int((time.time() - NOSTR_REPLAY_SECONDS) * 1_000_000))),
                ("maxMessageSizeBytes", str(NOSTR_ENVELOPE_LIMIT_BYTES)),
            ]
        )
        return urlunsplit(
            (parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment)
        )

    def handle_message(
        self, message: ReceivedMessage, stats: SourceStats, elapsed: float
    ) -> None:
        stats.counters["data_messages_received"] += 1
        if message.oversized:
            stats.counters["oversized_envelopes"] += 1
            return
        assert message.payload is not None
        decoded, error = bounded_json(message.payload, NOSTR_ENVELOPE_LIMIT_BYTES)
        if error:
            stats.counters[f"{error}_envelopes"] += 1
            return
        if isinstance(decoded, dict) and str(decoded.get("$type", "")).endswith("#info"):
            stats.counters["control_messages"] += 1
            return
        stats.counters["event_messages"] += 1
        stats.last_event_after_seconds = elapsed
        result = classify_jetstream_event(decoded)
        if result.body_oversized:
            stats.counters["oversized_bodies"] += 1
            return
        if not result.valid_shape:
            stats.counters["invalid_or_nonpost_events"] += 1
            if result.reason:
                stats.counters[f"rejected_{result.reason}"] += 1
            return
        stats.counters["valid_post_events"] += 1
        assert result.sequence is not None
        if result.sequence in self._seen_sequences:
            stats.counters["duplicate_events"] += 1
            return
        self._seen_sequences.add(result.sequence)
        if not result.standalone:
            stats.counters["structurally_addressed_or_conversational"] += 1
            if result.reason:
                stats.counters[f"rejected_{result.reason}"] += 1
            return
        stats.counters["standalone_unique"] += 1
        assert result.content is not None and result.author_key is not None
        stats.content.observe(
            result.content,
            author_key=result.author_key,
            event_time=result.created_at_seconds,
            envelope_size=message.size_bytes,
        )


class AdapterWorker:
    def __init__(
        self,
        adapter: BaseAdapter,
        *,
        stop_event: threading.Event,
        started_at: float,
        deadline: float,
        reconnect_after_seconds: float | None,
    ) -> None:
        self.adapter = adapter
        self.stop_event = stop_event
        self.started_at = started_at
        self.deadline = deadline
        self.reconnect_after_seconds = reconnect_after_seconds
        self.stats = SourceStats(adapter.source_id, adapter.family)
        self.thread = threading.Thread(target=self._run, name=adapter.source_id, daemon=True)
        self._connection_lock = threading.Lock()
        self._connection: WebSocketConnection | None = None
        self.stopped_at: float | None = None

    def start(self) -> None:
        self.thread.start()

    def request_stop(self, requested_at: float) -> None:
        self.stop_event.set()
        with self._connection_lock:
            connection = self._connection
        if connection:
            connection.close()
        if self.stopped_at is not None:
            self.stats.stop_close_latency_ms = max(0.0, (self.stopped_at - requested_at) * 1000)

    def join(self, timeout: float) -> None:
        self.thread.join(timeout)

    def _run(self) -> None:
        backoff = 0.5
        planned_done = False
        try:
            while not self.stop_event.is_set() and time.monotonic() < self.deadline:
                if self.stats.counters["event_messages"] >= MAX_EVENTS_PER_SOURCE:
                    self.stats.counters["intake_cap_reached"] += 1
                    break
                connection: WebSocketConnection | None = None
                connected_at: float | None = None
                try:
                    connection = WebSocketConnection(
                        self.adapter.url_for_connection(),
                        stop_event=self.stop_event,
                        max_message_bytes=self.adapter.max_message_bytes,
                        subprotocol=self.adapter.subprotocol,
                        operator_contact=self.adapter.operator_contact,
                    )
                    with self._connection_lock:
                        self._connection = connection
                    connection.connect()
                    connected_at = time.monotonic()
                    self.stats.counters["connections_succeeded"] += 1
                    if self.stats.first_connected_after_seconds is None:
                        self.stats.first_connected_after_seconds = connected_at - self.started_at
                    if self.stats.counters["connections_succeeded"] > 1:
                        self.stats.counters["reconnections_succeeded"] += 1
                    self.adapter.on_connected(connection)
                    backoff = 0.5
                    while not self.stop_event.is_set() and time.monotonic() < self.deadline:
                        now = time.monotonic()
                        if (
                            not planned_done
                            and self.reconnect_after_seconds is not None
                            and now - self.started_at >= self.reconnect_after_seconds
                        ):
                            planned_done = True
                            self.stats.counters["planned_disconnects"] += 1
                            connection.close()
                            break
                        if self.stats.counters["event_messages"] >= MAX_EVENTS_PER_SOURCE:
                            self.stats.counters["intake_cap_reached"] += 1
                            break
                        try:
                            message = connection.recv_message()
                        except socket.timeout:
                            continue
                        if message is None:
                            continue
                        elapsed = time.monotonic() - self.started_at
                        self.adapter.handle_message(message, self.stats, elapsed)
                    if self.stats.counters["event_messages"] >= MAX_EVENTS_PER_SOURCE:
                        break
                    if planned_done and self.stats.counters["reconnections_succeeded"] == 0:
                        self.stats.counters["reconnect_attempts"] += 1
                        continue
                except StopRequested:
                    break
                except BaseException as error:
                    self.stats.errors[_safe_error_category(error)] += 1
                    if self.stop_event.is_set() or time.monotonic() >= self.deadline:
                        break
                    self.stats.counters["reconnect_attempts"] += 1
                    wait_until = min(self.deadline, time.monotonic() + backoff)
                    while not self.stop_event.is_set() and time.monotonic() < wait_until:
                        time.sleep(0.05)
                    backoff = min(backoff * 2, 8.0)
                finally:
                    if connected_at is not None:
                        self.stats.connection_seconds += max(
                            0.0, time.monotonic() - connected_at
                        )
                    if connection:
                        connection.close()
                    if connection is not None:
                        self.stats.inbound_wire_bytes += connection.inbound_wire_bytes
                        self.stats.outbound_wire_bytes += connection.outbound_wire_bytes
                    with self._connection_lock:
                        self._connection = None
        finally:
            self.stopped_at = time.monotonic()
            self.stats.counters["worker_exited"] += 1


def _nonblank_sloc(target: type[Any]) -> int:
    return sum(
        1
        for line in inspect.getsource(target).splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )


def run_comparison(
    duration_seconds: float,
    reconnect_after_seconds: float | None,
    source_family: str,
    operator_contact: str | None,
) -> dict[str, Any]:
    if not 1.0 <= duration_seconds <= MAX_DURATION_SECONDS:
        raise ValueError(f"duration must be between 1 and {MAX_DURATION_SECONDS:g} seconds")
    if reconnect_after_seconds is not None and not (
        0.5 <= reconnect_after_seconds < duration_seconds
    ):
        raise ValueError("reconnect-after must be at least 0.5 and below duration")
    if source_family not in {"nostr", "jetstream", "all"}:
        raise ValueError("sources must be nostr, jetstream, or all")
    if source_family in {"jetstream", "all"}:
        if not operator_contact:
            raise ValueError(
                "Jetstream requires --operator-contact containing an already-published "
                "honest project contact"
            )
        if (
            len(operator_contact) > 256
            or any(ord(character) < 33 or ord(character) > 126 for character in operator_contact)
            or ":" not in operator_contact
        ):
            raise ValueError(
                "operator contact must be a 1..256 byte printable ASCII URI or mailto URI"
            )

    stop_event = threading.Event()
    combined = NostrCombined()
    adapters: list[BaseAdapter] = []
    if source_family in {"nostr", "all"}:
        adapters.extend(
            [
                NostrAdapter("nostr_damus", SOURCES["nostr_damus"], combined),
                NostrAdapter("nostr_nos_lol", SOURCES["nostr_nos_lol"], combined),
            ]
        )
    if source_family in {"jetstream", "all"}:
        assert operator_contact is not None
        adapters.append(
            JetstreamAdapter(
                "jetstream_v2_us_east",
                SOURCES["jetstream_v2_us_east"],
                operator_contact,
            )
        )
    started = time.monotonic()
    deadline = started + duration_seconds
    cpu_started = time.process_time()
    tracemalloc.start()
    workers = [
        AdapterWorker(
            adapter,
            stop_event=stop_event,
            started_at=started,
            deadline=deadline,
            reconnect_after_seconds=reconnect_after_seconds,
        )
        for adapter in adapters
    ]
    for worker in workers:
        worker.start()
    while time.monotonic() < deadline and any(worker.thread.is_alive() for worker in workers):
        time.sleep(0.05)
    stop_requested_at = time.monotonic()
    stop_event.set()
    for worker in workers:
        worker.request_stop(stop_requested_at)
    for worker in workers:
        worker.join(3.0)
        if worker.thread.is_alive():
            worker.stats.counters["stop_timeout"] += 1
        elif worker.stopped_at is not None:
            worker.stats.stop_close_latency_ms = max(
                0.0, (worker.stopped_at - stop_requested_at) * 1000
            )
    current_heap, peak_heap = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    ended = time.monotonic()
    wall_seconds = ended - started

    per_source = {
        worker.stats.source_id: worker.stats.aggregate(wall_seconds) for worker in workers
    }
    return {
        "schema": "cyber-space-radio/phase0a-comparison-aggregate/1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "method": {
            "duration_limit_seconds": duration_seconds,
            "replay_limit_seconds": NOSTR_REPLAY_SECONDS,
            "event_limit_per_source": MAX_EVENTS_PER_SOURCE,
            "nostr_local_subscription_limit": NOSTR_RELAY_LIMIT,
            "nostr_envelope_limit_bytes": NOSTR_ENVELOPE_LIMIT_BYTES,
            "decoded_body_limit_bytes": BODY_LIMIT_BYTES,
            "planned_reconnect_after_seconds": reconnect_after_seconds,
            "source_family_selection": source_family,
            "source_ids_included": [adapter.source_id for adapter in adapters],
            "operator_contact_prerequisite_satisfied": bool(operator_contact),
            "operator_contact_value_output_or_persisted": False,
            "credentials_or_authentication_used": False,
            "publishing_or_contact_performed": False,
            "raw_content_output_or_persistence": False,
            "nostr_event_id_recalculation": True,
            "nostr_schnorr_signature_verification_available": True,
            "nostr_signature_verifier": "coincurve",
            "nostr_signature_verifier_version": coincurve.__version__,
            "nostr_signature_verified_count": sum(
                worker.stats.counters["schnorr_signature_valid"]
                for worker in workers
                if worker.adapter.family == "nostr"
            ),
            "jetstream_repository_signature_verification": False,
        },
        "resource": {
            "wall_seconds": round(wall_seconds, 3),
            "cpu_seconds": round(time.process_time() - cpu_started, 3),
            "traced_python_heap_current_bytes": current_heap,
            "traced_python_heap_peak_bytes": peak_heap,
            "worker_threads": len(workers),
        },
        "per_source": per_source,
        "nostr_combined_deduplicated": combined.aggregate(),
        "adapter_complexity": {
            "shared_websocket_nonblank_sloc": _nonblank_sloc(WebSocketConnection),
            "nostr_adapter_nonblank_sloc": _nonblank_sloc(NostrAdapter),
            "jetstream_adapter_nonblank_sloc": _nonblank_sloc(JetstreamAdapter),
            "measurement_note": "class-source nonblank lines; excludes shared classifiers/tests",
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the bounded aggregate-only Phase 0A live comparison."
    )
    parser.add_argument(
        "--sources",
        choices=("nostr", "jetstream", "all"),
        default="all",
        help="Source family to sample (default: all).",
    )
    parser.add_argument(
        "--operator-contact",
        help=(
            "Already-published honest project contact URI. Required for Jetstream, "
            "exposed in the handshake, and never included in aggregate output."
        ),
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=60.0,
        help="Wall-clock sample duration, 1..60 seconds (default: 60).",
    )
    parser.add_argument(
        "--reconnect-after",
        type=float,
        default=5.0,
        help="One planned reconnect after this many seconds; use 0 to disable.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional aggregate-only JSON output path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    reconnect_after = None if args.reconnect_after == 0 else args.reconnect_after
    try:
        result = run_comparison(
            args.duration,
            reconnect_after,
            args.sources,
            args.operator_contact,
        )
    except ValueError as error:
        print(f"configuration error: {error}", file=sys.stderr)
        return 2
    serialized = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized + "\n", encoding="utf-8")
    print(serialized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
