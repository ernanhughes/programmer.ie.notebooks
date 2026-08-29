from pathlib import Path

import pytest

from first_principles_agent.acceptance import (
    AcceptanceStage,
    ActionAcceptanceBoundary,
)
from first_principles_agent.actions import Action, ActionKind, Observation, RawProposal
from first_principles_agent.agent import Agent
from first_principles_agent.policy import Stage01Policy


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    (tmp_path / "tests").mkdir()
    (tmp_path / "parser.py").write_text(
        'def split_record(text, delimiter=","):\n'
        '    return text.split(",")\n',
        encoding="utf-8",
    )
    return tmp_path


def test_acceptance_stages_are_distinguishable(repository: Path) -> None:
    boundary = ActionAcceptanceBoundary(repository)

    cases = [
        (
            RawProposal('{"action": "read_file"'),
            AcceptanceStage.REPRESENTATION,
        ),
        (
            RawProposal('{"target": "parser.py"}'),
            AcceptanceStage.SCHEMA,
        ),
        (
            RawProposal('{"action": "delete_file"}'),
            AcceptanceStage.SEMANTICS,
        ),
        (
            RawProposal(
                '{"action": "read_file", "target": "../secret.txt"}'
            ),
            AcceptanceStage.AUTHORIZATION,
        ),
        (
            RawProposal(
                '{"action": "read_file", "target": "missing.py"}'
            ),
            AcceptanceStage.PRECONDITIONS,
        ),
    ]

    for proposal, expected_stage in cases:
        result = boundary.accept(proposal)
        assert result.accepted is False
        assert result.stage == expected_stage
        assert result.action is None


def test_valid_proposal_becomes_a_typed_action(repository: Path) -> None:
    result = ActionAcceptanceBoundary(repository).accept(
        RawProposal(
            '{"action": "read_file", "target": "parser.py", '
            '"reason": "inspect implementation"}'
        )
    )

    assert result.accepted is True
    assert result.stage == AcceptanceStage.ACCEPTED
    assert result.action == Action(
        kind=ActionKind.READ_FILE,
        target="parser.py",
        reason="inspect implementation",
    )


class RecordingEnvironment:
    def __init__(self) -> None:
        self.actions: list[ActionKind] = []

    def execute(self, action: Action) -> Observation:
        self.actions.append(action.kind)

        if action.kind == ActionKind.RUN_TESTS:
            return Observation(
                source="pytest",
                ok=False,
                summary="tests failed",
                details="pipe delimiter failed",
            )

        if action.kind == ActionKind.READ_FILE:
            return Observation(
                source=action.target or "unknown",
                ok=True,
                summary="source inspected",
                details='return text.split(",")',
            )

        raise AssertionError(f"unexpected executed action: {action.kind}")


def test_stage01_agent_executes_only_accepted_typed_actions(
    repository: Path,
) -> None:
    environment = RecordingEnvironment()
    agent = Agent(
        policy=Stage01Policy(),
        environment=environment,
        acceptance=ActionAcceptanceBoundary(repository),
    )

    state = agent.run("Fix pipe-delimited records")

    assert environment.actions == [ActionKind.RUN_TESTS, ActionKind.READ_FILE]
    assert [attempt.stage for attempt in state.acceptance_attempts] == [
        AcceptanceStage.ACCEPTED,
        AcceptanceStage.ACCEPTED,
        AcceptanceStage.ACCEPTED,
    ]
    assert state.termination_reason == (
        "inspection complete; repair capability has not been introduced yet"
    )


class UnauthorizedPolicy:
    def choose_action(self, _state) -> RawProposal:
        return RawProposal(
            '{"action": "read_file", "target": "../secret.txt"}'
        )


class MustNotExecuteEnvironment:
    def execute(self, _action: Action) -> Observation:
        raise AssertionError("rejected proposals must never reach the environment")


def test_rejected_proposal_never_reaches_environment(repository: Path) -> None:
    agent = Agent(
        policy=UnauthorizedPolicy(),
        environment=MustNotExecuteEnvironment(),
        acceptance=ActionAcceptanceBoundary(repository),
    )

    state = agent.run("Read something outside the repository")

    assert state.transitions == []
    assert len(state.acceptance_attempts) == 1
    assert state.acceptance_attempts[0].stage == AcceptanceStage.AUTHORIZATION
    assert state.termination_reason.startswith("proposal rejected at authorization:")
