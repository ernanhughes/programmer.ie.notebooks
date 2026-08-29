from __future__ import annotations

import json

from .actions import Action, ActionKind, RawProposal
from .state import AgentState


class Stage00Policy:
    """Deterministic typed-action policy for the Stage-00 control experiment."""

    def choose_action(self, state: AgentState) -> Action:
        if not state.transitions:
            return Action(
                kind=ActionKind.RUN_TESTS,
                reason="establish the current repository state",
            )

        last = state.transitions[-1]

        if (
            last.action.kind == ActionKind.RUN_TESTS
            and not last.observation.ok
        ):
            return Action(
                kind=ActionKind.READ_FILE,
                target="parser.py",
                reason="the failed test makes the parser implementation relevant",
            )

        if last.action.kind == ActionKind.READ_FILE:
            return Action(
                kind=ActionKind.STOP,
                reason=(
                    "inspection complete; repair capability has not been "
                    "introduced yet"
                ),
            )

        return Action(
            kind=ActionKind.STOP,
            reason="no further Stage 00 action is justified",
        )


class Stage01Policy:
    """Same adaptive policy, but expressed as untrusted raw JSON proposals."""

    def choose_action(self, state: AgentState) -> RawProposal:
        if not state.transitions:
            return self._proposal(
                action="run_tests",
                reason="establish the current repository state",
            )

        last = state.transitions[-1]

        if (
            last.action.kind == ActionKind.RUN_TESTS
            and not last.observation.ok
        ):
            return self._proposal(
                action="read_file",
                target="parser.py",
                reason="the failed test makes the parser implementation relevant",
            )

        if last.action.kind == ActionKind.READ_FILE:
            return self._proposal(
                action="stop",
                reason=(
                    "inspection complete; repair capability has not been "
                    "introduced yet"
                ),
            )

        return self._proposal(
            action="stop",
            reason="no further Stage 01 action is justified",
        )

    @staticmethod
    def _proposal(
        *,
        action: str,
        target: str | None = None,
        reason: str | None = None,
    ) -> RawProposal:
        payload: dict[str, str] = {"action": action}
        if target is not None:
            payload["target"] = target
        if reason is not None:
            payload["reason"] = reason
        return RawProposal(json.dumps(payload))
