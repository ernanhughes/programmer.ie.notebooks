"""Shared helpers for the Retrieval from First Principles notebooks.

The notebooks are offline and deterministic.  This module resolves the
repository root by walking parent directories from the current working
directory, looking for the marker used by the book's content tree.
"""

from pathlib import Path
import sys

MARKER = Path("content") / "books" / "retrieval" / "_index.md"


def repo_root(start=None):
    """Return the repository root containing content/books/retrieval/_index.md."""
    if start is None:
        start = Path.cwd()
    start = Path(start).resolve()
    for candidate in (start, *start.parents):
        if (candidate / MARKER).is_file():
            return candidate
    raise FileNotFoundError(
        "Could not find %s while walking parents from %s" % (MARKER, start)
    )


def add_to_sys_path(path):
    resolved = str(Path(path).resolve())
    if resolved not in sys.path:
        sys.path.insert(0, resolved)


# Notebooks import this module from their own directory.
add_to_sys_path(Path(__file__).resolve().parent)

ROOT = repo_root()
EXAMPLES = ROOT / "examples"
add_to_sys_path(EXAMPLES)


def try_import(name):
    """Import an optional dependency; return None when it is unavailable."""
    try:
        return __import__(name)
    except Exception:
        return None
