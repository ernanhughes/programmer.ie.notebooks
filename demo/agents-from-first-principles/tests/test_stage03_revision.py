from first_principles_agent.candidates import Candidate
from first_principles_agent.revision import (
    Critique,
    EvidenceSet,
    FixedCritic,
    FunctionReviser,
    RevisionGate,
    measure_revision,
    refine_once,
)


def task_value(candidate: Candidate, _evidence: EvidenceSet) -> float:
    fragments = (
        "pipe delimiter",
        "parser.py",
        "keep comma records working",
    )
    return float(sum(fragment in candidate.patch for fragment in fragments))


def adherence(candidate: Candidate, critique: Critique) -> bool:
    if critique.target == "delimiter handling":
        return "pipe delimiter" in candidate.patch
    return False


def integrity(candidate: Candidate, _evidence: EvidenceSet) -> str | None:
    if "delete failing test" in candidate.patch.lower():
        return "protected test would be removed"
    return None


def gate() -> RevisionGate:
    return RevisionGate(
        value_function=task_value,
        adherence_check=adherence,
        integrity_check=integrity,
    )


def old_candidate() -> Candidate:
    return Candidate(
        id="A",
        action="repair_proposal",
        patch="Check for empty lines.",
        rationale="initial diagnosis focused on empty records",
    )


def critique() -> Critique:
    return Critique(
        defect="misses delimiter failure",
        evidence=("pytest shows pipe-delimited record fails",),
        target="delimiter handling",
    )


def test_useful_targeted_revision_is_accepted() -> None:
    old = old_candidate()
    evidence = EvidenceSet.from_iterable(
        ["pytest shows pipe-delimited record fails"]
    )
    critic = FixedCritic(critique())
    reviser = FunctionReviser(
        lambda candidate, _critique: Candidate(
            id=f"{candidate.id}-r1",
            action=candidate.action,
            patch=(
                "Update parser.py for pipe delimiter and keep comma records working."
            ),
            rationale="target the observed delimiter defect",
            accepted_by_stage01=candidate.accepted_by_stage01,
        )
    )

    decision = refine_once(
        old,
        critic=critic,
        reviser=reviser,
        gate=gate(),
        evidence=evidence,
    )

    assert decision.accepted is True
    assert decision.resulting == decision.proposed
    assert decision.rolled_back is False
    assert decision.revision_adherence is True
    assert decision.value_delta > 0

    diagnostics = measure_revision(
        decision,
        expected_defect="misses delimiter failure",
        should_accept=True,
    )
    assert diagnostics.critic_quality is True
    assert diagnostics.revision_adherence is True
    assert diagnostics.revision_value > 0
    assert diagnostics.acceptance_quality is True


def test_harmful_revision_rolls_back_even_if_it_looks_like_a_shortcut() -> None:
    old = old_candidate()
    evidence = EvidenceSet.from_iterable(
        ["pytest shows pipe-delimited record fails"]
    )
    critic = FixedCritic(critique())
    reviser = FunctionReviser(
        lambda candidate, _critique: Candidate(
            id=f"{candidate.id}-bad",
            action=candidate.action,
            patch="Handle pipe delimiter by delete failing test and report success.",
            rationale="shortcut the failing evidence",
            accepted_by_stage01=candidate.accepted_by_stage01,
        )
    )

    decision = refine_once(
        old,
        critic=critic,
        reviser=reviser,
        gate=gate(),
        evidence=evidence,
    )

    assert decision.accepted is False
    assert decision.rolled_back is True
    assert decision.resulting == old
    assert decision.integrity_violation == "protected test would be removed"
    assert "protected constraint" in decision.reason

    diagnostics = measure_revision(
        decision,
        expected_defect="misses delimiter failure",
        should_accept=False,
    )
    assert diagnostics.critic_quality is True
    assert diagnostics.revision_adherence is True
    assert diagnostics.acceptance_quality is True


def test_revision_that_does_not_address_the_target_rolls_back() -> None:
    old = old_candidate()
    evidence = EvidenceSet.from_iterable(
        ["pytest shows pipe-delimited record fails"]
    )
    critic = FixedCritic(critique())
    reviser = FunctionReviser(
        lambda candidate, _critique: Candidate(
            id=f"{candidate.id}-offtarget",
            action=candidate.action,
            patch="Improve empty-line handling in parser.py.",
            rationale="changes code but not the diagnosed defect",
            accepted_by_stage01=candidate.accepted_by_stage01,
        )
    )

    decision = refine_once(
        old,
        critic=critic,
        reviser=reviser,
        gate=gate(),
        evidence=evidence,
    )

    assert decision.accepted is False
    assert decision.revision_adherence is False
    assert decision.resulting == old
    assert decision.reason == "revision does not address the critique target"


def test_critic_quality_is_not_inferred_from_revision_acceptance() -> None:
    old = old_candidate()
    evidence = EvidenceSet.from_iterable(
        ["pytest shows pipe-delimited record fails"]
    )
    wrong_critique = Critique(
        defect="whitespace normalization failure",
        evidence=("guess from source style",),
        target="delimiter handling",
    )
    critic = FixedCritic(wrong_critique)
    reviser = FunctionReviser(
        lambda candidate, _critique: Candidate(
            id=f"{candidate.id}-lucky",
            action=candidate.action,
            patch=(
                "Update parser.py for pipe delimiter and keep comma records working."
            ),
            rationale="the intervention helps despite the wrong defect label",
            accepted_by_stage01=candidate.accepted_by_stage01,
        )
    )

    decision = refine_once(
        old,
        critic=critic,
        reviser=reviser,
        gate=gate(),
        evidence=evidence,
    )
    diagnostics = measure_revision(
        decision,
        expected_defect="misses delimiter failure",
        should_accept=True,
    )

    assert decision.accepted is True
    assert diagnostics.critic_quality is False
    assert diagnostics.revision_value > 0
    assert diagnostics.acceptance_quality is True
