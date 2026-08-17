# Phase 0A synthetic matcher corpus

This directory contains the reproducible, offline evaluation package for the
first relationship/gossip watch. Every message is newly written synthetic
fixture prose released as CC0-1.0. No live Nostr, Jetstream, social-network, or
private-message content was copied into the corpus.

The generator fixes the split before evaluation: within every semantic or
structural category, odd one-based concept indices are development examples
and even indices are held out. Each concept is rendered once as a Nostr fixture
and once as a Jetstream fixture. The held-out set was not used to alter terms,
tokenisation, thresholds, or labels.

The evaluator imports the production-spike `RELATIONSHIP_TERMS`, `TOKEN_RE`,
and protocol classifiers from `../phase0a_compare.py`. It applies protocol
validation, the 16,384-byte decoded-body limit, standalone classification, and
protocol-identity deduplication before the existing exact-token lexical match.
Ambiguous labels remain visible but are excluded from precision and recall.

Rebuild and verify from the repository root with the bundled or any compatible
Python 3.12 runtime:

```powershell
python tools/phase0a/corpus/generate_corpus.py
python -m unittest -v tools/phase0a/corpus/test_matcher_corpus.py
python tools/phase0a/corpus/evaluate_corpus.py
```

The evaluator intentionally exits `1` while the gate fails; this is a measured
product result, not a tool crash. `evidence/evaluation.json` contains synthetic
fixture IDs and aggregate metrics only. Explicit project-owner approval of the
provisional labels is still required even if a future matcher passes the metric
thresholds.
