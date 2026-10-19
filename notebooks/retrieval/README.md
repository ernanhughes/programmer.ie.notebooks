# Retrieval From First Principles — Chapter Notebooks

This directory contains one executable teaching notebook per chapter:

- `01-chapter.ipynb` through `30-chapter.ipynb`
- `_support.py` — small shared helpers for repository-root resolution and metrics
- `../../scripts/validate_retrieval_notebooks.py` — offline validator

## Running

From the repository root:

```powershell
python -m jupyter lab notebooks/books/retrieval
```

Then choose a notebook and use **Run All**. Notebooks are designed to run offline. They resolve the repository root by walking parent directories for `content/books/retrieval/_index.md`; they do not require a fixed working directory.

Core dependencies are the repository's existing Python environment plus `nbformat` and `nbclient` for validation. No notebook downloads models, calls remote services, installs packages, or modifies book chapters or frozen experiments.

## Optional features

- Some notebooks inspect retained consumer outputs only if `experiments/part6-system/final/calls` exists. This is read-only.
- Notebook 30 can invoke the checked Pi adapter only when `RETRIEVAL_RUN_PI_CAPSTONE=1` is set. It is disabled by default. The book did not run a model-directed Pi turn; tool delivery is not model use.
- Optional model-backed cells, where present, are guarded and skip gracefully if prerequisites are absent.

## Provenance and boundaries

Toy and constructed examples are labelled as such. Reused frozen data is read only and its provenance is stated in the notebook. Notebooks do not establish production security, independent replication, semantic answer correctness, causal evidence use, human helpfulness, or universal performance. Negative and bounded findings from the book are preserved, not rewritten.

## Validation

```powershell
python scripts/validate_retrieval_notebooks.py --timeout 120
```

This checks all 30 files, validates notebook structure, executes every notebook in a fresh kernel, and reports PASS/FAIL per notebook.