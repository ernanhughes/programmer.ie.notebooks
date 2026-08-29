from first_principles_agent.actions import Action, ActionKind, Observation
from first_principles_agent.agent import Agent
from first_principles_agent.policy import Stage00Policy


class FakeEnvironment:
    def __init__(self, tests_pass: bool) -> None:
        self.tests_pass = tests_pass
        self.actions: list[ActionKind] = []

    def execute(self, action: Action) -> Observation:
        self.actions.append(action.kind)

        if action.kind == ActionKind.RUN_TESTS:
            return Observation(
                source="pytest",
                ok=self.tests_pass,
                summary="tests passed" if self.tests_pass else "tests failed",
                details="synthetic test result",
            )

        if action.kind == ActionKind.READ_FILE:
            return Observation(
                source=action.target or "unknown",
                ok=True,
                summary="source inspected",
                details='return text.split(",")',
            )

        raise AssertionError(f"unexpected action: {action.kind}")


def test_failed_tests_change_the_next_action() -> None:
    environment = FakeEnvironment(tests_pass=False)
    agent = Agent(Stage00Policy(), environment)

    state = agent.run("Fix pipe-delimited records")

    assert environment.actions == [
        ActionKind.RUN_TESTS,
        ActionKind.READ_FILE,
    ]
    assert [t.action.kind for t in state.transitions] == [
        ActionKind.RUN_TESTS,
        ActionKind.READ_FILE,
    ]
    assert state.termination_reason == (
        "inspection complete; repair capability has not been introduced yet"
    )


def test_passing_tests_do_not_trigger_source_inspection() -> None:
    environment = FakeEnvironment(tests_pass=True)
    agent = Agent(Stage00Policy(), environment)

    state = agent.run("Inspect repository")

    assert environment.actions == [ActionKind.RUN_TESTS]
    assert state.step == 1
    assert state.termination_reason == "no further Stage 00 action is justified"
