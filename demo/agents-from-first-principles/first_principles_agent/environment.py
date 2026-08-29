from __future__ import annotations

import ast
import difflib
import subprocess
import sys
from pathlib import Path

from .actions import Action, ActionKind, Observation


class RepositoryEnvironment:
    """Small real environment for the capstone repository.

    The environment executes only typed actions that already crossed the
    acceptance boundary. Stage 10 adds concrete mutation/diff/test operations
    without widening the security boundary: protected paths remain denied by
    ActionAcceptanceBoundary.
    """

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self._baseline_text = self._text_files()

    def execute(self, action: Action) -> Observation:
        if action.kind == ActionKind.RUN_TESTS:
            return self._run_tests()
        if action.kind == ActionKind.RUN_TARGETED_TESTS:
            if action.target is None:
                raise ValueError("RUN_TARGETED_TESTS requires a target")
            return self._run_tests(action.target)
        if action.kind == ActionKind.READ_FILE:
            if action.target is None:
                raise ValueError("READ_FILE requires a target")
            return self._read_file(action.target)
        if action.kind == ActionKind.SEARCH_CODE:
            if action.target is None:
                raise ValueError("SEARCH_CODE requires a query")
            return self._search_code(action.target)
        if action.kind == ActionKind.FIND_SYMBOL:
            if action.target is None:
                raise ValueError("FIND_SYMBOL requires a symbol")
            return self._find_symbol(action.target)
        if action.kind == ActionKind.APPLY_PATCH:
            if action.target is None or action.content is None:
                raise ValueError("APPLY_PATCH requires target and replacement content")
            return self._apply_patch(action.target, action.content)
        if action.kind == ActionKind.INSPECT_DIFF:
            return self._inspect_diff()
        raise ValueError(f"environment cannot execute {action.kind.value}")

    def _run_tests(self, target: str | None = None) -> Observation:
        command = [sys.executable, "-m", "pytest", "-q"]
        if target is not None:
            command.append(target)
        completed = subprocess.run(
            command,
            cwd=self.root,
            capture_output=True,
            text=True,
            check=False,
        )
        details = (completed.stdout + completed.stderr).strip()
        return Observation(
            source="pytest" if target is None else f"pytest:{target}",
            ok=completed.returncode == 0,
            summary="tests passed" if completed.returncode == 0 else "tests failed",
            details=details,
            data={
                "returncode": completed.returncode,
                "output": details,
                "target": target,
            },
        )

    def _read_file(self, relative_path: str) -> Observation:
        candidate = (self.root / relative_path).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise ValueError("path escapes repository root") from exc

        text = candidate.read_text(encoding="utf-8")
        return Observation(
            source=relative_path,
            ok=True,
            summary=f"read {relative_path}",
            details=text,
            data={"path": relative_path, "content": text},
        )

    def _apply_patch(self, relative_path: str, replacement_content: str) -> Observation:
        candidate = (self.root / relative_path).resolve()
        previous = candidate.read_text(encoding="utf-8")
        candidate.write_text(replacement_content, encoding="utf-8")
        changed = previous != replacement_content
        return Observation(
            source=relative_path,
            ok=changed,
            summary=(f"updated {relative_path}" if changed else f"no change to {relative_path}"),
            details=replacement_content,
            data={"path": relative_path, "changed": changed},
        )

    def _inspect_diff(self) -> Observation:
        current = self._text_files()
        changed_paths = sorted(set(self._baseline_text) | set(current))
        changed_paths = [
            path for path in changed_paths if self._baseline_text.get(path) != current.get(path)
        ]
        chunks: list[str] = []
        for path in changed_paths:
            before = self._baseline_text.get(path, "").splitlines(keepends=True)
            after = current.get(path, "").splitlines(keepends=True)
            chunks.extend(
                difflib.unified_diff(
                    before,
                    after,
                    fromfile=f"a/{path}",
                    tofile=f"b/{path}",
                )
            )
        diff = "".join(chunks)
        return Observation(
            source="workspace_diff",
            ok=bool(changed_paths),
            summary=f"{len(changed_paths)} changed paths",
            details=diff,
            data={"changed_paths": changed_paths, "diff": diff},
        )

    def _text_files(self) -> dict[str, str]:
        result: dict[str, str] = {}
        for path in sorted(self.root.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(self.root)
            if any(part in {".git", ".pytest_cache", ".venv", "venv", "__pycache__"} for part in relative.parts):
                continue
            try:
                result[str(relative)] = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
        return result

    def _python_files(self):
        for path in sorted(self.root.rglob("*.py")):
            relative = path.relative_to(self.root)
            if any(part in {".git", ".venv", "venv", "__pycache__"} for part in relative.parts):
                continue
            yield path, relative

    def _search_code(self, query: str) -> Observation:
        needle = query.lower()
        matches: list[dict[str, object]] = []
        for path, relative in self._python_files():
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except UnicodeDecodeError:
                continue
            for line_number, line in enumerate(lines, start=1):
                if needle in line.lower():
                    matches.append({"path": str(relative), "line": line_number, "text": line.strip()})
                    if len(matches) >= 50:
                        break
            if len(matches) >= 50:
                break
        return Observation(
            source="search_code",
            ok=bool(matches),
            summary=f"found {len(matches)} code matches for {query!r}",
            details="\n".join(f"{item['path']}:{item['line']}: {item['text']}" for item in matches),
            data={"query": query, "matches": matches},
        )

    def _find_symbol(self, symbol: str) -> Observation:
        locations: list[dict[str, object]] = []
        for path, relative in self._python_files():
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except (SyntaxError, UnicodeDecodeError):
                continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == symbol:
                    locations.append({"path": str(relative), "line": node.lineno, "kind": type(node).__name__})
        return Observation(
            source="find_symbol",
            ok=bool(locations),
            summary=f"found {len(locations)} definitions for {symbol!r}",
            details="\n".join(f"{item['path']}:{item['line']} ({item['kind']})" for item in locations),
            data={"symbol": symbol, "locations": locations},
        )
