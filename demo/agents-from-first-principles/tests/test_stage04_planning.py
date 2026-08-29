from first_principles_agent.planning import (
    Plan,
    PlanStep,
    PlanValidator,
    Replanner,
    StepScheduler,
)


def build_plan() -> Plan:
    return Plan(
        goal="Fix pipe-delimited records",
        steps=(
            PlanStep(
                id="reproduce",
                action="run_tests",
                expected_evidence=("pipe test fails",),
            ),
            PlanStep(
                id="inspect",
                action="read_file parser.py",
                dependencies=("reproduce",),
                preconditions=("failure reproduced",),
                expected_evidence=("delimiter code seen",),
            ),
            PlanStep(
                id="patch",
                action="edit parser.py",
                dependencies=("inspect",),
                preconditions=("parser inspected",),
                expected_evidence=("source changed",),
            ),
        ),
    )


def test_valid_plan_and_invalid_order_are_distinguishable() -> None:
    plan = build_plan()
    validator = PlanValidator()

    assert validator.validate(plan).valid is True

    invalid = Plan(
        goal=plan.goal,
        steps=(plan.steps[2], plan.steps[0], plan.steps[1]),
    )
    validation = validator.validate(invalid)

    assert validation.valid is False
    assert "patch appears before dependency inspect" in validation.errors


def test_scheduler_requires_dependencies_and_current_preconditions() -> None:
    plan = build_plan()
    scheduler = StepScheduler()

    assert scheduler.ready_steps(
        plan,
        completed={"reproduce"},
        state_facts=set(),
    ) == ()

    ready = scheduler.ready_steps(
        plan,
        completed={"reproduce"},
        state_facts={"failure reproduced"},
    )

    assert [step.id for step in ready] == ["inspect"]


def test_plan_does_not_become_state_when_a_step_is_ready() -> None:
    plan = build_plan()
    scheduler = StepScheduler()
    completed = {"reproduce"}
    facts = {"failure reproduced"}

    ready = scheduler.ready_steps(
        plan,
        completed=completed,
        state_facts=facts,
    )

    assert ready[0].id == "inspect"
    assert "inspect" not in completed
    assert "parser inspected" not in facts
    assert plan.version == 1


def test_replanner_preserves_completed_work_and_replaces_only_remaining() -> None:
    plan = build_plan()
    decision = Replanner().replace_remaining(
        plan,
        completed={"reproduce"},
        replacement_steps=(
            PlanStep(
                id="inspect_adapter",
                action="read_file csv_adapter.py",
                dependencies=("reproduce",),
                preconditions=("failure reproduced",),
                expected_evidence=("adapter inspected",),
            ),
            PlanStep(
                id="patch_adapter",
                action="edit csv_adapter.py",
                dependencies=("inspect_adapter",),
                preconditions=("adapter inspected",),
                expected_evidence=("source changed",),
            ),
        ),
        reason="observation showed delimiter handling lives in csv_adapter.py",
    )

    assert decision.previous is plan
    assert decision.previous.version == 1
    assert decision.revised.version == 2
    assert decision.preserved_completed == ("reproduce",)
    assert decision.removed_remaining == ("inspect", "patch")
    assert [step.id for step in decision.revised.steps] == [
        "reproduce",
        "inspect_adapter",
        "patch_adapter",
    ]
    assert [step.id for step in plan.steps] == ["reproduce", "inspect", "patch"]


def test_replanner_rejects_replacement_that_depends_on_removed_work() -> None:
    plan = build_plan()

    try:
        Replanner().replace_remaining(
            plan,
            completed={"reproduce"},
            replacement_steps=(
                PlanStep(
                    id="patch_adapter",
                    action="edit csv_adapter.py",
                    dependencies=("inspect",),
                ),
            ),
            reason="bad replacement",
        )
    except ValueError as exc:
        assert "depends on missing inspect" in str(exc)
    else:
        raise AssertionError("invalid replacement plan should be rejected")
