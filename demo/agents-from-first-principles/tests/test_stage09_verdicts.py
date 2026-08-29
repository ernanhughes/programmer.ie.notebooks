from first_principles_agent.verification import (
    Adjudicator,
    EvidenceCollector,
    EvidenceLayer,
    EvidenceSet,
    GoalContract,
    IntegrityReport,
    IntegrityStatus,
    StateIdentity,
    Verdict,
)


def test_partial_required_criterion_produces_partial_verdict() -> None:
    contract = GoalContract(
        must_change=("pipe records accepted",),
        must_preserve=("comma records still pass",),
    )
    state_id = StateIdentity("state-current")
    collector = EvidenceCollector()
    evidence = EvidenceSet(
        (
            collector.collect(
                evidence_id="pipe-partial",
                criterion="pipe records accepted",
                layer=EvidenceLayer.GOAL_SATISFACTION,
                source="partial checker",
                state_id=state_id,
                contract=contract,
                verdict=Verdict.PARTIAL,
                collected_at=1,
            ),
            collector.collect(
                evidence_id="comma-pass",
                criterion="comma records still pass",
                layer=EvidenceLayer.GOAL_SATISFACTION,
                source="regression checker",
                state_id=state_id,
                contract=contract,
                verdict=Verdict.PASS,
                collected_at=1,
            ),
        )
    )

    result = Adjudicator().decide(
        contract=contract,
        evidence=evidence,
        state_id=state_id,
        integrity=IntegrityReport.clean(),
    )

    assert result.verdict == Verdict.PARTIAL
    assert result.verification_coverage == 1.0


def test_unknown_integrity_prevents_pass_even_with_complete_goal_evidence() -> None:
    contract = GoalContract(must_change=("pipe records accepted",))
    state_id = StateIdentity("state-current")
    collector = EvidenceCollector()
    evidence = EvidenceSet(
        (
            collector.collect(
                evidence_id="pipe-pass",
                criterion="pipe records accepted",
                layer=EvidenceLayer.GOAL_SATISFACTION,
                source="targeted checker",
                state_id=state_id,
                contract=contract,
                verdict=Verdict.PASS,
                collected_at=1,
            ),
        )
    )

    result = Adjudicator().decide(
        contract=contract,
        evidence=evidence,
        state_id=state_id,
        integrity=IntegrityReport(IntegrityStatus.UNKNOWN),
    )

    assert result.verdict == Verdict.UNKNOWN
