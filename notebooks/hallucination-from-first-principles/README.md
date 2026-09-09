# Hallucination From First Principles — Notebook Companions

Runnable notebook companions for **Hallucination From First Principles** (chapters 01–15).

The **book is the authority for chapter meaning**. The notebooks exercise its mechanisms
with small, falsifiable experiments that match the current chapter claims.

All fixtures are **synthetic and deterministic** (fixed seeds, stdlib + numpy only).
They demonstrate the mechanism *type* — they do not reproduce the book's 10k-row
summarization run or hard-negative tables, and they establish nothing about real
verifier or generator accuracy (per the appendix ledger's own discipline).

| Notebook | Chapter title | Question isolated |
|---|---|---|
| `01-chapter.ipynb` | When Models Make Things Up | Payoff structure: guessing vs abstaining |
| `02-chapter.ipynb` | Hallucination Is Not One Thing | Response label vs per-claim typed records |
| `03-chapter.ipynb` | Evidence, Truth, and Verifiability | Resolution before verification; citation chain |
| `04-chapter.ipynb` | How Do You Measure a Hallucination? | Proximity high where direction flips; trace first |
| `05-chapter.ipynb` | Hallucination Energy | SVD containment score; NO_EVIDENCE state; rank sweep |
| `06-chapter.ipynb` | How to Evaluate a Hallucination Detector | AUC vs error budget; prevalence vs precision |
| `07-chapter.ipynb` | Breaking the Detector | Content / context / configuration attacks |
| `08-chapter.ipynb` | Containment Is Not Truth | Full-rank limit; scalar aliasing vs coordinates |
| `09-chapter.ipynb` | Beyond Hallucination: Consistency and Sensitivity | Selective responsiveness vs brittleness |
| `10-chapter.ipynb` | The Safe but Useless Model | Static scoring vs paired-intervention exposure |
| `11-chapter.ipynb` | Knowing When Not to Answer | Coverage–risk curve; critical-field gaps |
| `12-chapter.ipynb` | From Measurements to Policy | Policy engine cases; v1 vs v2 replay |
| `13-chapter.ipynb` | Verification, Repair, and Rejection | Recovery loop invariants (imports `recovery_demo.py`) |
| `14-chapter.ipynb` | The Memory Contamination Problem | Admission + read-path gates; circularity block |
| `15-chapter.ipynb` | Building Systems That Distrust Their Models | Full proposal→enforcement→recording capstone |

## Reused implementation

- `experiments/hallucination-from-first-principles/policy_engine.py` (ch12, ch15)
- `experiments/hallucination-from-first-principles/recovery_demo.py` (ch13, ch15)
- Ch05 reference `hallucination_energy` from the chapter text (reimplemented in-notebook)

Notebook-local code is experiment setup, controls, assertions, and diagnostics only.

## Contract

- Notebooks live under `/notebooks/hallucination-from-first-principles/`, not under Hugo `content/`.
- Deterministic: fixed seeds. No network, no API keys, no live LM calls, no downloads.
- Each notebook executes CPU-only in well under 120 s (`newbooks-venv` kernel) and is
  committed stripped (empty outputs, null execution counts).

## Skip log

- `16-appendix.md` (Appendix: The Evidence Ledger) — **skipped deliberately**.
  The appendix is a provenance ledger over the book's empirical runs (10k-row run +
  hard-negative tables), not a mechanism. There is nothing falsifiable to execute;
  a notebook would only reprint the ledger. Reason recorded here so the gap is
  intentional, not an oversight.
