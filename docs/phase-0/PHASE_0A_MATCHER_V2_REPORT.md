# Phase 0A Matcher v2 report

**Evidence date:** 2026-08-18

**Corpus:** `relationship-gossip-synthetic-v2`

**Matcher:** `relationship-gossip-context-v2`

**Result:** **METRICS PASSED; OWNER LABEL APPROVAL OUTSTANDING**

## Decision

Matcher v2 passes the accepted held-out thresholds on both source structures:

| Held-out scope | Candidates evaluated | TP | FP | TN | FN | Precision | Recall | Metric result |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Nostr | 84 | 35 | 5 | 44 | 0 | 87.50% | 100.00% | Pass |
| Jetstream | 84 | 35 | 5 | 44 | 0 | 87.50% | 100.00% | Pass |
| Overall | 168 | 70 | 10 | 88 | 0 | 87.50% | 100.00% | Pass |

The required floors are 85% precision and 60% recall. The development split
scored 100% precision and 100% recall; those figures are diagnostic only and
do not decide the gate.

The overall Matcher v2 gate is not yet closed. The project owner must approve
or correct the provisional synthetic labels. Until then, the relationship and
gossip watch remains preview-only and cannot automatically persist or notify.

## Method and freeze order

The v1 held-out set was not used to tune Matcher v2. Work followed this order:

1. inspect only the v1 development split;
2. replace one-term matching with contextual phrase rules and conservative
   mechanical-junk suppression;
3. verify the development split and focused matcher tests;
4. freeze `phase0a_compare.py` at SHA-256
   `8c16b632ecf04e52dcdaa9ba124526c8d0f22bdd46c60ef1554d517f790f4757`;
5. author and freeze the fresh v2 held-out examples; and
6. evaluate the held-out set once and preserve the result without changing the
   matcher.

The corpus has 286 protocol records representing 143 concepts: 110 records
from the already-seen v1 development split and 176 newly authored held-out
records. Every concept is rendered once through the Nostr classifier and once
through the Jetstream classifier. There are 118 clear relevant records and 12
ambiguous records. Ambiguous labels remain visible but are excluded from
precision and recall.

All text is project-created synthetic fixture prose under CC0-1.0. No live
message body, identifier, public key, account, or private message was used.

## Preserved misses

There were no held-out false negatives. Five new non-personal word senses were
false positives in each source structure:

- a wedding venue price list;
- a divorce statute;
- dating-app company earnings;
- a current-affairs bulletin; and
- a marriage-licence office notice.

These misses are intentionally retained. Fixing them now would be tuning on the
held-out set and would require Matcher v3 plus another new held-out set. The
observed 87.50% precision already clears the agreed gate.

## Owner label review

The [owner review sheet](../../tools/phase0a/corpus_v2/owner_label_review.csv)
contains one row for each of the 143 unique concepts, with the proposed label,
event class, text, and rationale. Its frozen SHA-256 is
`817ff79aff151a55685e70ef4f65b66ddd9802837810d91c401503aaf6b29719`.

The owner may either list corrections by `concept_id`, or approve the sheet
unchanged with this exact statement:

> I approve the labels in `tools/phase0a/corpus_v2/owner_label_review.csv` at
> SHA-256 `817ff79aff151a55685e70ef4f65b66ddd9802837810d91c401503aaf6b29719`.

Approval changes label governance only. It does not enable sources, authorize
routine listening, waive the local-only privacy boundary, or close Phase 0B.

## Frozen evidence

| Input | SHA-256 |
|---|---|
| `corpus.jsonl` | `bd6ef5b997e136699aed7a57f670248c37780577737241cb0d1b6d4a12f2ec8b` |
| `owner_label_review.csv` | `817ff79aff151a55685e70ef4f65b66ddd9802837810d91c401503aaf6b29719` |
| `generate_corpus.py` | `2817e34b76dce35270a01d3a65e9f3d7a278fd94ff03646e7d15a8a1deda9d79` |
| `evaluate_corpus.py` | `01b8f3d6c03e38c314d8b85c5cc3bc8579471c71252d0167b5bdd8487f1bcce3` |
| `phase0a_compare.py` | `8c16b632ecf04e52dcdaa9ba124526c8d0f22bdd46c60ef1554d517f790f4757` |
| v1 source `corpus.jsonl` | `8df6624c5d29e4b7459ff968d4ce97120f561270448af302293479b814ce9019` |

The [manifest](../../tools/phase0a/corpus_v2/manifest.json) verifies those
inputs before evaluation. The machine-readable
[evaluation evidence](../../tools/phase0a/corpus_v2/evidence/evaluation.json)
contains aggregate results and synthetic fixture IDs only.

## Reproduction

From the repository root:

```powershell
tools\phase0a\.venv\Scripts\python.exe tools\phase0a\corpus_v2\generate_corpus.py
tools\phase0a\.venv\Scripts\python.exe -m unittest -v tools\phase0a\corpus_v2\test_matcher_corpus_v2.py
tools\phase0a\.venv\Scripts\python.exe tools\phase0a\corpus_v2\evaluate_corpus.py
```

The evaluator exits with status 1 while owner approval is outstanding even
though the metric gate passes. That is the declared product gate, not a crash.

## Remaining Phase 0 blockers

- Phase 0A: explicit owner approval or correction of the frozen label sheet.
- Phase 0B: physical Android lifecycle, notification STOP, encrypted-store,
  resource, and packaging evidence.

All reviewed sources remain `approved-disabled`; nothing in this report
deploys a listener or enables routine collection.
