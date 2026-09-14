# Embeddings From First Principles — Notebook Companions

Runnable notebook companions for **Embeddings From First Principles** (chapters 01–26).

The **book is the authority for chapter meaning.** Each notebook isolates one falsifiable
question from its chapter and answers it — the same "concept → demonstration" move the
chapters use, rebuilt as code.

## Approach for this book

Unlike the debugging book, this one *has* a measurement substrate:
`experiments/embeddings-from-first-principles/` ships the frozen **RELATE** corpus and the
committed **Wave 1–6 artifacts** (`wave{N}/artifacts/*.json`) that every `MEASURED on
RELATE …` table in the manuscript is drawn from. So the notebooks are **hybrid**:

1. **Mechanism, in NumPy.** The conceptual core of each chapter is a small self-contained
   computation — the identifier→embedding ladder, rotation invariance, the metric algebra,
   PPMI-SVD on a toy corpus, calibration curves, the alignment maps. Built from scratch,
   asserted directly.
2. **Claim, against the artifact.** Where the chapter cites a measured number
   (`Wave N row X.Y`), the notebook loads the committed JSON and asserts the book's claim
   against it — no model download, no `sentence-transformers`, no network. The artifacts
   already contain the computed cosines, effective ranks, preservation profiles, etc.

Every code cell ends in `assert`s plus one `print` line stating what was earned. Where a
chapter's measured result *contradicted* its pre-registered guess (whitening hurting a
contrastive encoder, the null map already winning, no bridge winning every column), the
notebook checks the *measured* outcome, not the hypothesis.

## Contract

- Notebooks live under `/notebooks/embeddings-from-first-principles/`, not under Hugo `content/`.
- Standard library + `numpy` only. No network, no API keys, no model downloads, no live LM.
- Deterministic: fixed seeds; artifact reads are exact. Each notebook runs CPU-only in well
  under 120 s on the `python3` kernel and is committed **stripped** (empty outputs, null
  execution counts).
- The repo checkout must contain `experiments/embeddings-from-first-principles/` (the
  notebooks find the repo root by walking up for that directory).

## Index

| Notebook | Chapter | Question isolated | Status |
|---|---|---|---|
| `01-chapter.ipynb` | What Is an Embedding? | Does a real encoder place a claim and its negation almost on top of each other (Wave 1)? | ✅ |
| `02-chapter.ipynb` | Meaning Becomes Geometry | Can a hand-built 2D space carry "meaning", and what does projecting 12 clusters to 2D fuse? | ✅ |
| `03-chapter.ipynb` | Learning an Embedding Space | Does PPMI + truncated SVD on a toy corpus recover the robust co-occurrence signal (Wave 3 relate)? | ✅ |
| `04-chapter.ipynb` | Similarity Is a Decision | Is cosine just the normalized dot product, and does the metric sweep spread stay < 0.002 (Wave 1)? | ✅ |
| `05-chapter.ipynb` | Dimensions Do Not Mean What You Think | Is retrieval exactly rotation-invariant while every axis statistic is scrambled — and is the cosine "origin" 0.06–0.45 (Wave 1–2)? | ✅ |
| `06-chapter.ipynb` | Neighborhoods and Manifolds | Does hubness reproduce, and does it correlate with anisotropy (Wave 1)? | ✅ |
| `07-chapter.ipynb` | How Many Dimensions Does Meaning Need? | Effective rank vs intrinsic dimension vs the retention knee — do the three disagree (Wave 2)? | ✅ |
| `08-chapter.ipynb` | The Shape of an Embedding Space | Does whitening help or hurt a contrastive encoder's retrieval (Wave 2)? | ✅ |
| `09-chapter.ipynb` | From Similarity to Search | The four-line retrieve primitive + toy IVF: how much does ANN lose vs exact (Wave 1)? | ✅ |
| `10-chapter.ipynb` | The Nearest Neighbor Can Be Wrong | Is a negation passage the nearest neighbour of the thing it negates (Wave 1 distractors)? | ✅ |
| `11-chapter.ipynb` | Hard Negatives | Does the hard-negative margin collapse under a realistic distractor set (Wave 1)? | ✅ |
| `12-chapter.ipynb` | Retrieval Is a Policy | Does the retrieval policy (chunking, rerank, cutoff) move end metrics more than the encoder (Wave 1)? | ✅ |
| `13-chapter.ipynb` | How Do You Evaluate an Embedding? | Does changing the relevance definition change which model wins (Wave 1 v0.1 vs v0.2)? | ✅ |
| `14-chapter.ipynb` | Calibration | Overlapping same/different distributions: how wide is the escalate band, and does the threshold drift (Wave 1)? | ✅ |
| `15-chapter.ipynb` | Is Similarity One-Dimensional? | Does a diagnostic signal vector beat a scalar cosine on hard negatives (Wave 1 signal ablation)? | ✅ |
| `16-chapter.ipynb` | Change the Model, Change the Universe | Two random encoders → orthogonal vectors for the same text; does CKA / NN-overlap still see shared structure (Wave 3)? | ✅ |
| `17-chapter.ipynb` | Versioning the Space | What identifies a space, and what does a naively mixed v1/v2 index cost (Wave 3)? | ✅ |
| `18-chapter.ipynb` | Can One Embedding Space Be Translated Into Another? | Does a linear bridge keep coarse structure (neighbourhoods, relation order) but lose the hard-negative margin on unseen entities (Wave 3)? | ✅ |
| `19-chapter.ipynb` | Alignment | Does a nonlinear MLP beat closed-form Procrustes/ridge on preservation — or lose while costing more (Wave 3 bake-off)? | ✅ |
| `20-chapter.ipynb` | The Embedding Bridge | Does `usable_for` come out `[retrieval, clustering]` and `not_usable_for` `[threshold_transfer, relation_tasks]` from the measured profile (Wave 3)? | ✅ |
| `21-chapter.ipynb` | Did the Bridge Preserve the Space? | Can a fitted bridge *invert* the paraphrase-vs-negation gap, and can a supervised bridge exceed the source-native score (Wave 3)? | ✅ |
| `22-chapter.ipynb` | Can a Smaller Representation Preserve a Larger One? | Can a bridge recover the paired target (R@10 1.000) while agreement@10 sits at 0.80 (Wave 6)? | ✅ |
| `23-chapter.ipynb` | What Should a Translation Preserve? | Does forcing source geometry help or hurt target behavior under a VSP sweep (Wave 6)? | ✅ |
| `24-chapter.ipynb` | Documents Are Not Sentences | Do 10–50% compressions preserve source top-1 while neighbourhood overlap falls, and does layer-1 drift detect 0% of controlled corruptions (Wave 4)? | ✅ |
| `25-chapter.ipynb` | From Deltas to Operators | On typed sentence edits, does anything above a constant offset ever win — or are the expressive rungs strictly worse (Wave 5)? | ✅ |
| `26-chapter.ipynb` | Building an Embedding Runtime | The Observatory composed over Waves 1–6: near-but-wrong caught by the *system*, not the geometry. | ✅ |

## Lab map — the laboratory behind the chapters

Every chapter lab is a three-layer artifact: the book demonstrates the measured result,
the notebook replays it from the frozen artifact, and the reader varies it. Statuses:
**MEASURED** (we ran it, the chapter reports it), **REPRODUCIBLE** (rerun command
reproduces it), **TRY IT** (reader knobs), **PARTLY** (lower bound / hypothesis labelled
as such in the chapter).

| Lab | Artifact | Reproduce | Status | Try-it knobs |
|---|---|---|---|---|
| 1 | `wave1/artifacts/relation-cosine-by-type.json` | `run_wave1.py 1.1` | MEASURED | model, sentence sets |
| 2 | `wave1/artifacts/lab02-break-one.json` + `pca-projection.json` | `lab02_break_one.py` | MEASURED | `WORDS`, `MODEL`, `SEED`, perplexity |
| 3 | `wave1/artifacts/ppmi-svd-relate.json` | `run_wave1.py 1.2` | MEASURED | SVD `k ∈ {10, 50, 200}`, seeds |
| 4 | `wave1/artifacts/metric-sweep.json` | `run_wave1.py 1.3` | MEASURED | un-normalized representation |
| 5 | `wave2/artifacts/rotation-invariance.json` + `wave1/artifacts/anisotropy.json` | `run_wave2.py 2.1` | MEASURED | rotation seeds, axis picks |
| 6 | `wave1/artifacts/hubness.json` | `run_wave1.py 1.5` | MEASURED | k, index size |
| 7 | `wave2/artifacts/retention-curves.json` + `dimensionality-report.json` | `run_wave2.py 2.2 2.3 2.4 2.5` | MEASURED | truncation set, second model/domain |
| 8 | `wave2/artifacts/shape-comparison.json` + `whitening-gain.json` | `run_wave2.py 2.8 2.9` | MEASURED | third model, whitening stages |
| 9 | `wave1/artifacts/ann-vs-exact.json` | `run_wave1.py 1.6` | MEASURED | `ef_search`, PQ, latency budget |
| 10 | `wave1/artifacts/distractor-winrate.json` | `run_wave1.py 1.7` | MEASURED | distractor types, reranker |
| 11 | `wave1/artifacts/margin-collapse.json` | `run_wave1.py 1.8` | MEASURED | negative-set construction |
| 12 | `wave1/artifacts/policy-ablation.json` | `run_wave1.py 1.13` | MEASURED | stages, chunk sizes, budget |
| 13 | `wave1/artifacts/relevance-definition-sweep.json` + `v02/` | `RELATE_RELEASE=relate-0.2.0 python run_wave1.py 1.9` | MEASURED | private queries, definitions |
| 14 | `wave1/artifacts/calibration.json` + `threshold-drift.json` | `run_wave1.py 1.10 1.11` | MEASURED | FAR/FRR targets, second corpus |
| 15 | `wave1/artifacts/signal-ablation.json` | `run_wave1.py 1.12` | MEASURED | signal subsets, verifier |
| 16 | `wave3/artifacts/space-comparison.json` | `run_wave3.py 3.1` | MEASURED | model pairs, hard regions |
| 17 | `wave3/artifacts/mixed-index-penalty-curve.json` | `run_wave3.py 3.2` | PARTLY (lower bound) | divergent v1→v2 pair |
| 18 | `wave3/artifacts/ladder-8property-matrix.json` | `run_wave3.py 3.4` | MEASURED | anchor counts, λ |
| 19 | `wave3/artifacts/null-map-baseline.json` + `nonlinear-vs-linear-unpaired.json` | `run_wave3.py 3.3 3.5` | MEASURED | map set, anchor coverage |
| 20 | `wave3/artifacts/ladder-8property-matrix.json` + `roundtrip.json` | `run_wave3.py 3.4 3.6 3.9` | MEASURED | per-task bars, direction |
| 21 | `wave3/artifacts/relation-preservation.json` + `supervised-bridge-ceiling.json` | `run_wave3.py 3.4 3.6 3.7 3.9` | MEASURED | consumer metric, supervision |
| 22 | `wave6/artifacts/cross-space-benchmark.json` | `run_wave6.py` | MEASURED | direction, anchor count |
| 23 | `wave6/artifacts/vsp-sweep.json` | `vsp_sweep.py` | MEASURED | VSP weight, rank loss |
| 24 | `wave4/artifacts/retention-curve.json` + `blindspot-matrix.json` | `run_wave4.py` | MEASURED | ratios, corruptions |
| 25 | `wave5/artifacts/operator-bakeoff.json` | `run_wave5.py` | MEASURED | 10th transformation |
| 26 | all of the above (composition) | `run_wave1.py && run_wave3.py && run_wave4.py` | MEASURED | corpus, models, invariant |

## Skip log

*(none yet)*
