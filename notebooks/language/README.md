# Language — Chapter Notebooks

This directory contains one executable teaching notebook per chapter of
*Language: When Intelligence Enters the Channel*:

- `01-chapter.ipynb` through `37-chapter.ipynb` — one primary notebook per chapter
- `_support.py` — shared helpers for repository-root resolution and fixtures
- `fixtures/language-fixtures.json` — deterministic, constructed fixtures used by the notebooks
- `../../scripts/validate_language_notebooks.py` — offline validator

## Running

From the repository root (`C:\Projects\language`):

```powershell
python -m jupyter lab notebooks/books/language
```

Then choose a notebook and use **Run All**. Notebooks are designed to run
offline. They resolve the repository root by walking parent directories for
`content/books/language/_index.md`; they do not require a fixed working directory.

Core dependencies are the repository's existing Python environment plus
`matplotlib` for visualizations and `nbformat`/`nbclient` for validation. No
notebook downloads models, calls remote services, installs packages, or modifies
book chapters or frozen experiments.

## Notebook conventions

Each notebook follows the Retrieval book's notebook conventions:

1. Resolve the repository root through `_support.repo_root()`.
2. Load deterministic fixtures from `fixtures/language-fixtures.json`.
3. Present a minimal executable example of the chapter's mechanism.
4. Run one or more experiments with parameters that can be changed.
5. Show clearly labelled results (actual measurement / deterministic simulation / synthetic demonstration).
6. State observed versus not established.
7. Offer a "Try it yourself" exercise.
8. Link back to the relevant book chapter and sections.

Every notebook has exactly one clear experimental or educational purpose.
Notebooks are not abbreviated versions of the chapters; they are practical
companions that demonstrate the mechanisms, experiments and applications
discussed in the book.

## Optional features

Some notebooks include clearly identified optional model-backed extensions.
These are disabled by default and skip gracefully when prerequisites are absent.
No paid inference is triggered during normal Run All.

## Validation

```powershell
python scripts/validate_language_notebooks.py --timeout 120
```

This checks all 37 files, validates notebook structure, executes every notebook
in a fresh kernel, and reports PASS/FAIL per notebook.

## Provenance and boundaries

Toy and constructed examples are labelled as such. Reused frozen data is read
only and its provenance is stated in the notebook. Notebooks do not establish
production security, independent replication, human helpfulness, or universal
performance. Negative and bounded findings from the book are preserved, not
rewritten. Simulations are labelled as simulations, not as measurements.
