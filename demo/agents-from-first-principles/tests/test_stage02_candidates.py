from first_principles_agent.candidates import (
    Candidate,
    CandidateSelector,
    CandidateSet,
    FixedCandidateGenerator,
    FunctionCandidateEvaluator,
    measure_selection,
)


def candidate_set() -> CandidateSet:
    return CandidateSet.from_iterable(
        [
            Candidate(
                id="A",
                action="edit_file",
                patch="delimiter=','",
                rationale="keeps existing comma behavior",
            ),
            Candidate(
                id="B",
                action="edit_file",
                patch="delimiter='|'",
                rationale="implements pipe-delimited records",
            ),
            Candidate(
                id="C",
                action="edit_file",
                patch="delimiter=None",
                rationale="tries autodetection but violates the task",
            ),
        ]
    )


def true_task_success(candidate: Candidate) -> bool:
    return "delimiter='|'" in candidate.patch


def test_generation_and_selection_are_independent() -> None:
    generated = FixedCandidateGenerator(candidate_set()).generate()

    weak_selector = CandidateSelector(
        FunctionCandidateEvaluator(
            lambda candidate: 1.0 if "comma" in candidate.rationale else 0.2
        )
    )
    strong_selector = CandidateSelector(
        FunctionCandidateEvaluator(
            lambda candidate: 1.0 if true_task_success(candidate) else 0.0
        )
    )

    weak_selected = weak_selector.select_complete(generated)
    strong_selected = strong_selector.select_complete(generated)

    weak = measure_selection(generated, weak_selected, true_task_success)
    strong = measure_selection(generated, strong_selected, true_task_success)

    assert weak.oracle_at_n == 1
    assert weak.selected_success_at_n == 0
    assert weak.selection_gap_at_n == 1
    assert weak.selected_id == "A"

    assert strong.oracle_at_n == 1
    assert strong.selected_success_at_n == 1
    assert strong.selection_gap_at_n == 0
    assert strong.selected_id == "B"

    # Generation did not change; only the evaluator changed.
    assert generated.diversity_count == 3


def test_stage01_ineligible_candidate_cannot_be_selected() -> None:
    candidates = CandidateSet.from_iterable(
        [
            Candidate(
                id="unsafe",
                action="edit_file",
                patch="perfect repair",
                rationale="would score highest",
                accepted_by_stage01=False,
            ),
            Candidate(
                id="allowed",
                action="edit_file",
                patch="safe repair",
                rationale="eligible alternative",
                accepted_by_stage01=True,
            ),
        ]
    )

    selector = CandidateSelector(
        FunctionCandidateEvaluator(
            lambda candidate: 100.0 if candidate.id == "unsafe" else 1.0
        )
    )

    selected = selector.select_complete(candidates)

    assert selected.candidate.id == "allowed"


def test_candidate_set_rejects_duplicate_ids() -> None:
    duplicate = Candidate(
        id="same",
        action="edit_file",
        patch="one",
        rationale="duplicate fixture",
    )

    try:
        CandidateSet.from_iterable([duplicate, duplicate])
    except ValueError as exc:
        assert "unique" in str(exc)
    else:
        raise AssertionError("duplicate candidate ids should be rejected")
