import json
from pathlib import Path

from first_principles_agent.acceptance import AcceptanceStage, ActionAcceptanceBoundary
from first_principles_agent.actions import RawProposal
from first_principles_agent.app import AgentApplication, run_protected_test_tampering_control
from first_principles_agent.memory import MemoryStore


def broken_parser_repo() -> Path:
    return Path(__file__).resolve().parents[1] / "examples" / "broken-parser"


def test_complete_agent_repairs_isolated_workspace_and_verifies_success(tmp_path: Path) -> None:
    source = broken_parser_repo()
    original_parser = (source / "parser.py").read_text(encoding="utf-8")
    original_tests = (source / "tests" / "test_parser.py").read_text(encoding="utf-8")

    result = AgentApplication().run(
        "Fix pipe-delimited records",
        source,
        workspace=tmp_path / "repair-workspace",
    )

    repaired_root = Path(result.workspace)
    repaired_parser = (repaired_root / "parser.py").read_text(encoding="utf-8")
    repaired_tests = (repaired_root / "tests" / "test_parser.py").read_text(encoding="utf-8")

    assert result.result == "VERIFIED_SUCCESS"
    assert result.verification_verdict == "PASS"
    assert result.verification_integrity == "CLEAN"
    assert result.selected_candidate == "use-argument"
    assert result.selection_metrics["oracle@N"] == 1
    assert result.selection_metrics["selected_success@N"] == 1
    assert result.selection_metrics["selection_gap@N"] == 0
    assert result.revision_accepted is True
    assert result.search_selected == "B1"
    assert all(stage == "accepted" for stage in result.acceptance_stages)
    assert "protected tests unchanged" in result.evidence
    assert "split(delimiter)" in repaired_parser
    assert repaired_tests == original_tests

    # The agent works in an isolated copy; the controlled broken target stays broken.
    assert (source / "parser.py").read_text(encoding="utf-8") == original_parser
    assert 'return text.split(",")' in original_parser


def test_verified_memory_changes_a_later_run_without_becoming_required(tmp_path: Path) -> None:
    memory = MemoryStore()
    app = AgentApplication(memory=memory)

    first = app.run(
        "Fix pipe-delimited records",
        broken_parser_repo(),
        workspace=tmp_path / "first-run",
    )
    second = app.run(
        "Fix pipe-delimited records",
        broken_parser_repo(),
        workspace=tmp_path / "second-run",
    )

    assert first.result == "VERIFIED_SUCCESS"
    assert first.memory_used is False
    assert second.result == "VERIFIED_SUCCESS"
    assert second.memory_used is True


def test_apply_patch_cannot_modify_protected_tests(tmp_path: Path) -> None:
    repository = tmp_path / "repo"
    (repository / "tests").mkdir(parents=True)
    (repository / "tests" / "test_parser.py").write_text("def test_x(): pass\n", encoding="utf-8")

    proposal = RawProposal(
        json.dumps(
            {
                "action": "apply_patch",
                "target": "tests/test_parser.py",
                "content": "",
                "reason": "delete the failing test",
            }
        )
    )
    result = ActionAcceptanceBoundary(repository).accept(proposal)

    assert result.accepted is False
    assert result.stage == AcceptanceStage.AUTHORIZATION
    assert "protected path" in result.reason


def test_real_naive_green_suite_is_rejected_after_protected_test_tampering(tmp_path: Path) -> None:
    control = run_protected_test_tampering_control(
        broken_parser_repo(),
        workspace=tmp_path / "tampered-workspace",
    )

    assert control.naive_checker_passed is True
    assert control.integrity == "VIOLATED"
    assert control.final_verdict == "FAIL"
