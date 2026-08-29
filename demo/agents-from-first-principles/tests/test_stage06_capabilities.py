from __future__ import annotations

from pathlib import Path

from first_principles_agent.acceptance import AcceptanceStage, ActionAcceptanceBoundary
from first_principles_agent.actions import ActionKind
from first_principles_agent.capabilities import (
    Capability,
    CapabilityCase,
    CapabilityExecutor,
    CapabilityNeed,
    CapabilityOutcome,
    CapabilityPipeline,
    CapabilityRegistry,
    ExposurePolicy,
    evaluate_capability_routing,
)
from first_principles_agent.environment import RepositoryEnvironment
from first_principles_agent.runtime import RuntimeState


def registry() -> CapabilityRegistry:
    return CapabilityRegistry(
        [
            Capability(
                name="search_code",
                purpose="find unknown file paths by query text",
                action_kind=ActionKind.SEARCH_CODE,
                eligible_when=frozenset({"repo_available"}),
                keywords=frozenset(
                    {"search", "code", "unknown", "path", "query", "text", "logic", "contains"}
                ),
                output_schema=("query", "matches"),
            ),
            Capability(
                name="read_file",
                purpose="read exact known path content",
                action_kind=ActionKind.READ_FILE,
                eligible_when=frozenset({"path_known"}),
                keywords=frozenset({"read", "exact", "known", "path", "content", "file"}),
                output_schema=("path", "content"),
            ),
            Capability(
                name="find_symbol",
                purpose="resolve Python symbol definition",
                action_kind=ActionKind.FIND_SYMBOL,
                eligible_when=frozenset({"repo_available"}),
                keywords=frozenset({"find", "resolve", "python", "symbol", "definition", "function", "class"}),
                output_schema=("symbol", "locations"),
            ),
        ]
    )


def test_exposure_reduces_action_space_without_granting_authority() -> None:
    available = registry()
    exposure = ExposurePolicy()

    unknown_path = RuntimeState(facts=frozenset({"repo_available"}))
    exposed = {capability.name for capability in exposure.expose(available, unknown_path)}
    assert exposed == {"search_code", "find_symbol"}

    known_path = RuntimeState(facts=frozenset({"repo_available", "path_known"}))
    exposed = {capability.name for capability in exposure.expose(available, known_path)}
    assert exposed == {"search_code", "read_file", "find_symbol"}


def test_routing_metrics_cover_selection_and_abstention() -> None:
    pipeline = CapabilityPipeline(registry(), retrieval_k=2)
    cases = [
        CapabilityCase(
            state=RuntimeState(facts=frozenset({"repo_available"})),
            need=CapabilityNeed("search code for unknown delimiter logic", target="delimiter"),
            expected_outcome=CapabilityOutcome.TOOL,
            expected_capability="search_code",
        ),
        CapabilityCase(
            state=RuntimeState(facts=frozenset({"repo_available", "path_known"})),
            need=CapabilityNeed("read known file content", target="parser.py"),
            expected_outcome=CapabilityOutcome.TOOL,
            expected_capability="read_file",
        ),
        CapabilityCase(
            state=RuntimeState(facts=frozenset({"repo_available"})),
            need=CapabilityNeed("find definition of Python symbol", target="split_record"),
            expected_outcome=CapabilityOutcome.TOOL,
            expected_capability="find_symbol",
        ),
        CapabilityCase(
            state=RuntimeState(),
            need=CapabilityNeed("which branch should I use?", requires_user_input=True),
            expected_outcome=CapabilityOutcome.ASK_USER,
        ),
        CapabilityCase(
            state=RuntimeState(facts=frozenset({"repo_available"})),
            need=CapabilityNeed(
                "edit parser.py",
                target="parser.py",
                required_facts=frozenset({"write_permission"}),
            ),
            expected_outcome=CapabilityOutcome.MISSING_PRECONDITION,
        ),
        CapabilityCase(
            state=RuntimeState(facts=frozenset({"repo_available"})),
            need=CapabilityNeed("summarize architecture diagram"),
            expected_outcome=CapabilityOutcome.NO_TOOL,
        ),
    ]

    metrics = evaluate_capability_routing(pipeline, cases)
    assert metrics.capability_coverage == 1.0
    assert metrics.tool_recall_at_k == 1.0
    assert metrics.selection_accuracy_given_available == 1.0
    assert metrics.wrong_tool_rate == 0.0
    assert metrics.abstention_accuracy == 1.0


def test_exposed_read_tool_can_still_be_rejected_by_stage01(tmp_path: Path) -> None:
    pipeline = CapabilityPipeline(registry())
    state = RuntimeState(facts=frozenset({"repo_available", "path_known"}))
    decision = pipeline.route(
        state,
        CapabilityNeed("read known file content", target="../secret.txt"),
    )
    assert decision.selected is not None
    assert decision.selected.name == "read_file"

    class MustNotExecute:
        def execute(self, action):
            raise AssertionError("authorization failure must prevent execution")

    result = CapabilityExecutor().execute(
        decision,
        ActionAcceptanceBoundary(tmp_path),
        MustNotExecute(),
    )
    assert result.acceptance.accepted is False
    assert result.acceptance.stage == AcceptanceStage.AUTHORIZATION
    assert result.observation is None


def test_selected_search_crosses_acceptance_and_returns_structured_observation() -> None:
    demo_root = Path(__file__).resolve().parents[1]
    target = demo_root / "examples" / "broken-parser"
    state = RuntimeState(facts=frozenset({"repo_available"}))
    pipeline = CapabilityPipeline(registry())

    decision = pipeline.route(
        state,
        CapabilityNeed("search code for delimiter logic", target="delimiter"),
    )
    execution = CapabilityExecutor().execute(
        decision,
        ActionAcceptanceBoundary(target),
        RepositoryEnvironment(target),
    )

    assert execution.acceptance.accepted is True
    assert execution.observation is not None
    assert execution.observation.capability == "search_code"
    matches = execution.observation.data["matches"]
    assert isinstance(matches, list)
    assert any(item["path"] == "parser.py" for item in matches)


def test_find_symbol_returns_locations_not_free_form_authority() -> None:
    demo_root = Path(__file__).resolve().parents[1]
    target = demo_root / "examples" / "broken-parser"
    state = RuntimeState(facts=frozenset({"repo_available"}))
    pipeline = CapabilityPipeline(registry())

    decision = pipeline.route(
        state,
        CapabilityNeed("find definition of Python symbol", target="split_record"),
    )
    execution = CapabilityExecutor().execute(
        decision,
        ActionAcceptanceBoundary(target),
        RepositoryEnvironment(target),
    )

    assert execution.observation is not None
    locations = execution.observation.data["locations"]
    assert isinstance(locations, list)
    assert locations == [{"path": "parser.py", "line": 1, "kind": "FunctionDef"}]
