# Applied AI — Notebook Regeneration Plan

## Build status (2026-09-19 continuation)

The plan below was written as a Wave 0 deliverable and is preserved as-is.
Build reality as of 2026-09-19:

- Chapters 01–17: rebuilt per this plan by the previous agent; re-executed
  from fresh kernels in this continuation — **17/17 PASS**, untouched.
- Chapters 18–29: were stale synthetic stubs (Sept 14 toy set); rebuilt per
  this plan in this continuation — **12/12 PASS** from fresh kernels.
- Chapter 30: no notebook, by design (unchanged).
- Planned modes match implementation for every chapter except two deliberate,
  evidence-driven adjustments: Ch 20 is Inspect + a small stdlib grant model
  (the chapter's illustrative assertions, not stage evidence), and Ch 22 is
  Reproduce + a local duplicate-effect fixture (the failure it demonstrates
  precedes the keyed fix).
- Whole set: **29/29 PASS**, no API keys, no machine paths in final cells or
  outputs (four output leaks scrubbed; see EXECUTION-REPORT.md).

Wave 0 deliverable below. Written after inspecting the current 30-chapter manuscript,
the current CodeAI source at `C:/Projects/codeai/src/codeai/`, and the 29
preserved evidence bundles under
`C:/Projects/new-books/experiments/applied-ai/evidence/`.

## What changed since the previous notebook set

The previous set (29 notebooks, built 2026-09-14/17) is uniformly synthetic:
every notebook is a 10-cell toy simulation seeded with `SEED = 42`. That was the
right shape when the runtime and the experiments did not yet exist.

They now exist. The book has 29 preserved evidence bundles, four frozen
P-series experiment exports, live provider captures, and SQLite ledgers from
pinned runs. Chapters 10–29 report measured results computed from those
artifacts.

So the governing change in this regeneration is:

> Where the chapter reports a real result and the evidence is on disk, the
> notebook **reproduces or inspects that evidence** instead of simulating a toy
> version of it.

Simulation is retained only for Chapters 02–09, where the chapters are
themselves arguments or arithmetic, and it is labelled as simulation.

## Execution constraints adopted

- **No CodeAI import on any default path.** `codeai` is not installed in the
  book repository's interpreter. Every notebook runs on the standard library
  plus `numpy` / `pandas` / `matplotlib` / `scipy`. Ledgers are read with stdlib
  `sqlite3`; exports and bundles are read with stdlib `json`.
- **No network and no API key on any default path.**
- **Evidence access is isolated to one constant per notebook**, `EVIDENCE_DIR`,
  resolved by searching upward for `experiments/applied-ai/evidence` and
  overridable with the `APPLIED_AI_EVIDENCE` environment variable. Each notebook
  names the exact files it reads, so they can be copied beside the notebook when
  the set moves to its own repository.
- Notebooks that need a filesystem effect write only inside
  `tempfile.mkdtemp()`.

## Mode key

- **Reproduce** — recompute a manuscript number from preserved evidence.
- **Inspect** — open a preserved ledger or bundle and read what it establishes.
- **Demonstrate** — build a small self-contained mechanism, used where the
  chapter is an argument or where the production code is too large to teach.

## Plan

| Ch | Chapter | Notebook question | Mode | Current evidence / source | Planned experiment | Existing notebook |
|----|---------|-------------------|------|---------------------------|--------------------|-------------------|
| 01 | Beyond the Chat Box | What does software gain when a review stops being text and becomes a value bound to its input? | Demonstrate | Chapter's record fields; fake adapter | Fake call produces a record carrying `paragraph_sha`, `prompt_version`, `disposition`; edit the paragraph; refuse to file the now-stale review | rebuild |
| 02 | Never Stand in Front of the Steamroller | Which of my own tasks are exposed: codified value with none of the four jobs held? | Demonstrate (worksheet) | Chapter's exposure audit and scoring table | Score the chapter's five illustrative tasks, reproduce "2 of 5 exposed", leave an editable block for the reader's own | rebuild, deliberately small (old one was 40 KB of simulation) |
| 03 | If There's Any Doubt, It's Deterministic | What does routing a deterministic operation through a stochastic one cost in variance, money and failure modes? | Demonstrate | Chapter's seven operations and classification table | Implement all seven deterministically; re-route three through a simulated sampler; repeat N times; show variance, cost and new failure modes; then the generator/verifier asymmetry | rebuild |
| 04 | Scrum Built the Training Set | How much of the correctness in generate-and-filter comes from the verifier rather than the generator? | Reproduce + Demonstrate | SWE-bench yield (2,294 of ~90,000) and the AlphaCode filter ratio, both from the chapter | Recompute the ~2.5% harvest yield; simulate a weak generator behind a cheap exact verifier; run the six-question terrain survey as code | rebuild |
| 05 | Meat Proxy | As a system's reliability rises, what happens to a reviewer's catch rate, and which review strategy still detects degradation? | Demonstrate (labelled simulation) | Chapter's review strategies | Compare universal skim, deep random sample, mechanical checks and seeded defects; show only sampling and seeding yield an error-rate estimate | rebuild |
| 06 | The Price of Intelligence | When does the cheapest model bill produce the most expensive process? | Reproduce | Chapter's own `run()` cascade and invoice arithmetic | Reproduce the $453,600 invoice and the three-row cascade table exactly; sweep the weak-check acceptance rate to find the crossover | rebuild (old was 37 KB) |
| 07 | Intelligence in the Wrong Direction | Can this evaluation tell two models apart? | Demonstrate | Chapter's 14-of-20 binomial and its 40/50 standard error | Reproduce p≈0.115 and SE≈0.057; compare paired against unpaired analysis; draw a power curve for the effect the reader wants to claim | rebuild |
| 08 | Where Are the Finished Projects? | What is the ceiling on whole-project speedup? | Reproduce + Demonstrate | Chapter's Amdahl table; Chapter 28's $35.01 / $45.03 cost instance | Reproduce the cap table and the 1.43×; show the ceiling falling as the serial remainder grows; reproduce the cost-Amdahl instance | rebuild (old was 57 KB) |
| 09 | One Runtime, Many Windows | Can a second process continue work it never saw, using only an identifier? | Demonstrate + Inspect | `working-state` ledger for shape; chapter's `surface_continuity_demo.py` | Build a tiny durable ledger; process A creates, process B continues by identity, process C reads it back; contrast with transcript summarisation | rebuild |
| 10 | A Revolver, Not a Foundation | Can one model win a chamber and lose another? | **Reproduce** | `p-series/p11/p11-export.json` (real per-model candidate rows) | Treat the three real models as three chamber occupants; per-task pass rates (qwen 30/40, llama 19/40, mistral 15/40); count real negative flips; price per passing item | rebuild — the old notebook invented rows, real ones exist |
| 11 | The Smallest Useful Model Call | Why must task, call and attempt identities stay separate? | **Inspect** + Demonstrate | `ch11-live-opencode/events.json` and its preserved response artifact | Read the four live OpenCode runs; open the preserved body and find `finish_reason: "length"` behind a recorded success; then demonstrate one call with two attempts | rebuild with real evidence |
| 12 | One Operation, Several Model APIs | What happens to each control on its way to three different dialects? | Inspect + Demonstrate | `protocol-conformance/` bundle (offline cases plus live captures) | Read the offline case table showing identical outcomes across all three dialects; implement the six fates of a control | rebuild |
| 13 | Token Counts Don't Add Up | Do these usage fields share a unit? | **Reproduce** | `usage-semantics/offline/report.json` and `expected.json` | Recompute v1 against v2 for the four real responses: fresh input 38 / 87 / 73, Messages total UNKNOWN with a lower bound; show zero-filling biasing cost downward | rebuild |
| 14 | A Successful Call Is Not Finished Work | What must exist before a task may be called complete? | Inspect + Demonstrate | `task-completion/` ledger | Show a succeeded call beside an incomplete task; implement acceptance validation; run the negative cases including the edited artifact that passes its own check | rebuild |
| 15 | What Did the Model Actually See? | Is "selected" the same as "sent"? | **Inspect** | `context-selection/` and `context-rendering/` bundles | Read the recorded package, trace, exclusion reasons and identity probes; then the rendered-bytes binding that closed the gap; show omitted lineage being admitted | rebuild |
| 16 | Restart Is Not Resume | Could the effect have happened? | **Inspect** | `working-state/2026-09-13-68f4ba0/` (8 cases plus provider receipt logs) | Classify each case from its ledger alone; show the naive restart's two receipts against resume's one; show the drift refusal | rebuild |
| 17 | Preserve Before You Interpret | Can yesterday's conclusion change from yesterday's bytes? | **Reproduce** | `reinterpretation/recorded-call-v1-v2/` replay table | Apply v1 and v2 to the same preserved bytes: succeeded becomes unresolved with zero new provider calls; then delete the bytes and watch reinterpretation refuse | rebuild |
| 18 | Claims, Evidence, and Decisions | What happens to a recorded decision when its basis moves? | **Inspect** | `claims-evidence/2026-09-14-3b6d8fb/` ledger | Trace claim to evidence to decision; add the refuting source; show `basis_changed` naming exactly what moved while the decision event stays byte-identical | rebuild |
| 19 | The Agent Said Done. Did Anything Change? | Does the worker's report match the world? | **Reproduce** | `decision-to-effect/2026-09-14-a1b562a/` | Read the honest, lying, partial and wrong-target cases; compare adapter status against runtime observation and the actual bytes; show `CHANGED` is not correctness | rebuild |
| 20 | Capability Is Not Authority | Can a caller widen a recorded grant? | **Inspect** | `grant-provenance/2026-09-14-a1b562a/` (7 cases) | Read all seven, especially the caller-forged broader parent; show the DENIED completion with zero adapter invocations | rebuild |
| 21 | The Agent Cannot Grade Its Own Homework | Independence, adequacy, binding — which one failed? | **Inspect** + Reproduce | `verification-binding/` (10 checks) and `execution-ladder/` items A05, T07, T10 | Read PASS, FAIL and ERROR side by side; then reproduce the real adequacy failure: A05 grounded and wrong, T07 and T10 correct and rejected | rebuild — far stronger than the old self-evaluation toy |
| 22 | Retries Are Side Effects Too | When does trying again cause a second effect? | **Reproduce** | `retry-rerun/2026-09-14-1b3c7a2/` including the concurrency probe | Reproduce sequential duplicate safety, the key-collision refusal and cached failure; then the frozen concurrency diagnostic: 6 submissions, 6 effects | rebuild |
| 23 | Blind Before You Compare | What does a seal exclude, and what walks straight through it? | **Inspect** | `sealed-proposals/` and `sealed-rendered/` | Read the clean fan-out, then the two boundaries: omitted provenance included, copied text present in the sent bytes; preserve the negative result | rebuild — the old "independent calls" concept is obsolete |
| 24 | The Models Were Different. Their Mistakes Weren't | Did model variety add coverage over matched redraws? | **Reproduce** | `p-series/p1/p1-export.json` (84 calls) | Recompute the arm table, premium 0.0, zero rescues, 1.20× tokens; read all seven failed repairs of `stale-state-average` and name the shared idea | rebuild — the old notebook simulated 60 tasks; 84 real calls exist |
| 25 | When Your Benchmark Is Too Easy | Did the harder corpus reveal a real difference? | **Reproduce** | `p-series/p11/p11-export.json` (280 calls) | Recompute 27 / 31 / 33 coverage against falling candidate rates; the four discordant tasks; the sign test at p=0.625; the per-model slot split | rebuild |
| 26 | Discovery Is Not Promotion | Can the manipulated variable be recovered from rows that never recorded it? | **Reproduce** | `p-series/p2/p2-export.json` (288 calls) | Recover stance by input-token signature (0, +32, +37, +44; 36 calls each); reproduce the per-stance solve sets 7/7/7/9; show the exposure-mismatch trap | rebuild |
| 27 | Replicate Before You Believe | Did the promising signal survive a matched replication? | **Reproduce** | `p-series/p3/p3-export.json` (288 calls) | Recompute the tie: 9/12 and 44/144 on both arms at +45.8% tokens; per-task movement summing to 18; permutation test at p≈0.31 | rebuild |
| 28 | What Should Happen Next? | Which operation comes next, and did the cheaper ladder earn adoption? | **Inspect** | `scheduler/results.json` and `execution-ladder/2026-09-14-7a0d43b/` | Reproduce the 16/16 policy matrix and the split-budget precedence; then the ladder decision: cheaper, one more correct, and still `ladder_justified: false` | rebuild |
| 29 | One Process, End to End | Which joints are enforced, and which are only reconstructable? | **Inspect** | `capstone-composition/` and `C:/Projects/codeai/experiments/W1-composition-results.md` | Walk one task through the ledger; then classify all thirteen joints (ENFORCED / DERIVED / RECORDED / CONVENTIONAL / ABSENT) and show which arrows moved | rebuild |
| 30 | Your Applied AI | — | — | — | **No notebook by design** | none — see below |

## Chapter 30: no notebook, by design

Chapter 30 contains an explicit section, *Why there is no demonstration here*,
which states that a demonstration would show one person's tool and that a reader
would reasonably take it as the shape theirs should have.

A notebook would contradict the chapter's own stated decision. The chapter's
"Do this now" is a written worksheet about the reader's own work and needs no
kernel.

No `30-chapter.ipynb` will be created. This omission is recorded here and in
`README.md`.

## Negative results that must survive into the notebooks

These are load-bearing. A notebook that produces a cleaner result than the
evidence does is a defect.

| Ch | Result that must be preserved |
|----|-------------------------------|
| 10 | Two of the three real models pass far less often than the baseline |
| 15 | Selection reached the request only by opt-in; omitted lineage is admitted |
| 19 | A worker reporting success while changing nothing; `CHANGED` is not correctness |
| 21 | A05 passed a well-built check and was wrong; T07 and T10 were correct and rejected |
| 22 | Six concurrent submissions produced six effects; there is no concurrency safety |
| 23 | Omitted provenance and copied text both defeat the seal |
| 24 | Premium 0.0, zero rescues, more tokens for identical coverage |
| 25 | Coverage rose while candidate reliability fell; the sign test gives p=0.625 |
| 26 | The stance portfolio lost; the attractive subgroup was not promoted |
| 27 | The replication tied at +45.8% tokens; movement is indistinguishable from chance |
| 28 | The cheaper ladder failed its own adoption rule on one wrong acceptance |
| 29 | Five of thirteen joints were not enforced at baseline |
