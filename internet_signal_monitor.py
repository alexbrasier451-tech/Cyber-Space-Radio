"""Record public feed entries that resemble one of the configured ideas.

This is an application-level public-content monitor, not a packet sniffer. It
reads only RSS/Atom feed URLs supplied by the operator and stores only matches.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import tempfile
import time
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable, Iterable
from urllib.parse import urlparse


MAX_FEED_BYTES = 5_000_000
MIN_CONTINUOUS_INTERVAL_SECONDS = 900
USER_AGENT = "CyberSpaceRadio-PublicFeedMonitor/1.0"
TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:['-][a-z0-9]+)?")
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "i",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "was",
    "what",
    "when",
    "where",
    "with",
    "you",
}


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def strip_markup(value: str) -> str:
    parser = _TextExtractor()
    try:
        parser.feed(html.unescape(value))
        parser.close()
    except (ValueError, AssertionError):
        return html.unescape(value)
    return " ".join(part.strip() for part in parser.parts if part.strip())


def tokens(value: str) -> set[str]:
    return {
        token
        for token in TOKEN_PATTERN.findall(strip_markup(value).casefold())
        if token not in STOP_WORDS
    }


def relevance_score(idea: str, text: str) -> float:
    """Return lexical idea coverage from 0.0 to 1.0.

    This deliberately makes no claim of understanding a person's intent. A
    local embedding model can replace this function if true semantic matching
    is required later.
    """
    idea_terms = tokens(idea)
    text_terms = tokens(text)
    if not idea_terms or not text_terms:
        return 0.0

    matched = idea_terms & text_terms
    minimum_terms = 1 if len(idea_terms) == 1 else 2
    if len(matched) < minimum_terms:
        return 0.0

    return len(matched) / len(idea_terms)


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _child(element: ET.Element, name: str) -> ET.Element | None:
    return next((item for item in element if _local_name(item.tag) == name), None)


def _text(element: ET.Element, *names: str) -> str:
    for name in names:
        item = _child(element, name)
        if item is not None:
            value = "".join(item.itertext()).strip()
            if value:
                return value
    return ""


def _atom_link(entry: ET.Element) -> str:
    fallback = ""
    for item in entry:
        if _local_name(item.tag) != "link":
            continue
        href = item.attrib.get("href", "").strip()
        if not href:
            continue
        if item.attrib.get("rel", "alternate") == "alternate":
            return href
        fallback = fallback or href
    return fallback


@dataclass(frozen=True)
class FeedEntry:
    feed_title: str
    title: str
    link: str
    entry_id: str
    summary: str
    author: str
    published: str

    @property
    def searchable_text(self) -> str:
        return f"{self.title} {self.summary}".strip()


def parse_feed(document: bytes) -> tuple[str, list[FeedEntry]]:
    """Parse RSS 2.x or Atom XML without resolving external entities."""
    root = ET.fromstring(document)
    root_name = _local_name(root.tag).casefold()

    if root_name in {"rss", "rdf"}:
        found_channel = _child(root, "channel")
        channel = found_channel if found_channel is not None else root
        feed_title = strip_markup(_text(channel, "title"))
        items = [item for item in channel if _local_name(item.tag) == "item"]
        entries = [
            FeedEntry(
                feed_title=feed_title,
                title=strip_markup(_text(item, "title")),
                link=_text(item, "link"),
                entry_id=_text(item, "guid") or _text(item, "link"),
                summary=strip_markup(_text(item, "description", "content")),
                author=strip_markup(_text(item, "creator", "author")),
                published=_text(item, "pubDate", "date"),
            )
            for item in items
        ]
        return feed_title, entries

    if root_name == "feed":
        feed_title = strip_markup(_text(root, "title"))
        entries: list[FeedEntry] = []
        for item in (node for node in root if _local_name(node.tag) == "entry"):
            author_element = _child(item, "author")
            author = _text(author_element, "name") if author_element is not None else ""
            link = _atom_link(item)
            entries.append(
                FeedEntry(
                    feed_title=feed_title,
                    title=strip_markup(_text(item, "title")),
                    link=link,
                    entry_id=_text(item, "id") or link,
                    summary=strip_markup(_text(item, "summary", "content")),
                    author=strip_markup(author),
                    published=_text(item, "published", "updated"),
                )
            )
        return feed_title, entries

    raise ValueError(f"Unsupported feed root element: {root_name}")


def fetch_feed(
    url: str,
    timeout: float = 15.0,
    user_agent: str = USER_AGENT,
) -> bytes:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Feed URLs must use http:// or https://")

    request = urllib.request.Request(
        url,
        headers={"User-Agent": user_agent, "Accept": "application/rss+xml, "
        "application/atom+xml, application/xml, text/xml"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        document = response.read(MAX_FEED_BYTES + 1)
    if len(document) > MAX_FEED_BYTES:
        raise ValueError(f"Feed exceeds the {MAX_FEED_BYTES}-byte limit")
    return document


def _fingerprint(feed_url: str, entry: FeedEntry) -> str:
    identity = entry.entry_id or entry.link or entry.title
    material = f"{feed_url}\n{identity}\n{entry.searchable_text}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def load_recorded_fingerprints(log_path: Path) -> set[str]:
    fingerprints: set[str] = set()
    if not log_path.exists():
        return fingerprints

    with log_path.open("r", encoding="utf-8") as log:
        for line_number, line in enumerate(log, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                fingerprint = record["fingerprint"]
            except (json.JSONDecodeError, KeyError, TypeError) as error:
                raise ValueError(
                    f"Invalid JSON Lines record at {log_path}:{line_number}"
                ) from error
            if isinstance(fingerprint, str):
                fingerprints.add(fingerprint)
    return fingerprints


def prune_expired_records(log_path: Path, retention_days: int) -> int:
    """Remove records older than the configured retention period atomically."""
    if not log_path.exists():
        return 0

    cutoff = datetime.now(timezone.utc).timestamp() - (retention_days * 86_400)
    kept: list[str] = []
    removed = 0
    with log_path.open("r", encoding="utf-8") as log:
        for line_number, line in enumerate(log, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                observed_at = datetime.fromisoformat(record["observed_at"])
                observed_timestamp = observed_at.timestamp()
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
                raise ValueError(
                    f"Invalid JSON Lines record at {log_path}:{line_number}"
                ) from error
            if observed_timestamp >= cutoff:
                kept.append(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
            else:
                removed += 1

    if not removed:
        return 0

    log_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name = ""
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            newline="\n",
            delete=False,
            dir=log_path.parent,
            prefix=f".{log_path.name}.",
            suffix=".tmp",
        ) as temporary:
            temporary_name = temporary.name
            for line in kept:
                temporary.write(line + "\n")
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_name, log_path)
    finally:
        if temporary_name and os.path.exists(temporary_name):
            os.unlink(temporary_name)
    return removed


@dataclass
class ScanResult:
    feeds_scanned: int = 0
    entries_seen: int = 0
    recorded: int = 0
    ignored: int = 0
    duplicates: int = 0
    errors: int = 0


Fetcher = Callable[[str], bytes]


def scan_once(
    feed_urls: Iterable[str],
    ideas: list[str],
    log_path: Path,
    *,
    min_score: float = 0.6,
    exclusions: Iterable[str] = (),
    store_content: bool = False,
    retention_days: int = 7,
    fetcher: Fetcher = fetch_feed,
    announce: Callable[[str], None] = print,
) -> ScanResult:
    result = ScanResult()
    prune_expired_records(log_path, retention_days)
    recorded = load_recorded_fingerprints(log_path)
    exclusion_terms = [tokens(value) for value in exclusions if tokens(value)]

    for feed_url in feed_urls:
        try:
            document = fetcher(feed_url)
            _feed_title, entries = parse_feed(document)
        except Exception as error:  # A bad feed must not stop the other feeds.
            result.errors += 1
            announce(f"[error] {feed_url}: {error}")
            continue

        result.feeds_scanned += 1
        for entry in entries:
            result.entries_seen += 1
            entry_terms = tokens(entry.searchable_text)
            if any(excluded <= entry_terms for excluded in exclusion_terms):
                result.ignored += 1
                continue

            scores = [(relevance_score(idea, entry.searchable_text), idea) for idea in ideas]
            score, matched_idea = max(scores, default=(0.0, ""))
            if score < min_score:
                result.ignored += 1
                continue

            fingerprint = _fingerprint(feed_url, entry)
            if fingerprint in recorded:
                result.duplicates += 1
                continue

            record = {
                "observed_at": datetime.now(timezone.utc).isoformat(),
                "source": {
                    "feed_url": feed_url,
                    "feed_title": entry.feed_title,
                    "entry_url": entry.link,
                },
                "entry": {
                    "title": entry.title,
                    "published": entry.published,
                },
                "match": {"idea": matched_idea, "score": round(score, 4)},
                "fingerprint": fingerprint,
            }
            if store_content:
                record["source"]["public_author"] = entry.author
                record["entry"]["summary"] = entry.summary
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with log_path.open("a", encoding="utf-8", newline="\n") as log:
                log.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
                log.write("\n")
            recorded.add(fingerprint)
            result.recorded += 1
            announce(f"[match {score:.0%}] {entry.title} - {entry.link or feed_url}")

    return result


def load_feed_urls(inline: Iterable[str], files: Iterable[Path]) -> list[str]:
    urls = [value.strip() for value in inline if value.strip()]
    for path in files:
        for line in path.read_text(encoding="utf-8").splitlines():
            value = line.strip()
            if value and not value.startswith("#"):
                urls.append(value)
    return list(dict.fromkeys(urls))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--idea",
        action="append",
        required=True,
        help="Idea or question to match; may be supplied more than once",
    )
    parser.add_argument("--feed", action="append", default=[], help="RSS/Atom URL")
    parser.add_argument(
        "--feeds-file",
        action="append",
        type=Path,
        default=[],
        help="Text file containing one feed URL per line",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Ignore entries containing all terms in this phrase",
    )
    parser.add_argument("--min-score", type=float, default=0.6)
    parser.add_argument("--log", type=Path, default=Path("matches.jsonl"))
    parser.add_argument(
        "--retention-days",
        type=int,
        default=7,
        help="Delete local records older than this many days (default: 7)",
    )
    parser.add_argument(
        "--store-content",
        action="store_true",
        help="Also retain public author and summary; off by default",
    )
    parser.add_argument(
        "--contact",
        help="Operator email or URL included in continuous-poll User-Agent",
    )
    parser.add_argument(
        "--interval",
        type=int,
        help="Repeat every N seconds (minimum 900); otherwise scan once",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    feed_urls = load_feed_urls(args.feed, args.feeds_file)
    if not feed_urls:
        raise SystemExit("Supply at least one --feed or --feeds-file.")
    if not 0.0 < args.min_score <= 1.0:
        raise SystemExit("--min-score must be greater than 0 and at most 1.")
    if args.retention_days < 1:
        raise SystemExit("--retention-days must be at least 1.")
    if args.interval is not None and args.interval < MIN_CONTINUOUS_INTERVAL_SECONDS:
        raise SystemExit(
            f"--interval must be at least {MIN_CONTINUOUS_INTERVAL_SECONDS} seconds."
        )
    if args.interval is not None and not args.contact:
        raise SystemExit("Continuous polling requires --contact.")

    user_agent = USER_AGENT
    if args.contact:
        clean_contact = re.sub(r"[\x00-\x20\x7f]+", " ", args.contact).strip()
        if not clean_contact or len(clean_contact) > 200:
            raise SystemExit("--contact must contain 1 to 200 printable characters.")
        user_agent = f"{USER_AGENT} (+{clean_contact})"
    configured_fetcher = lambda url: fetch_feed(url, user_agent=user_agent)

    while True:
        result = scan_once(
            feed_urls,
            args.idea,
            args.log,
            min_score=args.min_score,
            exclusions=args.exclude,
            store_content=args.store_content,
            retention_days=args.retention_days,
            fetcher=configured_fetcher,
        )
        print(json.dumps(asdict(result), separators=(",", ":")))
        if args.interval is None:
            break
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
