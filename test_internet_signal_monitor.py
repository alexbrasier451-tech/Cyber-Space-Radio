import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from internet_signal_monitor import (
    parse_feed,
    prune_expired_records,
    relevance_score,
    scan_once,
)


RSS = b"""<?xml version="1.0"?>
<rss version="2.0"><channel><title>Public Questions</title>
  <item><guid>1</guid><title>Community-owned networks</title>
    <link>https://example.test/posts/1</link>
    <description>How can we build a decentralized local network?</description>
    <author>Public Author</author><pubDate>Thu, 13 Aug 2026 10:00:00 GMT</pubDate>
  </item>
  <item><guid>2</guid><title>Ordinary cooking question</title>
    <link>https://example.test/posts/2</link>
    <description>How long should pasta cook?</description>
  </item>
</channel></rss>"""


ATOM = b"""<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom"><title>Idea Feed</title>
  <entry><id>tag:example.test,2026:3</id><title>Local mesh networking</title>
    <link href="https://example.test/posts/3"/>
    <summary>Building a decentralized community network.</summary>
    <author><name>Visible Name</name></author><updated>2026-08-13T11:00:00Z</updated>
  </entry>
</feed>"""


class InternetSignalMonitorTests(unittest.TestCase):
    def test_relevance_requires_multiple_meaningful_terms(self) -> None:
        idea = "decentralized community network"
        self.assertEqual(relevance_score(idea, "A cooking network show"), 0.0)
        self.assertAlmostEqual(
            relevance_score(idea, "A decentralized community project"), 2 / 3
        )

    def test_parses_rss_and_atom_sources(self) -> None:
        rss_title, rss_entries = parse_feed(RSS)
        atom_title, atom_entries = parse_feed(ATOM)

        self.assertEqual(rss_title, "Public Questions")
        self.assertEqual(rss_entries[0].author, "Public Author")
        self.assertEqual(atom_title, "Idea Feed")
        self.assertEqual(atom_entries[0].link, "https://example.test/posts/3")
        self.assertEqual(atom_entries[0].author, "Visible Name")

    def test_records_only_matches_with_source_and_deduplicates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            log_path = Path(directory) / "matches.jsonl"
            fetcher = lambda _url: RSS

            first = scan_once(
                ["https://example.test/feed.xml"],
                ["decentralized community network"],
                log_path,
                fetcher=fetcher,
                announce=lambda _message: None,
            )
            second = scan_once(
                ["https://example.test/feed.xml"],
                ["decentralized community network"],
                log_path,
                fetcher=fetcher,
                announce=lambda _message: None,
            )

            self.assertEqual(first.recorded, 1)
            self.assertEqual(first.ignored, 1)
            self.assertEqual(second.recorded, 0)
            self.assertEqual(second.duplicates, 1)
            self.assertEqual(second.ignored, 1)

            records = [
                json.loads(line)
                for line in log_path.read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(len(records), 1)
            self.assertEqual(
                records[0]["source"]["entry_url"], "https://example.test/posts/1"
            )
            self.assertNotIn("public_author", records[0]["source"])
            self.assertNotIn("summary", records[0]["entry"])

    def test_content_retention_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            log_path = Path(directory) / "matches.jsonl"
            scan_once(
                ["https://example.test/feed.xml"],
                ["decentralized community network"],
                log_path,
                store_content=True,
                fetcher=lambda _url: RSS,
                announce=lambda _message: None,
            )
            record = json.loads(log_path.read_text(encoding="utf-8"))
            self.assertEqual(record["source"]["public_author"], "Public Author")
            self.assertIn("decentralized local network", record["entry"]["summary"])

    def test_prunes_expired_records(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            log_path = Path(directory) / "matches.jsonl"
            old = {
                "observed_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "fingerprint": "old",
            }
            recent = {
                "observed_at": datetime.now(timezone.utc).isoformat(),
                "fingerprint": "recent",
            }
            log_path.write_text(
                json.dumps(old) + "\n" + json.dumps(recent) + "\n",
                encoding="utf-8",
            )

            self.assertEqual(prune_expired_records(log_path, 7), 1)
            remaining = json.loads(log_path.read_text(encoding="utf-8"))
            self.assertEqual(remaining["fingerprint"], "recent")

    def test_exclusion_phrase_overrides_a_match(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = scan_once(
                ["https://example.test/feed.xml"],
                ["decentralized community network"],
                Path(directory) / "matches.jsonl",
                exclusions=["local network"],
                fetcher=lambda _url: RSS,
                announce=lambda _message: None,
            )
            self.assertEqual(result.recorded, 0)
            self.assertEqual(result.ignored, 2)


if __name__ == "__main__":
    unittest.main()
