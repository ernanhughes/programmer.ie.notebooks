# Debugging AI From First Principles — Notebook Companions

Runnable notebook companions for **Debugging AI From First Principles** (chapters 01–60).

The **book is the authority for chapter meaning.** Each notebook isolates one falsifiable
question from its chapter and answers it with a small, deterministic experiment — the same
"concept → demonstration" move the chapters use, rebuilt as code you can run and poke.

## Approach for this book

The book's chapters are deliberately *method* chapters: every worked example is labelled a
**constructed illustration**, every lab is **PROPOSED, not executed**, and there is no
`experiments/debugging-ai/` measurement substrate. So these notebooks do not check numbers
against artifacts — they make the **mechanism** runnable:

- The chapter's constructed scenario becomes a small self-contained simulation
  (a five-line billing function, a five-stage pipeline, a trajectory schema, a guardrail).
- Every code cell ends in `assert`s that encode the chapter's claim, plus one `print`
  line stating what was earned.
- Where the chapter warns about a failure mode (noisy oracle, masking stage,
  explanation-as-trace, symptom relief), the notebook *reproduces the failure mode* too,
  not just the happy path.

No LM is called anywhere. Fixtures are synthetic and deterministic (fixed seeds).

## Contract

- Notebooks live under `/notebooks/debugging-ai/`, not under Hugo `content/`.
- Standard library + `numpy` only. No network, no API keys, no live LM calls, no downloads.
- Deterministic: fixed seeds. Each notebook runs CPU-only in well under 120 s on the
  `python3` kernel and is committed **stripped** (empty outputs, null execution counts).
- Notebook-local code is experiment setup, controls, assertions, and diagnostics only.

## Index

| Notebook | Chapter | Question isolated | Status |
|---|---|---|---|
| `01-chapter.ipynb` | What Does It Mean to Debug? | Two edits pass the €1,200 invoice — does the checkpoint table + a counterfactual name the one on the causal path? | ✅ |
| `02-chapter.ipynb` | The First Divergence | Three defects, one symptom — different first-divergence stages; does a monotonicity check gate bisection? | ✅ |
| `03-chapter.ipynb` | Evidence Before Explanation | Three pipeline boundaries produce one wrong RAG answer — do the frozen handoff artifacts separate them where the model's self-explanation cannot? | ✅ |
| `04-chapter.ipynb` | The Debugging Stack | One `KeyError`, three layers — does a layer-swap probe eliminate cheapest-first and convict exactly one? | ✅ |
| `05-chapter.ipynb` | Reading Python Exceptions | Two incidents, byte-identical traceback — does two-pass reading + an old-snapshot swap separate a code assumption from a data regression? | ✅ |
| `06-chapter.ipynb` | Inspect State, Don't Guess | `$160` not `$140` from two mechanisms — does predict-then-inspect at entry convict the right one in one pass? | ✅ |
| `07-chapter.ipynb` | Debug the Boundary | 47 green tests, a phantom page — does a six-cell boundary table turn one failure into a failure *shape* that names a fencepost? | ✅ |
| `08-chapter.ipynb` | Assertions, Invariants, and Contracts | Four weeks of silent drift — does a consumer-entry contract stop it loudly, and why consumer entry over producer exit? | ✅ |
| `09-chapter.ipynb` | Environment Bugs | Same code + data hash, passes local / fails CI — does the locked-container probe + freeze-diff bisect name the one package? | ✅ |
| `10-chapter.ipynb` | The Notebook Is Not the Program You See | Passes interactively, dies on Restart & Run All — does the `execution_count` gutter reconstruct what actually ran? | ✅ |
| `11-chapter.ipynb` | Hidden Notebook State | Kernel knows `threshold`, no cell defines it — does a fresh-vs-dirty diff separate deleted-cell residue from an overwritten line? | ✅ |
| `12-chapter.ipynb` | Reproducible Notebooks | 0.91 / 0.84 / 0.88, all green — can each pin (substrate → seed → data) be attributed one class at a time? | ✅ |
| `13-chapter.ipynb` | Debug the Data Before the Model | Validation 0.99, live 0.61 — does the train-vs-data swap (both arms) convict the data before any retrain? | ✅ |
| `14-chapter.ipynb` | Shapes, Types, Devices, and Tensors | `matmul` crashes two ways — does an upstream triple survey name the first divergent handoff? | ✅ |
| `15-chapter.ipynb` | When Training Goes Wrong | Flat loss at `ln(10)` — does H3 → H2 → H1 triage (raw-vs-reported, overfit-64, one LR change) convict one system? | ✅ |
| `16-chapter.ipynb` | Debugging Evaluation | 0.97 vs 0.55 intent slice — do seed / fresh-slice / metric-swap perturbations separate leakage, metric mismatch, and luck? | ✅ |
| `17-chapter.ipynb` | Debugging What You Cannot See | Wrong answer, no interior to inspect — does a frozen-bundle boundary probe convict a layer, and is the model's explanation admissible? | ✅ |
| `18-chapter.ipynb` | Is the Model Actually the Problem? | Ticket says "model failure" — do stack-order swap probes with a stop rule convict pipeline / params / weights cheapest-first? | ✅ |
| `19-chapter.ipynb` | Inspect the Actual Model Input | Prompt cites 4.2, render does not — does a per-segment account + tokenizer round-trip separate retrieval miss / assembly loss / distortion? | ✅ |
| `20-chapter.ipynb` | Context Windows and Truncation | Short passes, long fails — do shorten / reorder / budget probes separate a cut from a burial from a starved finish? | ✅ |
| `21-chapter.ipynb` | Sampling Is Part of the Program | Fixture flickers 9/12 → 5/12 — does an N≥20 series with a fixed signature separate sampling spread from bimodal competence, and is pass@k the shipped rate? | ✅ |
| `22-chapter.ipynb` | Internal Signals | The logprob dips at the veer token — does locate-then-probe (nominated probe flips it, un-nominated control stays flat) convict, or is the signal a mirage? | ✅ |
| `23-chapter.ipynb` | Representation and Behavioral Diffs | rev-B drops the fixture 11/12 → 7/12 — does a harness-equal per-case diff separate regression / harness drift / redistributed competence, and which gate fires? | ✅ |
| `24-chapter.ipynb` | AI as Builder, Designer, Researcher, and Reviewer | One prompt, four fluent defective artifacts — does role → evidence → failure catch all four where one careful read catches none? | ✅ |
| `25-chapter.ipynb` | Debugging Intent | "Make it standard" returns rejected code — does the intent-diff separate intent-gaps (prompt defect) from generation-gaps (model defect)? | ✅ |
| `26-chapter.ipynb` | Debugging Context for Coding Agents | Agent edits the wrong file — does the working-set dump (sent hash vs current vs absent, per file) separate missing / misread / stale context? | ✅ |
| `27-chapter.ipynb` | Debugging AI-Generated Designs | "Clean" diagram, 450ms over a 200ms budget — does a constraint table + tradeoff matrix separate violation / unverifiable / tradeoff-blindness? | ✅ |
| `28-chapter.ipynb` | Debugging AI Research | Three citations, one fake — does resolving every claim to a retrieved byte separate fabrication / misattribution / synthesis overreach? | ✅ |
| `29-chapter.ipynb` | Debugging Coding Agents | Agent loops 40 min, closes "verified" on a red suite — does segmenting the trajectory separate looping / premature completion / gate tampering? | ✅ |
| `30-chapter.ipynb` | Treat Prompts as Programs | A dashboard "tweak" breaks citations — does repo/hash/byte-diff/fixture-gate separate prompt regression / environment drift / no-suite? | ✅ |
| `31`–`35` | Part VI (prompts, retrieval, hallucinations) | minimize the prompt · retrieval stages · retriever-vs-generator · claim tables · explanation audit | pending |
| `36`–`43` | Part VII (agents & trajectories) | trajectory schema · failure taxonomy · loop detection · replay/fork · causal replay · trajectory diff · multi-agent routing | pending |
| `44`–`51` | Part VIII (building the AI debugger) | delegation gates · the crash dump · machine invariants · hypothesis enumeration · discriminating experiments · verification bar · benchmark design · debug the debugger | pending |
| `52`–`60` | Part IX–X (production & playbook) | per-request records · incident conveyor · runtime guardrails · cost/latency ledger · live-incident order · ten-minute triage · one-hour isolation · full investigation · the toolkit | pending |

## Skip log

*(none yet — every chapter has a mechanism that can be exercised)*
