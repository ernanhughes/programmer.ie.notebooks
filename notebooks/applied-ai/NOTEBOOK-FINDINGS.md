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
