from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlanStep:
    """One intended future step.

    A step records relationships that matter to correctness. It is not runtime
    state and does not become true merely because it appears in a plan.
    """

    id: str
    action: str
    dependencies: tuple[str, ...] = ()
    preconditions: tuple[str, ...] = ()
    expected_evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class Plan:
    """A versioned hypothesis about a route from current state to a goal."""

    goal: str
    steps: tuple[PlanStep, ...]
    version: int = 1
    reason: str | None = None

    def step(self, step_id: str) -> PlanStep:
        for step in self.steps:
            if step.id == step_id:
                return step
        raise KeyError(step_id)


@dataclass(frozen=True)
class PlanValidation:
    valid: bool
    errors: tuple[str, ...]


class PlanValidator:
    """Validate structural relationships inside an ordered plan."""

    def validate(self, plan: Plan) -> PlanValidation:
        errors: list[str] = []
        ids = [step.id for step in plan.steps]

        duplicates = sorted({step_id for step_id in ids if ids.count(step_id) > 1})
        for duplicate in duplicates:
            errors.append(f"duplicate step id: {duplicate}")

        all_ids = set(ids)
        seen: set[str] = set()
        for step in plan.steps:
            if step.id in step.dependencies:
                errors.append(f"{step.id} depends on itself")

            for dependency in step.dependencies:
                if dependency not in all_ids:
                    errors.append(f"{step.id} depends on missing {dependency}")
                elif dependency not in seen:
                    errors.append(
                        f"{step.id} appears before dependency {dependency}"
                    )

            seen.add(step.id)

        return PlanValidation(valid=not errors, errors=tuple(errors))

    def require_valid(self, plan: Plan) -> None:
        validation = self.validate(plan)
        if not validation.valid:
            raise ValueError("; ".join(validation.errors))


class StepScheduler:
    """Choose steps whose dependencies and current preconditions are satisfied."""

    def __init__(self, validator: PlanValidator | None = None) -> None:
        self.validator = validator or PlanValidator()

    def ready_steps(
        self,
        plan: Plan,
        *,
        completed: set[str] | frozenset[str],
        state_facts: set[str] | frozenset[str],
    ) -> tuple[PlanStep, ...]:
        self.validator.require_valid(plan)

        known_ids = {step.id for step in plan.steps}
        unknown_completed = set(completed) - known_ids
        if unknown_completed:
            names = ", ".join(sorted(unknown_completed))
            raise ValueError(f"completed set contains unknown plan steps: {names}")

        return tuple(
            step
            for step in plan.steps
            if step.id not in completed
            and set(step.dependencies) <= set(completed)
            and set(step.preconditions) <= set(state_facts)
        )


@dataclass(frozen=True)
class ReplanDecision:
    previous: Plan
    revised: Plan
    preserved_completed: tuple[str, ...]
    removed_remaining: tuple[str, ...]
    reason: str


class Replanner:
    """Replace only uncompleted intended work after evidence changes the route."""

    def __init__(self, validator: PlanValidator | None = None) -> None:
        self.validator = validator or PlanValidator()

    def replace_remaining(
        self,
        plan: Plan,
        *,
        completed: set[str] | frozenset[str],
        replacement_steps: tuple[PlanStep, ...],
        reason: str,
    ) -> ReplanDecision:
        self.validator.require_valid(plan)

        known_ids = {step.id for step in plan.steps}
        unknown_completed = set(completed) - known_ids
        if unknown_completed:
            names = ", ".join(sorted(unknown_completed))
            raise ValueError(f"completed set contains unknown plan steps: {names}")

        preserved_steps = tuple(
            step for step in plan.steps if step.id in completed
        )
        preserved_ids = {step.id for step in preserved_steps}

        replacement_ids = [step.id for step in replacement_steps]
        reused_completed = preserved_ids.intersection(replacement_ids)
        if reused_completed:
            names = ", ".join(sorted(reused_completed))
            raise ValueError(
                f"replacement cannot redefine completed steps: {names}"
            )

        removed_remaining = tuple(
            step.id for step in plan.steps if step.id not in completed
        )

        revised = Plan(
            goal=plan.goal,
            steps=preserved_steps + tuple(replacement_steps),
            version=plan.version + 1,
            reason=reason,
        )
        self.validator.require_valid(revised)

        return ReplanDecision(
            previous=plan,
            revised=revised,
            preserved_completed=tuple(step.id for step in preserved_steps),
            removed_remaining=removed_remaining,
            reason=reason,
        )
