from __future__ import annotations

import json
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .acceptance import AcceptanceResult, ActionAcceptanceBoundary
from .actions import ActionKind, RawProposal
from .candidates import (
    Candidate,
    CandidateSelector,
    CandidateSet,
    FixedCandidateGenerator,
    FunctionCandidateEvaluator,
    measure_selection,
)
from .capabilities import (
    Capability,
    CapabilityExecutor,
    CapabilityNeed,
    CapabilityPipeline,
    CapabilityRegistry,
)
from .environment import RepositoryEnvironment
from .memory import MemoryCycle, MemoryStore, WritePolicy
from .planning import Plan, PlanStep, PlanValidator
from .revision import (
    Critique,
    EvidenceSet as RevisionEvidenceSet,
    FixedCritic,
    FunctionReviser,
    RevisionGate,
    refine_once,
)
from .runtime import (
    Budgets,
    ContinuationDisposition,
    ContinuationPolicy,
    ExecutionTrace,
    RuntimeState,
    StepRecord,
)
from .search import (
    FixedExpansionPolicy,
    IsolatedEnvironmentFactory,
    PruningPolicy,
    SearchController,
    SearchTransition,
)
from .verification import (
    Adjudicator,
    ContractIntegrityVerifier,
    EvidenceCollector,
    EvidenceLayer,
    EvidenceSet as VerificationEvidenceSet,
    GoalContract,
    ProtectedPathVerifier,
    Verdict,
    WorkspaceSnapshot,
    combine_integrity,
)

TARGETED_TEST = "tests/test_parser.py::test_pipe_delimiter"
PROTECTED_TEST = "tests/test_parser.py"


@dataclass(frozen=True)
class RecordedRepairModel:
    """Deterministic model fixture so the experiment tests runtime mechanisms."""

    def candidates(self) -> CandidateSet:
        return CandidateSet.from_iterable(
            [
                Candidate(
                    id="hardcode-pipe",
                    action="apply_patch",
                    patch=(
                        'def split_record(text: str, delimiter: str = ",") -> list[str]:\n'
                        '    return text.split("|")\n'
                    ),
                    rationale="makes the visible pipe example pass but breaks comma records",
                ),
                Candidate(
                    id="use-argument",
                    action="apply_patch",
                    patch=(
                        'def split_record(text: str, delimiter: str = ",") -> list[str]:\n'
                        '    return text.split(delimiter)\n'
                    ),
                    rationale="use the caller-supplied delimiter",
                ),
                Candidate(
                    id="no-change",
                    action="apply_patch",
                    patch=(
                        'def split_record(text: str, delimiter: str = ",") -> list[str]:\n'
                        '    return text.split(",")\n'
                    ),
                    rationale="preserve current implementation",
                ),
            ]
        )

    def revise(self, candidate: Candidate, _critique: Critique) -> Candidate:
        return Candidate(
            id=f"{candidate.id}-revised",
            action=candidate.action,
            patch=(
                'def split_record(text: str, delimiter: str = ",") -> list[str]:\n'
                '    """Split one record using the caller-supplied delimiter."""\n'
                "\n"
                "    return text.split(delimiter)\n"
            ),
            rationale="preserve a clear function contract while fixing delimiter handling",
            accepted_by_stage01=candidate.accepted_by_stage01,
        )


@dataclass(frozen=True)
class AgentRunResult:
    task: str
    diagnosis: str
    plan: tuple[str, ...]
    result: str
    evidence: tuple[str, ...]
    workspace: str
    final_state_id: str
    architecture_trace: tuple[str, ...]
    acceptance_stages: tuple[str, ...]
    selected_candidate: str
    selection_metrics: dict[str, int | str]
    revision_accepted: bool
    search_selected: str | None
    memory_used: bool
    verification_verdict: str
    verification_integrity: str

    def as_dict(self) -> dict[str, object]:
        return {
            "TASK": self.task,
            "DIAGNOSIS": self.diagnosis,
            "PLAN": list(self.plan),
            "RESULT": self.result,
            "EVIDENCE": list(self.evidence),
            "workspace": self.workspace,
            "final_state_id": self.final_state_id,
            "architecture_trace": list(self.architecture_trace),
            "acceptance_stages": list(self.acceptance_stages),
            "selected_candidate": self.selected_candidate,
            "selection_metrics": self.selection_metrics,
            "revision_accepted": self.revision_accepted,
            "search_selected": self.search_selected,
            "memory_used": self.memory_used,
            "verification_verdict": self.verification_verdict,
            "verification_integrity": self.verification_integrity,
        }


@dataclass(frozen=True)
class TamperingControlResult:
    naive_checker_passed: bool
    integrity: str
    final_verdict: str
    workspace: str


class AgentApplication:
    """Integration-only capstone over the mechanisms earned in Stages 00-09."""

    def __init__(
        self,
        *,
        model: RecordedRepairModel | None = None,
        memory: MemoryStore | None = None,
        budgets: Budgets | None = None,
    ) -> None:
        self.model = model or RecordedRepairModel()
        self.memory = memory or MemoryStore()
        self.budgets = budgets or Budgets(max_steps=20, max_model_calls=10, no_progress_window=4)

    def run(self, task: str, repo: str | Path, *, workspace: str | Path | None = None) -> AgentRunResult:
        source = Path(repo).resolve()
        work = self._copy_workspace(source, workspace)
        environment = RepositoryEnvironment(work)
        acceptance = ActionAcceptanceBoundary(work)
        baseline = self._snapshot(work)
        contract = self._goal_contract()
        trace = ExecutionTrace()
        runtime = RuntimeState(facts=frozenset({"repo_available", "path_known", "write_permission"}))
        acceptance_log: list[AcceptanceResult] = []

        plan = self._plan(task)
        PlanValidator().require_valid(plan)

        memory_decision = MemoryCycle().decide(
            self.memory,
            key="targeted_test",
            scope="project",
            current_evidence={},
            fallback=TARGETED_TEST,
        )
        targeted_test = memory_decision.choice
        memory_used = bool(memory_decision.used_ids)

        reproduced = self._execute_raw(
            environment,
            acceptance,
            action=ActionKind.RUN_TARGETED_TESTS,
            target=targeted_test,
            reason="reproduce the reported delimiter failure",
            acceptance_log=acceptance_log,
        )
        if reproduced.ok:
            raise ValueError("capstone fixture did not reproduce the expected pipe-delimiter failure")
        runtime = self._record(runtime, trace, "run targeted tests", "pipe failure reproduced", True, 1)

        registry = CapabilityRegistry(
            [
                Capability(
                    name="read_file",
                    purpose="read exact known path content",
                    action_kind=ActionKind.READ_FILE,
                    eligible_when=frozenset({"path_known"}),
                    keywords=frozenset({"read", "known", "file", "content", "parser"}),
                )
            ]
        )
        decision = CapabilityPipeline(registry).route(
            runtime,
            CapabilityNeed("read known parser file content", target="parser.py"),
        )
        inspected = CapabilityExecutor().execute(decision, acceptance, environment)
        acceptance_log.append(inspected.acceptance)
        if inspected.observation is None:
            raise RuntimeError(f"parser inspection was rejected: {inspected.acceptance.reason}")
        source_text = str(inspected.observation.data["content"])
        runtime = self._record(runtime, trace, "read parser.py", "fixed comma delimiter observed", True, 1)

        generated = FixedCandidateGenerator(self.model.candidates()).generate()
        selector = CandidateSelector(
            FunctionCandidateEvaluator(
                lambda candidate: (
                    3.0 if "split(delimiter)" in candidate.patch else
                    1.0 if 'split("|")' in candidate.patch else 0.0
                )
            )
        )
        selected = selector.select_complete(generated)
        selection_metrics = measure_selection(
            generated,
            selected,
            lambda candidate: "split(delimiter)" in candidate.patch,
        )
        runtime = self._model_step(runtime)
        trace.append(StepRecord("select repair candidate", selected.candidate.id, new_evidence=True, progress_delta=1))

        critique = Critique(
            defect="repair should preserve a clear delimiter contract",
            evidence=("source inspection confirmed delimiter is caller supplied",),
            target="delimiter handling",
        )
        revision = refine_once(
            selected.candidate,
            critic=FixedCritic(critique),
            reviser=FunctionReviser(self.model.revise),
            gate=RevisionGate(
                value_function=lambda candidate, _evidence: float(
                    2 * ("split(delimiter)" in candidate.patch)
                    + ("caller-supplied delimiter" in candidate.patch)
                ),
                adherence_check=lambda candidate, _critique: "split(delimiter)" in candidate.patch,
                integrity_check=lambda candidate, _evidence: (
                    "repair proposal targets protected tests"
                    if "tests/" in candidate.patch or "delete failing test" in candidate.patch.lower()
                    else None
                ),
            ),
            evidence=RevisionEvidenceSet.from_iterable([source_text, reproduced.details]),
        )
        final_candidate = revision.resulting
        runtime = self._model_step(runtime)
        trace.append(StepRecord("targeted revision", final_candidate.id, new_evidence=True, progress_delta=1))

        search = self._search(runtime, final_candidate, generated)
        if search.selected != "B1":
            raise RuntimeError("controlled search did not preserve the repair trajectory")
        trace.append(StepRecord("search repair trajectories", search.selected or "none", new_evidence=True, progress_delta=1))

        patched = self._execute_raw(
            environment,
            acceptance,
            action=ActionKind.APPLY_PATCH,
            target="parser.py",
            content=final_candidate.patch,
            reason="commit the selected repair once",
            acceptance_log=acceptance_log,
        )
        if not patched.ok:
            raise RuntimeError("selected repair produced no workspace change")
        runtime = self._record(runtime, trace, "apply parser patch", "parser source changed", True, 1)

        diff = self._execute_raw(
            environment,
            acceptance,
            action=ActionKind.INSPECT_DIFF,
            reason="inspect the committed workspace change",
            acceptance_log=acceptance_log,
        )
        changed_paths = tuple(diff.data.get("changed_paths", []))
        if changed_paths != ("parser.py",):
            raise RuntimeError(f"unexpected changed paths: {changed_paths}")
        runtime = self._record(runtime, trace, "inspect diff", "only parser.py changed", True, 1)

        targeted = self._execute_raw(
            environment,
            acceptance,
            action=ActionKind.RUN_TARGETED_TESTS,
            target=targeted_test,
            reason="verify the original failing criterion on current state",
            acceptance_log=acceptance_log,
        )
        runtime = self._record(runtime, trace, "run targeted tests", "pipe test rerun", True, int(targeted.ok))

        full = self._execute_raw(
            environment,
            acceptance,
            action=ActionKind.RUN_TESTS,
            reason="verify the complete regression suite",
            acceptance_log=acceptance_log,
        )
        runtime = self._record(runtime, trace, "run full tests", "full suite rerun", True, int(full.ok))

        current = self._snapshot(work)
        path_integrity = ProtectedPathVerifier(baseline, [PROTECTED_TEST]).check(current)
        contract_integrity = ContractIntegrityVerifier().check(contract, observed_events=())
        integrity = combine_integrity(path_integrity, contract_integrity)
        collector = EvidenceCollector(verifier_version="stage10-capstone-v1")
        evidence = VerificationEvidenceSet(
            (
                collector.collect(
                    evidence_id="pipe-targeted",
                    criterion="pipe records accepted",
                    layer=EvidenceLayer.GOAL_SATISFACTION,
                    source=f"pytest:{targeted_test}",
                    state_id=current.state_id,
                    contract=contract,
                    verdict=Verdict.PASS if targeted.ok else Verdict.FAIL,
                    collected_at=runtime.step_count + 1,
                    payload={"returncode": str(targeted.data.get("returncode"))},
                ),
                collector.collect(
                    evidence_id="regression-suite",
                    criterion="comma records still pass",
                    layer=EvidenceLayer.GOAL_SATISFACTION,
                    source="pytest:full-suite",
                    state_id=current.state_id,
                    contract=contract,
                    verdict=Verdict.PASS if full.ok else Verdict.FAIL,
                    collected_at=runtime.step_count + 2,
                    payload={"returncode": str(full.data.get("returncode"))},
                ),
            )
        )
        verification = Adjudicator().decide(
            contract=contract,
            evidence=evidence,
            state_id=current.state_id,
            integrity=integrity,
        )

        if verification.verdict == Verdict.PASS and not memory_used:
            self.memory.write(
                memory_id=f"targeted-test-{current.state_id.value}",
                key="targeted_test",
                value=TARGETED_TEST,
                scope="project",
                provenance=f"verified capstone state {current.state_id.value}",
                policy=WritePolicy(),
                verified=True,
                reusable=True,
            )

        result_name = "VERIFIED_SUCCESS" if verification.verdict == Verdict.PASS else verification.verdict.value
        evidence_summary = (
            "original failure reproduced",
            "targeted pipe test passed" if targeted.ok else "targeted pipe test failed",
            "full suite passed" if full.ok else "full suite failed",
            "protected tests unchanged" if integrity.status.value == "CLEAN" else "verification integrity violated",
            f"final state identity {current.state_id.value}",
        )
        architecture_trace = (
            "user task",
            "goal contract",
            "runtime state",
            "capability selection",
            "Stage-01 acceptance",
            "environment observation",
            "candidate selection",
            "targeted revision",
            "structured planning",
            "progress control",
            "memory lifecycle",
            "isolated trajectory search",
            "single committed repair",
            "state-bound evidence",
            "protected verification",
        )
        return AgentRunResult(
            task=task,
            diagnosis="split_record ignores the caller-supplied delimiter and always splits on comma",
            plan=tuple(step.action for step in plan.steps),
            result=result_name,
            evidence=evidence_summary,
            workspace=str(work),
            final_state_id=current.state_id.value,
            architecture_trace=architecture_trace,
            acceptance_stages=tuple(item.stage.value for item in acceptance_log),
            selected_candidate=selected.candidate.id,
            selection_metrics=selection_metrics.as_dict(),
            revision_accepted=revision.accepted,
            search_selected=search.selected,
            memory_used=memory_used,
            verification_verdict=verification.verdict.value,
            verification_integrity=verification.integrity.status.value,
        )

    @staticmethod
    def _goal_contract() -> GoalContract:
        return GoalContract(
            must_change=("pipe records accepted",),
            must_preserve=("comma records still pass",),
            must_not=("delete protected tests", "weaken goal contract"),
        )

    @staticmethod
    def _plan(task: str) -> Plan:
        return Plan(
            goal=task,
            steps=(
                PlanStep("reproduce", "reproduce failing pipe test", expected_evidence=("pipe failure",)),
                PlanStep("inspect", "inspect parser implementation", dependencies=("reproduce",)),
                PlanStep("alternatives", "generate and select complete repair candidates", dependencies=("inspect",)),
                PlanStep("revise", "critique and refine selected repair", dependencies=("alternatives",)),
                PlanStep("search", "compare isolated partial repair trajectories", dependencies=("revise",)),
                PlanStep("commit", "authorize and commit one repair", dependencies=("search",)),
                PlanStep("verify", "collect current evidence and adjudicate", dependencies=("commit",)),
            ),
        )

    def _search(self, runtime: RuntimeState, repaired: Candidate, generated: CandidateSet):
        hardcode = next(candidate for candidate in generated.candidates if candidate.id == "hardcode-pipe")
        expansion = FixedExpansionPolicy(
            {
                "root": (
                    SearchTransition(
                        "A", "hardcode visible pipe example", 0.75,
                        success_reachable=False,
                        workspace_updates=(("parser.py", hardcode.patch),),
                    ),
                    SearchTransition(
                        "B", "respect delimiter argument", 0.55,
                        success_reachable=True,
                        workspace_updates=(("parser.py", repaired.patch),),
                    ),
                ),
                "A": (SearchTransition("A1", "comma regression", 0.2, terminal=True, goal_satisfied=False),),
                "B": (SearchTransition("B1", "both delimiter behaviours", 0.9, terminal=True, goal_satisfied=True, success_reachable=True),),
            }
        )
        return SearchController(
            expansion=expansion,
            pruning=PruningPolicy(beam_width=2),
            max_depth=2,
        ).run(
            runtime,
            IsolatedEnvironmentFactory(),
            workspace={"parser.py": "original"},
        )

    def _record(
        self,
        runtime: RuntimeState,
        trace: ExecutionTrace,
        action: str,
        relevant_state: str,
        new_evidence: bool,
        progress_delta: int,
    ) -> RuntimeState:
        trace.append(StepRecord(action, relevant_state, new_evidence=new_evidence, progress_delta=progress_delta))
        updated = RuntimeState(
            facts=runtime.facts,
            step_count=runtime.step_count + 1,
            model_calls=runtime.model_calls,
        )
        decision = ContinuationPolicy().decide(updated, trace, self.budgets)
        if decision.disposition == ContinuationDisposition.STOP:
            raise RuntimeError(f"runtime stopped before verification: {decision.reason}")
        return updated

    @staticmethod
    def _model_step(runtime: RuntimeState) -> RuntimeState:
        return RuntimeState(
            facts=runtime.facts,
            step_count=runtime.step_count,
            model_calls=runtime.model_calls + 1,
        )

    @staticmethod
    def _execute_raw(
        environment: RepositoryEnvironment,
        acceptance: ActionAcceptanceBoundary,
        *,
        action: ActionKind,
        reason: str,
        acceptance_log: list[AcceptanceResult],
        target: str | None = None,
        content: str | None = None,
    ):
        payload: dict[str, str] = {"action": action.value, "reason": reason}
        if target is not None:
            payload["target"] = target
        if content is not None:
            payload["content"] = content
        accepted = acceptance.accept(RawProposal(json.dumps(payload, sort_keys=True)))
        acceptance_log.append(accepted)
        if not accepted.accepted or accepted.action is None:
            raise RuntimeError(f"action rejected at {accepted.stage.value}: {accepted.reason}")
        return environment.execute(accepted.action)

    @staticmethod
    def _copy_workspace(source: Path, workspace: str | Path | None) -> Path:
        if workspace is None:
            parent = Path(tempfile.mkdtemp(prefix="first-principles-agent-"))
            destination = parent / source.name
        else:
            destination = Path(workspace).resolve()
            if destination.exists():
                raise FileExistsError(f"workspace already exists: {destination}")
        shutil.copytree(source, destination)
        return destination

    @staticmethod
    def _snapshot(root: Path) -> WorkspaceSnapshot:
        files: dict[str, str] = {}
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(root)
            if any(part in {".pytest_cache", "__pycache__", ".git", ".venv", "venv"} for part in relative.parts):
                continue
            try:
                files[str(relative)] = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
        return WorkspaceSnapshot.from_mapping(files)


def run_protected_test_tampering_control(
    repo: str | Path,
    *,
    workspace: str | Path | None = None,
) -> TamperingControlResult:
    """Adversarial evaluation control; not an action available to the agent."""

    source = Path(repo).resolve()
    work = AgentApplication._copy_workspace(source, workspace)
    baseline = AgentApplication._snapshot(work)
    test_path = work / PROTECTED_TEST
    text = test_path.read_text(encoding="utf-8")
    marker = "\ndef test_pipe_delimiter()"
    if marker not in text:
        raise ValueError("protected pipe test was not found")
    test_path.write_text(text.split(marker, 1)[0].rstrip() + "\n", encoding="utf-8")

    environment = RepositoryEnvironment(work)
    acceptance = ActionAcceptanceBoundary(work)
    accepted = acceptance.accept(RawProposal(json.dumps({"action": "run_tests", "reason": "naive full-suite checker"})))
    assert accepted.accepted and accepted.action is not None
    naive = environment.execute(accepted.action)

    contract = AgentApplication._goal_contract()
    current = AgentApplication._snapshot(work)
    integrity = ProtectedPathVerifier(baseline, [PROTECTED_TEST]).check(current)
    collector = EvidenceCollector(verifier_version="stage10-adversarial-control")
    naive_verdict = Verdict.PASS if naive.ok else Verdict.FAIL
    evidence = VerificationEvidenceSet(
        (
            collector.collect(
                evidence_id="naive-pipe",
                criterion="pipe records accepted",
                layer=EvidenceLayer.GOAL_SATISFACTION,
                source="naive full-suite checker",
                state_id=current.state_id,
                contract=contract,
                verdict=naive_verdict,
                collected_at=1,
            ),
            collector.collect(
                evidence_id="naive-comma",
                criterion="comma records still pass",
                layer=EvidenceLayer.GOAL_SATISFACTION,
                source="naive full-suite checker",
                state_id=current.state_id,
                contract=contract,
                verdict=naive_verdict,
                collected_at=1,
            ),
        )
    )
    verification = Adjudicator().decide(
        contract=contract,
        evidence=evidence,
        state_id=current.state_id,
        integrity=integrity,
    )
    return TamperingControlResult(
        naive_checker_passed=naive.ok,
        integrity=integrity.status.value,
        final_verdict=verification.verdict.value,
        workspace=str(work),
    )
