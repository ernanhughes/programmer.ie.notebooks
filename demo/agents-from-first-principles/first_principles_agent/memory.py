from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum


class MemoryStatus(str, Enum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    EXPIRED = "expired"
    FORGOTTEN = "forgotten"
    DELETED = "deleted"


@dataclass(frozen=True)
class MemoryRecord:
    id: str
    key: str
    value: str
    scope: str
    provenance: str
    verified: bool = True
    reusable: bool = True
    status: MemoryStatus = MemoryStatus.ACTIVE
    sequence: int = 0
    supersedes: str | None = None


@dataclass(frozen=True)
class WriteDecision:
    write: bool
    reason: str


class WritePolicy:
    """Write only information that is both verified and plausibly reusable."""

    def decide(self, *, verified: bool, reusable: bool) -> WriteDecision:
        if not verified:
            return WriteDecision(False, "unverified information is not persistent memory")
        if not reusable:
            return WriteDecision(False, "transient information stays in state or trace")
        return WriteDecision(True, "verified reusable information may be persisted")


class MemoryStore:
    def __init__(self, records: tuple[MemoryRecord, ...] | list[MemoryRecord] = ()) -> None:
        self._records: dict[str, MemoryRecord] = {}
        self._sequence = 0
        for record in records:
            self.add(record)

    @property
    def records(self) -> tuple[MemoryRecord, ...]:
        return tuple(sorted(self._records.values(), key=lambda record: record.sequence))

    def get(self, memory_id: str) -> MemoryRecord:
        return self._records[memory_id]

    def add(self, record: MemoryRecord) -> MemoryRecord:
        if record.id in self._records:
            raise ValueError(f"duplicate memory id: {record.id}")
        self._sequence += 1
        stored = replace(record, sequence=self._sequence)
        self._records[stored.id] = stored
        return stored

    def write(
        self,
        *,
        memory_id: str,
        key: str,
        value: str,
        scope: str,
        provenance: str,
        policy: WritePolicy,
        verified: bool = True,
        reusable: bool = True,
        supersedes: str | None = None,
    ) -> MemoryRecord | None:
        decision = policy.decide(verified=verified, reusable=reusable)
        if not decision.write:
            return None

        if supersedes is not None:
            self.supersede(supersedes)

        return self.add(
            MemoryRecord(
                id=memory_id,
                key=key,
                value=value,
                scope=scope,
                provenance=provenance,
                verified=verified,
                reusable=reusable,
                supersedes=supersedes,
            )
        )

    def _set_status(self, memory_id: str, status: MemoryStatus) -> MemoryRecord:
        current = self.get(memory_id)
        updated = replace(current, status=status)
        self._records[memory_id] = updated
        return updated

    def supersede(self, memory_id: str) -> MemoryRecord:
        return self._set_status(memory_id, MemoryStatus.SUPERSEDED)

    def expire(self, memory_id: str) -> MemoryRecord:
        return self._set_status(memory_id, MemoryStatus.EXPIRED)

    def forget(self, memory_id: str) -> MemoryRecord:
        return self._set_status(memory_id, MemoryStatus.FORGOTTEN)

    def delete(self, memory_id: str) -> MemoryRecord:
        return self._set_status(memory_id, MemoryStatus.DELETED)


class RetrievalPolicy:
    """Retrieve active scoped records; ranking is deterministic and inspectable."""

    def retrieve(
        self,
        store: MemoryStore,
        *,
        key: str,
        scope: str | None = None,
        limit: int = 5,
    ) -> tuple[MemoryRecord, ...]:
        if limit <= 0:
            raise ValueError("limit must be positive")
        eligible = [
            record
            for record in store.records
            if record.status == MemoryStatus.ACTIVE
            and record.key == key
            and (scope is None or record.scope == scope)
        ]
        eligible.sort(key=lambda record: record.sequence, reverse=True)
        return tuple(eligible[:limit])


@dataclass(frozen=True)
class MemoryContext:
    included: tuple[MemoryRecord, ...]
    excluded_by_current_evidence: tuple[str, ...] = ()


class ContextAssembler:
    """Current evidence outranks conflicting persistent memory."""

    def assemble(
        self,
        retrieved: tuple[MemoryRecord, ...],
        *,
        current_evidence: dict[str, str] | None = None,
    ) -> MemoryContext:
        evidence = current_evidence or {}
        included: list[MemoryRecord] = []
        excluded: list[str] = []
        for record in retrieved:
            if record.key in evidence and evidence[record.key] != record.value:
                excluded.append(record.id)
                continue
            included.append(record)
        return MemoryContext(tuple(included), tuple(excluded))


@dataclass(frozen=True)
class MemoryDecision:
    choice: str
    retrieved_ids: tuple[str, ...]
    included_ids: tuple[str, ...]
    used_ids: tuple[str, ...]
    reason: str


class MemoryCycle:
    """Retrieve, assemble, and causally use memory only when current evidence is absent."""

    def __init__(
        self,
        *,
        retrieval: RetrievalPolicy | None = None,
        assembler: ContextAssembler | None = None,
    ) -> None:
        self.retrieval = retrieval or RetrievalPolicy()
        self.assembler = assembler or ContextAssembler()

    def decide(
        self,
        store: MemoryStore,
        *,
        key: str,
        scope: str,
        current_evidence: dict[str, str] | None = None,
        fallback: str,
    ) -> MemoryDecision:
        evidence = current_evidence or {}
        retrieved = self.retrieval.retrieve(store, key=key, scope=scope)
        context = self.assembler.assemble(retrieved, current_evidence=evidence)

        if key in evidence:
            return MemoryDecision(
                choice=evidence[key],
                retrieved_ids=tuple(record.id for record in retrieved),
                included_ids=tuple(record.id for record in context.included),
                used_ids=(),
                reason="current evidence outranks persistent memory",
            )

        if context.included:
            chosen = context.included[0]
            return MemoryDecision(
                choice=chosen.value,
                retrieved_ids=tuple(record.id for record in retrieved),
                included_ids=tuple(record.id for record in context.included),
                used_ids=(chosen.id,),
                reason="used most recent eligible persistent memory",
            )

        return MemoryDecision(
            choice=fallback,
            retrieved_ids=tuple(record.id for record in retrieved),
            included_ids=(),
            used_ids=(),
            reason="no eligible memory; use fallback exploration",
        )


@dataclass
class ProspectiveMemory:
    id: str
    condition: str
    action: str
    fired: bool = False

    def observe(self, event: str) -> str | None:
        if self.fired or event != self.condition:
            return None
        self.fired = True
        return self.action


@dataclass(frozen=True)
class MemoryOutcome:
    success: bool
    steps: int


@dataclass(frozen=True)
class MemoryDiagnostics:
    write_precision: float
    retrieval_recall: float
    context_inclusion_rate: float
    decision_use_rate: float
    outcome_delta_steps: int
    memory_induced_regret: bool

    def as_dict(self) -> dict[str, float | int | bool]:
        return {
            "write_precision": self.write_precision,
            "retrieval_recall": self.retrieval_recall,
            "context_inclusion_rate": self.context_inclusion_rate,
            "decision_use_rate": self.decision_use_rate,
            "outcome_delta_steps": self.outcome_delta_steps,
            "memory_induced_regret": self.memory_induced_regret,
        }


def memory_induced_regret(*, no_memory: MemoryOutcome, with_memory: MemoryOutcome) -> bool:
    return no_memory.success and not with_memory.success
