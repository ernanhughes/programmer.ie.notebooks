from __future__ import annotations

from typing import Protocol

from .acceptance import AcceptanceResult, DirectActionAcceptance
from .actions import Action, ActionKind, Observation, RawProposal
from .state import AgentState


class Policy(Protocol):
    def choose_action(self, state: AgentState) -> Action | RawProposal: ...


class Environment(Protocol):
    def execute(self, action: Action) -> Observation: ...


class AcceptanceBoundary(Protocol):
    def accept(self, proposal: Action | RawProposal) -> AcceptanceResult: ...


class Agent:
    """Small agent loop with an explicit proposal-to-execution boundary.

    Stage 00 uses DirectActionAcceptance so its original experiment remains a
    pure control-loop demonstration. Stage 01 injects a stronger boundary that
    parses and validates raw proposals before the environment can see them.
    """

    def __init__(
        self,
        policy: Policy,
        environment: Environment,
        max_steps: int = 4,
        acceptance: AcceptanceBoundary | None = None,
    ) -> None:
        self.policy = policy
        self.environment = environment
        self.max_steps = max_steps
        self.acceptance = acceptance or DirectActionAcceptance()

    def run(self, task: str) -> AgentState:
        state = AgentState(task=task)

        while state.step < self.max_steps:
            proposal = self.policy.choose_action(state)
            acceptance = self.acceptance.accept(proposal)
            state.record_acceptance(acceptance)

            if not acceptance.accepted or acceptance.action is None:
                state.termination_reason = (
                    f"proposal rejected at {acceptance.stage.value}: "
                    f"{acceptance.reason}"
                )
                return state

            action = acceptance.action

            if action.kind == ActionKind.STOP:
                state.termination_reason = action.reason or "policy stopped"
                return state

            observation = self.environment.execute(action)
            state.record(action, observation)

        state.termination_reason = "max_steps reached"
        return state
