# Phase 0A relationship/gossip matcher report

**Evidence date:** 2026-08-17

**Corpus:** `relationship-gossip-synthetic-v1`

**Matcher:** `phase0a-relationship-terms-v1`
**Result:** **FAIL — do not enable durable topic matches**

## Decision

The existing exact-token lexical matcher passes the held-out recall floor but
fails the precision gate by a large margin:

| Held-out scope | Candidates evaluated | TP | FP | TN | FN | Precision | Recall | Result |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Nostr | 53 | 16 | 12 | 17 | 8 | 57.14% | 66.67% | Fail precision |
| Jetstream | 53 | 16 | 12 | 17 | 8 | 57.14% | 66.67% | Fail precision |
| Overall | 106 | 32 | 24 | 34 | 16 | 57.14% | 66.67% | Fail precision |

The accepted thresholds are precision at least 85% and recall at least 60%.
Recall passes; precision does not. There were 22.642 false positives per 100
evaluated held-out candidates.

Label approval is a second independent failure: clear labels were assigned as
provisional product-team labels, but the project owner has not explicitly
approved them. Approval remains outstanding. Owner approval alone would not
make this result pass because precision is still below threshold.

## Corpus and split

The frozen corpus contains 220 protocol candidates representing 110 concepts:

- 110 Nostr fixtures and 110 Jetstream fixtures;
- 110 development and 110 held-out records;
- 96 clear relevant records, 116 clear non-relevant records, and 8 ambiguous
  records;
- positive lexical examples and positive paraphrases without current terms;
- ordinary negatives, word-sense near misses, replies, recipient-tagged events,
  quotes, reposts, direct/group structures, mechanical spam, and repeated
  protocol identities;
- ASCII and multibyte Unicode bodies at 16,383, 16,384, and 16,385 UTF-8 bytes.

Every concept is rendered once through each source structure. The equal
per-source scores therefore demonstrate consistent adapter/classifier
behaviour; they are not independent estimates of real-world Nostr or Bluesky
prevalence.

The split was declared in the generator before evaluation: within every
category, odd one-based concept indices are development and even indices are
held out. The matcher terms, tokenisation, threshold, and labels were not
changed after observing held-out results. Ambiguous records are reported but
excluded from precision and recall.

All corpus prose is newly created synthetic fixture material released as
CC0-1.0. No live Nostr or Jetstream body, identifier, account, key, or private
message was read, copied, or persisted for this corpus.

## Evaluated behaviour

The evaluator imports the existing `RELATIONSHIP_TERMS`, `TOKEN_RE`, and source
classifiers from `phase0a_compare.py`. Its order is:

1. validate the protocol fixture, Nostr event ID and Schnorr signature;
2. enforce the 16,384-byte decoded-body limit;
3. reject addressed/conversational structures;
4. suppress a repeated protocol identity;
5. case-fold and tokenize with `TOKEN_RE`;
6. predict relevant if any exact `RELATIONSHIP_TERMS` token is present.

The main false-positive class is polysemy: terms such as `relationship`,
`dating`, `drama`, `marriage`, `crush`, `cheating`, `affair`, `gossip`, and
`rumor` also occur in scientific, technical, artistic, sporting, or figurative
contexts. Mechanically obvious keyword spam also matches because the current
lexical matcher has no integrated spam rejection decision.

The false negatives are clear interpersonal statements expressed with words
outside the fixed term set, including `partner`, `fiancé`, `dumped`, `exes`,
`separated`, `couple`, `romance`, and indirect descriptions of secrecy or
reconciliation.

The held-out set has now been evaluated and its error classes are disclosed.
It must not be used to tune a successor matcher. Any changed matcher or changed
label requires a new version and a fresh, unseen held-out set.

## Frozen evidence

| Input | SHA-256 |
|---|---|
| `corpus.jsonl` | `8df6624c5d29e4b7459ff968d4ce97120f561270448af302293479b814ce9019` |
| `generate_corpus.py` | `509359275f517acb0fa20cf485cd705a1b521b8dc9d5bf1b5235baaafc6bf1db` |
| `evaluate_corpus.py` | `fe978cd66a4cdbeb209976a23a84200160533ac3c50a1047bd409114ac7564a5` |
| `phase0a_compare.py` | `51fe3d3805d53049dd47c50b92f77097708e38318d682a350dd1ddb1f06f0c31` |

The [manifest](../../tools/phase0a/corpus/manifest.json) verifies all four
inputs before evaluation. The machine-readable [evaluation evidence](../../tools/phase0a/corpus/evidence/evaluation.json)
contains aggregate results and synthetic fixture IDs only.

The Jetstream synthetic path now includes the observed v2 XRPC outer
`message`/`payload` envelope before the unchanged commit and post classifier.
Metrics remain unchanged after regenerating and re-evaluating all 220 records.

## Reproduction

From the repository root on the qualified Windows Python environment:

```powershell
tools\phase0a\.venv\Scripts\python.exe tools\phase0a\corpus\generate_corpus.py
tools\phase0a\.venv\Scripts\python.exe -m unittest -v tools\phase0a\corpus\test_matcher_corpus.py
tools\phase0a\.venv\Scripts\python.exe tools\phase0a\corpus\evaluate_corpus.py
```

The focused suite passes 8 of 8 tests. The final evaluator intentionally exits
with status 1 because the gate result is `FAIL`; its evidence file is still a
successful, complete measurement.

## Required next evidence

Before this bundled topic can create persistent signals:

1. the owner reviews and explicitly accepts or corrects the provisional labels;
2. matcher improvements are developed only against development material;
3. a new corpus version supplies a fresh unseen held-out set;
4. both per-source and overall held-out precision reach 85% and recall reaches
   60%; and
5. a later authorised live sample is used only as a separate usefulness check,
   not copied into this synthetic corpus.
