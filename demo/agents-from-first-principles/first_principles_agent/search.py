from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Protocol

from .runtime import RuntimeState


@dataclass(frozen=True)
class BranchSnapshot:
    """Immutable continuable branch state used by prefix-level search."""

    runtime: RuntimeState
    workspace: tuple[tuple[str, str], ...] = ()

    @property
    def fingerprint(self) -> str:
        payload = (
            tuple(sorted(self.runtime.facts)),
            self.runtime.step_count,
            self.runtime.model_calls,
            self.runtime.success_signal,
            self.runtime.missing_precondition,
            self.runtime.user_input_request,
            tuple(sorted(self.workspace)),
        )
        return sha256(repr(payload).encode("utf-8")).hexdigest()[:16]

    def with_changes(
        self,
        *,
        facts_add: tuple[str, ...] = (),
        workspace_updates: dict[str, str] | None = None,
    ) -> "BranchSnapshot":
        workspace = dict(self.workspace)
        workspace.update(workspace_updates or {})
        runtime = self.runtime.with_facts(*facts_add)
        return BranchSnapshot(runtime=runtime, workspace=tuple(sorted(workspace.items())))


@dataclass(frozen=True)
class SearchNode:
    id: str
    snapshot: BranchSnapshot
    depth: int
    parent_id: str | None = None
    branch_id: str = "root"
    score: float = 0.0
    terminal: bool = False
    goal_satisfied: bool = False
    success_reachable: bool = False
    cost: int = 1
    label: str = ""

    @property
    def fingerprint(self) -> str:
        return self.snapshot.fingerprint


@dataclass(frozen=True)
class SearchTransition:
    id: str
    label: str
    score: float
    terminal: bool = False
    goal_satisfied: bool = False
    success_reachable: bool = False
    facts_add: tuple[str, ...] = ()
    workspace_updates: tuple[tuple[str, str], ...] = ()
    cost: int = 1


class IsolatedEnvironmentFactory:
    """Fork immutable branch snapshots so sibling branches cannot contaminate one another."""

    def root(self, state: RuntimeState, workspace: dict[str, str] | None = None) -> SearchNode:
        snapshot = BranchSnapshot(
            runtime=state,
            workspace=tuple(sorted((workspace or {}).items())),
        )
        return SearchNode(
            id="root",
            snapshot=snapshot,
            depth=0,
            branch_id="root",
            success_reachable=True,
            cost=0,
        )

    def fork(self, parent: SearchNode, transition: SearchTransition) -> SearchNode:
        child_snapshot = parent.snapshot.with_changes(
            facts_add=transition.facts_add,
            workspace_updates=dict(transition.workspace_updates),
        )
        return SearchNode(
            id=transition.id,
            snapshot=child_snapshot,
            depth=parent.depth + 1,
            parent_id=parent.id,
            branch_id=f"{parent.branch_id}/{transition.id}",
            score=transition.score,
            terminal=transition.terminal,
            goal_satisfied=transition.goal_satisfied,
            success_reachable=transition.success_reachable,
            cost=transition.cost,
            label=transition.label,
        )


class ExpansionPolicy(Protocol):
    def expand(self, node: SearchNode) -> tuple[SearchTransition, ...]: ...


class FixedExpansionPolicy:
    def __init__(self, tree: dict[str, tuple[SearchTransition, ...] | list[SearchTransition]]) -> None:
        self.tree = {key: tuple(value) for key, value in tree.items()}

    def expand(self, node: SearchNode) -> tuple[SearchTransition, ...]:
        return self.tree.get(node.id, ())


class NodeEvaluator(Protocol):
    def score(self, node: SearchNode) -> float: ...


class RecordedNodeEvaluator:
    """Use recorded scores so the search experiment is deterministic."""

    def score(self, node: SearchNode) -> float:
        return node.score


class AllocationPolicy:
    """Allocate more expansion effort to states whose score is less decisive."""

    def __init__(
        self,
        *,
        base_compute: int = 1,
        extra_compute: int = 1,
        uncertainty_threshold: float = 0.5,
    ) -> None:
        self.base_compute = base_compute
        self.extra_compute = extra_compute
        self.uncertainty_threshold = uncertainty_threshold

    def allocation(self, node: SearchNode) -> int:
        uncertainty = 1.0 - abs(node.score - 0.5) * 2.0
        return self.base_compute + (
            self.extra_compute if uncertainty > self.uncertainty_threshold else 0
        )

    def allocate(self, nodes: tuple[SearchNode, ...]) -> dict[str, int]:
        return {node.id: self.allocation(node) for node in nodes}


@dataclass(frozen=True)
class PruningDecision:
    retained: tuple[SearchNode, ...]
    pruned: tuple[SearchNode, ...]
    duplicates: tuple[SearchNode, ...]


class PruningPolicy:
    """Deduplicate effective states, then retain the strongest beam."""

    def __init__(self, beam_width: int) -> None:
        if beam_width <= 0:
            raise ValueError("beam_width must be positive")
        self.beam_width = beam_width

    def prune(
        self,
        nodes: tuple[SearchNode, ...],
        evaluator: NodeEvaluator,
    ) -> PruningDecision:
        best_by_fingerprint: dict[str, SearchNode] = {}
        duplicates: list[SearchNode] = []
        for node in nodes:
            existing = best_by_fingerprint.get(node.fingerprint)
            if existing is None:
                best_by_fingerprint[node.fingerprint] = node
                continue
            if evaluator.score(node) > evaluator.score(existing):
                duplicates.append(existing)
                best_by_fingerprint[node.fingerprint] = node
            else:
                duplicates.append(node)

        distinct = tuple(best_by_fingerprint.values())
        ranked = sorted(distinct, key=lambda node: (-evaluator.score(node), node.id))
        retained = tuple(ranked[: self.beam_width])
        retained_ids = {node.id for node in retained}
        pruned = tuple(node for node in distinct if node.id not in retained_ids)
        return PruningDecision(
            retained=retained,
            pruned=pruned,
            duplicates=tuple(duplicates),
        )


class TerminalOracle:
    """Controlled experimental oracle only; Stage 09 owns real verification."""

    def satisfied(self, node: SearchNode) -> bool:
        return node.terminal and node.goal_satisfied


@dataclass(frozen=True)
class SearchResult:
    generated: tuple[str, ...]
    distinct: tuple[str, ...]
    retained: tuple[str, ...]
    expanded: tuple[str, ...]
    pruned: tuple[str, ...]
    pruned_reachable: tuple[str, ...]
    duplicates: tuple[str, ...]
    verified: tuple[str, ...]
    selected: str | None
    allocations: dict[str, int]
    total_cost: int

    @property
    def pruning_regret(self) -> bool:
        return bool(self.pruned_reachable)

    @property
    def cost_per_verified_success(self) -> float:
        return self.total_cost / max(1, len(self.verified))


class SearchController:
    """Prefix-level search over isolated continuable states."""

    def __init__(
        self,
        *,
        expansion: ExpansionPolicy,
        evaluator: NodeEvaluator | None = None,
        allocation: AllocationPolicy | None = None,
        pruning: PruningPolicy,
        terminal_oracle: TerminalOracle | None = None,
        max_depth: int = 2,
    ) -> None:
        if max_depth <= 0:
            raise ValueError("max_depth must be positive")
        self.expansion = expansion
        self.evaluator = evaluator or RecordedNodeEvaluator()
        self.allocation = allocation or AllocationPolicy()
        self.pruning = pruning
        self.terminal_oracle = terminal_oracle or TerminalOracle()
        self.max_depth = max_depth

    def run(
        self,
        root: RuntimeState,
        environment_factory: IsolatedEnvironmentFactory,
        *,
        workspace: dict[str, str] | None = None,
    ) -> SearchResult:
        frontier = (environment_factory.root(root, workspace),)
        generated: list[str] = []
        distinct: list[str] = []
        retained: list[str] = []
        expanded: list[str] = []
        pruned: list[str] = []
        pruned_reachable: list[str] = []
        duplicates: list[str] = []
        verified: list[str] = []
        allocations: dict[str, int] = {}
        total_cost = 0
        selected: str | None = None

        for _ in range(self.max_depth):
            children: list[SearchNode] = []
            for node in frontier:
                if node.terminal:
                    continue
                expanded.append(node.id)
                for transition in self.expansion.expand(node):
                    child = environment_factory.fork(node, transition)
                    children.append(child)
                    generated.append(child.id)
                    total_cost += child.cost

            if not children:
                break

            decision = self.pruning.prune(tuple(children), self.evaluator)
            duplicates.extend(node.id for node in decision.duplicates)
            distinct.extend(node.id for node in decision.retained + decision.pruned)
            pruned.extend(node.id for node in decision.pruned)
            pruned_reachable.extend(
                node.id for node in decision.pruned if node.success_reachable
            )
            retained.extend(node.id for node in decision.retained)
            allocations.update(self.allocation.allocate(decision.retained))

            for node in decision.retained:
                if self.terminal_oracle.satisfied(node):
                    verified.append(node.id)
                    if selected is None:
                        selected = node.id

            frontier = tuple(node for node in decision.retained if not node.terminal)
            if not frontier:
                break

        return SearchResult(
            generated=tuple(generated),
            distinct=tuple(distinct),
            retained=tuple(retained),
            expanded=tuple(expanded),
            pruned=tuple(pruned),
            pruned_reachable=tuple(pruned_reachable),
            duplicates=tuple(duplicates),
            verified=tuple(verified),
            selected=selected,
            allocations=allocations,
            total_cost=total_cost,
        )
