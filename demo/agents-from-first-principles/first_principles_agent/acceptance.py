from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .actions import Action, ActionKind, RawProposal


class AcceptanceStage(str, Enum):
    REPRESENTATION = "representation"
    SCHEMA = "schema"
    SEMANTICS = "semantics"
    AUTHORIZATION = "authorization"
    PRECONDITIONS = "preconditions"
    ACCEPTED = "accepted"


@dataclass(frozen=True)
class AcceptanceResult:
    accepted: bool
    stage: AcceptanceStage
    reason: str
    action: Action | None = None
    proposal_text: str | None = None


class DirectActionAcceptance:
    """Stage-00 adapter: trust an already-typed Action."""

    def accept(self, proposal: Action | RawProposal) -> AcceptanceResult:
        if not isinstance(proposal, Action):
            return AcceptanceResult(
                accepted=False,
                stage=AcceptanceStage.SCHEMA,
                reason="Stage 00 accepts only an already-typed Action",
                proposal_text=getattr(proposal, "text", None),
            )
        return AcceptanceResult(
            accepted=True,
            stage=AcceptanceStage.ACCEPTED,
            reason="trusted typed Stage-00 action",
            action=proposal,
        )


class ActionAcceptanceBoundary:
    """Turn an untrusted raw proposal into an executable typed Action."""

    _allowed_keys = {"action", "target", "reason", "content"}
    _target_required = {
        ActionKind.READ_FILE,
        ActionKind.SEARCH_CODE,
        ActionKind.FIND_SYMBOL,
        ActionKind.RUN_TARGETED_TESTS,
        ActionKind.APPLY_PATCH,
    }
    _target_forbidden = {
        ActionKind.RUN_TESTS,
        ActionKind.INSPECT_DIFF,
        ActionKind.STOP,
    }

    def __init__(self, repository_root: str | Path) -> None:
        self.repository_root = Path(repository_root).resolve()

    def accept(self, proposal: Action | RawProposal) -> AcceptanceResult:
        if not isinstance(proposal, RawProposal):
            return self._reject(
                AcceptanceStage.REPRESENTATION,
                "Stage 01 requires a raw proposal rather than an executable Action",
            )

        raw = proposal.text
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            return self._reject(
                AcceptanceStage.REPRESENTATION,
                f"proposal is not valid JSON: {exc.msg}",
                raw,
            )

        if not isinstance(parsed, dict):
            return self._reject(AcceptanceStage.SCHEMA, "proposal must decode to a JSON object", raw)

        unknown = set(parsed) - self._allowed_keys
        if unknown:
            return self._reject(
                AcceptanceStage.SCHEMA,
                f"unexpected fields: {', '.join(sorted(unknown))}",
                raw,
            )

        if "action" not in parsed or not isinstance(parsed["action"], str):
            return self._reject(
                AcceptanceStage.SCHEMA,
                "field 'action' is required and must be a string",
                raw,
            )

        for key in ("target", "reason", "content"):
            value = parsed.get(key)
            if value is not None and not isinstance(value, str):
                return self._reject(
                    AcceptanceStage.SCHEMA,
                    f"field '{key}' must be a string or null",
                    raw,
                )

        try:
            kind = ActionKind(parsed["action"])
        except ValueError:
            return self._reject(
                AcceptanceStage.SEMANTICS,
                f"unsupported action kind: {parsed['action']!r}",
                raw,
            )

        target = parsed.get("target")
        reason = parsed.get("reason")
        content = parsed.get("content")

        if kind in self._target_required and (target is None or not target.strip()):
            return self._reject(
                AcceptanceStage.SEMANTICS,
                f"{kind.value} requires a non-empty target",
                raw,
            )
        if kind in self._target_forbidden and target is not None:
            return self._reject(
                AcceptanceStage.SEMANTICS,
                f"{kind.value} does not accept a target",
                raw,
            )
        if kind == ActionKind.APPLY_PATCH and content is None:
            return self._reject(
                AcceptanceStage.SEMANTICS,
                "apply_patch requires replacement content",
                raw,
            )
        if kind != ActionKind.APPLY_PATCH and content is not None:
            return self._reject(
                AcceptanceStage.SEMANTICS,
                f"{kind.value} does not accept replacement content",
                raw,
            )

        action = Action(kind=kind, target=target, reason=reason, content=content)
        authorization_error = self._authorization_error(action)
        if authorization_error is not None:
            return self._reject(AcceptanceStage.AUTHORIZATION, authorization_error, raw)

        precondition_error = self._precondition_error(action)
        if precondition_error is not None:
            return self._reject(AcceptanceStage.PRECONDITIONS, precondition_error, raw)

        return AcceptanceResult(
            accepted=True,
            stage=AcceptanceStage.ACCEPTED,
            reason="proposal passed all acceptance stages",
            action=action,
            proposal_text=raw,
        )

    def _candidate_path(self, target: str) -> Path:
        path_part = target.split("::", 1)[0]
        return (self.repository_root / path_part).resolve()

    def _authorization_error(self, action: Action) -> str | None:
        if action.kind not in {
            ActionKind.READ_FILE,
            ActionKind.RUN_TARGETED_TESTS,
            ActionKind.APPLY_PATCH,
        }:
            return None

        assert action.target is not None
        candidate = self._candidate_path(action.target)
        try:
            relative = candidate.relative_to(self.repository_root)
        except ValueError:
            return f"{action.kind.value} target escapes the authorized repository root"

        if action.kind == ActionKind.APPLY_PATCH:
            if relative.parts and relative.parts[0] in {"tests", ".git"}:
                return f"apply_patch cannot modify protected path: {relative}"
        return None

    def _precondition_error(self, action: Action) -> str | None:
        if action.kind in {ActionKind.READ_FILE, ActionKind.APPLY_PATCH}:
            assert action.target is not None
            candidate = self._candidate_path(action.target)
            if not candidate.exists():
                return f"{action.kind.value} target does not exist: {action.target}"
            if not candidate.is_file():
                return f"{action.kind.value} target is not a file: {action.target}"

        if action.kind in {ActionKind.RUN_TESTS, ActionKind.RUN_TARGETED_TESTS}:
            tests = self.repository_root / "tests"
            if not tests.exists():
                return "repository has no tests directory"

        if action.kind == ActionKind.RUN_TARGETED_TESTS:
            assert action.target is not None
            candidate = self._candidate_path(action.target)
            if not candidate.exists():
                return f"targeted test path does not exist: {action.target.split('::', 1)[0]}"

        return None

    @staticmethod
    def _reject(
        stage: AcceptanceStage,
        reason: str,
        proposal_text: str | None = None,
    ) -> AcceptanceResult:
        return AcceptanceResult(
            accepted=False,
            stage=stage,
            reason=reason,
            proposal_text=proposal_text,
        )
