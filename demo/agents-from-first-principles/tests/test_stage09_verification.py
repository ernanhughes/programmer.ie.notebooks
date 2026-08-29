from first_principles_agent.verification import (
    Adjudicator,
    ContractIntegrityVerifier,
    EvidenceCollector,
    EvidenceLayer,
    EvidenceSet,
    GoalContract,
    IntegrityStatus,
    ProtectedPathVerifier,
    StateIdentity,
    Verdict,
    WorkspaceSnapshot,
    combine_integrity,
)


def contract() -> GoalContract:
    return GoalContract(
        must_change=("pipe records accepted",),
        must_preserve=("comma records still pass",),
        must_not=("delete protected tests", "weaken goal contract"),
    )


def baseline_workspace() -> WorkspaceSnapshot:
    return WorkspaceSnapshot.from_mapping(
        {
            "parser.py": 'return text.split(",")',
            "tests/test_parser.py": "test_comma\ntest_pipe\n",
        }
    )


def collect_passes(state_id: StateIdentity, goal: GoalContract) -> EvidenceSet:
    collector = EvidenceCollector(verifier_version="stage09-test")
    return EvidenceSet(
        (
            collector.collect(
                evidence_id="pipe-pass",
                criterion="pipe records accepted",
                layer=EvidenceLayer.GOAL_SATISFACTION,
                source="targeted pytest",
                state_id=state_id,
                contract=goal,
                verdict=Verdict.PASS,
                collected_at=1,
            ),
            collector.collect(
                evidence_id="comma-pass",
                criterion="comma records still pass",
                layer=EvidenceLayer.GOAL_SATISFACTION,
                source="regression pytest",
                state_id=state_id,
                contract=goal,
                verdict=Verdict.PASS,
                collected_at=1,
            ),
        )
    )


def test_clean_current_goal_evidence_can_earn_pass() -> None:
    goal = contract()
    fixed = WorkspaceSnapshot.from_mapping(
        {
            "parser.py": "return text.split(delimiter)",
            "tests/test_parser.py": "test_comma\ntest_pipe\n",
        }
    )
    evidence = collect_passes(fixed.state_id, goal)
    integrity = ProtectedPathVerifier(
        baseline_workspace(), ["tests/test_parser.py"]
    ).check(fixed)

    result = Adjudicator().decide(
        contract=goal,
        evidence=evidence,
        state_id=fixed.state_id,
        integrity=integrity,
    )

    assert integrity.status == IntegrityStatus.CLEAN
    assert result.verdict == Verdict.PASS
    assert result.verification_coverage == 1.0


def test_action_receipt_pass_cannot_be_promoted_to_goal_success() -> None:
    goal = contract()
    state = baseline_workspace().state_id
    collector = EvidenceCollector()
    evidence = EvidenceSet(
        (
            collector.collect(
                evidence_id="command-returned-zero",
                criterion="pipe records accepted",
                layer=EvidenceLayer.ACTION_RECEIPT,
                source="tool receipt",
                state_id=state,
                contract=goal,
                verdict=Verdict.PASS,
                collected_at=1,
            ),
        )
    )

    result = Adjudicator().decide(
        contract=goal,
        evidence=evidence,
        state_id=state,
        integrity=combine_integrity(),
    )

    assert result.verdict == Verdict.UNKNOWN
    assert result.verification_coverage == 0.0


def test_evidence_becomes_stale_after_state_changes() -> None:
    goal = contract()
    state_a = baseline_workspace()
    state_b = WorkspaceSnapshot.from_mapping(
        {
            "parser.py": "changed after verification",
            "tests/test_parser.py": "test_comma\ntest_pipe\n",
        }
    )
    evidence = collect_passes(state_a.state_id, goal)

    result = Adjudicator().decide(
        contract=goal,
        evidence=evidence,
        state_id=state_b.state_id,
        integrity=combine_integrity(),
    )

    assert result.verdict == Verdict.UNKNOWN
    assert set(result.stale_evidence_ids) == {"pipe-pass", "comma-pass"}
    assert result.verification_coverage == 0.0


def test_naive_task_pass_cannot_override_protected_test_modification() -> None:
    goal = contract()
    baseline = baseline_workspace()
    tampered = WorkspaceSnapshot.from_mapping(
        {
            "parser.py": 'return text.split(",")',
            "tests/test_parser.py": "test_comma\n",  # failing protected test removed
        }
    )
    evidence = collect_passes(tampered.state_id, goal)
    integrity = ProtectedPathVerifier(
        baseline, ["tests/test_parser.py"]
    ).check(tampered)

    result = Adjudicator().decide(
        contract=goal,
        evidence=evidence,
        state_id=tampered.state_id,
        integrity=integrity,
    )

    assert all(item.verdict == Verdict.PASS for item in result.criteria)
    assert integrity.status == IntegrityStatus.VIOLATED
    assert "protected path modified" in integrity.violations[0]
    assert result.verdict == Verdict.FAIL


def test_deleting_protected_test_is_integrity_violation() -> None:
    baseline = baseline_workspace()
    deleted = WorkspaceSnapshot.from_mapping(
        {"parser.py": "return text.split(delimiter)"}
    )

    integrity = ProtectedPathVerifier(
        baseline, ["tests/test_parser.py"]
    ).check(deleted)

    assert integrity.status == IntegrityStatus.VIOLATED
    assert integrity.violations == (
        "protected path deleted: tests/test_parser.py",
    )


def test_forbidden_goal_contract_event_forces_failure() -> None:
    goal = contract()
    fixed = WorkspaceSnapshot.from_mapping(
        {
            "parser.py": "return text.split(delimiter)",
            "tests/test_parser.py": "test_comma\ntest_pipe\n",
        }
    )
    evidence = collect_passes(fixed.state_id, goal)
    path_integrity = ProtectedPathVerifier(
        baseline_workspace(), ["tests/test_parser.py"]
    ).check(fixed)
    contract_integrity = ContractIntegrityVerifier().check(
        goal,
        observed_events=("weaken goal contract",),
    )

    result = Adjudicator().decide(
        contract=goal,
        evidence=evidence,
        state_id=fixed.state_id,
        integrity=combine_integrity(path_integrity, contract_integrity),
    )

    assert result.integrity.status == IntegrityStatus.VIOLATED
    assert result.verdict == Verdict.FAIL


def test_evidence_for_weakened_contract_does_not_satisfy_original_contract() -> None:
    original = contract()
    weakened = GoalContract(
        must_change=("pipe records accepted",),
        must_preserve=(),
        must_not=(),
    )
    state = baseline_workspace().state_id
    collector = EvidenceCollector()
    evidence = EvidenceSet(
        (
            collector.collect(
                evidence_id="weakened-pass",
                criterion="pipe records accepted",
                layer=EvidenceLayer.GOAL_SATISFACTION,
                source="task checker",
                state_id=state,
                contract=weakened,
                verdict=Verdict.PASS,
                collected_at=1,
            ),
        )
    )

    result = Adjudicator().decide(
        contract=original,
        evidence=evidence,
        state_id=state,
        integrity=combine_integrity(),
    )

    assert result.verdict == Verdict.UNKNOWN
    assert result.verification_coverage == 0.0
