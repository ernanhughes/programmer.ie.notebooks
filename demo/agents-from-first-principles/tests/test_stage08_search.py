from first_principles_agent.runtime import RuntimeState
from first_principles_agent.search import (
    AllocationPolicy,
    FixedExpansionPolicy,
    IsolatedEnvironmentFactory,
    PruningPolicy,
    RecordedNodeEvaluator,
    SearchController,
    SearchTransition,
    TerminalOracle,
)


def controlled_tree() -> FixedExpansionPolicy:
    return FixedExpansionPolicy(
        {
            "root": (
                SearchTransition(
                    id="A",
                    label="obvious parser edit",
                    score=0.9,
                    success_reachable=False,
                    workspace_updates=(("parser.py", "candidate A"),),
                ),
                SearchTransition(
                    id="B",
                    label="inspect delimiter assumptions",
                    score=0.4,
                    success_reachable=True,
                    workspace_updates=(("parser.py", "candidate B"),),
                ),
            ),
            "A": (
                SearchTransition(
                    id="A1",
                    label="delete failing test",
                    score=0.95,
                    terminal=True,
                    goal_satisfied=False,
                    success_reachable=False,
                ),
            ),
            "B": (
                SearchTransition(
                    id="B1",
                    label="patch delimiter parser",
                    score=0.8,
                    terminal=True,
                    goal_satisfied=True,
                    success_reachable=True,
                ),
            ),
        }
    )


def run_search(beam_width: int):
    controller = SearchController(
        expansion=controlled_tree(),
        pruning=PruningPolicy(beam_width),
        max_depth=2,
    )
    return controller.run(
        RuntimeState(facts=frozenset({"repo_available"})),
        IsolatedEnvironmentFactory(),
        workspace={"parser.py": "original"},
    )


def test_narrow_pruning_can_kill_a_reachable_success() -> None:
    result = run_search(1)

    assert "B" in result.generated
    assert "B" in result.pruned
    assert result.pruned_reachable == ("B",)
    assert result.pruning_regret is True
    assert result.selected is None
    assert result.verified == ()


def test_wider_prefix_search_preserves_and_reaches_success() -> None:
    result = run_search(2)

    assert "B" in result.retained
    assert "B" in result.expanded
    assert "B1" in result.verified
    assert result.selected == "B1"
    assert result.pruning_regret is False
    assert result.cost_per_verified_success > 0


def test_adaptive_allocation_spends_more_on_uncertain_partial_state() -> None:
    result = run_search(2)

    assert result.allocations["B"] > result.allocations["A"]


def test_sibling_branch_workspaces_are_isolated() -> None:
    factory = IsolatedEnvironmentFactory()
    root = factory.root(
        RuntimeState(facts=frozenset({"repo_available"})),
        {"parser.py": "original"},
    )
    a = factory.fork(
        root,
        SearchTransition(
            id="A",
            label="branch A edit",
            score=0.5,
            workspace_updates=(("parser.py", "A edit"),),
        ),
    )
    b = factory.fork(
        root,
        SearchTransition(
            id="B",
            label="branch B edit",
            score=0.5,
            workspace_updates=(("parser.py", "B edit"),),
        ),
    )

    assert dict(root.snapshot.workspace)["parser.py"] == "original"
    assert dict(a.snapshot.workspace)["parser.py"] == "A edit"
    assert dict(b.snapshot.workspace)["parser.py"] == "B edit"
    assert a.fingerprint != b.fingerprint


def test_pruning_deduplicates_same_effective_state_before_spending_beam() -> None:
    factory = IsolatedEnvironmentFactory()
    root = factory.root(RuntimeState(), {"parser.py": "original"})
    low = factory.fork(
        root,
        SearchTransition(id="low", label="same state", score=0.2),
    )
    high = factory.fork(
        root,
        SearchTransition(id="high", label="same state", score=0.8),
    )

    decision = PruningPolicy(beam_width=2).prune(
        (low, high),
        RecordedNodeEvaluator(),
    )

    assert tuple(node.id for node in decision.retained) == ("high",)
    assert tuple(node.id for node in decision.duplicates) == ("low",)


def test_terminal_oracle_is_only_a_controlled_search_oracle() -> None:
    factory = IsolatedEnvironmentFactory()
    root = factory.root(RuntimeState())
    partial = factory.fork(
        root,
        SearchTransition(
            id="partial",
            label="promising but unfinished",
            score=0.7,
            terminal=False,
            goal_satisfied=True,
            success_reachable=True,
        ),
    )
    terminal = factory.fork(
        root,
        SearchTransition(
            id="terminal",
            label="controlled target reached",
            score=0.7,
            terminal=True,
            goal_satisfied=True,
            success_reachable=True,
        ),
    )

    oracle = TerminalOracle()
    assert oracle.satisfied(partial) is False
    assert oracle.satisfied(terminal) is True


def test_allocation_policy_is_explicit_and_deterministic() -> None:
    factory = IsolatedEnvironmentFactory()
    root = factory.root(RuntimeState())
    certain = factory.fork(
        root,
        SearchTransition(id="certain", label="clear", score=0.95),
    )
    uncertain = factory.fork(
        root,
        SearchTransition(id="uncertain", label="ambiguous", score=0.5),
    )

    policy = AllocationPolicy(base_compute=1, extra_compute=2)
    assert policy.allocation(certain) == 1
    assert policy.allocation(uncertain) == 3
