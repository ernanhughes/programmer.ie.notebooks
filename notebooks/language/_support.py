"""Shared helpers for the Language chapter notebooks.

The notebooks are offline and deterministic.  This module resolves the
repository root by walking parent directories from the current working
directory, looking for the marker used by the Language book's content tree.

Notebooks import this module from their own directory, exactly as the
Retrieval book notebooks import ``_support``.
"""

from pathlib import Path
import sys

MARKER = Path("content") / "books" / "language" / "_index.md"


def repo_root(start=None):
    """Return the repository root containing content/books/language/_index.md."""
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

# Deterministic fixtures and generated output locations, all local.
FIXTURES = ROOT / "notebooks" / "books" / "language" / "fixtures"
OUTPUTS = ROOT / ".artifacts" / "language-notebooks" / "outputs"


def try_import(name):
    """Import an optional dependency; return None when it is unavailable."""
    try:
        return __import__(name)
    except Exception:
        return None


def chapter_path(n):
    """Return the source chapter Markdown path for chapter number n."""
    return ROOT / "content" / "books" / "language" / f"{n:02d}-chapter.md"


def chapter_title(n):
    """Read the Hugo title front matter for chapter number n."""
    path = chapter_path(n)
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.strip().startswith("title ="):
            return line.split('"')[1]
    raise RuntimeError(f"title not found for chapter {n:02d}")
