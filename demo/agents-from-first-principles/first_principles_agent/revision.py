from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

from .candidates import Candidate


@dataclass(frozen=True)
class EvidenceSet:
    """Small immutable evidence bundle for one revision decision.

    Stage 03 only needs enough structure to keep critique/revision experiments
    explicit. Rich evidence provenance belongs to Stage 09.
    """

    items: tuple[str, ...] = ()

    @classmethod
    def from_iterable(cls, items: list[str] | tuple[str, ...]) -> "EvidenceSet":
        return cls(tuple(items))


@dataclass(frozen=True)
class Critique:
    """A defect hypothesis about one current candidate."""

    defect: str
    evidence: tuple[str, ...]
    target: str


class Critic(Protocol):
    def critique(self, candidate: Candidate, evidence: EvidenceSet) -> Critique: ...


class Reviser(Protocol):
    def revise(self, candidate: Candidate, critique: Critique) -> Candidate: ...


@dataclass(frozen=True)
class FixedCritic:
    """Deterministic critic used by controlled book experiments."""

    result: Critique

    def critique(self, candidate: Candidate, evidence: EvidenceSet) -> Critique:
        del candidate, evidence
        return self.result


@dataclass(frozen=True)
class FunctionReviser:
    """Adapter that keeps revision behaviour independently testable."""

    function: Callable[[Candidate, Critique], Candidate]

    def revise(self, candidate: Candidate, critique: Critique) -> Candidate:
        return self.function(candidate, critique)


ValueFunction = Callable[[Candidate, EvidenceSet], float]
AdherenceCheck = Callable[[Candidate, Critique], bool]
IntegrityCheck = Callable[[Candidate, EvidenceSet], str | None]


@dataclass(frozen=True)
class RevisionDecision:
    """Result of comparing one proposed revision with the current candidate."""

    old: Candidate
    critique: Critique
    proposed: Candidate
    resulting: Candidate
    accepted: bool
    reason: str
    old_score: float
    proposed_score: float
    value_delta: float
    revision_adherence: bool
    integrity_violation: str | None = None

    @property
    def rolled_back(self) -> bool:
        return not self.accepted and self.resulting == self.old


class RevisionGate:
    """Accept or roll back one targeted revision.

    The gate does not decide whether the critique was true. Critic quality is
    measured separately in controlled experiments. The gate asks only whether
    the proposed intervention adheres to the stated target, respects protected
    constraints, and improves the configured task-value signal.
    """

    def __init__(
        self,
        *,
        value_function: ValueFunction,
        adherence_check: AdherenceCheck,
        integrity_check: IntegrityCheck | None = None,
    ) -> None:
        self.value_function = value_function
        self.adherence_check = adherence_check
        self.integrity_check = integrity_check or (lambda candidate, evidence: None)

    def evaluate(
        self,
        old: Candidate,
        critique: Critique,
        revised: Candidate,
        evidence: EvidenceSet,
    ) -> RevisionDecision:
        old_score = float(self.value_function(old, evidence))
        proposed_score = float(self.value_function(revised, evidence))
        value_delta = proposed_score - old_score
        adherence = bool(self.adherence_check(revised, critique))
        integrity_violation = self.integrity_check(revised, evidence)

        if integrity_violation is not None:
            return self._reject(
                old=old,
                critique=critique,
                revised=revised,
                old_score=old_score,
                proposed_score=proposed_score,
                value_delta=value_delta,
                adherence=adherence,
                reason=f"revision violates protected constraint: {integrity_violation}",
                integrity_violation=integrity_violation,
            )

        if not adherence:
            return self._reject(
                old=old,
                critique=critique,
                revised=revised,
                old_score=old_score,
                proposed_score=proposed_score,
                value_delta=value_delta,
                adherence=False,
                reason="revision does not address the critique target",
            )

        if value_delta <= 0:
            return self._reject(
                old=old,
                critique=critique,
                revised=revised,
                old_score=old_score,
                proposed_score=proposed_score,
                value_delta=value_delta,
                adherence=True,
                reason="targeted revision did not improve measured task value",
            )

        return RevisionDecision(
            old=old,
            critique=critique,
            proposed=revised,
            resulting=revised,
            accepted=True,
            reason="targeted revision improved measured task value",
            old_score=old_score,
            proposed_score=proposed_score,
            value_delta=value_delta,
            revision_adherence=True,
        )

    @staticmethod
    def _reject(
        *,
        old: Candidate,
        critique: Critique,
        revised: Candidate,
        old_score: float,
        proposed_score: float,
        value_delta: float,
        adherence: bool,
        reason: str,
        integrity_violation: str | None = None,
    ) -> RevisionDecision:
        return RevisionDecision(
            old=old,
            critique=critique,
            proposed=revised,
            resulting=old,
            accepted=False,
            reason=reason,
            old_score=old_score,
            proposed_score=proposed_score,
            value_delta=value_delta,
            revision_adherence=adherence,
            integrity_violation=integrity_violation,
        )


@dataclass(frozen=True)
class RevisionDiagnostics:
    """Ground-truth diagnostics used only for controlled evaluation."""

    critic_quality: bool
    revision_adherence: bool
    revision_value: float
    acceptance_quality: bool

    def as_dict(self) -> dict[str, bool | float]:
        return {
            "critic_quality": self.critic_quality,
            "revision_adherence": self.revision_adherence,
            "revision_value": self.revision_value,
            "acceptance_quality": self.acceptance_quality,
        }


def measure_revision(
    decision: RevisionDecision,
    *,
    expected_defect: str,
    should_accept: bool,
) -> RevisionDiagnostics:
    """Measure independent failure surfaces against experiment ground truth."""

    return RevisionDiagnostics(
        critic_quality=decision.critique.defect == expected_defect,
        revision_adherence=decision.revision_adherence,
        revision_value=decision.value_delta,
        acceptance_quality=decision.accepted is should_accept,
    )


def refine_once(
    candidate: Candidate,
    *,
    critic: Critic,
    reviser: Reviser,
    gate: RevisionGate,
    evidence: EvidenceSet,
) -> RevisionDecision:
    """Perform exactly one critique -> revision -> acceptance experiment."""

    critique = critic.critique(candidate, evidence)
    revised = reviser.revise(candidate, critique)
    return gate.evaluate(candidate, critique, revised, evidence)
