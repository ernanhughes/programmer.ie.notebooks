# Notebook Migration Matrix

Claim → evidence migration map from the **current** manuscript (`content/books/digital-life/`, 18 chapters) to historical source material (`content/books/original/`, `notebooks_original/`, `research/digital-life/`, `scripts/books/digital-life/`), and forward to the new canonical notebook suite under `notebooks/`.

**Authority direction:** current book → current claim → required evidence → historical source → reconstructed experiment → new notebook. This document does not rename old notebooks; it traces each current-book claim back to whatever historical artifact actually tested it, then decides how (or whether) that artifact becomes a new notebook.

Built from three read-only reconnaissance passes (full text of all 18 current chapters; full text of all 31 original chapters + all 31 legacy notebooks; summary-level read of ~90 files across the 800-file `research/digital-life/` archive), cross-validated against each other by matching quoted numbers (e.g. current Ch.9's `p≈0.00025` / `0.00440` interaction values are the exact same numbers as `research/digital-life/ch19-*` v1's reported statistics — confirms the mapping is not guesswork).

Status vocabulary below follows the **current book's own** taxonomy (Ch.17), not a simplified 5-label scheme: SUPPORTED, UNRESOLVED, BOUNDED NEAR ZERO, BOUNDED BELOW SEI, INVALID (run defect, not a finding), ASSERTION/IDENTITY (correctness facts), DESCRIPTIVE ONLY, NOT CLAIMED / NOT ESTABLISHED (scope markers). "Disposition" is one of: REUSE, ADAPT, COMBINE, SPLIT, REIMPLEMENT, RERUN, HISTORICAL ONLY, OBSOLETE, NO NOTEBOOK REQUIRED.

---

## Headline cross-cutting findings (read this before the per-chapter tables)

1. **Substantial narrative compression at the front of the book.** Original chapters 00, 02, 03, 05, 06, 07, 08, 09, 10 — the elementary-cellular-automaton thread (Rule 22 / Rule 30, spacetime diagrams, Hamming-distance divergence), the Game-of-Life glider damage/IoU-regeneration study, the toy tri-control population-genetics "evolution" model, and the fork/merge/checkpoint DAG bookkeeping toy — **do not appear anywhere in the current 18-chapter book**. Current Ch.1–2 are now pure methodological/conceptual framing with zero experiments (confirmed by close reading, not inference from titles). These original chapters' notebooks are **HISTORICAL ONLY**: valuable as provenance for *how the method was developed*, but no current claim depends on them, so no new notebook reproduces them.
2. **Two "new" chapters have real experimental backing that the original 31-chapter book never had a chapter for.** Current Ch.3's Physarum-model experiments (sensing ablation 0.883→0.153, field-erasure, turnover) have checked-in figures (`static/images/books/digital-life/ch02-physarum-*.png`) but **no discoverable generating script** anywhere in `scripts/books/digital-life/` — a genuine gap, disposition REIMPLEMENT. Current Ch.5's swarm decoy experiment, by contrast, has a *complete* source: the previously chapter-unassigned `research/digital-life/adversarial-swarm*/` archive and `scripts/books/digital-life/adversarial_swarm_*.py` — confirmed by exact parameter match (256 particles, 8 seeds, four branches, dose-response sweep with a break only at 50% rewiring).
3. **The legacy notebook `notebooks_original/03-now-there-are-two.ipynb`** — filed oddly under "Chapter 03" in the old numbering and flagged by the old README as a "bonus" notebook — is in fact the direct ancestor of **current Chapter 4, "Now There Are Two"** (same title, same c2/causal-graph content, same expected counts: 138,891 clusters, 144 c2 occurrences). This resolves what looked like a stray artifact.
4. **The Digital Crystal chapters (current Ch.7–16) map cleanly to original Ch.11 and Ch.14–30**, and this is where `research/digital-life/` is richest (staged, versioned experiments with machine-checkable verdicts). Several current chapters combine 2–3 original chapters' worth of experiments (e.g. current Ch.8 = original Ch.15 + Ch.16 + the terminal `ch17-perturbation-dynamics-v6` thread; current Ch.9 = original Ch.18 (v1–v10) + Ch.19). This is exactly the "several old notebooks combine into one new chapter" pattern the reconstruction is supposed to find, not a 1:1 rename.
5. **The version chains in `research/digital-life/` are not simple "latest wins" chains.** Many early/mid versions remain independently canonical for narrower sub-claims even after later versions run (e.g. Ch.28/ch16's v1 raw-modularity result is explicitly *preserved*, not overturned, by v2's matched-null result — v2 narrows, it doesn't erase). The per-chapter tables below record the terminal version used for the chapter's headline claim *and* which earlier versions still carry independent weight.
6. Chapters 17 and 18 of the current book (methodology synthesis) reference an external **machine-readable "failure ledger"** — this is `research/digital-life/ch29-how-to-fail-correctly-v1/stage-05-verdict.md`, confirmed to exist and containing exactly the 10-case/5-cross-check audit the chapter narrates. This is a strong, load-bearing artifact for the Ch.17 notebook.
7. Two literal unfilled template placeholders exist in the current book text itself (Ch.4's "[N]"/"[M]" in a causal-return-graph passage; Ch.9's "[INSERT EXACT DIRECTIONAL-DIAGNOSTIC NAME AND A/B VALUES...]", appearing twice) — these are manuscript gaps, not evidence gaps; flagged for the audit phase, not fixed here.

---

## Current Chapter 01 — How to Read This Book

**Purpose:** Methodological charter (evidence trail, no cross-experiment score aggregation, "the experimental record wins over prose"). No experiments.

**Claims requiring executable evidence:** None.

**Historical sources:** Original Ch.00 (partial — general method loop) — conceptual only.

**Disposition:** NO NOTEBOOK REQUIRED.

---

## Current Chapter 02 — What Is Digital Life? (What Would Digital Life Mean?)

**Purpose:** "Names are not evidence" / biology-as-evidence-not-specification framing. No experiments.

**Historical sources:** Original Ch.00 (conceptual charter).

**Disposition:** NO NOTEBOOK REQUIRED.

---

## Current Chapter 03 — Look at This Thing

**Scientific purpose:** Does recognizable organization persist without persistent material? Three systems: Lenia (persistent pattern via local reconstruction, not travel), Conway glider (exact recurrence without material continuity), Physarum-style particle/field model (stigmergy — agents alter the conditions of their own future behavior; survives sustained turnover).

| Claim ID | Claim (paraphrase) | Status |
|---|---|---|
| DL-03-C01 | Lenia produces a persistent localized pattern with no explicit "creature" object | DESCRIPTIVE / SUPPORTED |
| DL-03-C02 | Glider persists without persistent material identity (exact recurrence, displaced) | SUPPORTED |
| DL-03-C03 | Glider fails Hintze&Bohm self-replication criterion (chains, not branches) | BOUNDED NEGATIVE |
| DL-03-C04 | Sensing is causally necessary for Physarum network formation (0.883→0.153 with sensing disabled) | SUPPORTED |
| DL-03-C05 | Neither field alone nor agent population alone is the sole history-carrier (field-erasure / full-replacement ablations) | SUPPORTED |
| DL-03-C06 | Macroscopic network organization persists through >99.9% agent turnover, degraded from baseline | BOUNDED / SUPPORTED (single-run, explicitly flagged as not population-level) |

**Historical sources:**
- Lenia: original Ch.01 ("Look at This Thing"), notebook `notebooks_original/01-look-at-this-thing.ipynb` (own simplified Lenia-like implementation, NOT canonical Lenia code — executes live). Scripts: `ch01_lenia_animation.py`, `ch01_lenia_damage_triptych.py`, `ch01_lenia_fixed_grid.py`.
- Glider persistence: original Ch.04 ("When Does a Pattern Become a Thing?"), notebook `04-when-does-a-pattern-become-a-thing.ipynb` (executes Game of Life live, `np.array_equal` translation-compensated verification). **Only the persistence-without-material-identity sub-result is reused** — Ch.05's damage/IoU/regeneration material is NOT part of current Ch.03 (see "cut" list above).
- Physarum: **no original-book chapter, no notebook, no generating script found.** Only artifacts are 4 checked-in figures (`static/images/books/digital-life/ch02-physarum-{growth,interventions,route-correlation,turnover}.png`) with a "ch02" legacy prefix suggesting a different intermediate manuscript numbering that predates both the original 00-30 set and the current set. Quantitative claims (0.883/0.153, 0.897/0.911, 0.658/0.304 etc.) exist only in the current book's prose — no machine-readable backing found anywhere in `research/` or `scripts/`.

**Disposition:**
- Lenia sub-experiment: ADAPT (reuse original Ch.01 notebook's simplified model, note explicitly that it is not canonical Lenia/Flow-Lenia code — the current book doesn't require Flow-Lenia's mass-conservation extension, so this is fine, but must be disclosed).
- Glider persistence sub-experiment: ADAPT (extract just the persistence-under-translation cell from `04-when-does-a-pattern-become-a-thing.ipynb`; drop the damage/IoU cells, which belong to no current chapter).
- Physarum sub-experiment: **REIMPLEMENT from the book's own quantitative description.** This is a genuine gap — flag in NOTEBOOK_AUDIT.md as "SOURCE MISSING, values quoted in prose only." A new implementation should be written to hit the same qualitative shape (sensing ablation, field erasure, agent replacement, continual turnover) but exact number reproduction cannot be verified against a historical run and must be labeled as a fresh, not a reproduced, result.

**Proposed new notebook(s):**
- `03a-lenia-persistent-pattern.ipynb` — Lenia demo + glider persistence-without-material-identity (DL-03-C01, C02, C03).
- `03b-physarum-stigmergy-turnover.ipynb` — Physarum sensing-ablation / field-erasure / turnover experiment, explicitly labeled as a reconstruction with no historical numeric ground truth (DL-03-C04–C06).

---

## Current Chapter 04 — Now There Are Two

**Scientific purpose:** Does Outlier exhibit genuine causal (not merely visual) self-replication? Own 512×512/1600-generation reconstruction of the published rule, c2-lineage detection, causal-graph construction, causal-return analysis.

| Claim ID | Claim | Status |
|---|---|---|
| DL-04-C01 | Own reconstruction verifies published Outlier rule (512/512 decoded, 220 active, rotational symmetry) | ASSERTION / SUPPORTED |
| DL-04-C02 | 144 c2-equivalent occurrences found in own 512×512/1600-gen run; causal graph 138,891 clusters / 196,466 edges | SUPPORTED (own measurement) |
| DL-04-C03 | 99 causal return edges across the 144 occurrences (branching causal recurrence) | SUPPORTED, but explicitly bounded short of full Hintze–Bohm self-replication (no offspring-independence test) |
| DL-04-C04 | Published-paper numbers (1024×1024/20,000 ticks, 433 copies from c0, etc.) | EXTERNAL CITATION, not reproduced at that scale |

**Historical sources:**
- `notebooks_original/03-now-there-are-two.ipynb` (22 cells) — **direct ancestor**, confirmed by title and by exact matching expected-value assertions (138,891 clusters, 144 c2 occurrences). Implements both the "but-for" single-predecessor-removal causal selector (repo's existing method) and an exhaustive minimal-live-subset selector per Hintze & Bohm (2026), and writes a JSON provenance record.
- `scripts/books/digital-life/ch10_outlier_lineage.py` (the actual Outlier CA implementation — "ch10" prefix is a fossil of an even earlier manuscript numbering), `scripts/books/digital-life/test_outlier_minimal_causal_lineage.py`.
- `research/digital-life/ch03-outlier-minimal-causality.json`, `ch03-outlier-replication-criterion.json` — canonical output. Confirmed: `strict_reproduction_survives_candidate_minimal_graph: true`, but flags a **DIAGNOSTIC MISMATCH** (115/220 live rule codes have multiple minimal causal sets where the paper reports none) — an open discrepancy the current book does not resolve either; the current book's [N]/[M] placeholder gap (see finding #7 above) is likely exactly this unresolved multiplicity.
- Also relevant: original Ch.12 ("The Closest Thing We Have") for the rule-verification/decode-and-implement teaching material, and original Ch.13's counterfactual causal-edge machinery (same mechanism, applied at the smaller-scale demo in `12-the-closest-thing-we-have.ipynb`).

**Disposition:** REUSE (the existing bonus notebook is essentially the right shape already) + ADAPT (retitle/reframe explicitly as current-Ch.4 companion; carry forward the DIAGNOSTIC MISMATCH finding rather than silently dropping it, since it is the likely source of the current book's unfilled [N]/[M] placeholders).

**Proposed new notebook:** `04-outlier-causal-self-replication.ipynb`.

**Gap:** the current book's bracketed "[N]" / "[M]" placeholders (count of multi-first-return / never-return c2 occurrences) should be computable directly from re-running this notebook — this is a case where reconstruction can likely *fill* a manuscript gap rather than merely flag it. Record as a to-do in NOTEBOOK_AUDIT.md.

---

## Current Chapter 05 — So We Built the Wrong Thing on Purpose

**Scientific purpose:** Adversarial calibration — does a deliberately organism-free friend/enemy particle swarm decoy pass tests we'd treat as evidence of digital life? Four-branch damage study + full 0–100% rewiring dose-response sweep with a frozen break criterion.

| Claim ID | Claim | Status |
|---|---|---|
| DL-05-C01 | Identity-label replacement (causally inert) does not change persistence measurement | SUPPORTED (manipulation check) |
| DL-05-C02 | 30% material damage does not reliably exceed ordinary control self-variation | BOUNDED NEAR ZERO |
| DL-05-C03 | 30% organizational (relationship) damage also does not reliably separate from self-variation | BOUNDED NEAR ZERO |
| DL-05-C04 | Full dose-response sweep: no monotonic dose-response; frozen break criterion crosses only at 50% (likely false-positive-shaped, not promoted to a mechanistic claim) | BOUNDED / UNRESOLVED (explicit non-promotion) |
| DL-05-C05 | 100% rewiring still does not reliably exceed self-variation | BOUNDED NEAR ZERO |

**Historical sources:** `research/digital-life/adversarial-swarm/run.json`, `adversarial-swarm-regimes/run.json`, `adversarial-swarm-rewire-dose/{run.json, dose_response_summary.csv, per_seed_dose_response.csv}`; `scripts/books/digital-life/adversarial_swarm_persistence.py`, `adversarial_swarm_regimes.py`, `adversarial_swarm_rewire_dose_response.py`. Confirmed exact parameter match against current-book prose: 256 particles, 10,000 burn-in, 12,000 post-intervention, 8 seeds, four branches (control/material_damage/organizational_damage/material_replacement), 0.949 mean shift at 100% rewiring. No original-book chapter (this experiment postdates the 31-chapter manuscript entirely) and no `notebooks_original` companion.

**Disposition:** REIMPLEMENT-from-script (the scripts and JSON/CSV outputs are complete and directly runnable; there is simply no notebook wrapper yet). This is close to RERUN — the scripts exist and are runnable, so the new notebook should genuinely execute them (or a lightweight faithful port) rather than merely audit precomputed CSVs, since the runtime cost (256 particles, ~22k steps) is modest.

**Proposed new notebook:** `05-adversarial-swarm-decoy.ipynb`.

---

## Current Chapter 06 — It Looked Like Flocking

**Scientific purpose:** Does ancestry-dependent motion coherence survive matched (distance/time/density) comparison, or is it a distance confound?

| Claim ID | Claim | Status |
|---|---|---|
| DL-06-C01 | Short-range motion coherence real (0.7373 raw vs. 0.1933 shuffled), survives radial-expansion subtraction | SUPPORTED |
| DL-06-C02 | Naive same-family-vs-different-family gap (0.645) is an artifact of a buggy background-flow estimator | INVALID → CORRECTED |
| DL-06-C03 | After distance/time/density exact matching, ancestry effect collapses to near-zero/negative (pooled −0.0071, 95% CI [−0.0665,+0.0122]) | BOUNDED NEAR ZERO |
| DL-06-C04 | 0–4 cell regime: inadequate different-family common support | UNRESOLVED (not "no effect") |

**Historical sources:** Original Ch.13 ("Is It Really Reproducing?") — same canonical 512×512/1600-gen run as Ch.4/Ch.12, motion-tracking half of the chapter. Notebook `notebooks_original/13-is-it-really-reproducing.ipynb`; scripts `ch11_outlier_radial_flocking.py`, `ch11_outlier_local_flow.py`, `ch11_outlier_causal_motion.py`, `ch11_outlier_distance_matched.py`, `ch13_outlier_overlap_analysis.py`; canonical DB `research/digital-life/ch13-reports/` + the nested `research/digital-life/digital-life/outlier.sqlite3` (759 MB, contains the `ch13_pair_datasets`/`ch13_pair_records` tables — confirmed the more-current of the two `outlier.sqlite3` copies in the repo). `research/digital-life/ch13-reports/ch13-overlap-analysis.md` gives the exact matched pooled effect (−0.0071) and bootstrap CI matching the current book verbatim.

**Disposition:** ADAPT (the legacy `13-is-it-really-reproducing.ipynb` is explicitly a hybrid "small live demo + audit against `data/digital-life/outlier.sqlite3` if present" notebook; the reproduction half of that chapter belongs to current Ch.4/12, not Ch.6 — SPLIT the old notebook's content: reproduction-test cells → Ch.4 material (already covered above), flocking/motion-tracking cells → this chapter).

**Proposed new notebook:** `06-flocking-vs-ancestry-confound.ipynb`.

---

## Current Chapter 07 — The Digital Crystal

**Scientific purpose:** Deterministic hex-growth prototype (hole-filling ≠ repair) + Digital Crystal v1 (stochastic, environmentally forced) — can final morphology recover source-signal family and/or exact temporal order?

| Claim ID | Claim | Status |
|---|---|---|
| DL-07-C01 | Deterministic prototype hex-ball growth matches N(r)=1+3r(r+1) exactly | ASSERTION / SUPPORTED |
| DL-07-C02 | Prototype hole-filling is not repair (same rule, no detector) | DESCRIPTIVE / SUPPORTED |
| DL-07-C03 | Source-family recoverable from final morphology (RF 52.2%/LogReg 53.9% vs 16.7% chance), not explained by mean-forcing confound, survives amplitude sweep | SUPPORTED |
| DL-07-C04 | Exact temporal order NOT recoverable (matched-value-set confirmatory test: 11.1%/11.1% vs 16.7% chance, below permutation null) | BOUNDED NEGATIVE |

**Historical sources:**
- Deterministic prototype: original Ch.11 ("The Crystal"), notebook `11-the-crystal.ipynb` — includes a genuine `assert np.array_equal(measured, theory)` regression check against the closed-form growth law (the single strongest hard-assertion moment in the early notebook suite). Script `ch11_the_crystal.py`.
- Stochastic v1 + classification: original Ch.14 ("The Digital Crystal"), notebook `14-the-digital-crystal.ipynb` — first notebook to import the full `_shared/digital_crystal.py` API; documented "quick-recomputed + canonical-artifact-audit" hybrid pattern (live small-scale run + `assert` against precomputed JSON). Scripts `ch14_digital_crystal.py`, `ch14_digital_crystal_temporal_matched.py`. Canonical artifacts `research/digital-life/ch14-reports/` (9-stage pipeline, `ch14-digital-crystal.sqlite3`) + `ch14-temporal-matched-reports/` (`ch14-temporal-matched.sqlite3`) for the sharper matched-value-set temporal test.

**Disposition:** COMBINE (two original chapters, two legacy notebooks, into one current chapter) + ADAPT (reuse `_shared/digital_crystal.py` directly rather than the notebook's local geometry reimplementations; reuse the hybrid quick-run + artifact-audit pattern, which is a good template for the whole Digital Crystal arc).

**Proposed new notebook:** `07-digital-crystal-source-and-temporal-recovery.ipynb`.

---

## Current Chapter 08 — The Crystal Gets a Past

**Scientific purpose:** STATE vs. HISTORY vs. causally-active-past; checkpoint/restore sufficiency; event-log replay; pulse signalling between crystals; matched-history (codeword) population-level signature test.

| Claim ID | Claim | Status |
|---|---|---|
| DL-08-C01 | Full checkpoint sufficient for exact continuation (30/30 exact, after fixing a Python-`set`-iteration-order bug) | SUPPORTED (post-fix) |
| DL-08-C02 | Ablations: RNG-state and signal-cursor required for exact continuation; birth-time metadata is not; visible-morphology-only is insufficient | SUPPORTED |
| DL-08-C03 | Event log sufficient to reconstruct exact morphology trajectory (96/96) but not RNG state (no exact continuation) | SUPPORTED, bounded |
| DL-08-C04 | Single received pulse usually alters receiver morphology (95.8%, mean diff 0.163) | SUPPORTED |
| DL-08-C05 | Receiver detects coarse pulse timing but not sender identity or exact chronology (control ladder: 2/4 controls beaten, 2/4 not) | BOUNDED (mixed pass/fail) |
| DL-08-C06 | Sequential-RNG-coupling is a major measurement artifact; fixed via cell-keyed CRN runner | INVALID → CORRECTED (methodological finding) |
| DL-08-C07 | Multi-pulse response compatible with linear superposition after CRN fix | SUPPORTED (post-fix) |
| DL-08-C08 | Matched-history (codewords A=11100001/B=10001101) produces different immediate futures but NOT a stable population-level morphology signature (p=0.7366 primary, p=0.9320 secondary) | BOUNDED NEGATIVE (predeclared) |

**Historical sources:**
- Checkpoint/history: original Ch.15 ("The Crystal Gets a Past"), notebook `15-the-crystal-gets-a-past.ipynb`. Canonical: `research/digital-life/ch15-reports/` (stages 00–07) + `ch15-digital-crystal-history.sqlite3`. Verdict `RECOVERABLE_PAST_SUPPORTED`.
- Pulse signalling: original Ch.16 ("Before There Are Messages"), notebook `16-before-there-are-messages.ipynb`. Canonical: `research/digital-life/ch16-reports/` (stages 00–07) + `ch16-digital-crystal-signalling.sqlite3` (~412 MB, the largest DB in the archive). Verdict `CAUSAL_TRANSMISSION_SUPPORTED` (bounded).
- Matched-history codeword test: this is the **terminal v6 of the `ch17-perturbation-dynamics` chain** (`research/digital-life/ch17-perturbation-dynamics-v6/`), confirmed by exact codeword match (A=11100001, B=10001101) and exact p-value match (0.7366) against the current book. Note: `research/digital-life/ch17-reports/` and `ch17-v2-reports/`/`ch17-v3-reports/` are a **separate, superseded framing** ("what survives the channel" / codebook decoding) that was abandoned in favor of the perturbation-dynamics thread — do not confuse the two ch17 branches. Legacy notebook `17-how-does-the-crystal-respond-to-perturbation.ipynb` covers this thread but under the *old* chapter-17 title; in the current book this material is folded into Ch.8, not given its own chapter.

**Disposition:** COMBINE (three original chapters/threads — Ch.15, Ch.16, and the ch17-perturbation-dynamics v1→v6 chain — into one current chapter) + ADAPT. The v1→v6 supersession chain (naive test → underpowered → CRN-audit → confirmatory) is itself a good worked example of "how to fail correctly" and should be preserved as a documented pipeline within the notebook, not collapsed to just the v6 endpoint, since the current book explicitly narrates the CRN-artifact discovery as a major methodological finding of this chapter.

**Proposed new notebook(s):**
- `08a-checkpoint-state-vs-history.ipynb` (DL-08-C01–C03).
- `08b-pulse-signalling-and-matched-history.ipynb` (DL-08-C04–C08) — include the CRN-artifact discovery/fix as a documented cell, not silently normalized away.

---

## Current Chapter 09 — Can Experience Change the Material?

**Scientific purpose:** Smallest local material change from a pulse that persists AND remains causally accessible; causal aperture concept; placement-vs-quantity confound; symbolic and non-symbolic history-discrimination tests.

| Claim ID | Claim | Status |
|---|---|---|
| DL-09-C01 | MODIFIED material persists trivially but late-erasure ablation shows no downstream effect (buried material) | BOUNDED NEGATIVE |
| DL-09-C02 | Causal chain audit confirms real causal power exists; bottleneck is access, not effect strength | SUPPORTED |
| DL-09-C03 | Uncontrolled surface-placement result confounds placement with quantity | INVALID |
| DL-09-C04 | Matched-quantity placement comparison: INTERIOR < RANDOM < SURFACE for causal lifetime (integrated access/leverage/flips) | SUPPORTED |
| DL-09-C05 | Symbolic history-discrimination: statistically significant (p≈0.00025) but fails predeclared magnitude gate (0.383 SD vs required 0.500 SD) | BOUNDED BELOW SEI (statistically detectable, not scientifically meaningful) |
| DL-09-C06 | Non-symbolic history-discrimination (geometry-only-erasure control added): fails both significance and magnitude gates | BOUNDED NEGATIVE |

**Historical sources:**
- Placement/accessibility/causal-aperture arc: original Ch.18 ("Persistent Material State"), the ten-version `research/digital-life/ch18-persistent-material-state-v1` … `-v10` chain. **Not a simple supersession chain** — v2 establishes the accessibility mechanism, v5/v7 establish the placement-ordering result (v7's exact-budget-matched integrated causal-lifetime test is the chapter's strongest positive, matching DL-09-C04 exactly), v6/v8/v9/v10 are further negative refinements of adjacent hypotheses (temporal alignment, self-reinforcement) that don't overturn v7. Legacy notebook: `18-persistent-material-state.ipynb`.
- History-discrimination arc: original Ch.19 ("Two Pasts"), `research/digital-life/ch19-two-pasts-v1` (symbolic, p=0.00025/0.0044 — exact match to current book) / `-v2` (non-symbolic, adds the geometry-only erasure control, p=0.163/0.00043 — exact match). Legacy notebook `19-two-pasts.ipynb`.

**Disposition:** COMBINE (Ch.18's ten-version chain + Ch.19's two-version chain) + ADAPT. Given the number of versions, the new notebook should implement the substrate mechanism once (extending `_shared/digital_crystal.py` with the MODIFIED-cell state) and run the small number of distinct *experimental designs* (ablation timing, matched-quantity placement, symbolic/non-symbolic discrimination) rather than one cell per historical version — the versions differ mostly in bug-fixes and control tightening, which the new notebook should fold directly into a single corrected design, with the superseded attempts documented in prose/markdown rather than re-executed.

**Proposed new notebook:** `09-material-accessibility-and-history-discrimination.ipynb`.

**Manuscript gap:** current book's twice-repeated "[INSERT EXACT DIRECTIONAL-DIAGNOSTIC NAME AND A/B VALUES FROM THE EXPERIMENTAL REPORT]" placeholder is almost certainly resolvable from `ch19-two-pasts-v1`'s stage reports — flag for filling during the audit pass.

---

## Current Chapter 10 — What Survives Material Loss?

**Scientific purpose:** δ-parametrized material loss; does the crystal reach a finite sustainable size? What actually happens to construction/loss/reoccupation dynamics; interior-vs-surface loss placement.

| Claim ID | Claim | Status |
|---|---|---|
| DL-10-C01 | Finite-sustainable-size hypothesis fails across full δ sweep (0–0.16); no δ meets frozen 4-gate criteria | BOUNDED NEGATIVE |
| DL-10-C02 | Gross construction rises dramatically with δ ("loss manufactures frontier") while net growth falls only gently | SUPPORTED |
| DL-10-C03 | ~93–96% of lost locations reoccupy; reoccupation ≠ repair (no detector, no target morphology) | SUPPORTED |
| DL-10-C04 | Interior loss → 11.1% higher late population than surface loss (cleared predeclared 10% gate) | SUPPORTED |
| DL-10-C05 | But the reoccupation-rate mechanism proposed to explain C04 fails its own gate (0.0198 vs required 0.15) | BOUNDED NEGATIVE (mechanism NOT RESOLVED even though the population effect is real) |

**Historical sources:** Original Ch.20 ("Material Loss"), two-version chain `research/digital-life/ch20-material-loss-v1` (finite-regime sweep + exact-count interior/surface test) / `-v2` (reoccupation-mechanism test) — confirmed v2 is a distinct follow-on question, not a correction of v1. Legacy notebook `20-material-loss.ipynb`.

**Disposition:** ADAPT (straightforward 1:1 chapter correspondence; extend `_shared/digital_crystal.py` with the loss rule).

**Proposed new notebook:** `10-material-loss-and-reoccupation.ipynb`.

---

## Current Chapter 11 — What Does It Cost to Stay?

**Scientific purpose:** Finite per-update evaluation budget B; effect on population/scheduling/allocation; can a genuinely stationary population with turnover be produced?

| Claim ID | Claim | Status |
|---|---|---|
| DL-11-C01 | Late population strongly depends on B in the binding regime, flattens above ~512 | DESCRIPTIVE / SUPPORTED |
| DL-11-C02 | Scheduling policy (support-biased) at fixed B produces dramatically different material futures, even flipping net-growth sign | SUPPORTED, but explicitly confounded with the attachment rule itself (no support-matched control run — disclosed limitation) |
| DL-11-C03 | Two-sided allocation tradeoff hypothesis: one arm passes, one arm fails (61.6% of threshold) | BOUNDED NEGATIVE (partial) |
| DL-11-C04 | Stationary-population-with-turnover hypothesis fails at all 5 tested budgets (closest miss at B=80, by 0.00002 in normalized-slope units) | BOUNDED NEGATIVE (near-miss explicitly not reinterpreted) |
| DL-11-C05 | Apparent "stable gross-turnover fraction" is mostly a mechanical accounting artifact of fixed δ, not emergent regulation | BOUNDED NEGATIVE |
| DL-11-C06 | Full normalized process-vector invariance fails (first-occupation-fraction CV exceeds gate at low B) | BOUNDED NEGATIVE |

**Historical sources:** Original Ch.21 ("What Does It Cost to Stay?"), three-version chain `research/digital-life/ch21-finite-update-budget-v1` (tradeoff) / `-v2` (budget sweep) / `-v3` (normalized turnover-regime stability, explicit stop-rule: "Close Chapter 21 and move to causal-individuation tests" — directly foreshadowing current Ch.12). Legacy notebook `21-what-does-it-cost-to-stay.ipynb`.

**Disposition:** ADAPT (1:1 correspondence, three versions represent three genuinely separate sub-experiments (V1/V2/V3) that the current chapter's own "Experimental Note" structure already names — preserve as three sections of one notebook, matching the book's own V1/V2/V3 framing).

**Proposed new notebook:** `11-finite-evaluation-budget.ipynb`.

---

## Current Chapter 12 — Is There Actually One Thing Here?

**Scientific purpose:** Does the connected crystal have a privileged causal boundary? V1 predictive-coherence screen; V2 causal-boundary-localization test.

| Claim ID | Claim | Status |
|---|---|---|
| DL-12-C01 | V1: excess predictive coherence peaks at R=0.90 (0.2906) but fails family-level permutation null (p≈0.0849) | BOUNDED NEGATIVE |
| DL-12-C02 | V2: causal-boundary-localization does not favor the candidate boundary over an arbitrary interior control (diff ≈−0.0072, one-sided p≈0.9693) | BOUNDED NEGATIVE |
| DL-12-C03 | Same-side causal localization exists generally at both tested radii (a real, non-discriminating locality finding) | SUPPORTED (narrow) |

**Historical sources:** Original Ch.22 ("Is the Crystal a Thing or a Flow?"), two-version chain `research/digital-life/ch22-predictive-coherence-v1` / `ch22-causal-boundary-coherence-v2` — confirmed exact number match (0.291 excess R² at radius 0.9, family-null p=0.0849; V2 excess mean −0.0072, sign-flip p=0.969). Legacy notebook `22-is-the-crystal-a-thing-or-a-flow.ipynb` — noted in phase 2a as a **pure-audit notebook with no live computation**.

**Disposition:** ADAPT, but **upgrade from pure-audit to at least partial live recompute** — the old notebook's audit-only pattern is a weaker template than most of the suite; the new notebook should genuinely run the predictive-coherence regression and the matched-intervention localization test at reduced scale, consistent with the "quick + audit" hybrid used elsewhere (Ch.7/8), rather than only asserting against precomputed JSON.

**Proposed new notebook:** `12-predictive-and-causal-boundary-tests.ipynb`.

---

## Current Chapter 13 — What Does One Attachment Cause?

**Scientific purpose:** FORCE/PREVENT/RETAINED/TRANSIENT decomposition of a single forced attachment's causal consequence; sparse/dense geometry; three generations of local causal-gain predictors (FCP/motif/history).

| Claim ID | Claim | Status |
|---|---|---|
| DL-13-C01 | Propagation-as-distance-lag-ridge is an estimator artifact, not a real phenomenon | INVALID (diagnosed) |
| DL-13-C02 | One-step mechanical match: FORCE/PREVENT immediate effect matches mechanical prediction | ASSERTION / CONSISTENT |
| DL-13-C03 | Positive TRANSIENT cumulative consequence at 30 updates: not established; no continuing cascade | BOUNDED NEGATIVE |
| DL-13-C04 | RETAINED arm produces much larger cumulative consequence than TRANSIENT (0.740 vs 0.042) but no permanent growth-rate offset | SUPPORTED (retained>transient) + BOUNDED NEGATIVE (no permanent offset) |
| DL-13-C05 | Sparse/dense geometry changes immediate frontier-opportunity dramatically but does not predict long-run causal gain | MIXED (immediate SUPPORTED, long-run NOT ESTABLISHED) |
| DL-13-C06 | Three generations of local predictors (FCP, motif, recent-turnover) fail to predict downstream causal gain; final adequately-powered extreme-FCP test is a genuine bounded negative | INCONCLUSIVE (1st,2nd) → BOUNDED NEGATIVE (3rd, adequately powered) |
| DL-13-C07 | Far-field (outside local region) negative construction effect discovered; mechanism NOT isolated here | DESCRIPTIVE, mechanism deferred to Ch.14 |

**Historical sources:** Original Ch.23 ("What Does One Attachment Cause?") — exact title match. Five-version chain `research/digital-life/ch23-active-process-propagation-v1` (propagation ridge, FAILED/diagnosed-artifact) → `interface-source-sink-v2` (partial support) → `causal-attachment-gain-v3` (first positive direct causal result) → `persistent-transient-causal-gain-v4` (transient converges, no persistent offset) → `retained-transient-causal-gain-v5` (**corrects v4** by separating retained/transient arms — terminal). Legacy notebook `23-what-does-one-attachment-cause.ipynb` (noted as a **pure-audit notebook**, like Ch.22's). Local-predictor threads (FCP/motif/history) are original Ch.24 v1–v3 (`frontier-creation-causal-gain-v1`, `local-frontier-motifs-v2`, `local-process-history-v3`), legacy notebook `24-where-is-causal-gain-created.ipynb`.

**Disposition:** COMBINE (original Ch.23's v1–v5 + Ch.24's v1–v3 local-predictor threads — note Ch.24's v4/v5 belong to current Ch.14, not here, see below) + ADAPT, upgrading from pure-audit to live recompute for at least the FORCE/PREVENT/RETAINED/TRANSIENT core mechanism (this is the book's central recurring experimental idiom and deserves a genuinely executable implementation other chapters can import).

**Proposed new notebook:** `13-single-attachment-causal-decomposition.ipynb`. This notebook's FORCE/PREVENT/RETAINED/TRANSIENT machinery and cell-keyed CRN runner should be written as reusable functions (in a new shared module, see Phase 4/6 design) since Ch.14, 15, and 16 all explicitly reuse this idiom.

---

## Current Chapter 14 — Can Finite Computation Couple Distant Events?

**Scientific purpose:** Does competition for the shared finite evaluation budget (Ch.11/13) couple locations outside the local rule's one-step reach? Does it amplify or merely redistribute causal consequence?

| Claim ID | Claim | Status |
|---|---|---|
| DL-14-C01 | Fraction-sweep: far-field expected construction difference is nonzero under subsampling, exactly zero under full evaluation (proven identity) | ASSERTION/IDENTITY (correctness fact) + SUPPORTED (empirical shape) |
| DL-14-C02 | Mechanism isolated to finite candidate selection ("candidate displacement ≠ construction displacement") | SUPPORTED |
| DL-14-C03 | Coarse-grained approximation E_far≈−ΔF×f×p̄_far supported at f≤0.25; parameter-free −2:1 ratio does not survive | SUPPORTED (approximation) / UNRESOLVED (ratio) |
| DL-14-C04 | First amplification design (single-lag calibration) is invalid; dynamic per-lag recalibration corrects it | INVALID → CORRECTED |
| DL-14-C05 | Mean 12-step amplification bounded near zero at declared ±0.15 scale (achieved MDE looser than a tighter ±0.10 would need) | BOUNDED NEAR ZERO |
| DL-14-C06 | Pathway rotates (promotion vs. shared-shift) even though the mean amplification doesn't move | SUPPORTED |
| DL-14-C07 | Expressibility gating matches a combinatorial (not fitted) prediction closely | SUPPORTED |

**Historical sources:** Original Ch.25 ("How Does Finite Computation Create Non-Local Coupling?"), single version `research/digital-life/ch25-finite-budget-redistribution-v1` (9 internal stages) — verdict `LOW_BUDGET_SCALING_SUPPORTED_EXTREME_RATIO_UNRESOLVED`. Legacy notebook `25-how-does-finite-computation-create-non-local-coupling.ipynb`. Amplification test: original Ch.26 ("Does Candidate Subsampling Change Causal Amplification?"), two-version chain `ch26-matched-rate-causal-amplification-v1` (static rate match) + audit → `ch26-dynamically-matched-rate-causal-amplification-v2` (dynamic match, fixes v1's rate-drift issue found by its own audit) + two further audits (analytic, mechanism) that corroborate without overturning v2. Legacy notebook `26-does-candidate-subsampling-change-causal-amplification.ipynb`. The mechanical-accounting closeout (original Ch.24 v5, `causal-accounting-v5`, `FIXED_BUDGET_SELECTOR_ACCOUNTING_SUPPORTED`, explicit "STOP. No V6.") is the conceptual bridge cited by this chapter's far-field mechanism discussion — belongs here, not Ch.13.

**Disposition:** COMBINE (Ch.25 + Ch.26 v1/v2/audits + Ch.24-v5's accounting closeout) + ADAPT, reusing the FORCE/PREVENT/CRN machinery built for Ch.13's notebook. Preserve the v1-invalid→v2-corrected amplification story explicitly (it is the chapter's central methodological narrative, not incidental).

**Proposed new notebook:** `14-finite-budget-nonlocal-coupling.ipynb`.

---

## Current Chapter 15 — Can the Past Redirect the Future?

**Scientific purpose:** Do identical-geometry states with different hidden material state respond differently to the same perturbation? Accessible/remote/erased arms; logistic-saturation mechanism; trajectory-decay closeout.

| Claim ID | Claim | Status |
|---|---|---|
| DL-15-C01 | First (V1) pilot run is INVALID (PREVENT branch could naturally reacquire the target cell — contamination correlated with arm) | INVALID |
| DL-15-C02 | One quantity survives the invalid run (computed pre-contamination): accessible material reduces immediate causal response, via logistic-saturation operating-point mechanism | SUPPORTED (mechanism identified) |
| DL-15-C03 | V2 (corrected): immediate effect replicates (−0.01499, CI excludes 0) | SUPPORTED |
| DL-15-C04 | V2: twelve-step effect direction supported (negative) but predeclared minimum magnitude UNRESOLVED (achieved MDE exceeds required precision) | UNRESOLVED (direction ≠ magnitude, explicit) |
| DL-15-C05 | REMOTE arm not certifiable as a proven zero-effect comparator over the 12-step horizon (though lag-one leakage negligible) | NOT ESTABLISHED |
| DL-15-C06 | Trajectory-decay closeout: ~75% of final effect accrues after the trace falls below half strength — suggestive of state-conditioned routing, not measured mediation | DESCRIPTIVE ONLY |

**Historical sources:** Original Ch.27 ("Can Stored History Redirect the Future?"), chain `research/digital-life/ch27-decaying-material-history-causal-response-v1` (run under an engineering **smoke-test profile** — confirmed via `run-metadata.json` `profile: "smoke"` field — `primary_status: ENGINEERING_SMOKE_ONLY`) → `ch27-v1-construct-validity-audit` (finds the PREVENT-x confound) → `-v2` (corrected, `DOWNSTREAM_MATERIAL_HISTORY_EFFECT_UNRESOLVED`) → `ch27-v2-trajectory-closeout-audit` (descriptive-only, explicitly `CORRECTNESS_ASSERTION_NOT_FINDING`). Legacy notebook `27-can-stored-history-redirect-the-future.ipynb`.

**Disposition:** ADAPT (1:1 chapter correspondence; the V1-invalid→V2-corrected narrative must be preserved explicitly, including the smoke-test-profile detail, since this is one of the clearest teaching examples of RUN VALIDITY vs. INFERENTIAL STATUS in the whole book — Ch.17 cites it by name).

**Proposed new notebook:** `15-hidden-state-causal-sufficiency.ipynb`.

---

## Current Chapter 16 — We Found an Individual. Then We Didn't.

**Scientific purpose:** Causal-modularity statistic M (internal retention − external penetration); does it exceed a geometry-matched spatial null?

| Claim ID | Claim | Status |
|---|---|---|
| DL-16-C01 | V1 raw causal modularity M=0.4402 (CI [0.419,0.461]), well above declared 0.15 threshold | SUPPORTED (as measurement) |
| DL-16-C02 | Radius sweep shows monotonic M-vs-radius, no characteristic scale — warning sign of a locality-only effect | DESCRIPTIVE / cautionary |
| DL-16-C03 | V2: excess modularity over a same-checkpoint geometry-matched null is −0.0123 (CI [−0.0327,+0.0072]), below the +0.10 threshold | BOUNDED BELOW SEI |
| DL-16-C04 | Post-hoc spatial-overlap filtering does not move the estimate toward positive privilege at any filtering level | SUPPORTED (robustness) |
| DL-16-C05 | Central conclusion: CAUSAL CONTAINMENT ≠ CAUSAL INDIVIDUATION | FAILED AS INTERPRETATION (measurement valid, promotion invalid) |

**Historical sources:** Original Ch.28 ("Containment Is Not Individuation"), two-version chain `research/digital-life/ch28-causal-modularity-v1` (raw containment, `CAUSAL_MODULARITY_SUPPORTED`) → `-v2` (adds matched-null control, `EXCESS_CAUSAL_MODULARITY_BOUNDED_BELOW_SEI`, explicitly preserves `V1_status_preserved: RAW_CAUSAL_MODULARITY_SUPPORTED` — v2 narrows, does not erase v1). This exact narrowing is independently cited by name in `ch29`'s cross-check X003. Legacy notebook `28-containment-is-not-individuation.ipynb` (noted as a **pure-audit notebook**).

**Disposition:** ADAPT, upgrading from pure-audit to live recompute (same reasoning as Ch.12/13 — this is a headline chapter and deserves genuine execution, not just JSON assertion). Preserve both v1 and v2 explicitly as two stages of one notebook (raw measurement, then matched-null narrowing), matching the book's own "we found an individual, then we didn't" narrative arc.

**Proposed new notebook:** `16-causal-modularity-vs-matched-null.ipynb`.

---

## Current Chapter 17 — How to Fail Correctly

**Purpose:** Meta-scientific chapter formalizing the epistemic-status taxonomy (ESTIMAND/CONSTRUCT/SEI/MDE80; RUN VALIDITY / INFERENTIAL STATUS / EVIDENCE ROLE / CLAIM TRANSITION axes) and auditing whether Ch.14–16's evidence transitions were bookkept consistently. No new Digital Crystal experiments.

**Claims requiring executable evidence:** One — the "failure ledger" audit itself.

| Claim ID | Claim | Status |
|---|---|---|
| DL-17-C01 | 10 registered evidence-transition cases across Ch.14–16, all resolve to source artifacts; 5 named cross-checks (X001–X005) all pass | SUPPORTED — `FAILURE_LEDGER_CONSISTENT` |

**Historical sources:** Original Ch.29 ("How to Fail Correctly"), single version `research/digital-life/ch29-how-to-fail-correctly-v1/stage-05-verdict.md` — a genuine meta-audit artifact, not a Digital Crystal experiment; confirmed to contain exactly the 10-case/5-cross-check structure the current book narrates, with explicit named references (CH27_V1_PRIMARY/IMMEDIATE, CH28_V1_RAW/V2_EXCESS, CH26_V2_PRIMARY/MECHANISM, etc.) matching this migration matrix's own chapter-16/15/14 supersession determinations almost exactly — this file is strong independent confirmation that the reconstruction above is correct, not merely internally consistent. Legacy notebook `29-how-to-fail-correctly.ipynb`.

**Disposition:** ADAPT — this notebook should load and display the actual failure-ledger verdict file (not narrate it in prose) and, ideally, programmatically re-derive at least one or two of the named cross-checks (e.g. X003, the Ch.28 v1-preserved/v2-narrowed check) directly from the Ch.13–16 notebooks' own outputs, turning the audit into something this notebook suite can genuinely re-verify rather than just cite.

**Proposed new notebook:** `17-failure-ledger-audit.ipynb`.

---

## Current Chapter 18 — What Is Digital Life?

**Purpose:** Synthesis chapter. No new experiments; re-quotes and reframes prior results as substrate-affordance vs. experimental-finding; proposes "organizational self-conditioning" as a future (untested) research target; the chapter's own headline synthesis is deliberately falsified in real time via a database counterexample.

**Claims requiring executable evidence:** None new — reuses Ch.8's "30/30"/"96/96" and Ch.10's ">93% reoccupation" numbers, already covered above.

**Historical sources:** Original Ch.30 ("What Is Digital Life?"), legacy notebook `30-what-is-digital-life.ipynb`, script `ch30_digital_life_synthesis_visual.py`.

**Disposition:** NO NOTEBOOK REQUIRED for new content; OPTIONAL a very light "synthesis figure" notebook that pulls one or two headline numbers from Ch.8/Ch.10's notebooks to illustrate the substrate-affordance vs. finding distinction, purely for narrative/appendix use — not confirmatory.

**Proposed new notebook (optional, low priority):** `18-synthesis-figure.ipynb`.

---

## Chapters/threads with NO current-book claim (HISTORICAL ONLY / OBSOLETE)

These original chapters and their notebooks are preserved as historical record but do not back any claim in the current 18-chapter book, so no new notebook reproduces them:

| Original chapter | Notebook | Why retired |
|---|---|---|
| 00 (what would digital life mean) | `00-what-is-digital-life.ipynb` (Rule 22 ECA) | Current Ch.1–2 are pure meta-framing with zero ECA content |
| 02 (remove almost everything) | `02-remove-almost-everything.ipynb` (Rule 22 vs 30) | ECA thread dropped entirely from current book |
| 03 (the first surprise) | `03-the-first-surprise.ipynb` (Rule 30 divergence) | ECA thread dropped entirely |
| 05 (kill it) | `05-kill-it.ipynb` (glider damage/IoU/survival curve) | Current Ch.3 keeps only glider *persistence*, not the damage study |
| 06 (can it make another one) | `06-can-it-make-another-one.ipynb` (toy pattern detector) | Purely illustrative toy; current book's reproduction claims are carried entirely by Ch.4/Outlier instead |
| 07 (evolution without life) | `07-evolution-without-life.ipynb` (tri-control population-genetics toy) | No current chapter discusses evolution/fitness/selection as a standalone experiment |
| 08 (now prove it) | `08-now-prove-it.ipynb` (evidence-ladder audit re-run) | Superseded in role by current Ch.17's more developed multi-axis taxonomy |
| 09 (don't build an animal) | `09-dont-build-an-animal.ipynb` (fork/merge/checkpoint DAG toy) | Conceptual bridge; substance absorbed narratively into current Ch.2/7 without needing the toy notebook |
| 10 (properties of digital life) | `10-properties-of-digital-life.ipynb` (hypothesis-map bridge) | Same — bridge chapter, no standalone current-book claim |

This is a deliberate finding, not an oversight: the current book's rewrite chose to open directly with Lenia/Physarum/Outlier (current Ch.3–4) rather than rebuilding the ECA-to-crystal on-ramp. Nine legacy notebooks are retired as a result.

---

## Summary table: current chapter → disposition → new notebook(s)

| Ch. | Title | Disposition | New notebook(s) |
|---|---|---|---|
| 01 | How to Read This Book | NO NOTEBOOK REQUIRED | — |
| 02 | What Is Digital Life? | NO NOTEBOOK REQUIRED | — |
| 03 | Look at This Thing | ADAPT + REIMPLEMENT | `03a-lenia-persistent-pattern.ipynb`, `03b-physarum-stigmergy-turnover.ipynb` |
| 04 | Now There Are Two | REUSE + ADAPT | `04-outlier-causal-self-replication.ipynb` |
| 05 | So We Built the Wrong Thing on Purpose | REIMPLEMENT-from-script | `05-adversarial-swarm-decoy.ipynb` |
| 06 | It Looked Like Flocking | ADAPT (split from Ch.4 source) | `06-flocking-vs-ancestry-confound.ipynb` |
| 07 | The Digital Crystal | COMBINE + ADAPT | `07-digital-crystal-source-and-temporal-recovery.ipynb` |
| 08 | The Crystal Gets a Past | COMBINE + ADAPT | `08a-checkpoint-state-vs-history.ipynb`, `08b-pulse-signalling-and-matched-history.ipynb` |
| 09 | Can Experience Change the Material? | COMBINE + ADAPT | `09-material-accessibility-and-history-discrimination.ipynb` |
| 10 | What Survives Material Loss? | ADAPT | `10-material-loss-and-reoccupation.ipynb` |
| 11 | What Does It Cost to Stay? | ADAPT | `11-finite-evaluation-budget.ipynb` |
| 12 | Is There Actually One Thing Here? | ADAPT (upgrade from audit-only) | `12-predictive-and-causal-boundary-tests.ipynb` |
| 13 | What Does One Attachment Cause? | COMBINE + ADAPT (upgrade from audit-only) | `13-single-attachment-causal-decomposition.ipynb` |
| 14 | Can Finite Computation Couple Distant Events? | COMBINE + ADAPT | `14-finite-budget-nonlocal-coupling.ipynb` |
| 15 | Can the Past Redirect the Future? | ADAPT | `15-hidden-state-causal-sufficiency.ipynb` |
| 16 | We Found an Individual. Then We Didn't. | ADAPT (upgrade from audit-only) | `16-causal-modularity-vs-matched-null.ipynb` |
| 17 | How to Fail Correctly | ADAPT | `17-failure-ledger-audit.ipynb` |
| 18 | What Is Digital Life? | NO NOTEBOOK REQUIRED (optional figure) | `18-synthesis-figure.ipynb` (optional) |

**16 required notebooks** (+1 optional), reconstructed from 22 legacy notebooks' worth of relevant content (9 legacy notebooks retired as historical-only), backed primarily by the `research/digital-life/` archive's staged, versioned evidence for chapters 7–17.

---

## Open gaps for NOTEBOOK_AUDIT.md to track

1. **Ch.3 Physarum experiment** — no source script found anywhere in the repo; current book's numeric claims (0.883/0.153 etc.) cannot be independently verified against a historical run. Needs a fresh implementation, explicitly labeled as such.
2. **Ch.4's "[N]"/"[M]" placeholders** — likely resolvable by re-running `research/digital-life/ch03-outlier-minimal-causality.json`'s underlying computation via the reconstructed `04-outlier-causal-self-replication.ipynb`.
3. **Ch.9's twice-repeated "[INSERT EXACT DIRECTIONAL-DIAGNOSTIC NAME...]" placeholder** — likely resolvable from `ch19-two-pasts-v1` stage reports.
4. **Outlier canonical database path**: original notebooks reference `data/digital-life/outlier.sqlite3` (a path that did not exist at legacy-notebook capture time); the actual current data lives at `research/digital-life/digital-life/outlier.sqlite3` (759 MB, nested path) — new notebooks must use the correct current repo-relative path, not the legacy one.
5. **Outlier rule minimal-causal-set DIAGNOSTIC MISMATCH** (115/220 rule codes have multiple minimal causal sets vs. the published paper's claim of none) — an open discrepancy neither the original nor current book resolves; worth surfacing explicitly rather than silently carrying forward.
