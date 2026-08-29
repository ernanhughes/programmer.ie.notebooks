from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

from .state import AgentState


@dataclass(frozen=True)
class Candidate:
    """A complete proposal considered at one decision point.

    Stage 02 treats candidates as complete alternatives. They are data, not
    executable authority. Later stages may turn a selected candidate into a
    revision, plan, or action, but this module owns only generation,
    evaluation, and selection.
    """

    id: str
    action: str
    patch: str
    rationale: str
    accepted_by_stage01: bool = True

    @property
    def diversity_key(self) -> str:
        return self.patch


@dataclass(frozen=True)
class CandidateSet:
    candidates: tuple[Candidate, ...]

    def __post_init__(self) -> None:
        if not self.candidates:
            raise ValueError("candidate set cannot be empty")
        ids = [candidate.id for candidate in self.candidates]
        if len(ids) != len(set(ids)):
            raise ValueError("candidate ids must be unique")

    @classmethod
    def from_iterable(cls, candidates: list[Candidate] | tuple[Candidate, ...]) -> "CandidateSet":
        return cls(tuple(candidates))

    @property
    def eligible(self) -> tuple[Candidate, ...]:
        return tuple(
            candidate
            for candidate in self.candidates
            if candidate.accepted_by_stage01
        )

    @property
    def diversity_count(self) -> int:
        return len({candidate.diversity_key for candidate in self.eligible})


class CandidateGenerator(Protocol):
    def generate(self, state: AgentState | None = None) -> CandidateSet: ...


class CandidateEvaluator(Protocol):
    def score(
        self,
        candidate: Candidate,
        state: AgentState | None = None,
    ) -> float: ...


@dataclass(frozen=True)
class FixedCandidateGenerator:
    """Deterministic generator used by the book's controlled experiments."""

    candidate_set: CandidateSet

    def generate(self, state: AgentState | None = None) -> CandidateSet:
        del state
        return self.candidate_set


@dataclass(frozen=True)
class FunctionCandidateEvaluator:
    """Small adapter that keeps evaluator behaviour independently testable."""

    function: Callable[[Candidate], float]

    def score(
        self,
        candidate: Candidate,
        state: AgentState | None = None,
    ) -> float:
        del state
        return float(self.function(candidate))


@dataclass(frozen=True)
class SelectedCandidate:
    candidate: Candidate
    score: float


class CandidateSelector:
    """Select one complete eligible candidate using an explicit evaluator."""

    def __init__(self, evaluator: CandidateEvaluator) -> None:
        self.evaluator = evaluator

    def select_complete(
        self,
        candidates: CandidateSet,
        state: AgentState | None = None,
    ) -> SelectedCandidate:
        eligible = candidates.eligible
        if not eligible:
            raise ValueError("no Stage-01-eligible candidates are available")

        scored = [
            SelectedCandidate(
                candidate=candidate,
                score=self.evaluator.score(candidate, state),
            )
            for candidate in eligible
        ]
        return max(scored, key=lambda item: item.score)


@dataclass(frozen=True)
class CandidateSelectionMetrics:
    oracle_at_n: int
    selected_success_at_n: int
    selection_gap_at_n: int
    selected_id: str
    eligible_count: int
    diversity_count: int

    def as_dict(self) -> dict[str, int | str]:
        return {
            "oracle@N": self.oracle_at_n,
            "selected_success@N": self.selected_success_at_n,
            "selection_gap@N": self.selection_gap_at_n,
            "selected_id": self.selected_id,
            "eligible_count": self.eligible_count,
            "diversity_count": self.diversity_count,
        }


def measure_selection(
    candidates: CandidateSet,
    selected: SelectedCandidate,
    success_criterion: Callable[[Candidate], bool],
) -> CandidateSelectionMetrics:
    eligible = candidates.eligible
    oracle = int(any(success_criterion(candidate) for candidate in eligible))
    selected_success = int(success_criterion(selected.candidate))

    return CandidateSelectionMetrics(
        oracle_at_n=oracle,
        selected_success_at_n=selected_success,
        selection_gap_at_n=oracle - selected_success,
        selected_id=selected.candidate.id,
        eligible_count=len(eligible),
        diversity_count=candidates.diversity_count,
    )
