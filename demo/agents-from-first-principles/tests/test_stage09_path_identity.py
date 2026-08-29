import pytest

from first_principles_agent.verification import (
    IntegrityStatus,
    ProtectedPathVerifier,
    StateIdentity,
    WorkspaceSnapshot,
)


def test_workspace_snapshot_canonicalizes_windows_style_paths() -> None:
    snapshot = WorkspaceSnapshot.from_mapping(
        {"tests\\test_parser.py": "test_pipe_delimiter\n"}
    )

    assert snapshot.as_dict() == {
        "tests/test_parser.py": "test_pipe_delimiter\n"
    }


def test_protected_path_verifier_detects_windows_style_snapshot_modification() -> None:
    baseline = WorkspaceSnapshot.from_mapping(
        {"tests\\test_parser.py": "test_comma\ntest_pipe\n"}
    )
    current = WorkspaceSnapshot.from_mapping(
        {"tests\\test_parser.py": "test_comma\n"}
    )

    integrity = ProtectedPathVerifier(
        baseline,
        ["tests/test_parser.py"],
    ).check(current)

    assert integrity.status == IntegrityStatus.VIOLATED
    assert integrity.violations == (
        "protected path modified: tests/test_parser.py",
    )


def test_state_identity_is_independent_of_path_separator_style() -> None:
    windows = StateIdentity.from_files(
        {"tests\\test_parser.py": "same content"}
    )
    posix = StateIdentity.from_files(
        {"tests/test_parser.py": "same content"}
    )

    assert windows == posix


def test_conflicting_aliases_for_same_canonical_path_are_rejected() -> None:
    with pytest.raises(ValueError, match="conflicting contents"):
        WorkspaceSnapshot.from_mapping(
            {
                "tests\\test_parser.py": "before",
                "tests/test_parser.py": "after",
            }
        )
