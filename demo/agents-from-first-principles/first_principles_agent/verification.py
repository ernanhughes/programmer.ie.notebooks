from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from typing import Iterable


def _canonical_repo_path(path: str) -> str:
    """Use one platform-independent namespace for repository-relative paths."""

    return path.replace("\\", "/")


def _canonical_files(files: dict[str, str]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for path, content in files.items():
        canonical = _canonical_repo_path(path)
        existing = normalized.get(canonical)
        if existing is not None and existing != content:
            raise ValueError(
                f"conflicting contents for canonical repository path: {canonical}"
            )
        normalized[canonical] = content
    return normalized


class Verdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    PARTIAL = "PARTIAL"
    UNKNOWN = "UNKNOWN"


class EvidenceLayer(str, Enum):
    ACTION_RECEIPT = "action_receipt"
    STATE_TRANSITION = "state_transition"
    GOAL_SATISFACTION = "goal_satisfaction"
    EVALUATION_INTEGRITY = "evaluation_integrity"


class IntegrityStatus(str, Enum):
    CLEAN = "CLEAN"
    VIOLATED = "VIOLATED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class GoalContract:
    """Immutable definition of what must be earned before success is claimed."""

    must_change: tuple[str, ...] = ()
    must_preserve: tuple[str, ...] = ()
    must_not: tuple[str, ...] = ()

    @property
    def required_criteria(self) -> tuple[str, ...]:
        return self.must_change + self.must_preserve

    @property
    def fingerprint(self) -> str:
        payload = (self.must_change, self.must_preserve, self.must_not)
        return sha256(repr(payload).encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class StateIdentity:
    value: str

    @classmethod
    def from_files(cls, files: dict[str, str]) -> "StateIdentity":
        payload = tuple(sorted(_canonical_files(files).items()))
        digest = sha256(repr(payload).encode("utf-8")).hexdigest()[:16]
        return cls(digest)


@dataclass(frozen=True)
class WorkspaceSnapshot:
    files: tuple[tuple[str, str], ...]

    @classmethod
    def from_mapping(cls, files: dict[str, str]) -> "WorkspaceSnapshot":
        return cls(tuple(sorted(_canonical_files(files).items())))

    @property
    def state_id(self) -> StateIdentity:
        return StateIdentity.from_files(dict(self.files))

    def as_dict(self) -> dict[str, str]:
        return dict(self.files)


@dataclass(frozen=True)
class EvidenceRecord:
    id: str
    criterion: str
    layer: EvidenceLayer
    source: str
    state_id: StateIdentity
    collected_at: int
    verifier_version: str
    contract_fingerprint: str
    verdict: Verdict
    payload: tuple[tuple[str, str], ...] = ()
    integrity_tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class EvidenceSet:
    records: tuple[EvidenceRecord, ...] = ()

    def add(self, record: EvidenceRecord) -> "EvidenceSet":
        return EvidenceSet(self.records + (record,))

    def current_for(
        self,
        *,
        state_id: StateIdentity,
        contract: GoalContract,
    ) -> tuple[EvidenceRecord, ...]:
        return tuple(
            record
            for record in self.records
            if record.state_id == state_id
            and record.contract_fingerprint == contract.fingerprint
        )

    def stale_for(
        self,
        *,
        state_id: StateIdentity,
        contract: GoalContract,
    ) -> tuple[EvidenceRecord, ...]:
        return tuple(
            record
            for record in self.records
            if record.contract_fingerprint == contract.fingerprint
            and record.state_id != state_id
        )


# Keep the package-level name distinct from Stage-03 revision.EvidenceSet.
VerificationEvidenceSet = EvidenceSet


class EvidenceCollector:
    """Create evidence records bound to the exact state and goal contract."""

    def __init__(self, *, verifier_version: str = "v1") -> None:
        self.verifier_version = verifier_version

    def collect(
        self,
        *,
        evidence_id: str,
        criterion: str,
        layer: EvidenceLayer,
        source: str,
        state_id: StateIdentity,
        contract: GoalContract,
        verdict: Verdict,
        collected_at: int,
        payload: dict[str, str] | None = None,
        integrity_tags: Iterable[str] = (),
    ) -> EvidenceRecord:
        return EvidenceRecord(
            id=evidence_id,
            criterion=criterion,
            layer=layer,
            source=source,
            state_id=state_id,
            collected_at=collected_at,
            verifier_version=self.verifier_version,
            contract_fingerprint=contract.fingerprint,
            verdict=verdict,
            payload=tuple(sorted((payload or {}).items())),
            integrity_tags=tuple(integrity_tags),
        )


@dataclass(frozen=True)
class IntegrityReport:
    status: IntegrityStatus
    violations: tuple[str, ...] = ()
    checked_paths: tuple[str, ...] = ()

    @classmethod
    def clean(cls, *checked_paths: str) -> "IntegrityReport":
        return cls(IntegrityStatus.CLEAN, (), tuple(checked_paths))

    @classmethod
    def violated(
        cls,
        violations: Iterable[str],
        *,
        checked_paths: Iterable[str] = (),
    ) -> "IntegrityReport":
        return cls(
            IntegrityStatus.VIOLATED,
            tuple(violations),
            tuple(checked_paths),
        )


class ProtectedPathVerifier:
    """Detect deletion or modification of protected evaluation assets."""

    def __init__(self, baseline: WorkspaceSnapshot, protected_paths: Iterable[str]) -> None:
        self.protected_paths = tuple(
            sorted({_canonical_repo_path(path) for path in protected_paths})
        )
        baseline_files = baseline.as_dict()
        self._baseline_hashes: dict[str, str | None] = {
            path: self._hash(baseline_files.get(path)) for path in self.protected_paths
        }

    @staticmethod
    def _hash(content: str | None) -> str | None:
        if content is None:
            return None
        return sha256(content.encode("utf-8")).hexdigest()

    def check(self, current: WorkspaceSnapshot) -> IntegrityReport:
        current_files = current.as_dict()
        violations: list[str] = []
        for path in self.protected_paths:
            before = self._baseline_hashes[path]
            after = self._hash(current_files.get(path))
            if before == after:
                continue
            if after is None:
                violations.append(f"protected path deleted: {path}")
            else:
                violations.append(f"protected path modified: {path}")

        if violations:
            return IntegrityReport.violated(
                violations,
                checked_paths=self.protected_paths,
            )
        return IntegrityReport.clean(*self.protected_paths)


class ContractIntegrityVerifier:
    """Detect forbidden evaluation-path events named by the goal contract."""

    def check(
        self,
        contract: GoalContract,
        *,
        observed_events: Iterable[str] = (),
    ) -> IntegrityReport:
        events = set(observed_events)
        violations = tuple(
            f"forbidden condition observed: {condition}"
            for condition in contract.must_not
            if condition in events
        )
        if violations:
            return IntegrityReport.violated(violations)
        return IntegrityReport.clean()


def combine_integrity(*reports: IntegrityReport) -> IntegrityReport:
    violations = tuple(
        violation
        for report in reports
        for violation in report.violations
    )
    checked_paths = tuple(
        path
        for report in reports
        for path in report.checked_paths
    )
    if violations:
        return IntegrityReport.violated(violations, checked_paths=checked_paths)
    if any(report.status == IntegrityStatus.UNKNOWN for report in reports):
        return IntegrityReport(IntegrityStatus.UNKNOWN, (), checked_paths)
    return IntegrityReport.clean(*checked_paths)


class Verifier:
    """Protected evaluation boundary; collection and adjudication remain separate."""

    def __init__(
        self,
        *,
        baseline: WorkspaceSnapshot,
        protected_paths: Iterable[str] = (),
    ) -> None:
        self.protected = ProtectedPathVerifier(baseline, protected_paths)
        self.contract = ContractIntegrityVerifier()

    def check_integrity(
        self,
        *,
        contract: GoalContract,
        current: WorkspaceSnapshot,
        observed_events: Iterable[str] = (),
    ) -> IntegrityReport:
        return combine_integrity(
            self.protected.check(current),
            self.contract.check(contract, observed_events=observed_events),
        )


@dataclass(frozen=True)
class CriterionResult:
    criterion: str
    verdict: Verdict
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class VerificationResult:
    verdict: Verdict
    criteria: tuple[CriterionResult, ...]
    integrity: IntegrityReport
    stale_evidence_ids: tuple[str, ...]
    reason: str

    @property
    def verification_coverage(self) -> float:
        if not self.criteria:
            return 1.0
        covered = sum(
            1
            for result in self.criteria
            if result.verdict != Verdict.UNKNOWN
        )
        return covered / len(self.criteria)


class Adjudicator:
    """Decide what current goal-level evidence and integrity actually earn."""

    def decide(
        self,
        *,
        contract: GoalContract,
        evidence: EvidenceSet,
        state_id: StateIdentity,
        integrity: IntegrityReport,
    ) -> VerificationResult:
        current = evidence.current_for(state_id=state_id, contract=contract)
        stale = evidence.stale_for(state_id=state_id, contract=contract)

        results: list[CriterionResult] = []
        for criterion in contract.required_criteria:
            matching = tuple(
                record
                for record in current
                if record.criterion == criterion
                and record.layer == EvidenceLayer.GOAL_SATISFACTION
            )
            if not matching:
                verdict = Verdict.UNKNOWN
            elif any(record.verdict == Verdict.FAIL for record in matching):
                verdict = Verdict.FAIL
            elif any(record.verdict == Verdict.PARTIAL for record in matching):
                verdict = Verdict.PARTIAL
            elif all(record.verdict == Verdict.PASS for record in matching):
                verdict = Verdict.PASS
            else:
                verdict = Verdict.UNKNOWN

            results.append(
                CriterionResult(
                    criterion=criterion,
                    verdict=verdict,
                    evidence_ids=tuple(record.id for record in matching),
                )
            )

        if integrity.status == IntegrityStatus.VIOLATED:
            final = Verdict.FAIL
            reason = "evaluation integrity was violated"
        elif integrity.status == IntegrityStatus.UNKNOWN:
            final = Verdict.UNKNOWN
            reason = "evaluation integrity is unknown"
        elif any(result.verdict == Verdict.FAIL for result in results):
            final = Verdict.FAIL
            reason = "at least one required criterion failed"
        elif any(result.verdict == Verdict.UNKNOWN for result in results):
            final = Verdict.UNKNOWN
            reason = "current state lacks sufficient goal-level evidence for every required criterion"
        elif any(result.verdict == Verdict.PARTIAL for result in results):
            final = Verdict.PARTIAL
            reason = "at least one required criterion is only partially satisfied"
        else:
            final = Verdict.PASS
            reason = "all required criteria passed on current state with clean integrity"

        return VerificationResult(
            verdict=final,
            criteria=tuple(results),
            integrity=integrity,
            stale_evidence_ids=tuple(record.id for record in stale),
            reason=reason,
        )
