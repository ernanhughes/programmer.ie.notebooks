# Applied AI — Notebook Companions

Executable companions to the book **Applied AI**. Each notebook backs up its
chapter: the chapter makes the argument, the notebook makes the mechanism
visible.

## Setup

```bash
pip install -r requirements.txt
jupyter lab
```

No API key is required. No notebook imports `codeai`, needs the network, or
calls a commercial model. Notebooks that reproduce a chapter result read the
book's preserved evidence bundles (JSON/SQLite via the standard library),
located through one `EVIDENCE_DIR` constant per notebook and overridable with
the `APPLIED_AI_EVIDENCE` environment variable. Notebooks that teach an
argument instead use small self-contained demonstrations, labelled as such.

All notebooks run top-to-bottom from a fresh kernel. Where randomness
appears, the seed is fixed and printed. Synthetic evidence is labelled
synthetic; preserved evidence is never rewritten to fit the prose.

## Index

Mode: **Reproduce** = recompute a manuscript number from preserved evidence;
**Inspect** = open a preserved ledger/bundle and read what it establishes;
**Demonstrate** = small self-contained mechanism where the chapter is an
argument; **No notebook** = intentional omission (Chapter 30).

| Ch | Notebook | Executable question | Mode | Evidence | Network |
| -- | -------- | ------------------- | ---- | -------- | ------- |
| 01 Beyond the Chat Box | `01-chapter.ipynb` | What does software gain when a review stops being text and becomes a value bound to its input? | Demonstrate | Controlled demonstration | No |
| 02 Never Stand in Front of the Steamroller | `02-chapter.ipynb` | Which of my own tasks are exposed: codified value with none of the four jobs held? | Demonstrate | Controlled demonstration (worksheet) | No |
| 03 If There's Any Doubt, It's Deterministic | `03-chapter.ipynb` | What does routing a deterministic operation through a stochastic one cost? | Demonstrate | Controlled demonstration | No |
| 04 Scrum Built the Training Set | `04-chapter.ipynb` | What does a verifier buy you when candidates are cheap and noisy? | Reproduce + Demonstrate | Chapter figures + labelled simulation | No |
| 05 Meat Proxy | `05-chapter.ipynb` | How does review effectiveness decay as inspection effort falls? | Demonstrate | Synthetic simulation (labelled) | No |
| 06 The Price of Intelligence | `06-chapter.ipynb` | When does the cheapest model bill produce the most expensive process? | Reproduce | Chapter invoice arithmetic | No |
| 07 Intelligence in the Wrong Direction | `07-chapter.ipynb` | How to distinguish apparent improvement from statistical noise? | Demonstrate | Controlled demonstration | No |
| 08 Where Are the Finished Projects? | `08-chapter.ipynb` | What is the ceiling on whole-project speedup? | Reproduce + Demonstrate | Chapter Amdahl table + REAL ladder cost instance | No |
| 09 One Runtime, Many Windows | `09-chapter.ipynb` | Can a second process continue work it never saw, using only an identifier? | Demonstrate + Inspect | Durable-ledger demonstration | No |
| 10 A Revolver, Not a Foundation | `10-chapter.ipynb` | Can one model win a chamber and lose another? | Reproduce | REAL: `p-series/p11` candidate rows | No |
| 11 The Smallest Useful Model Call | `11-chapter.ipynb` | Why must task, call and attempt identities stay separate? | Inspect + Demonstrate | REAL: `ch11-live-opencode` runs | No |
| 12 One Operation, Several Model APIs | `12-chapter.ipynb` | What happens to each control on its way to three different dialects? | Inspect + Demonstrate | REAL: `protocol-conformance` cases | No |
| 13 Token Counts Don't Add Up | `13-chapter.ipynb` | Do these usage fields share a unit? | Reproduce | REAL: `usage-semantics` report + expectations | No |
| 14 A Successful Call Is Not Finished Work | `14-chapter.ipynb` | What must exist before a task may be called complete? | Inspect + Demonstrate | REAL: `task-completion` ledger | No |
| 15 What Did the Model Actually See? | `15-chapter.ipynb` | Is "selected" the same as "sent"? | Inspect | REAL: `context-selection` + `context-rendering` | No |
| 16 Restart Is Not Resume | `16-chapter.ipynb` | Could the effect have happened? | Inspect | REAL: `working-state` ledgers | No |
| 17 Preserve Before You Interpret | `17-chapter.ipynb` | Can yesterday's conclusion change from yesterday's bytes? | Reproduce | REAL: `reinterpretation` replay table | No |
| 18 Claims, Evidence, and Decisions | `18-chapter.ipynb` | What happens to a recorded decision when its basis moves? | Inspect | REAL: `claims-evidence` day-1/day-2 exports | No |
| 19 The Agent Said Done. Did Anything Change? | `19-chapter.ipynb` | Does the world agree that the action occurred? | Reproduce | REAL: `decision-to-effect` five cases | No |
| 20 Capability Is Not Authority | `20-chapter.ipynb` | Can a caller widen a recorded grant? | Inspect + Demonstrate | REAL: `grant-provenance` seven cases | No |
| 21 The Agent Cannot Grade Its Own Homework | `21-chapter.ipynb` | Independence, adequacy, binding — which one failed? | Inspect + Reproduce | REAL: `verification-binding` + `execution-ladder` rows | No |
| 22 Retries Are Side Effects Too | `22-chapter.ipynb` | When does trying again cause a second effect? | Reproduce + Demonstrate | REAL: `retry-rerun` incl. concurrency probe + local fixture | No |
| 23 Blind Before You Compare | `23-chapter.ipynb` | What does a seal exclude, and what walks straight through it? | Inspect | REAL: `sealed-proposals` + `sealed-rendered` (+ sent bodies) | No |
| 24 The Models Were Different. Their Mistakes Weren't | `24-chapter.ipynb` | How much extra coverage did model diversity actually buy? | Reproduce | REAL: `p-series/p1` 84 candidate rows | No |
| 25 When Your Benchmark Is Too Easy | `25-chapter.ipynb` | Did the harder corpus reveal a real difference? | Reproduce | REAL: `p-series/p11` 280 candidate rows | No |
| 26 Discovery Is Not Promotion | `26-chapter.ipynb` | What evidence would promote this discovered pattern? | Reproduce | REAL: `p-series/p2` 288 candidate rows | No |
| 27 Replicate Before You Believe | `27-chapter.ipynb` | Did the promising signal survive a matched replication? | Reproduce | REAL: `p-series/p3` 288 candidate rows | No |
| 28 What Should Happen Next? | `28-chapter.ipynb` | Which operation comes next — and did the cheaper ladder earn adoption? | Inspect + Reproduce | REAL: `scheduler` matrix + `execution-ladder` decision | No |
| 29 One Process, End to End | `29-chapter.ipynb` | Which joints are enforced, and which are only reconstructable? | Inspect | REAL: `capstone-composition` report + ledger | No |
| 30 Your Applied AI | — | — | No notebook, by design | — | — |

Chapter 30 has no notebook by design: the chapter's own section *Why there
is no demonstration here* states that a demonstration would show one
person's tool, which a reader would reasonably take as the shape theirs
should have. See `NOTEBOOK-PLAN.md`.

## Negative results preserved in this set

These are load-bearing — a notebook producing a cleaner result than the
evidence would be a defect:

- Ch 10: two of three real models pass far less often than the baseline.
- Ch 15: selection reached the request only by opt-in; omitted lineage admitted.
- Ch 19: workers reporting `succeeded` while changing nothing; `CHANGED` is not correctness.
- Ch 21: A05 passed a well-built check and was wrong; T07/T10 correct and rejected.
- Ch 22: six concurrent submissions produced six effects — no concurrency safety.
- Ch 23: omitted provenance and copied text both defeat the seal.
- Ch 24: premium 0.0, zero rescues, more tokens for identical coverage.
- Ch 25: coverage rose while candidate reliability fell; sign test p = 0.625.
- Ch 26: the stance portfolio lost; the attractive subgroup was not promoted.
- Ch 27: the replication tied at +45.8% tokens; movement is chance-like.
- Ch 28: the cheaper ladder failed its own adoption rule on one wrong acceptance.
- Ch 29: five of thirteen joints weaker than enforced at baseline.

## Notes for the separate repository

- Notebooks are self-contained: standard library plus `numpy`, `pandas`,
  `matplotlib`, `scipy` where noted (see `requirements.txt`). No imports from
  the book repository, no private packages, no absolute paths, no private data.
- Evidence access is isolated to one `EVIDENCE_DIR` constant per notebook,
  overridable with `APPLIED_AI_EVIDENCE`. Each notebook names the exact files
  it reads, so they can be copied beside the notebook when the set moves.
- File writes are confined to temporary directories.
- Outputs checked in are the result of fresh-kernel top-to-bottom runs;
  plots and compact tables are kept, debug noise removed.
- Execution status for the whole set: see `EXECUTION-REPORT.md`.
- Discrepancies found by executing notebooks against the manuscript:
  see `NOTEBOOK-FINDINGS.md`.
