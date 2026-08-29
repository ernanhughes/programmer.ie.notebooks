from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from .acceptance import AcceptanceResult
from .actions import ActionKind, Observation, RawProposal
from .runtime import RuntimeState


class CapabilityOutcome(str, Enum):
    TOOL = "tool"
    NO_TOOL = "no_tool"
    ASK_USER = "ask_user"
    MISSING_PRECONDITION = "missing_precondition"


@dataclass(frozen=True)
class Capability:
    """A capability contract exposed to the agent's decision policy."""

    name: str
    purpose: str
    action_kind: ActionKind
    eligible_when: frozenset[str] = frozenset()
    keywords: frozenset[str] = frozenset()
    output_schema: tuple[str, ...] = ()


@dataclass(frozen=True)
class CapabilityNeed:
    """A current information/action need before tool selection."""

    text: str
    target: str | None = None
    required_facts: frozenset[str] = frozenset()
    requires_user_input: bool = False


class CapabilityRegistry:
    def __init__(self, capabilities: tuple[Capability, ...] | list[Capability]) -> None:
        self.capabilities = tuple(capabilities)
        names = [capability.name for capability in self.capabilities]
        if len(names) != len(set(names)):
            raise ValueError("capability names must be unique")

    def get(self, name: str) -> Capability | None:
        return next(
            (capability for capability in self.capabilities if capability.name == name),
            None,
        )


class ExposurePolicy:
    """Decide which capabilities are visible for the current state.

    Exposure reduces the policy's decision surface. It is not authorization.
    Stage 01 remains the execution authority boundary.
    """

    def expose(
        self,
        registry: CapabilityRegistry,
        state: RuntimeState,
    ) -> tuple[Capability, ...]:
        return tuple(
            capability
            for capability in registry.capabilities
            if capability.eligible_when <= state.facts
        )


@dataclass(frozen=True)
class RetrievedCapability:
    capability: Capability
    score: float


class CapabilityRetriever:
    """Small deterministic lexical retriever for the controlled experiment."""

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return set(re.findall(r"[a-z0-9_]+", text.lower()))

    def retrieve(
        self,
        need: CapabilityNeed,
        exposed: tuple[Capability, ...],
        *,
        k: int = 2,
    ) -> tuple[RetrievedCapability, ...]:
        if k <= 0:
            raise ValueError("k must be positive")

        need_tokens = self._tokens(need.text)
        ranked: list[RetrievedCapability] = []
        for capability in exposed:
            capability_tokens = set(capability.keywords)
            capability_tokens |= self._tokens(capability.name)
            capability_tokens |= self._tokens(capability.purpose)
            overlap = need_tokens & capability_tokens
            if not overlap:
                continue
            ranked.append(
                RetrievedCapability(
                    capability=capability,
                    score=float(len(overlap)),
                )
            )

        ranked.sort(key=lambda item: (-item.score, item.capability.name))
        return tuple(ranked[:k])


class ToolSelector:
    """Select one retrieved capability without granting execution authority."""

    def select(
        self,
        retrieved: tuple[RetrievedCapability, ...],
    ) -> Capability | None:
        if not retrieved:
            return None
        return retrieved[0].capability


@dataclass(frozen=True)
class CapabilityDecision:
    outcome: CapabilityOutcome
    need: CapabilityNeed
    exposed: tuple[str, ...] = ()
    retrieved: tuple[str, ...] = ()
    selected: Capability | None = None
    reason: str = ""

    def to_raw_proposal(self) -> RawProposal:
        if self.outcome != CapabilityOutcome.TOOL or self.selected is None:
            raise ValueError("only a selected tool decision can become a proposal")

        payload: dict[str, str] = {"action": self.selected.action_kind.value}
        if self.need.target is not None:
            payload["target"] = self.need.target
        payload["reason"] = self.need.text
        return RawProposal(json.dumps(payload, sort_keys=True))


class CapabilityPipeline:
    def __init__(
        self,
        registry: CapabilityRegistry,
        *,
        exposure: ExposurePolicy | None = None,
        retriever: CapabilityRetriever | None = None,
        selector: ToolSelector | None = None,
        retrieval_k: int = 2,
    ) -> None:
        self.registry = registry
        self.exposure = exposure or ExposurePolicy()
        self.retriever = retriever or CapabilityRetriever()
        self.selector = selector or ToolSelector()
        self.retrieval_k = retrieval_k

    def route(self, state: RuntimeState, need: CapabilityNeed) -> CapabilityDecision:
        if need.requires_user_input:
            return CapabilityDecision(
                outcome=CapabilityOutcome.ASK_USER,
                need=need,
                reason="the decision requires information or authority from the user",
            )

        missing = sorted(need.required_facts - state.facts)
        if missing:
            return CapabilityDecision(
                outcome=CapabilityOutcome.MISSING_PRECONDITION,
                need=need,
                reason=f"missing required facts: {', '.join(missing)}",
            )

        exposed = self.exposure.expose(self.registry, state)
        retrieved = self.retriever.retrieve(
            need,
            exposed,
            k=self.retrieval_k,
        )
        selected = self.selector.select(retrieved)

        if selected is None:
            return CapabilityDecision(
                outcome=CapabilityOutcome.NO_TOOL,
                need=need,
                exposed=tuple(capability.name for capability in exposed),
                retrieved=(),
                reason="no exposed capability matches the current need",
            )

        return CapabilityDecision(
            outcome=CapabilityOutcome.TOOL,
            need=need,
            exposed=tuple(capability.name for capability in exposed),
            retrieved=tuple(item.capability.name for item in retrieved),
            selected=selected,
            reason="selected from the currently exposed and retrieved action space",
        )


class AcceptanceBoundary(Protocol):
    def accept(self, proposal: RawProposal) -> AcceptanceResult: ...


class ActionEnvironment(Protocol):
    def execute(self, action: object) -> Observation: ...


@dataclass(frozen=True)
class ToolObservation:
    capability: str
    source: str
    ok: bool
    summary: str
    data: dict[str, object]


@dataclass(frozen=True)
class CapabilityExecution:
    decision: CapabilityDecision
    acceptance: AcceptanceResult
    observation: ToolObservation | None


class CapabilityExecutor:
    """Cross Stage 01 after selection, then execute exactly one accepted tool."""

    def execute(
        self,
        decision: CapabilityDecision,
        acceptance: AcceptanceBoundary,
        environment: ActionEnvironment,
    ) -> CapabilityExecution:
        proposal = decision.to_raw_proposal()
        accepted = acceptance.accept(proposal)
        if not accepted.accepted or accepted.action is None:
            return CapabilityExecution(
                decision=decision,
                acceptance=accepted,
                observation=None,
            )

        raw_observation = environment.execute(accepted.action)
        selected = decision.selected
        assert selected is not None
        return CapabilityExecution(
            decision=decision,
            acceptance=accepted,
            observation=ToolObservation(
                capability=selected.name,
                source=raw_observation.source,
                ok=raw_observation.ok,
                summary=raw_observation.summary,
                data=dict(raw_observation.data),
            ),
        )


@dataclass(frozen=True)
class CapabilityCase:
    state: RuntimeState
    need: CapabilityNeed
    expected_outcome: CapabilityOutcome
    expected_capability: str | None = None


@dataclass(frozen=True)
class CapabilityMetrics:
    capability_coverage: float
    tool_recall_at_k: float
    selection_accuracy_given_available: float
    wrong_tool_rate: float
    abstention_accuracy: float

    def as_dict(self) -> dict[str, float]:
        return {
            "capability_coverage": self.capability_coverage,
            "tool_recall@k": self.tool_recall_at_k,
            "selection_accuracy_given_available": self.selection_accuracy_given_available,
            "wrong_tool_rate": self.wrong_tool_rate,
            "abstention_accuracy": self.abstention_accuracy,
        }


def evaluate_capability_routing(
    pipeline: CapabilityPipeline,
    cases: tuple[CapabilityCase, ...] | list[CapabilityCase],
) -> CapabilityMetrics:
    cases = tuple(cases)
    tool_cases = tuple(case for case in cases if case.expected_capability is not None)
    abstention_cases = tuple(case for case in cases if case.expected_capability is None)

    coverage_hits = 0
    recall_hits = 0
    selection_hits = 0
    wrong_tool = 0

    for case in tool_cases:
        if pipeline.registry.get(case.expected_capability or "") is not None:
            coverage_hits += 1
        decision = pipeline.route(case.state, case.need)
        if case.expected_capability in decision.retrieved:
            recall_hits += 1
        if decision.selected is not None and decision.selected.name == case.expected_capability:
            selection_hits += 1
        elif decision.outcome == CapabilityOutcome.TOOL:
            wrong_tool += 1

    abstention_hits = 0
    for case in abstention_cases:
        decision = pipeline.route(case.state, case.need)
        if decision.outcome == case.expected_outcome:
            abstention_hits += 1

    tool_count = len(tool_cases)
    abstention_count = len(abstention_cases)
    return CapabilityMetrics(
        capability_coverage=(coverage_hits / tool_count if tool_count else 1.0),
        tool_recall_at_k=(recall_hits / tool_count if tool_count else 1.0),
        selection_accuracy_given_available=(
            selection_hits / tool_count if tool_count else 1.0
        ),
        wrong_tool_rate=(wrong_tool / tool_count if tool_count else 0.0),
        abstention_accuracy=(
            abstention_hits / abstention_count if abstention_count else 1.0
        ),
    )
