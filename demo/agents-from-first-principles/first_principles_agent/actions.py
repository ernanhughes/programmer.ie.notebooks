from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ActionKind(str, Enum):
    RUN_TESTS = "run_tests"
    RUN_TARGETED_TESTS = "run_targeted_tests"
    READ_FILE = "read_file"
    SEARCH_CODE = "search_code"
    FIND_SYMBOL = "find_symbol"
    APPLY_PATCH = "apply_patch"
    INSPECT_DIFF = "inspect_diff"
    STOP = "stop"


@dataclass(frozen=True)
class RawProposal:
    """Untrusted policy/model output before the execution boundary."""

    text: str


@dataclass(frozen=True)
class Action:
    """Typed action that has crossed the relevant acceptance boundary."""

    kind: ActionKind
    target: str | None = None
    reason: str | None = None
    content: str | None = None


@dataclass(frozen=True)
class Observation:
    source: str
    ok: bool
    summary: str
    details: str = ""
    data: dict[str, object] = field(default_factory=dict)
