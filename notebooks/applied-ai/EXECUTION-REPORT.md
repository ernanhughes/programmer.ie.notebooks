# Applied AI Notebooks — Execution Report (2026-09-19)

Fresh-kernel `nbclient` execution of the full set, `allow_errors=False`.
Every notebook catches its own pedagogical failure demonstrations internally,
so PASS means the notebook ran top-to-bottom with no cell error escaping.

| Ch | Notebook | Status | Runtime | Evidence mode |
| -- | -------- | ------ | ------- | ------------- |
| 01 | `01-chapter.ipynb` | PASS | ~1 s | Controlled demonstration |
| 02 | `02-chapter.ipynb` | PASS | ~1 s | Controlled demonstration (worksheet) |
| 03 | `03-chapter.ipynb` | PASS | ~1 s | Controlled demonstration |
| 04 | `04-chapter.ipynb` | PASS | ~1 s | Chapter figures + labelled simulation |
| 05 | `05-chapter.ipynb` | PASS | ~2 s | Synthetic simulation (labelled) |
| 06 | `06-chapter.ipynb` | PASS | ~2 s | Chapter invoice arithmetic |
| 07 | `07-chapter.ipynb` | PASS | ~3 s | Controlled demonstration |
| 08 | `08-chapter.ipynb` | PASS | ~2 s | Chapter table + REAL ladder cost instance |
| 09 | `09-chapter.ipynb` | PASS | ~1 s | Durable-ledger demonstration |
| 10 | `10-chapter.ipynb` | PASS | ~2 s | REAL: `p-series/p11` |
| 11 | `11-chapter.ipynb` | PASS | ~1 s | REAL: `ch11-live-opencode` |
| 12 | `12-chapter.ipynb` | PASS | ~1 s | REAL: `protocol-conformance` |
| 13 | `13-chapter.ipynb` | PASS | ~1 s | REAL: `usage-semantics` |
| 14 | `14-chapter.ipynb` | PASS | ~1 s | REAL: `task-completion` |
| 15 | `15-chapter.ipynb` | PASS | ~1 s | REAL: `context-selection` + `context-rendering` |
| 16 | `16-chapter.ipynb` | PASS | ~2 s | REAL: `working-state` |
| 17 | `17-chapter.ipynb` | PASS | ~1 s | REAL: `reinterpretation` |
| 18 | `18-chapter.ipynb` | PASS | ~1 s | REAL: `claims-evidence` |
| 19 | `19-chapter.ipynb` | PASS | ~1 s | REAL: `decision-to-effect` |
| 20 | `20-chapter.ipynb` | PASS | ~1 s | REAL: `grant-provenance` |
| 21 | `21-chapter.ipynb` | PASS | ~1 s | REAL: `verification-binding` + `execution-ladder` |
| 22 | `22-chapter.ipynb` | PASS | ~1 s | REAL: `retry-rerun` + local fixture |
| 23 | `23-chapter.ipynb` | PASS | ~1 s | REAL: `sealed-proposals` + `sealed-rendered` |
| 24 | `24-chapter.ipynb` | PASS | ~2 s | REAL: `p-series/p1` |
| 25 | `25-chapter.ipynb` | PASS | ~2 s | REAL: `p-series/p11` |
| 26 | `26-chapter.ipynb` | PASS | ~1 s | REAL: `p-series/p2` |
| 27 | `27-chapter.ipynb` | PASS | ~2 s | REAL: `p-series/p3` (permutation check reseeded, 20k trials) |
| 28 | `28-chapter.ipynb` | PASS | ~1 s | REAL: `scheduler` + `execution-ladder` |
| 29 | `29-chapter.ipynb` | PASS | ~1 s | REAL: `capstone-composition` |
| 30 | — | No notebook, by design | — | — |

**29/29 PASS, 0 FAIL.** Chapter 30 is intentionally omitted: the chapter's
own section *Why there is no demonstration here* refuses a demonstration, and
a notebook would contradict it.

Audit actions taken in this pass: stale chapter-mapping scan (one historical
phrase in Ch 15 explanatory text, legitimate — no change); secret scan (three
`task-<hex>` false positives, no credentials); machine-path scrub of four
saved-output leaks (`08`/`10`/`12` evidence root, `09` tempfile path) with no
cell-source changes; cell IDs stable and sequential (`c00…`), no `nbformat`
warnings; zero `error` outputs in any checked-in notebook.
