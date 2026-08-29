from first_principles_agent.runtime import (
    Budgets,
    ContinuationDisposition,
    ContinuationPolicy,
    ExecutionTrace,
    LongTermMemory,
    ModelVisibleContext,
    ProgressMeasure,
    RuntimeState,
    StepRecord,
    TerminationReason,
)


def test_same_action_same_state_without_new_evidence_is_nonproductive_cycle() -> None:
    trace = ExecutionTrace([
        StepRecord("read_file parser.py", "parser unchanged", new_evidence=True, progress_delta=1),
        StepRecord("read_file parser.py", "parser unchanged", new_evidence=False, progress_delta=0),
    ])

    decision = ContinuationPolicy().decide(
        RuntimeState(step_count=2, model_calls=2),
        trace,
        Budgets(max_steps=10, max_model_calls=10, no_progress_window=3),
    )

    assert decision.disposition is ContinuationDisposition.RECOVER
    assert decision.reason is TerminationReason.NONPRODUCTIVE_CYCLE


def test_repeated_action_is_productive_when_it_returns_new_evidence() -> None:
    trace = ExecutionTrace([
        StepRecord("run_tests", "one failure", new_evidence=True, progress_delta=1),
        StepRecord("run_tests", "different failure detail", new_evidence=True, progress_delta=1),
    ])

    decision = ContinuationPolicy().decide(
        RuntimeState(step_count=2, model_calls=2),
        trace,
        Budgets(max_steps=10, max_model_calls=10, no_progress_window=2),
    )

    assert decision.disposition is ContinuationDisposition.CONTINUE
    assert decision.reason is None
    assert decision.steps_after_last_progress == 0


def test_no_progress_window_is_measured_from_last_progress_event() -> None:
    trace = ExecutionTrace([
        StepRecord("inspect", "state A", new_evidence=True, progress_delta=1),
        StepRecord("inspect", "state B"),
        StepRecord("inspect", "state C"),
    ])

    measure = ProgressMeasure()
    assert measure.steps_after_last_progress(trace) == 2

    decision = ContinuationPolicy(measure).decide(
        RuntimeState(step_count=3, model_calls=3),
        trace,
        Budgets(max_steps=10, max_model_calls=10, no_progress_window=2),
    )
    assert decision.disposition is ContinuationDisposition.RECOVER
    assert decision.reason is TerminationReason.NO_PROGRESS
    assert decision.steps_after_last_progress == 2


def test_step_and_model_call_budgets_are_independent() -> None:
    policy = ContinuationPolicy()
    trace = ExecutionTrace()

    by_steps = policy.decide(
        RuntimeState(step_count=5, model_calls=1),
        trace,
        Budgets(max_steps=5, max_model_calls=10),
    )
    by_model_calls = policy.decide(
        RuntimeState(step_count=1, model_calls=4),
        trace,
        Budgets(max_steps=10, max_model_calls=4),
    )

    assert by_steps.reason is TerminationReason.MAX_STEPS
    assert by_model_calls.reason is TerminationReason.MAX_MODEL_CALLS
    assert by_steps.disposition is ContinuationDisposition.STOP
    assert by_model_calls.disposition is ContinuationDisposition.STOP


def test_recoverable_and_external_stop_signals_are_named() -> None:
    policy = ContinuationPolicy()
    budgets = Budgets()
    trace = ExecutionTrace()

    missing = policy.decide(
        RuntimeState(missing_precondition="repository must be checked out"),
        trace,
        budgets,
    )
    user = policy.decide(
        RuntimeState(user_input_request="choose deployment environment"),
        trace,
        budgets,
    )
    success = policy.decide(
        RuntimeState(success_signal=True),
        trace,
        budgets,
    )

    assert missing.disposition is ContinuationDisposition.RECOVER
    assert missing.reason is TerminationReason.PRECONDITION_MISSING
    assert user.disposition is ContinuationDisposition.STOP
    assert user.reason is TerminationReason.USER_INPUT_REQUIRED
    assert success.disposition is ContinuationDisposition.STOP
    assert success.reason is TerminationReason.SUCCESS
    assert "Stage 09" in (success.detail or "")


def test_runtime_state_context_trace_and_memory_are_distinct_objects() -> None:
    state = RuntimeState(facts=frozenset({"parser unchanged"}))
    context = ModelVisibleContext(
        summary="parser still appears to use a fixed comma delimiter",
        facts=("parser unchanged",),
    )
    trace = ExecutionTrace([
        StepRecord("read_file parser.py", "parser unchanged", new_evidence=True),
    ])
    memory = LongTermMemory()

    assert state is not context
    assert trace is not memory
    assert state.facts == frozenset({"parser unchanged"})
    assert context.summary.startswith("parser")
    assert memory.entries == ()


def test_budget_validation_rejects_nonpositive_limits() -> None:
    try:
        Budgets(max_steps=0)
    except ValueError as error:
        assert "max_steps" in str(error)
    else:
        raise AssertionError("max_steps=0 should be rejected")
