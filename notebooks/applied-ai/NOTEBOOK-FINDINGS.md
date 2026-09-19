# Notebook Findings (executable artifacts feeding back into the manuscript)

Only entries where building or executing a notebook revealed something worth
changing in the manuscript. Routine notes do not belong here.

## Chapter 03

The misrouting experiment shows the penalty is two-dimensional (cost *and*
variance), while the chapter's prose leans on cost alone. If the manuscript
presents a "route deterministically" rule, consider stating both penalties:
a misrouted deterministic step is not just expensive, it is irreproducible
across reruns.

Suggested manuscript change: add one sentence pairing the cost penalty with
the variance penalty wherever deterministic-routing is prescribed.

## Chapter 11

The retry demonstration shows naive per-call cost accounting undercounts by
exactly the attempt multiplier (2x for one retry). If the chapter's cost
example counts one price per logical call, it understates usage whenever a
failed attempt is billable.

Suggested manuscript change: state explicitly whether the chapter's cost
figures count attempts or logical calls, and keep `retry_count ==
len(attempts)` visible near any pricing example.

## Chapter 13

The zero-fill experiment produces a cost of exactly $0.000000 for an unknown
fresh-input field — a number that looks precise while being unmeasured. This
is a stronger formulation of the chapter's warning than "don't default
missing fields": a silent zero does not read as missing, it reads as free.

Suggested manuscript change: if the chapter shows a normalization table,
include the zero-filled row as an anti-example with its misleading $0.00.

## Chapter 21

While building the toy task, `eval("100/4")` returned `25.0` (float), which
broke a strict integer comparison in the first draft of the checker. The
notebook now compares numerically, but the incident is the chapter's point in
miniature: a verifier must normalize representation before comparing, or
`asserted == executed` fails on type trivia.

Suggested manuscript change: nowhere — already consistent; recorded so the
manuscript keeps a representation-normalization remark wherever checkers are
specified.

## Chapter 23 — Blind Before You Compare

### Finding

`analysis.json` in the sealed-rendered bundle reports `sentinel_in_bytes:
false` for the copied-prompt case. Read alone, that looks like the seal
stopped copied text. The companion `transport_bodies.json` shows the opposite:
the sent body carries the sentinel in via the branch prompt (the render
covers context items only).

### Manuscript says

The chapter already reports both halves correctly (render clean, sent body
carrying the sentinel).

### Evidence

`experiments/applied-ai/evidence/sealed-rendered/2026-09-14-1b3c7a2/analysis.json`
vs `transport_bodies.json` (`call-copied`).

### Suggested follow-up

None for the manuscript. Recorded so future notebook readers check the sent
body, not just the analysis summary, when judging what a seal stopped.

## Chapter 29 — One Process, End to End (evidence hygiene)

### Finding

`results.json` in the capstone-composition bundle embeds a machine-specific
workspace path (`C:\Users\...\Temp\ch29-composition-...`). It is evidence
metadata about where the producer ran, not a result — but any notebook that
prints the results file verbatim would leak it.

### Manuscript says

Nothing (not a manuscript claim).

### Evidence

`experiments/applied-ai/evidence/capstone-composition/results.json`
(`workspace` field).

### Suggested follow-up

Strip or relativize ephemeral producer paths from evidence JSON before
archiving bundles; notebook-side, the Ch 29 notebook reads every field except
`workspace`.

## Continuation audit notes (2026-09-19, process — not manuscript)

- Chapters 18–29 on disk were the stale Sept-14 synthetic toy set, not the
  rebuilds the previous transcript implied; all twelve were rebuilt against
  preserved evidence in this continuation.
- Saved outputs in `08`/`10`/`12` (`EVIDENCE_DIR: C:\Projects\...`) and `09`
  (tempfile path with username) leaked machine-specific paths; scrubbed to
  `$APPLIED_AI_EVIDENCE` / `$TMP\...` in outputs only — no cell sources
  changed.
- Secret scan over all 29 notebooks: three `sk-...` regex hits, all false
  positives on `task-<hex>` identifiers. No credentials anywhere.
- No unexplained FAIL: 29/29 PASS from fresh kernels (see
  `EXECUTION-REPORT.md`).
