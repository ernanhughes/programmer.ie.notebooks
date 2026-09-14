# Applied AI — Notebook Companions

Executable companions to the book **Applied AI**. Each notebook backs up its
chapter: the chapter makes the argument, the notebook makes the mechanism
visible.

## Setup

```bash
pip install -r requirements.txt
jupyter lab
```

No API key is required. Every notebook runs locally with deterministic mocks,
seeded simulations, or tiny synthetic datasets. A few notebooks include a
clearly marked *optional* live-model cell, but the lesson never depends on it.

All notebooks use `SEED = 42` where randomness appears, run top-to-bottom
from a fresh kernel, and label synthetic evidence as synthetic.

## Index

| Chapter | Notebook | Executable question | Live API required? |
| ------- | -------- | ------------------- | ------------------ |
| 01 Beyond the Chat Box | `01-chapter.ipynb` | What changes when a model call becomes a recorded operation? | No |
| 02 Never Stand in Front of the Steamroller | `02-chapter.ipynb` | Where does my own work sit: codified routine or tacit judgment? | No |
| 03 If There's Any Doubt, It's Deterministic | `03-chapter.ipynb` | Which operations genuinely need stochasticity? | No |
| 04 Scrum Built the Training Set | `04-chapter.ipynb` | What does a verifier buy you when candidates are cheap and noisy? | No |
| 05 Meat Proxy | `05-chapter.ipynb` | How does review effectiveness decay as inspection effort falls? | No |
| 06 The Price of Intelligence | `06-chapter.ipynb` | How quickly does per-call cost become material at production scale? | No |
| 07 Intelligence in the Wrong Direction | `07-chapter.ipynb` | How to distinguish apparent improvement from statistical noise? | No |
| 08 Where Are the Finished Projects? | `08-chapter.ipynb` | How much does Amdahl's law constrain a coding speedup? | No |
| 09 One Runtime, Many Windows | `09-chapter.ipynb` | What breaks when state lives in the interface? | No |
| 10 A Revolver, Not a Foundation | `10-chapter.ipynb` | Can one model win a chamber and lose the next? | No |
| 11 The Smallest Useful Model Call | `11-chapter.ipynb` | What changes when a call becomes a recorded operation? | No |
| 12 One Operation, Several Model APIs | `12-chapter.ipynb` | Can one operation survive three different provider dialects? | No |
| 13 Normalize at the Boundary | `13-chapter.ipynb` | What breaks when usage fields with different meanings are merged? | No |
| 14 The Model Is Not the Process | `14-chapter.ipynb` | Can the process restart honestly after a crash? | No |
| 15 Context Is an Input, Not a Transcript | `15-chapter.ipynb` | Can we compile bounded, inspectable context instead of forwarding transcripts? | No |
| 16 Externalize Working Memory | `16-chapter.ipynb` | Why is working state in variables insufficient? | No |
| 17 Raw Output First | `17-chapter.ipynb` | Why must the observation outlive its interpretation? | No |
| 18 Claims, Evidence, and Decisions | `18-chapter.ipynb` | Why should decisions depend on evidence state, not confident prose? | No |
| 19 Let the Machine Touch Something | `19-chapter.ipynb` | How do we know the written file is the file on disk? | No |
| 20 Capability Is Not Authority | `20-chapter.ipynb` | Does possessing a function confer permission to invoke it? | No |
| 21 The Agent Cannot Grade Its Own Homework | `21-chapter.ipynb` | Does generator–judge agreement count as evidence of correctness? | No |
| 22 Retries Are Side Effects Too | `22-chapter.ipynb` | What happens when a completed-but-timed-out effect is retried? | No |
| 23 Independent Calls | `23-chapter.ipynb` | Does issuing several calls make results independent? | No |
| 24 The Models Were Different. Their Mistakes Weren't | `24-chapter.ipynb` | Does nominal model diversity produce effective diversity? | No |
| 25 Make the Problems Harder | `25-chapter.ipynb` | Why does an evaluation everyone passes tell you nothing? | No |
| 26 Diversity Without More Models | `26-chapter.ipynb` | Can one base capability diversify itself — and how would we know? | No |
| 27 Replicate Before You Believe | `27-chapter.ipynb` | What does a matched replication do to an exciting result? | No |
| 28 What Should Happen Next? | `28-chapter.ipynb` | Can routing stay deterministic, with no model call? | No |
| 29 Applied AI | `29-chapter.ipynb` | Does the whole machine hold together in miniature? | No |

No chapter was deliberately omitted: every chapter supported a meaningful
executable question, so every chapter has a notebook.

## Notes for the separate repository

- Notebooks are self-contained: standard library plus `numpy`, `pandas`,
  `matplotlib` (see `requirements.txt`). No imports from the book repository,
  no private packages, no absolute paths, no private data.
- File writes are confined to temporary directories; the SQLite ledgers in
  chapters 09 and 16 use `:memory:` or temp files cleaned up by the notebook.
- Outputs checked in are the result of a fresh-kernel top-to-bottom run;
  plots and compact tables are kept, debug noise removed.
