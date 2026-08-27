# Agents From First Principles — Notebook Companions

This directory contains the runnable notebook companions for the current **Agents From First Principles** book.

The **book is the authority for chapter meaning**. The shared Python package under `/demo/agents-from-first-principles/first_principles_agent/` remains the implementation authority. The notebooks connect those two: they exercise the shared implementation with small, falsifiable experiments that match the current chapter claims.

The implementation was built in internal stages numbered `00` through `10`, while the book is numbered Chapters `1` through `11`. That offset is intentional and is now stated in every notebook.

| Book chapter | Notebook | Internal demo stage | Current chapter title |
|---:|---|---:|---|
| 1 | `01-chapter.ipynb` | 00 | What Is an Agent, Really? |
| 2 | `02-chapter.ipynb` | 01 | The Action Boundary |
| 3 | `03-chapter.ipynb` | 02 | Candidate Generation and Selection |
| 4 | `04-chapter.ipynb` | 03 | Critique, Revision, and Acceptance |
| 5 | `05-chapter.ipynb` | 04 | Planning and Execution |
| 6 | `06-chapter.ipynb` | 05 | Runtime State, Progress, and Termination |
| 7 | `07-chapter.ipynb` | 06 | Capabilities and Routing |
| 8 | `08-chapter.ipynb` | 07 | Memory and Selective Recall |
| 9 | `09-chapter.ipynb` | 08 | Trajectory Search |
| 10 | `10-chapter.ipynb` | 09 | Evidence and Verification |
| 11 | `11-chapter.ipynb` | 10 | Building the Complete Agent |

## 01–10 — Earn one mechanism at a time

The first ten notebooks progressively establish:

```text
adaptive control
→ action authority boundary
→ complete alternatives + selection
→ critique + targeted revision + acceptance
→ explicit planning
→ runtime state + progress + termination
→ capability routing
→ selective memory
→ isolated trajectory search
→ state-bound evidence + protected verification
```

The notebooks do **not** maintain a second agent implementation. They import the shared demo package and use deterministic or recorded fixtures so the mechanism under test is observable without a live model API.

The upgraded notebooks also preserve distinctions sharpened in the current book: structural plan validity is not semantic plan validity; progress signals need integrity; lifecycle eligibility precedes memory ranking; search branches do not equal committed state; and verification has four verdicts rather than a boolean success flag.

## 11 — Integration, not a new mechanism

`11-chapter.ipynb` imports `AgentApplication` and assembles the already-earned system against the controlled broken-parser repair task:

```text
controlled broken repository
→ isolated workspace + state identity
→ reproduce failure before diagnosis
→ inspect through an eligible capability
→ generate/select complete repair alternatives
→ critique and conditionally revise
→ compare isolated partial trajectories
→ authorize and commit one mutation
→ inspect the committed diff
→ rerun targeted and full tests
→ collect evidence after the final mutation
→ bind evidence to the committed state
→ protected adjudication
→ VERIFIED_SUCCESS
```

The capstone also demonstrates verified memory on a later run and two adversarial verification surfaces: protected-test tampering and the Windows/POSIX repository-path canonicalisation regression described in Chapter 11.

The **nine integration findings** are reproduced in the Chapter 11 notebook because they are the actual result of composition: several naming/type/policy collisions required correction, memory/search required an explicit budget assumption, branch evidence held because state identity already matched, and path identity exposed a real verifier bug.

## Contract

- Keep notebook files under `/notebooks/agents-from-first-principles/`, not under Hugo `content/`.
- Keep shared implementation under `/demo/agents-from-first-principles/first_principles_agent/`.
- Do not copy agent implementation into notebook cells; notebook-local code should be experiment setup, controls, assertions, and diagnostics.
- When the book and notebook explanation diverge, update the notebook to the current book claim while preserving valid earlier experiments.
- Keep book chapter number and internal demo stage explicit; do not use one as if it were the other.
- Use deterministic or recorded model fixtures so mechanism experiments remain reproducible without a live API.
- Chapter 11 / Stage 10 is integration only: wiring and regression controls are allowed; new conceptual agent mechanisms are not.
