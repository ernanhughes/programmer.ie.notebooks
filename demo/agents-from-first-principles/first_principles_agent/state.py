from __future__ import annotations

from dataclasses import dataclass, field

from .acceptance import AcceptanceResult
from .actions import Action, Observation


@dataclass(frozen=True)
class Transition:
    step: int
    action: Action
    observation: Observation


@dataclass
class AgentState:
    task: str
    step: int = 0
    transitions: list[Transition] = field(default_factory=list)
    acceptance_attempts: list[AcceptanceResult] = field(default_factory=list)
    termination_reason: str | None = None

    @property
    def last_observation(self) -> Observation | None:
        if not self.transitions:
            return None
        return self.transitions[-1].observation

    @property
    def is_done(self) -> bool:
        return self.termination_reason is not None

    def record_acceptance(self, result: AcceptanceResult) -> None:
        self.acceptance_attempts.append(result)

    def record(self, action: Action, observation: Observation) -> None:
        self.transitions.append(
            Transition(
                step=self.step,
                action=action,
                observation=observation,
            )
        )
        self.step += 1
