# Matcher v2 frozen corpus

This package evaluates `relationship-gossip-context-v2` without using or
retaining live message content.

- Development is the already-seen v1 development split. Only that split was
  used while designing Matcher v2.
- The fresh v2 held-out examples were written after the production matcher was
  frozen at SHA-256
  `8c16b632ecf04e52dcdaa9ba124526c8d0f22bdd46c60ef1554d517f790f4757`.
- Every concept is rendered once as Nostr and once as Jetstream so the two
  protocol classifiers receive the same semantic material.
- Ambiguous examples remain visible but do not count toward precision or
  recall.
- Labels remain provisional until the project owner reviews
  `owner_label_review.csv` and explicitly accepts or corrects them.

The evaluator must be run only after generation and the Matcher v2 freeze. Its
first held-out result is evidence and must not be tuned away. Any matcher or
label change requires a new version and another genuinely new held-out set.

From the repository root:

```powershell
tools\phase0a\.venv\Scripts\python.exe tools\phase0a\corpus_v2\generate_corpus.py
tools\phase0a\.venv\Scripts\python.exe -m unittest -v tools\phase0a\corpus_v2\test_matcher_corpus_v2.py
tools\phase0a\.venv\Scripts\python.exe tools\phase0a\corpus_v2\evaluate_corpus.py
```

The evaluator exits `1` while owner approval is outstanding even when metric
thresholds pass. That exit is a product gate, not a tool failure.
