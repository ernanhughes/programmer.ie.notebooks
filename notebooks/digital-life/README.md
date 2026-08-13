# Digital Life Notebooks

These notebooks are executable companions to **Digital Life: From First Principles**. They sit between the book chapters and the research scripts: the chapters provide the question and bounded claim, the scripts preserve raw experiment history, and the notebooks curate the experimental argument into runnable form.

Run from this directory with Jupyter, VS Code, or:

```bash
jupyter nbconvert --to notebook --execute 03-the-first-surprise.ipynb --inplace
```

The first batch uses Python 3 with `numpy`, `matplotlib`, and, for Chapter 01's Lenia-style continuous CA, `scipy`. GIF creation in source scripts uses Pillow, but these notebooks focus on inline reproducible figures and measurements rather than rebuilding every animation frame.

Randomness is exposed through explicit `EXPERIMENT` dictionaries. The notebooks do not `%run` the research scripts; central mechanisms, interventions, measurements, and controls are visible in the notebook cells. Where a book figure is conceptual or came from browser capture, the provenance section says so instead of pretending it was recomputed from hidden state.

Regenerated notebook figures are written to `notebooks/generated-figures/` so executing the notebooks does not overwrite the book's checked-in static images.

Chapters 07-13 add `pandas` and `tqdm` for the optional/heavier Outlier analysis path used by the research scripts. The Chapter 13 notebook can validate the canonical manuscript-scale run from `data/digital-life/outlier.sqlite3` when that SQLite specimen exists; otherwise it runs the core causal mechanism on a small example and prints the rebuild path for the canonical pipeline.
