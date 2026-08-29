# Agents From First Principles — Demo

This directory contains the runnable capstone application for **Agents From First Principles**.

The book earned one mechanism at a time; Stage 10 now assembles them without introducing another conceptual subsystem.

## Completed causal spine

```text
00  adaptive control
01  explicit action acceptance
02  complete candidate generation / selection
03  critique, targeted revision and rollback
04  planning as explicit intended future work
05  runtime state, progress and named continuation
06  capability contracts and action-space design
07  controlled memory lifecycle
08  isolated prefix-level trajectory search
09  evidence-backed verification and integrity
10  integration only
```

The cumulative boundaries remain:

```text
proposal        ≠ execution authority
plan            ≠ runtime state
activity        ≠ progress
exposure        ≠ authorization
retrieved       ≠ used
complete choice ≠ partial-trajectory search
tool PASS       ≠ verified goal success
```

## Complete local repair agent

The integrated application is in:

```text
first_principles_agent/app.py
```

Run it from this directory:

```bash
python -m pip install -e ".[test]"
python -m first_principles_agent \
    --repo examples/broken-parser \
    --task "Fix pipe-delimited records"
```

The CLI defaults to Stage 10. `--stage 00` and `--stage 01` remain available for the earlier controlled demonstrations.

The Stage-10 run performs:

```text
user task
→ immutable goal contract
→ isolated copy of the broken repository
→ real targeted pytest failure reproduction
→ constrained parser inspection
→ complete repair candidate generation / selection
→ targeted critique and revision
→ structured plan
→ runtime progress accounting
→ controlled memory read/write
→ isolated prefix-level repair search
→ one Stage-01-authorized parser mutation
→ real diff inspection
→ real targeted pytest
→ real full pytest suite
→ evidence bound to final workspace identity
→ protected integrity checks
→ PASS / FAIL / PARTIAL / UNKNOWN
```

A successful controlled run returns `VERIFIED_SUCCESS` only when the Stage-09 adjudicator returns `PASS`.

## Mutation boundary

Stage 10 adds concrete actions already earned by the action/capability chapters:

```text
run_targeted_tests
apply_patch
inspect_diff
```

`apply_patch` still crosses the Stage-01 acceptance boundary. It may modify source inside the isolated workspace but is explicitly denied access to:

```text
tests/
.git/
```

The original broken repository is not modified.

## Real reward-hacking control

`run_protected_test_tampering_control(...)` is an **external adversarial evaluation fixture**, not an action available to the normal agent.

It deliberately removes the protected pipe test and runs the real remaining suite:

```text
broken implementation remains
→ protected pipe test removed externally
→ pytest reports green
→ naive checker = PASS
→ protected-path integrity = VIOLATED
→ final verifier = FAIL
```

This proves that a green task checker cannot launder evaluation tampering into verified success.

## Deterministic model mode

The default capstone uses `RecordedRepairModel`. This keeps the core experiment reproducible and separates:

```text
runtime mechanism quality
from
current live-model quality
```

A live model adapter can be added later without changing the architecture.

## Memory across runs

Pass the same `MemoryStore` to multiple `AgentApplication` runs and the later run can use a verified stored project fact (the targeted test identity). The first run still succeeds without memory, so memory remains an optional causal improvement rather than a hidden correctness dependency.

## Run tests

From this directory:

```bash
python -m pip install -e ".[test]"
python -m pytest -q
```

The deliberately broken target is tested separately from its own directory:

```bash
python -m pytest tests/test_parser.py -q
```

Before repair, the expected target baseline is one passing comma test and one failing pipe-delimiter test.

## Repository structure

```text
demo/agents-from-first-principles/
├── first_principles_agent/
│   ├── acceptance.py
│   ├── actions.py
│   ├── agent.py
│   ├── app.py
│   ├── candidates.py
│   ├── capabilities.py
│   ├── environment.py
│   ├── memory.py
│   ├── planning.py
│   ├── policy.py
│   ├── revision.py
│   ├── runtime.py
│   ├── search.py
│   ├── state.py
│   └── verification.py
├── examples/
│   └── broken-parser/
├── tests/
│   ├── test_stage00_control_loop.py
│   ├── ...
│   └── test_stage10_integration.py
├── pyproject.toml
└── README.md
```

All notebooks 00–10 now exercise the same reusable implementation under this directory.
