from __future__ import annotations

import copy
import hashlib
import json
import math
import random
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Set, Tuple

Cell = Tuple[int, int]

HEX_DIRECTIONS: Sequence[Cell] = (
    (1, 0),
    (1, -1),
    (0, -1),
    (-1, 0),
    (-1, 1),
    (0, 1),
)


@dataclass(frozen=True)
class CrystalParams:
    base_bias: float = -2.10
    neighbor_gain: float = 0.78
    signal_rate_gain: float = 0.28
    anisotropy_gain: float = 0.95
    signal_phase_gain: float = 1.15
    crowding_penalty: float = 0.22


@dataclass
class CrystalState:
    occupied: Set[Cell]
    birth_time: Dict[Cell, int]
    step: int
    rng_state: object
    attachments_by_step: List[int]
    population_by_step: List[int]


def neighbors(cell: Cell) -> Iterable[Cell]:
    q, r = cell
    for dq, dr in HEX_DIRECTIONS:
        yield q + dq, r + dr


def hex_distance(cell: Cell) -> int:
    q, r = cell
    s = -q - r
    return max(abs(q), abs(r), abs(s))


def hex_capacity(radius: int) -> int:
    return 1 + 3 * radius * (radius + 1)


def axial_to_xy(cell: Cell) -> tuple[float, float]:
    q, r = cell
    return math.sqrt(3.0) * (q + r / 2.0), 1.5 * r


def logistic(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def local_exposure_angle(cell: Cell, occupied: Set[Cell]) -> float:
    x, y = axial_to_xy(cell)
    vx = 0.0
    vy = 0.0
    count = 0
    for nb in neighbors(cell):
        if nb in occupied:
            nx, ny = axial_to_xy(nb)
            vx += x - nx
            vy += y - ny
            count += 1
    if count == 0 or abs(vx) + abs(vy) < 1e-12:
        return 0.0
    return math.atan2(vy, vx)


def initial_state(seed: int = 0) -> CrystalState:
    rng = random.Random(seed)
    return CrystalState(
        occupied={(0, 0)},
        birth_time={(0, 0): 0},
        step=0,
        rng_state=rng.getstate(),
        attachments_by_step=[1],
        population_by_step=[1],
    )


def clone_state(state: CrystalState) -> CrystalState:
    return CrystalState(
        occupied=set(state.occupied),
        birth_time=dict(state.birth_time),
        step=state.step,
        rng_state=copy.deepcopy(state.rng_state),
        attachments_by_step=list(state.attachments_by_step),
        population_by_step=list(state.population_by_step),
    )


def morphology_hash(state_or_cells) -> str:
    cells = state_or_cells.occupied if hasattr(state_or_cells, "occupied") else state_or_cells
    payload = json.dumps(
        sorted((int(q), int(r)) for q, r in cells),
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:24]


def frontier(occupied: Set[Cell], max_radius: int) -> Set[Cell]:
    cells: Set[Cell] = set()
    for cell in occupied:
        for nb in neighbors(cell):
            if nb not in occupied and hex_distance(nb) <= max_radius:
                cells.add(nb)
    return cells


def attachment_probability(
    cell: Cell,
    occupied: Set[Cell],
    input_value: float,
    params: CrystalParams = CrystalParams(),
) -> float:
    n = sum(nb in occupied for nb in neighbors(cell))
    theta = local_exposure_angle(cell, occupied)
    phase = params.signal_phase_gain * float(input_value)
    anisotropy = math.cos(6.0 * theta + phase)
    crowding = max(0, n - 2)
    score = (
        params.base_bias
        + params.neighbor_gain * n
        + params.signal_rate_gain * float(input_value)
        + params.anisotropy_gain * anisotropy
        - params.crowding_penalty * crowding
    )
    return logistic(score)


def advance_one_step(
    state: CrystalState,
    input_value: float,
    max_radius: int,
    params: CrystalParams = CrystalParams(),
    *,
    sorted_frontier: bool = True,
) -> tuple[CrystalState, int]:
    rng = random.Random()
    rng.setstate(state.rng_state)

    occupied = set(state.occupied)
    birth_time = dict(state.birth_time)
    candidates = frontier(occupied, max_radius)
    traversal = sorted(candidates) if sorted_frontier else list(candidates)

    additions: list[Cell] = []
    for cell in traversal:
        if rng.random() < attachment_probability(cell, occupied, input_value, params):
            additions.append(cell)

    next_step = state.step + 1
    for cell in additions:
        occupied.add(cell)
        birth_time[cell] = next_step

    return (
        CrystalState(
            occupied=occupied,
            birth_time=birth_time,
            step=next_step,
            rng_state=rng.getstate(),
            attachments_by_step=state.attachments_by_step + [len(additions)],
            population_by_step=state.population_by_step + [len(occupied)],
        ),
        len(additions),
    )


def run_crystal(
    inputs: Sequence[float],
    *,
    seed: int,
    max_radius: int,
    params: CrystalParams = CrystalParams(),
) -> CrystalState:
    state = initial_state(seed)
    for value in inputs:
        state, _ = advance_one_step(state, value, max_radius, params)
    return state


def cell_keyed_uniform(seed: int, absolute_step: int, cell: Cell) -> float:
    payload = f"{seed}:{absolute_step}:{cell[0]}:{cell[1]}".encode("utf-8")
    raw = hashlib.sha256(payload).digest()[:8]
    return int.from_bytes(raw, "big") / 2**64
