from first_principles_agent.memory import (
    ContextAssembler,
    MemoryCycle,
    MemoryOutcome,
    MemoryRecord,
    MemoryStatus,
    MemoryStore,
    ProspectiveMemory,
    RetrievalPolicy,
    WritePolicy,
    memory_induced_regret,
)


def test_write_policy_rejects_unverified_or_transient_information() -> None:
    store = MemoryStore()
    policy = WritePolicy()

    assert store.write(
        memory_id="unverified",
        key="test_command",
        value="pytest -q",
        scope="project",
        provenance="model guess",
        policy=policy,
        verified=False,
    ) is None

    assert store.write(
        memory_id="transient",
        key="last_stdout",
        value="1 failed",
        scope="run",
        provenance="current trace",
        policy=policy,
        verified=True,
        reusable=False,
    ) is None

    written = store.write(
        memory_id="verified",
        key="test_command",
        value="pytest -q",
        scope="project",
        provenance="successful repository run",
        policy=policy,
        verified=True,
        reusable=True,
    )
    assert written is not None
    assert [record.id for record in store.records] == ["verified"]


def test_retrieval_excludes_superseded_expired_forgotten_and_deleted_records() -> None:
    store = MemoryStore([
        MemoryRecord("old", "orders_api", "/v1/orders", "project", "old run"),
        MemoryRecord("expired", "orders_api", "/legacy/orders", "project", "old docs"),
        MemoryRecord("forgotten", "orders_api", "/temp/orders", "project", "temporary note"),
        MemoryRecord("deleted", "orders_api", "/private/orders", "project", "private note"),
    ])
    store.supersede("old")
    store.expire("expired")
    store.forget("forgotten")
    store.delete("deleted")
    store.add(MemoryRecord("current", "orders_api", "/v2/orders", "project", "verified run"))

    retrieved = RetrievalPolicy().retrieve(store, key="orders_api", scope="project")
    assert [record.id for record in retrieved] == ["current"]
    assert store.get("old").status == MemoryStatus.SUPERSEDED


def test_current_evidence_outranks_stale_memory_then_supersedes_it() -> None:
    store = MemoryStore([
        MemoryRecord("v1", "orders_api", "/v1/orders", "project", "old run"),
    ])
    cycle = MemoryCycle()

    decision = cycle.decide(
        store,
        key="orders_api",
        scope="project",
        current_evidence={"orders_api": "/v2/orders"},
        fallback="discover endpoint",
    )

    assert decision.choice == "/v2/orders"
    assert decision.retrieved_ids == ("v1",)
    assert decision.included_ids == ()
    assert decision.used_ids == ()

    replacement = store.write(
        memory_id="v2",
        key="orders_api",
        value="/v2/orders",
        scope="project",
        provenance="current successful request",
        policy=WritePolicy(),
        supersedes="v1",
    )
    assert replacement is not None
    assert store.get("v1").status == MemoryStatus.SUPERSEDED

    next_run = cycle.decide(
        store,
        key="orders_api",
        scope="project",
        current_evidence={},
        fallback="discover endpoint",
    )
    assert next_run.choice == "/v2/orders"
    assert next_run.used_ids == ("v2",)


def test_prospective_memory_fires_only_on_its_cue_and_only_once() -> None:
    reminder = ProspectiveMemory(
        id="full-suite-after-patch",
        condition="tests_pass_after_patch",
        action="run_full_suite",
    )

    events = ["read_file", "edit_parser", "tests_pass_after_patch", "tests_pass_after_patch"]
    fired = [action for event in events if (action := reminder.observe(event)) is not None]

    assert fired == ["run_full_suite"]
    assert reminder.fired is True


def test_verified_memory_can_reduce_work() -> None:
    store = MemoryStore([
        MemoryRecord("test-command", "test_command", "pytest -q", "project", "verified prior run"),
    ])
    cycle = MemoryCycle()

    with_memory = cycle.decide(
        store,
        key="test_command",
        scope="project",
        current_evidence={},
        fallback="discover test command",
    )

    no_memory_steps = 3
    memory_steps = 1 if with_memory.used_ids else 3
    assert with_memory.choice == "pytest -q"
    assert memory_steps < no_memory_steps


def test_stale_memory_can_cause_memory_induced_regret() -> None:
    store = MemoryStore([
        MemoryRecord("stale", "orders_api", "/v1/orders", "project", "old run"),
    ])
    decision = MemoryCycle().decide(
        store,
        key="orders_api",
        scope="project",
        current_evidence={},
        fallback="/v2/orders",
    )

    no_memory = MemoryOutcome(success=True, steps=2)
    with_memory = MemoryOutcome(success=decision.choice == "/v2/orders", steps=1)

    assert decision.used_ids == ("stale",)
    assert memory_induced_regret(no_memory=no_memory, with_memory=with_memory) is True


def test_context_assembler_records_conflicting_memory_exclusion() -> None:
    memory = MemoryRecord("old", "orders_api", "/v1/orders", "project", "old run")
    context = ContextAssembler().assemble(
        (memory,),
        current_evidence={"orders_api": "/v2/orders"},
    )
    assert context.included == ()
    assert context.excluded_by_current_evidence == ("old",)
