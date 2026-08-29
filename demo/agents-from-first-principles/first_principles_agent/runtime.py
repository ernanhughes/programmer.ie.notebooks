from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class TerminationReason(str, Enum):
    SUCCESS = "SUCCESS"
    MAX_STEPS = "MAX_STEPS"
    MAX_MODEL_CALLS = "MAX_MODEL_CALLS"
    NO_PROGRESS = "NO_PROGRESS"
    NONPRODUCTIVE_CYCLE = "NONPRODUCTIVE_CYCLE"
    PRECONDITION_MISSING = "PRECONDITION_MISSING"
    USER_INPUT_REQUIRED = "USER_INPUT_REQUIRED"


class ContinuationDisposition(str, Enum):
    CONTINUE = "CONTINUE"
    RECOVER = "RECOVER"
    STOP = "STOP"


@dataclass(frozen=True)
class RuntimeState:
    """Facts the runtime currently treats as true.

    This is intentionally distinct from model-visible context, execution trace,
    and long-term memory. Stage 05 owns current control facts only.
    """

    facts: frozenset[str] = frozenset()
    step_count: int = 0
    model_calls: int = 0
    success_signal: bool = False
    missing_precondition: str | None = None
    user_input_request: str | None = None

    def with_facts(self, *facts: str) -> "RuntimeState":
        return RuntimeState(
            facts=self.facts.union(facts),
            step_count=self.step_count,
            model_calls=self.model_calls,
            success_signal=self.success_signal,
            missing_precondition=self.missing_precondition,
            user_input_request=self.user_input_request,
        )


@dataclass(frozen=True)
class ModelVisibleContext:
    """What the model is shown now; not authoritative runtime state."""

    summary: str
    facts: tuple[str, ...] = ()


@dataclass(frozen=True)
class LongTermMemory:
    """Boundary object only. Stage 07 will earn the memory lifecycle."""

    entries: tuple[str, ...] = ()


@dataclass(frozen=True)
class StepRecord:
    action: str
    relevant_state: str
    new_evidence: bool = False
    progress_delta: int = 0

    @property
    def made_progress(self) -> bool:
        return self.progress_delta > 0 or self.new_evidence


@dataclass
class ExecutionTrace:
    records: list[StepRecord] = field(default_factory=list)

    def append(self, record: StepRecord) -> None:
        self.records.append(record)

    def __len__(self) -> int:
        return len(self.records)


@dataclass(frozen=True)
class Budgets:
    max_steps: int = 20
    max_model_calls: int = 20
    no_progress_window: int = 3

    def __post_init__(self) -> None:
        if self.max_steps <= 0:
            raise ValueError("max_steps must be positive")
        if self.max_model_calls <= 0:
            raise ValueError("max_model_calls must be positive")
        if self.no_progress_window <= 0:
            raise ValueError("no_progress_window must be positive")


class ProgressMeasure:
    """Measure useful change without confusing activity with progress."""

    @staticmethod
    def steps_after_last_progress(trace: ExecutionTrace) -> int:
        last_progress_index = -1
        for index, record in enumerate(trace.records):
            if record.made_progress:
                last_progress_index = index
        return len(trace.records) - last_progress_index - 1

    @staticmethod
    def nonproductive_cycle(trace: ExecutionTrace) -> bool:
        if len(trace.records) < 2:
            return False
        previous, current = trace.records[-2:]
        same_relevant_transition = (
            previous.action == current.action
            and previous.relevant_state == current.relevant_state
        )
        return (
            same_relevant_transition
            and not current.new_evidence
            and current.progress_delta <= 0
        )


@dataclass(frozen=True)
class ContinuationDecision:
    disposition: ContinuationDisposition
    reason: TerminationReason | None = None
    steps_after_last_progress: int = 0
    detail: str | None = None

    @property
    def should_continue(self) -> bool:
        return self.disposition is ContinuationDisposition.CONTINUE


class ContinuationPolicy:
    """Decide whether another action should execute at all.

    Stage 05 does not define the final success oracle. `success_signal` is an
    externally supplied runtime signal; Stage 09 will define how success is
    actually verified.
    """

    def __init__(self, progress: ProgressMeasure | None = None) -> None:
        self.progress = progress or ProgressMeasure()

    def decide(
        self,
        state: RuntimeState,
        trace: ExecutionTrace,
        budgets: Budgets,
    ) -> ContinuationDecision:
        stalled_for = self.progress.steps_after_last_progress(trace)

        if state.success_signal:
            return ContinuationDecision(
                ContinuationDisposition.STOP,
                TerminationReason.SUCCESS,
                stalled_for,
                "runtime received a success signal; Stage 09 still owns verification",
            )

        if state.user_input_request is not None:
            return ContinuationDecision(
                ContinuationDisposition.STOP,
                TerminationReason.USER_INPUT_REQUIRED,
                stalled_for,
                state.user_input_request,
            )

        if state.missing_precondition is not None:
            return ContinuationDecision(
                ContinuationDisposition.RECOVER,
                TerminationReason.PRECONDITION_MISSING,
                stalled_for,
                state.missing_precondition,
            )

        if state.step_count >= budgets.max_steps:
            return ContinuationDecision(
                ContinuationDisposition.STOP,
                TerminationReason.MAX_STEPS,
                stalled_for,
            )

        if state.model_calls >= budgets.max_model_calls:
            return ContinuationDecision(
                ContinuationDisposition.STOP,
                TerminationReason.MAX_MODEL_CALLS,
                stalled_for,
            )

        if self.progress.nonproductive_cycle(trace):
            return ContinuationDecision(
                ContinuationDisposition.RECOVER,
                TerminationReason.NONPRODUCTIVE_CYCLE,
                stalled_for,
            )

        if stalled_for >= budgets.no_progress_window:
            return ContinuationDecision(
                ContinuationDisposition.RECOVER,
                TerminationReason.NO_PROGRESS,
                stalled_for,
            )

        return ContinuationDecision(
            ContinuationDisposition.CONTINUE,
            None,
            stalled_for,
        )
