import json
import tempfile
import unittest
from pathlib import Path

from manage_records import rewrite_records, source_value


class RecordManagementTests(unittest.TestCase):
    def test_deletes_only_exact_requested_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            log_path = Path(directory) / "matches.jsonl"
            records = [
                {"source": {"entry_url": "https://example.test/one"}},
                {"source": {"entry_url": "https://example.test/two"}},
            ]
            log_path.write_text(
                "".join(json.dumps(record) + "\n" for record in records),
                encoding="utf-8",
            )

            removed = rewrite_records(
                log_path,
                lambda record: source_value(record, "entry_url")
                != "https://example.test/one",
            )

            self.assertEqual(removed, 1)
            remaining = json.loads(log_path.read_text(encoding="utf-8"))
            self.assertEqual(remaining["source"]["entry_url"], "https://example.test/two")


if __name__ == "__main__":
    unittest.main()
