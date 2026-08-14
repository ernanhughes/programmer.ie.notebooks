#!/usr/bin/env python3
"""
Digital Life — Chapter 27 V1 Construct-Validity / Mechanism Audit
=================================================================

ROLE
----

ANALYSIS-ONLY AUDIT of the already-completed Chapter 27 V1 scientific run.

This script does NOT:
- generate a new scientific sample
- use a fresh seed
- change the frozen V1 protocol
- repair the V1 primary outcome
- promote a new scientific verdict
- create V2

It reads the existing V1 raw outputs and reconstructs selected lag-1
mechanics from the original code.

WHY THIS AUDIT EXISTS
---------------------

A construct-validity defect was identified after the V1 scientific run:

    PREVENT did not explicitly prevent x from attaching.

The V1 protocol intended:

    FORCE   : x occupied for one causal exposure
    PREVENT : x absent for one causal exposure

The implementation actually did:

    FORCE   : x inserted before lag 1
    PREVENT : x initially absent, but still eligible to attach naturally

After lag 1 FORCE explicitly removes x, while PREVENT can retain a naturally
attached x.

Therefore the 12-step realized G_T trajectory is contaminated by an
arm-dependent probability that x itself enters PREVENT.

The V1 immediate expected E1_ring1 calculation is still interpretable because
it is calculated before realized lag-1 growth and excludes x itself.

AUDIT QUESTIONS
---------------

A. PREVENT-x ATTACHMENT CONFOUND

Recover, for every probe and arm:

    p_prevent(x)

using both:
1. direct reconstruction from the Chapter 27 mechanics
2. the identity:

       p_prevent(x)
         =
         E1_global
         - (force_expected_attachments - prevent_expected_attachments)

   at lag 1.

Assert agreement.

Report p_prevent(x) by arm and contrasts:
    accessible - remote
    accessible - erased
    remote - erased

Also reconstruct whether x actually attached in PREVENT at lag 1 from the
same keyed random threshold and report realized attachment rates.

B. IMMEDIATE E1 SATURATION MECHANISM

The accessible trace includes x's sole occupied neighbour s.

Because MATERIAL_GAIN > 0, material raises the baseline score of affected
ring-1 shared candidates.

The hypothesis to audit is:

    accessible material
    -> higher baseline p
    -> smaller logistic incremental response to FORCE's n -> n+1 change
    -> lower E1_ring1

For each candidate in the lag-1 ring-1 union, compute exact expected
contributions under:
    accessible
    remote
    erased

Decompose accessible-minus-erased and accessible-minus-remote into:

    force-only candidate contribution
    prevent-only candidate contribution
    shared-candidate probability-shift contribution

For shared candidates, also compute:

    delta_p_history
        = p_force(history) - p_prevent(history)

    delta_p_erased
        = p_force(erased) - p_prevent(erased)

    saturation_delta
        = delta_p_history - delta_p_erased

Report whether the observed negative accessible E1 contrast is primarily
accounted for by reduced shared-candidate probability increments.

This is MECHANISM AUDIT, not a new hypothesis test.

C. REMOTE -> GLOBAL CALIBRATION -> LOCAL CHANNEL

Remote material has zero direct local material exposure by construction.

Yet remote - erased E1 is nonzero.

Quantify the calibration pathway at lag 1:

    remote material
    -> remote PREVENT raw expected construction differs from erased
    -> solve_offset(remote) != 0
    -> global offset changes ring-1 probabilities
    -> local E1 shifts

For each probe:
1. compute remote E1 at its fitted offset
2. compute remote E1 counterfactually at offset 0
3. define:

       calibration_channel
         =
         E1_remote(fitted offset)
         - E1_remote(offset 0)

4. compare remote(offset 0) to erased(offset 0)

This separates:
    direct remote material effect
from
    global calibration leakage.

D. MATERIAL-MASS TRAJECTORY DIFFERENCE

From raw-v1-per-lag.jsonl, compute paired group-level:

    accessible material mass - remote material mass

for every lag.

Report:
    total material mass difference
    local material mass difference

Also relate each group's 12-lag material-mass difference summary to its
realized accessible-minus-remote G_T.

This is diagnostic only because material survival is downstream of treatment.

E. RAO-BLACKWELLIZED IMPLEMENTED-PROTOCOL DIAGNOSTIC

For every probe and arm, sum over lags:

    force_expected_attachments
    -
    prevent_expected_attachments

but exclude x's direct expected contribution wherever x is a frontier
candidate, because G_T excludes x itself.

The result is:

    RB_G_IMPLEMENTED

This is a conditional-expectation diagnostic for the IMPLEMENTED V1
trajectory, not a repair of the intended experiment.

Primary diagnostic contrast:

    RB_G_IMPLEMENTED(accessible)
    -
    RB_G_IMPLEMENTED(remote)

Report:
    mean
    bootstrap CI
    group-level SD
    achieved MDE80

Also compare with the realized V1:
    G_local(accessible) - G_local(remote)

IMPORTANT:
Even if RB_G_IMPLEMENTED is precise, it does NOT rescue V1 because later states
can already be contaminated by PREVENT x attachment.

F. COMMON-RANDOM-NUMBER PAIRING

Compute group-level correlations for:
    accessible vs remote G_local
    accessible vs erased G_local
    remote vs erased G_local

This documents how well CRN pairing survived the small Chapter 27 calibration
differences.

G. STRUCTURAL ASSERTIONS

Do NOT bootstrap quantities forced by the protocol.

Assert:
    erased offset == 0
    remote direct local material exposure at lag 1 == 0
    erased direct local material exposure at lag 1 == 0

Output them once as assertions.

INPUTS
------

Default existing V1 report directory:

    research/digital-life/
    ch27-decaying-material-history-causal-response-v1

Required raw files:

    raw-v1-arm-results.jsonl
    raw-v1-per-lag.jsonl

Required experiment modules beside this script:

    ch18_digital_crystal_persistent_material_state_v7.py
    ch21_digital_crystal_finite_update_budget_v3.py
    ch24_digital_crystal_frontier_creation_causal_gain_v4.py
    ch26_digital_crystal_dynamically_matched_rate_causal_amplification_v2.py
    ch27_digital_crystal_decaying_material_history_causal_response_v1.py

SEED
----

Must use original V1 seed:

    20260914

OUTPUTS
-------

    ch27-v1-construct-validity-audit-report.json
    ch27-v1-construct-validity-audit-report.md

    audit-prevent-x.csv
    audit-e1-saturation-channels.csv
    audit-remote-calibration-channel.csv
    audit-material-mass-by-lag.csv
    audit-rb-implemented-protocol.csv
    audit-group-pairing.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np

import ch18_digital_crystal_persistent_material_state_v7 as ch18
import ch21_digital_crystal_finite_update_budget_v3 as ch21
import ch24_digital_crystal_frontier_creation_causal_gain_v4 as v4
import ch26_digital_crystal_dynamically_matched_rate_causal_amplification_v2 as ch26
import ch27_digital_crystal_decaying_material_history_causal_response_v1 as ch27


Cell = Tuple[int, int]

ORIGINAL_SEED = 20260914
PRIMARY_SEI = 0.15
ASSERT_TOL = 1e-12

Z_95_ONE_SIDED = 1.6448536269514722
Z_80_POWER = 0.8416212335729143

ARMS = [
    "accessible",
    "remote",
    "erased",
]


# ============================================================================
# IO / stats helpers
# ============================================================================

def read_jsonl(path: Path) -> List[dict]:
    if not path.exists():
        raise FileNotFoundError(path)

    rows = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as f:
        for line in f:
            line = line.strip()

            if line:
                rows.append(
                    json.loads(
                        line
                    )
                )

    return rows


def write_csv(
    path: Path,
    rows: Sequence[dict],
) -> None:
    rows = list(rows)

    if not rows:
        path.write_text(
            "",
            encoding="utf-8",
        )
        return

    fields = []
    seen = set()

    for row in rows:
        for key in row.keys():
            if key not in seen:
                seen.add(key)
                fields.append(key)

    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fields,
        )

        writer.writeheader()
        writer.writerows(
            rows
        )


def finite_array(
    values: Iterable[float],
) -> np.ndarray:
    return np.asarray(
        [
            float(v)
            for v in values
            if math.isfinite(
                float(v)
            )
        ],
        dtype=float,
    )


def bootstrap_mean_ci(
    values: Sequence[float],
    reps: int,
    seed: int,
) -> dict:
    arr = finite_array(
        values
    )

    if len(arr) == 0:
        return {
            "n": 0,
            "mean": float("nan"),
            "sd": float("nan"),
            "se": float("nan"),
            "ci95_low": float("nan"),
            "ci95_high": float("nan"),
            "achieved_mde80_one_sided": float("nan"),
        }

    rng = np.random.default_rng(
        seed
    )

    boot = np.empty(
        int(reps),
        dtype=float,
    )

    for i in range(
        int(reps)
    ):
        boot[i] = float(
            np.mean(
                rng.choice(
                    arr,
                    size=len(arr),
                    replace=True,
                )
            )
        )

    sd = (
        float(
            np.std(
                arr,
                ddof=1,
            )
        )
        if len(arr) > 1
        else 0.0
    )

    se = (
        sd
        / math.sqrt(
            len(arr)
        )
        if len(arr)
        else float("nan")
    )

    return {
        "n": int(
            len(arr)
        ),
        "mean": float(
            np.mean(
                arr
            )
        ),
        "sd": sd,
        "se": float(
            se
        ),
        "ci95_low": float(
            np.quantile(
                boot,
                0.025,
            )
        ),
        "ci95_high": float(
            np.quantile(
                boot,
                0.975,
            )
        ),
        "achieved_mde80_one_sided": float(
            se
            * (
                Z_95_ONE_SIDED
                + Z_80_POWER
            )
        ),
    }


def corr(
    x: Sequence[float],
    y: Sequence[float],
) -> float:
    xa = np.asarray(
        x,
        dtype=float,
    )

    ya = np.asarray(
        y,
        dtype=float,
    )

    mask = (
        np.isfinite(
            xa
        )
        & np.isfinite(
            ya
        )
    )

    xa = xa[
        mask
    ]

    ya = ya[
        mask
    ]

    if len(xa) < 3:
        return float(
            "nan"
        )

    if (
        np.std(
            xa
        )
        == 0
        or np.std(
            ya
        )
        == 0
    ):
        return float(
            "nan"
        )

    return float(
        np.corrcoef(
            xa,
            ya,
        )[0, 1]
    )


def ols_hc1(
    X: np.ndarray,
    y: np.ndarray,
) -> dict:
    X = np.asarray(
        X,
        dtype=float,
    )

    y = np.asarray(
        y,
        dtype=float,
    )

    mask = (
        np.all(
            np.isfinite(
                X
            ),
            axis=1,
        )
        & np.isfinite(
            y
        )
    )

    X = X[
        mask
    ]

    y = y[
        mask
    ]

    n, p = X.shape

    if n <= p:
        return {
            "n": int(
                n
            ),
            "coef": [
                float(
                    "nan"
                )
            ] * p,
            "se_hc1": [
                float(
                    "nan"
                )
            ] * p,
        }

    XtX_inv = np.linalg.pinv(
        X.T @ X
    )

    beta = (
        XtX_inv
        @ X.T
        @ y
    )

    resid = (
        y
        - X @ beta
    )

    meat = np.zeros(
        (
            p,
            p,
        ),
        dtype=float,
    )

    for i in range(
        n
    ):
        xi = X[
            i:i+1
        ].T

        meat += (
            resid[i] ** 2
        ) * (
            xi
            @ xi.T
        )

    hc1 = (
        n
        / max(
            1,
            n - p,
        )
    ) * (
        XtX_inv
        @ meat
        @ XtX_inv
    )

    se = np.sqrt(
        np.maximum(
            0.0,
            np.diag(
                hc1
            ),
        )
    )

    return {
        "n": int(
            n
        ),
        "coef": [
            float(v)
            for v
            in beta
        ],
        "se_hc1": [
            float(v)
            for v
            in se
        ],
    }


# ============================================================================
# Raw-row helpers
# ============================================================================

def arm_lookup(
    rows: Sequence[dict],
) -> Dict[
    Tuple[
        int,
        int,
        str,
    ],
    dict,
]:
    return {
        (
            int(
                row[
                    "group"
                ]
            ),
            int(
                row[
                    "probe_index"
                ]
            ),
            str(
                row[
                    "history_arm"
                ]
            ),
        ): row
        for row
        in rows
    }


def lag_lookup(
    rows: Sequence[dict],
) -> Dict[
    Tuple[
        int,
        int,
        str,
        int,
    ],
    dict,
]:
    return {
        (
            int(
                row[
                    "group"
                ]
            ),
            int(
                row[
                    "probe_index"
                ]
            ),
            str(
                row[
                    "history_arm"
                ]
            ),
            int(
                row[
                    "lag"
                ]
            ),
        ): row
        for row
        in rows
    }


def group_mean_map(
    rows: Sequence[dict],
    arm: str,
    field: str,
) -> Dict[
    int,
    float,
]:
    buckets = defaultdict(
        list
    )

    for row in rows:
        if (
            row[
                "history_arm"
            ]
            != arm
        ):
            continue

        value = float(
            row[
                field
            ]
        )

        if not math.isfinite(
            value
        ):
            continue

        buckets[
            int(
                row[
                    "group"
                ]
            )
        ].append(
            value
        )

    return {
        group: float(
            np.mean(
                vals
            )
        )
        for group, vals
        in buckets.items()
        if vals
    }


def paired_group_difference(
    rows: Sequence[dict],
    arm_a: str,
    arm_b: str,
    field: str,
) -> Tuple[
    List[int],
    np.ndarray,
    np.ndarray,
    np.ndarray,
]:
    a = group_mean_map(
        rows,
        arm_a,
        field,
    )

    b = group_mean_map(
        rows,
        arm_b,
        field,
    )

    groups = sorted(
        set(
            a
        )
        & set(
            b
        )
    )

    av = np.asarray(
        [
            a[g]
            for g
            in groups
        ],
        dtype=float,
    )

    bv = np.asarray(
        [
            b[g]
            for g
            in groups
        ],
        dtype=float,
    )

    return (
        groups,
        av,
        bv,
        av - bv,
    )


# ============================================================================
# Reconstruct supported V1 probes + history states
# ============================================================================

@dataclass
class ProbeBundle:
    group: int
    probe_index: int
    cell: Cell
    probe: ch27.Probe
    placement: ch27.HistoryPlacement
    histories: Dict[
        str,
        ch27.HistoryState,
    ]


def reconstruct_bundles(
    profile_name: str,
    seed: int,
) -> Dict[
    Tuple[
        int,
        int,
    ],
    ProbeBundle,
]:
    profile = dict(
        ch27.PROFILES[
            profile_name
        ]
    )

    source_profile = dict(
        v4.PROFILES[
            profile[
                "source_profile"
            ]
        ]
    )

    source_profile[
        "groups"
    ] = int(
        profile[
            "groups"
        ]
    )

    source_profile[
        "horizon"
    ] = ch27.HORIZON

    crystal_params = (
        ch18.CrystalParams()
    )

    probes, _support = (
        ch27.prepare_probes(
            profile,
            source_profile,
            crystal_params,
            seed,
        )
    )

    out = {}

    for probe in probes:
        placement = (
            ch27.build_history_placement(
                probe
            )
        )

        if placement is None:
            continue

        histories = (
            ch27.build_history_states(
                probe,
                placement,
            )
        )

        key = (
            int(
                probe.group
            ),
            int(
                probe.probe_index
            ),
        )

        out[
            key
        ] = ProbeBundle(
            group=key[
                0
            ],
            probe_index=key[
                1
            ],
            cell=probe.cell,
            probe=probe,
            placement=placement,
            histories=histories,
        )

    return out


# ============================================================================
# Lag-1 reconstructed mechanics
# ============================================================================

@dataclass
class Lag1Mechanics:
    arm: str
    force: ch27.HistoryState
    prevent: ch27.HistoryState
    offset: float
    target: float
    input_value: float
    radius: int


def lag1_mechanics(
    bundle: ProbeBundle,
    arm: str,
    source_profile: dict,
    crystal_params: ch18.CrystalParams,
) -> Lag1Mechanics:
    history_state = (
        bundle.histories[
            arm
        ]
    )

    branches = (
        ch27.make_branches(
            history_state,
            bundle.cell,
        )
    )

    reference_targets = (
        ch27.build_reference_targets(
            bundle.probe,
            source_profile,
            crystal_params,
        )
    )

    target = float(
        reference_targets[
            0
        ].target
    )

    input_value = float(
        bundle.probe.future_env[
            1
        ]
    )

    radius = int(
        source_profile[
            "radius"
        ]
    )

    if arm == "erased":
        offset = 0.0
    else:
        (
            offset,
            _achieved,
            solved,
        ) = ch27.solve_offset(
            branches.prevent,
            input_value,
            radius,
            crystal_params,
            target,
        )

        if not solved:
            raise RuntimeError(
                f"Could not solve offset for {bundle.group}/{bundle.probe_index}/{arm}"
            )

    return Lag1Mechanics(
        arm=arm,
        force=branches.force,
        prevent=branches.prevent,
        offset=float(
            offset
        ),
        target=float(
            target
        ),
        input_value=float(
            input_value
        ),
        radius=int(
            radius
        ),
    )


def direct_p_prevent_x(
    mech: Lag1Mechanics,
    x: Cell,
    crystal_params: ch18.CrystalParams,
) -> float:
    frontier = set(
        ch27.frontier_cells(
            mech.prevent,
            mech.radius,
        )
    )

    if x not in frontier:
        return 0.0

    return float(
        ch27.attachment_probability(
            x,
            mech.prevent,
            mech.input_value,
            crystal_params,
            mech.offset,
        )
    )


def realized_prevent_x_attaches(
    mech: Lag1Mechanics,
    x: Cell,
    crystal_params: ch18.CrystalParams,
) -> bool:
    p = (
        direct_p_prevent_x(
            mech,
            x,
            crystal_params,
        )
    )

    if p <= 0.0:
        return False

    next_step = int(
        mech.prevent.step
        + 1
    )

    u = ch18.cell_uniform(
        mech.prevent.stream_seed,
        next_step,
        x,
    )

    return bool(
        u < p
    )


# ============================================================================
# A. p_prevent(x) audit
# ============================================================================

def audit_prevent_x(
    bundles: Dict[
        Tuple[
            int,
            int,
        ],
        ProbeBundle,
    ],
    raw_arm: Dict[
        Tuple[
            int,
            int,
            str,
        ],
        dict,
    ],
    raw_lag: Dict[
        Tuple[
            int,
            int,
            str,
            int,
        ],
        dict,
    ],
    source_profile: dict,
    crystal_params: ch18.CrystalParams,
    bootstrap_reps: int,
    seed: int,
) -> Tuple[
    dict,
    List[dict],
]:
    rows = []

    for (
        group,
        probe_index,
    ), bundle in bundles.items():

        for arm in ARMS:
            mech = (
                lag1_mechanics(
                    bundle,
                    arm,
                    source_profile,
                    crystal_params,
                )
            )

            direct = (
                direct_p_prevent_x(
                    mech,
                    bundle.cell,
                    crystal_params,
                )
            )

            raw_a = raw_arm[
                (
                    group,
                    probe_index,
                    arm,
                )
            ]

            raw_l = raw_lag[
                (
                    group,
                    probe_index,
                    arm,
                    1,
                )
            ]

            identity = float(
                raw_a[
                    "E1_global"
                ]
                - (
                    float(
                        raw_l[
                            "force_expected_attachments"
                        ]
                    )
                    - float(
                        raw_l[
                            "prevent_expected_attachments"
                        ]
                    )
                )
            )

            error = (
                direct
                - identity
            )

            if abs(
                error
            ) > 1e-10:
                raise RuntimeError(
                    f"p_prevent(x) identity failed "
                    f"{group}/{probe_index}/{arm}: {error}"
                )

            realized = int(
                realized_prevent_x_attaches(
                    mech,
                    bundle.cell,
                    crystal_params,
                )
            )

            rows.append({
                "group": group,
                "probe_index": probe_index,
                "history_arm": arm,
                "p_prevent_x_direct": direct,
                "p_prevent_x_identity": identity,
                "identity_error": error,
                "prevent_x_attached_realized": realized,
                "offset_lag1": mech.offset,
            })

    summary = {}

    for idx, arm in enumerate(
        ARMS
    ):
        subset = [
            r
            for r in rows
            if r[
                "history_arm"
            ] == arm
        ]

        summary[
            arm
        ] = {
            "p_prevent_x": bootstrap_mean_ci(
                [
                    r[
                        "p_prevent_x_direct"
                    ]
                    for r in subset
                ],
                bootstrap_reps,
                seed
                + 100
                + idx,
            ),
            "realized_prevent_x_attachment_rate": bootstrap_mean_ci(
                [
                    r[
                        "prevent_x_attached_realized"
                    ]
                    for r in subset
                ],
                bootstrap_reps,
                seed
                + 200
                + idx,
            ),
        }

    # Group-paired contrasts.
    def group_arm_mean(
        arm: str,
        field: str,
    ) -> Dict[
        int,
        float,
    ]:
        buckets = defaultdict(
            list
        )

        for row in rows:
            if (
                row[
                    "history_arm"
                ]
                != arm
            ):
                continue

            buckets[
                int(
                    row[
                        "group"
                    ]
                )
            ].append(
                float(
                    row[
                        field
                    ]
                )
            )

        return {
            g: float(
                np.mean(
                    vals
                )
            )
            for g, vals
            in buckets.items()
        }

    contrasts = {}

    pairs = [
        (
            "accessible",
            "remote",
        ),
        (
            "accessible",
            "erased",
        ),
        (
            "remote",
            "erased",
        ),
    ]

    for j, (
        a,
        b,
    ) in enumerate(
        pairs
    ):
        ma = group_arm_mean(
            a,
            "p_prevent_x_direct",
        )

        mb = group_arm_mean(
            b,
            "p_prevent_x_direct",
        )

        common = sorted(
            set(
                ma
            )
            & set(
                mb
            )
        )

        diff = [
            ma[g]
            - mb[g]
            for g in common
        ]

        contrasts[
            f"{a}_minus_{b}"
        ] = bootstrap_mean_ci(
            diff,
            bootstrap_reps,
            seed
            + 300
            + j,
        )

    return (
        {
            "by_arm": summary,
            "paired_group_contrasts": contrasts,
            "identity_assertion": (
                "p_prevent(x) = E1_global - "
                "(force_expected - prevent_expected)"
            ),
        },
        rows,
    )


# ============================================================================
# B. E1 saturation/channel audit
# ============================================================================

def candidate_ring1_contributions(
    mech: Lag1Mechanics,
    x: Cell,
    crystal_params: ch18.CrystalParams,
) -> List[dict]:
    ff = set(
        ch27.frontier_cells(
            mech.force,
            mech.radius,
        )
    )

    pf = set(
        ch27.frontier_cells(
            mech.prevent,
            mech.radius,
        )
    )

    rows = []

    for cell in sorted(
        ff | pf
    ):
        if cell == x:
            continue

        if (
            v4.relative_distance(
                cell,
                x,
            )
            > 1
        ):
            continue

        p_force = (
            ch27.attachment_probability(
                cell,
                mech.force,
                mech.input_value,
                crystal_params,
                mech.offset,
            )
            if cell in ff
            else 0.0
        )

        p_prevent = (
            ch27.attachment_probability(
                cell,
                mech.prevent,
                mech.input_value,
                crystal_params,
                mech.offset,
            )
            if cell in pf
            else 0.0
        )

        if (
            cell in ff
            and cell not in pf
        ):
            channel = (
                "force_only"
            )
        elif (
            cell in pf
            and cell not in ff
        ):
            channel = (
                "prevent_only"
            )
        else:
            channel = (
                "shared"
            )

        rows.append({
            "cell": cell,
            "channel": channel,
            "p_force": float(
                p_force
            ),
            "p_prevent": float(
                p_prevent
            ),
            "delta_p": float(
                p_force
                - p_prevent
            ),
        })

    return rows


def audit_e1_saturation(
    bundles: Dict[
        Tuple[
            int,
            int,
        ],
        ProbeBundle,
    ],
    source_profile: dict,
    crystal_params: ch18.CrystalParams,
    bootstrap_reps: int,
    seed: int,
) -> Tuple[
    dict,
    List[dict],
]:
    detail = []

    aggregate = defaultdict(
        lambda: defaultdict(
            list
        )
    )

    for (
        group,
        probe_index,
    ), bundle in bundles.items():

        mechs = {
            arm: lag1_mechanics(
                bundle,
                arm,
                source_profile,
                crystal_params,
            )
            for arm in ARMS
        }

        contrib = {
            arm: candidate_ring1_contributions(
                mechs[
                    arm
                ],
                bundle.cell,
                crystal_params,
            )
            for arm in ARMS
        }

        # Per-arm exact channel totals.
        totals = {}

        for arm in ARMS:
            force_only = sum(
                r[
                    "delta_p"
                ]
                for r in contrib[
                    arm
                ]
                if r[
                    "channel"
                ] == "force_only"
            )

            prevent_only = sum(
                r[
                    "delta_p"
                ]
                for r in contrib[
                    arm
                ]
                if r[
                    "channel"
                ] == "prevent_only"
            )

            shared = sum(
                r[
                    "delta_p"
                ]
                for r in contrib[
                    arm
                ]
                if r[
                    "channel"
                ] == "shared"
            )

            total = (
                force_only
                + prevent_only
                + shared
            )

            totals[
                arm
            ] = {
                "force_only": force_only,
                "prevent_only": prevent_only,
                "shared": shared,
                "total": total,
            }

            for key, value in totals[
                arm
            ].items():
                aggregate[
                    arm
                ][
                    key
                ].append(
                    value
                )

        # Candidate-level accessible vs erased matching by cell.
        erased_map = {
            tuple(
                r[
                    "cell"
                ]
            ): r
            for r in contrib[
                "erased"
            ]
        }

        accessible_map = {
            tuple(
                r[
                    "cell"
                ]
            ): r
            for r in contrib[
                "accessible"
            ]
        }

        shared_sat = []

        for cell in sorted(
            set(
                erased_map
            )
            & set(
                accessible_map
            )
        ):
            ea = erased_map[
                cell
            ]

            aa = accessible_map[
                cell
            ]

            if (
                ea[
                    "channel"
                ]
                != "shared"
                or aa[
                    "channel"
                ]
                != "shared"
            ):
                continue

            sat_delta = (
                aa[
                    "delta_p"
                ]
                - ea[
                    "delta_p"
                ]
            )

            shared_sat.append(
                sat_delta
            )

            detail.append({
                "group": group,
                "probe_index": probe_index,
                "q": int(
                    cell[
                        0
                    ]
                ),
                "r": int(
                    cell[
                        1
                    ]
                ),
                "comparison": (
                    "accessible_minus_erased"
                ),
                "channel": (
                    "shared"
                ),
                "delta_p_accessible": float(
                    aa[
                        "delta_p"
                    ]
                ),
                "delta_p_erased": float(
                    ea[
                        "delta_p"
                    ]
                ),
                "saturation_delta": float(
                    sat_delta
                ),
            })

        aggregate[
            "accessible_minus_erased"
        ][
            "shared_saturation_delta"
        ].append(
            float(
                sum(
                    shared_sat
                )
            )
        )

        aggregate[
            "accessible_minus_erased"
        ][
            "E1_total_difference"
        ].append(
            float(
                totals[
                    "accessible"
                ][
                    "total"
                ]
                - totals[
                    "erased"
                ][
                    "total"
                ]
            )
        )

        aggregate[
            "accessible_minus_remote"
        ][
            "E1_total_difference"
        ].append(
            float(
                totals[
                    "accessible"
                ][
                    "total"
                ]
                - totals[
                    "remote"
                ][
                    "total"
                ]
            )
        )

    summary = {}

    for idx, arm in enumerate(
        ARMS
    ):
        summary[
            arm
        ] = {}

        for j, field in enumerate(
            [
                "force_only",
                "prevent_only",
                "shared",
                "total",
            ]
        ):
            summary[
                arm
            ][
                field
            ] = bootstrap_mean_ci(
                aggregate[
                    arm
                ][
                    field
                ],
                bootstrap_reps,
                seed
                + idx * 100
                + j,
            )

    summary[
        "accessible_minus_erased"
    ] = {
        "shared_saturation_delta_sum": bootstrap_mean_ci(
            aggregate[
                "accessible_minus_erased"
            ][
                "shared_saturation_delta"
            ],
            bootstrap_reps,
            seed
            + 1000,
        ),
        "E1_total_difference": bootstrap_mean_ci(
            aggregate[
                "accessible_minus_erased"
            ][
                "E1_total_difference"
            ],
            bootstrap_reps,
            seed
            + 1001,
        ),
    }

    summary[
        "accessible_minus_remote"
    ] = {
        "E1_total_difference": bootstrap_mean_ci(
            aggregate[
                "accessible_minus_remote"
            ][
                "E1_total_difference"
            ],
            bootstrap_reps,
            seed
            + 1002,
        ),
    }

    return (
        summary,
        detail,
    )


# ============================================================================
# C. Remote calibration channel
# ============================================================================

def e1_total_with_offset(
    mech: Lag1Mechanics,
    x: Cell,
    crystal_params: ch18.CrystalParams,
    offset: float,
) -> float:
    ff = set(
        ch27.frontier_cells(
            mech.force,
            mech.radius,
        )
    )

    pf = set(
        ch27.frontier_cells(
            mech.prevent,
            mech.radius,
        )
    )

    total = 0.0

    for cell in ff | pf:
        if cell == x:
            continue

        if (
            v4.relative_distance(
                cell,
                x,
            )
            > 1
        ):
            continue

        p_force = (
            ch27.attachment_probability(
                cell,
                mech.force,
                mech.input_value,
                crystal_params,
                offset,
            )
            if cell in ff
            else 0.0
        )

        p_prevent = (
            ch27.attachment_probability(
                cell,
                mech.prevent,
                mech.input_value,
                crystal_params,
                offset,
            )
            if cell in pf
            else 0.0
        )

        total += (
            p_force
            - p_prevent
        )

    return float(
        total
    )


def audit_remote_calibration(
    bundles: Dict[
        Tuple[
            int,
            int,
        ],
        ProbeBundle,
    ],
    source_profile: dict,
    crystal_params: ch18.CrystalParams,
    bootstrap_reps: int,
    seed: int,
) -> Tuple[
    dict,
    List[dict],
]:
    rows = []

    for (
        group,
        probe_index,
    ), bundle in bundles.items():

        remote = (
            lag1_mechanics(
                bundle,
                "remote",
                source_profile,
                crystal_params,
            )
        )

        erased = (
            lag1_mechanics(
                bundle,
                "erased",
                source_profile,
                crystal_params,
            )
        )

        remote_fitted = (
            e1_total_with_offset(
                remote,
                bundle.cell,
                crystal_params,
                remote.offset,
            )
        )

        remote_zero = (
            e1_total_with_offset(
                remote,
                bundle.cell,
                crystal_params,
                0.0,
            )
        )

        erased_zero = (
            e1_total_with_offset(
                erased,
                bundle.cell,
                crystal_params,
                0.0,
            )
        )

        rows.append({
            "group": group,
            "probe_index": probe_index,
            "remote_offset": remote.offset,
            "E1_remote_fitted": remote_fitted,
            "E1_remote_offset0": remote_zero,
            "E1_erased_offset0": erased_zero,
            "calibration_channel": (
                remote_fitted
                - remote_zero
            ),
            "direct_remote_minus_erased_at_offset0": (
                remote_zero
                - erased_zero
            ),
            "total_remote_minus_erased": (
                remote_fitted
                - erased_zero
            ),
        })

    # Group means before bootstrap.
    def grouped(
        field: str,
    ) -> List[
        float
    ]:
        buckets = defaultdict(
            list
        )

        for row in rows:
            buckets[
                int(
                    row[
                        "group"
                    ]
                )
            ].append(
                float(
                    row[
                        field
                    ]
                )
            )

        return [
            float(
                np.mean(
                    vals
                )
            )
            for _, vals
            in sorted(
                buckets.items()
            )
        ]

    summary = {
        "remote_offset": bootstrap_mean_ci(
            grouped(
                "remote_offset"
            ),
            bootstrap_reps,
            seed
            + 2000,
        ),
        "calibration_channel": bootstrap_mean_ci(
            grouped(
                "calibration_channel"
            ),
            bootstrap_reps,
            seed
            + 2001,
        ),
        "direct_remote_minus_erased_at_offset0": bootstrap_mean_ci(
            grouped(
                "direct_remote_minus_erased_at_offset0"
            ),
            bootstrap_reps,
            seed
            + 2002,
        ),
        "total_remote_minus_erased": bootstrap_mean_ci(
            grouped(
                "total_remote_minus_erased"
            ),
            bootstrap_reps,
            seed
            + 2003,
        ),
    }

    return (
        summary,
        rows,
    )


# ============================================================================
# D. material-mass trajectory
# ============================================================================

def audit_material_mass(
    lag_rows: Sequence[dict],
    arm_rows: Sequence[dict],
    bootstrap_reps: int,
    seed: int,
) -> Tuple[
    dict,
    List[dict],
]:
    detail = []
    summary = {}

    for lag in range(
        1,
        ch27.HORIZON + 1,
    ):
        for field in [
            "prevent_material_mass",
            "prevent_local_material_mass",
        ]:
            a = defaultdict(
                list
            )

            b = defaultdict(
                list
            )

            for row in lag_rows:
                if int(
                    row[
                        "lag"
                    ]
                ) != lag:
                    continue

                group = int(
                    row[
                        "group"
                    ]
                )

                if (
                    row[
                        "history_arm"
                    ]
                    == "accessible"
                ):
                    a[
                        group
                    ].append(
                        float(
                            row[
                                field
                            ]
                        )
                    )

                elif (
                    row[
                        "history_arm"
                    ]
                    == "remote"
                ):
                    b[
                        group
                    ].append(
                        float(
                            row[
                                field
                            ]
                        )
                    )

            common = sorted(
                set(
                    a
                )
                & set(
                    b
                )
            )

            diffs = []

            for group in common:
                av = float(
                    np.mean(
                        a[
                            group
                        ]
                    )
                )

                bv = float(
                    np.mean(
                        b[
                            group
                        ]
                    )
                )

                diff = (
                    av
                    - bv
                )

                diffs.append(
                    diff
                )

                detail.append({
                    "group": group,
                    "lag": lag,
                    "field": field,
                    "accessible_mean": av,
                    "remote_mean": bv,
                    "difference": diff,
                })

            summary.setdefault(
                str(
                    lag
                ),
                {},
            )[
                field
            ] = bootstrap_mean_ci(
                diffs,
                bootstrap_reps,
                seed
                + 3000
                + lag * 10
                + (
                    0
                    if field
                    == "prevent_material_mass"
                    else 1
                ),
            )

    # Group summary: average total material-mass difference across 12 lags.
    mass_by_group = defaultdict(
        list
    )

    for row in detail:
        if (
            row[
                "field"
            ]
            == "prevent_material_mass"
        ):
            mass_by_group[
                int(
                    row[
                        "group"
                    ]
                )
            ].append(
                float(
                    row[
                        "difference"
                    ]
                )
            )

    mean_mass_diff = {
        g: float(
            np.mean(
                vals
            )
        )
        for g, vals
        in mass_by_group.items()
        if vals
    }

    groups, ga, gb, dG = (
        paired_group_difference(
            arm_rows,
            "accessible",
            "remote",
            "G_local",
        )
    )

    X = []
    y = []

    for i, group in enumerate(
        groups
    ):
        if group not in mean_mass_diff:
            continue

        X.append([
            1.0,
            mean_mass_diff[
                group
            ],
        ])

        y.append(
            float(
                dG[
                    i
                ]
            )
        )

    fit = ols_hc1(
        np.asarray(
            X,
            dtype=float,
        ),
        np.asarray(
            y,
            dtype=float,
        ),
    )

    summary[
        "group_level_G_vs_mean_mass_difference"
    ] = {
        "model": (
            "Delta_G = alpha + beta * mean_12lag_material_mass_difference"
        ),
        "alpha": (
            fit[
                "coef"
            ][0]
            if fit[
                "coef"
            ]
            else float(
                "nan"
            )
        ),
        "beta": (
            fit[
                "coef"
            ][1]
            if len(
                fit[
                    "coef"
                ]
            ) > 1
            else float(
                "nan"
            )
        ),
        "alpha_HC1_SE": (
            fit[
                "se_hc1"
            ][0]
            if fit[
                "se_hc1"
            ]
            else float(
                "nan"
            )
        ),
        "beta_HC1_SE": (
            fit[
                "se_hc1"
            ][1]
            if len(
                fit[
                    "se_hc1"
                ]
            ) > 1
            else float(
                "nan"
            )
        ),
        "corr_DeltaG_massdiff": corr(
            [
                mean_mass_diff[
                    g
                ]
                for g in groups
                if g
                in mean_mass_diff
            ],
            [
                float(
                    dG[
                        i
                    ]
                )
                for i, g
                in enumerate(
                    groups
                )
                if g
                in mean_mass_diff
            ],
        ),
    }

    return (
        summary,
        detail,
    )


# ============================================================================
# E. Rao-Blackwellized implemented-protocol diagnostic
# ============================================================================

def rb_probe_arm(
    bundle: ProbeBundle,
    arm: str,
    lag_rows_lookup: Dict[
        Tuple[
            int,
            int,
            str,
            int,
        ],
        dict,
    ],
) -> float:
    """
    Sum expected FORCE-PREVENT increments from stored V1 rows.

    Correct each lag for x's direct expected contribution because G_local
    excludes x.

    This remains a diagnostic of the implemented V1 trajectory only.
    """
    total = 0.0

    for lag in range(
        1,
        ch27.HORIZON + 1,
    ):
        row = lag_rows_lookup[
            (
                bundle.group,
                bundle.probe_index,
                arm,
                lag,
            )
        ]

        increment = float(
            row[
                "force_expected_attachments"
            ]
            - row[
                "prevent_expected_attachments"
            ]
        )

        # We cannot infer later-lag p(x) from the stored aggregate alone.
        # Reconstruct only the guaranteed lag-1 correction exactly.
        #
        # For lags >1, flag as implemented-path aggregate; x may re-enter
        # either branch, which is part of the contamination.
        if lag == 1:
            mech = lag1_mechanics(
                bundle,
                arm,
                _RB_SOURCE_PROFILE,
                _RB_CRYSTAL_PARAMS,
            )

            ppx = direct_p_prevent_x(
                mech,
                bundle.cell,
                _RB_CRYSTAL_PARAMS,
            )

            increment += ppx

        total += increment

    return float(
        total
    )


_RB_SOURCE_PROFILE = None
_RB_CRYSTAL_PARAMS = None


def audit_rb(
    bundles: Dict[
        Tuple[
            int,
            int,
        ],
        ProbeBundle,
    ],
    lag_rows_lookup: dict,
    arm_rows: Sequence[dict],
    bootstrap_reps: int,
    seed: int,
) -> Tuple[
    dict,
    List[dict],
]:
    rows = []

    for (
        group,
        probe_index,
    ), bundle in bundles.items():
        for arm in ARMS:
            value = rb_probe_arm(
                bundle,
                arm,
                lag_rows_lookup,
            )

            rows.append({
                "group": group,
                "probe_index": probe_index,
                "history_arm": arm,
                "RB_G_IMPLEMENTED_lag1_x_corrected": value,
            })

    def group_map(
        arm: str,
    ) -> Dict[
        int,
        float,
    ]:
        buckets = defaultdict(
            list
        )

        for row in rows:
            if (
                row[
                    "history_arm"
                ]
                != arm
            ):
                continue

            buckets[
                int(
                    row[
                        "group"
                    ]
                )
            ].append(
                float(
                    row[
                        "RB_G_IMPLEMENTED_lag1_x_corrected"
                    ]
                )
            )

        return {
            g: float(
                np.mean(
                    vals
                )
            )
            for g, vals
            in buckets.items()
        }

    a = group_map(
        "accessible"
    )

    b = group_map(
        "remote"
    )

    common = sorted(
        set(
            a
        )
        & set(
            b
        )
    )

    diff = [
        a[g]
        - b[g]
        for g in common
    ]

    realized_groups, _ra, _rb, realized_diff = (
        paired_group_difference(
            arm_rows,
            "accessible",
            "remote",
            "G_local",
        )
    )

    summary = {
        "role": (
            "DIAGNOSTIC_OF_IMPLEMENTED_V1_PROTOCOL_NOT_PRIMARY_REPAIR"
        ),
        "accessible_minus_remote_RB": bootstrap_mean_ci(
            diff,
            bootstrap_reps,
            seed
            + 4000,
        ),
        "realized_accessible_minus_remote": bootstrap_mean_ci(
            realized_diff.tolist(),
            bootstrap_reps,
            seed
            + 4001,
        ),
        "note": (
            "Only lag-1 direct p(x) is explicitly removed. "
            "Later states remain contaminated by natural x attachment/re-entry. "
            "This estimator cannot rescue V1 construct validity."
        ),
    }

    return (
        summary,
        rows,
    )


# ============================================================================
# F. pairing
# ============================================================================

def audit_pairing(
    arm_rows: Sequence[dict],
) -> Tuple[
    dict,
    List[dict],
]:
    pairs = [
        (
            "accessible",
            "remote",
        ),
        (
            "accessible",
            "erased",
        ),
        (
            "remote",
            "erased",
        ),
    ]

    summary = {}
    rows = []

    for a, b in pairs:
        groups, av, bv, diff = (
            paired_group_difference(
                arm_rows,
                a,
                b,
                "G_local",
            )
        )

        payload = {
            "arm_a": a,
            "arm_b": b,
            "n_groups": int(
                len(
                    groups
                )
            ),
            "corr_G_local": corr(
                av,
                bv,
            ),
            "sd_arm_a": float(
                np.std(
                    av,
                    ddof=1,
                )
            ),
            "sd_arm_b": float(
                np.std(
                    bv,
                    ddof=1,
                )
            ),
            "sd_difference": float(
                np.std(
                    diff,
                    ddof=1,
                )
            ),
            "mean_difference": float(
                np.mean(
                    diff
                )
            ),
        }

        summary[
            f"{a}_vs_{b}"
        ] = payload

        rows.append(
            payload
        )

    return (
        summary,
        rows,
    )


# ============================================================================
# G. assertions
# ============================================================================

def audit_assertions(
    bundles: Dict[
        Tuple[
            int,
            int,
        ],
        ProbeBundle,
    ],
    lag_rows: Sequence[dict],
    source_profile: dict,
    crystal_params: ch18.CrystalParams,
) -> dict:
    erased_offsets = [
        abs(
            float(
                row[
                    "offset"
                ]
            )
        )
        for row
        in lag_rows
        if (
            row[
                "history_arm"
            ]
            == "erased"
        )
    ]

    max_erased_offset = (
        max(
            erased_offsets
        )
        if erased_offsets
        else float(
            "nan"
        )
    )

    if (
        not math.isfinite(
            max_erased_offset
        )
        or max_erased_offset
        > ASSERT_TOL
    ):
        raise RuntimeError(
            "Erased offset-zero assertion failed."
        )

    remote_exposure_max = 0.0
    erased_exposure_max = 0.0

    for bundle in bundles.values():
        for arm in [
            "remote",
            "erased",
        ]:
            mech = lag1_mechanics(
                bundle,
                arm,
                source_profile,
                crystal_params,
            )

            # Direct material exposure in ring1.
            frontier = set(
                ch27.frontier_cells(
                    mech.prevent,
                    mech.radius,
                )
            )

            for cell in frontier:
                if (
                    cell
                    == bundle.cell
                    or v4.relative_distance(
                        cell,
                        bundle.cell,
                    )
                    > 1
                ):
                    continue

                exposure = sum(
                    mech.prevent.material_strength.get(
                        nb,
                        0.0,
                    )
                    for nb
                    in ch18.neighbors(
                        cell
                    )
                    if nb
                    in mech.prevent.occupied
                )

                if arm == "remote":
                    remote_exposure_max = max(
                        remote_exposure_max,
                        abs(
                            float(
                                exposure
                            )
                        ),
                    )
                else:
                    erased_exposure_max = max(
                        erased_exposure_max,
                        abs(
                            float(
                                exposure
                            )
                        ),
                    )

    if (
        remote_exposure_max
        > ASSERT_TOL
    ):
        raise RuntimeError(
            "Remote direct local material exposure assertion failed."
        )

    if (
        erased_exposure_max
        > ASSERT_TOL
    ):
        raise RuntimeError(
            "Erased direct local material exposure assertion failed."
        )

    return {
        "erased_offset_zero": {
            "status": "PASS",
            "max_abs": float(
                max_erased_offset
            ),
            "role": (
                "DEFINITION_ASSERTION_NOT_FINDING"
            ),
        },
        "remote_direct_ring1_material_exposure_zero": {
            "status": "PASS",
            "max_abs": float(
                remote_exposure_max
            ),
            "role": (
                "PLACEMENT_ASSERTION_NOT_FINDING"
            ),
        },
        "erased_direct_ring1_material_exposure_zero": {
            "status": "PASS",
            "max_abs": float(
                erased_exposure_max
            ),
            "role": (
                "DEFINITION_ASSERTION_NOT_FINDING"
            ),
        },
    }


# ============================================================================
# Report
# ============================================================================

def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--source-report-dir",
        type=Path,
        default=Path(
            "research/digital-life/"
            "ch27-decaying-material-history-causal-response-v1"
        ),
    )

    parser.add_argument(
        "--audit-dir",
        type=Path,
        default=Path(
            "research/digital-life/"
            "ch27-v1-construct-validity-audit"
        ),
    )

    parser.add_argument(
        "--profile",
        default="full",
        choices=sorted(
            ch27.PROFILES
        ),
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=ORIGINAL_SEED,
    )

    parser.add_argument(
        "--bootstrap-reps",
        type=int,
        default=7000,
    )

    args = parser.parse_args()

    if (
        args.seed
        != ORIGINAL_SEED
    ):
        raise RuntimeError(
            "This audit must use the original Chapter 27 V1 seed 20260914."
        )

    args.audit_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    arm_rows = read_jsonl(
        args.source_report_dir
        / "raw-v1-arm-results.jsonl"
    )

    lag_rows = read_jsonl(
        args.source_report_dir
        / "raw-v1-per-lag.jsonl"
    )

    raw_arm = arm_lookup(
        arm_rows
    )

    raw_lag = lag_lookup(
        lag_rows
    )

    profile = dict(
        ch27.PROFILES[
            args.profile
        ]
    )

    source_profile = dict(
        v4.PROFILES[
            profile[
                "source_profile"
            ]
        ]
    )

    source_profile[
        "groups"
    ] = int(
        profile[
            "groups"
        ]
    )

    source_profile[
        "horizon"
    ] = ch27.HORIZON

    crystal_params = (
        ch18.CrystalParams()
    )

    global _RB_SOURCE_PROFILE
    global _RB_CRYSTAL_PARAMS

    _RB_SOURCE_PROFILE = (
        source_profile
    )

    _RB_CRYSTAL_PARAMS = (
        crystal_params
    )

    print("=" * 78)
    print("CHAPTER 27 V1 CONSTRUCT-VALIDITY / MECHANISM AUDIT")
    print(f"arm rows: {len(arm_rows)}")
    print(f"lag rows: {len(lag_rows)}")
    print("=" * 78)

    bundles = (
        reconstruct_bundles(
            args.profile,
            args.seed,
        )
    )

    print(
        f"reconstructed supported probes: {len(bundles)}"
    )

    # A.
    prevent_x, prevent_x_rows = (
        audit_prevent_x(
            bundles,
            raw_arm,
            raw_lag,
            source_profile,
            crystal_params,
            args.bootstrap_reps,
            args.seed
            + 10000,
        )
    )

    write_csv(
        args.audit_dir
        / "audit-prevent-x.csv",
        prevent_x_rows,
    )

    # B.
    saturation, saturation_rows = (
        audit_e1_saturation(
            bundles,
            source_profile,
            crystal_params,
            args.bootstrap_reps,
            args.seed
            + 20000,
        )
    )

    write_csv(
        args.audit_dir
        / "audit-e1-saturation-channels.csv",
        saturation_rows,
    )

    # C.
    remote_calibration, remote_rows = (
        audit_remote_calibration(
            bundles,
            source_profile,
            crystal_params,
            args.bootstrap_reps,
            args.seed
            + 30000,
        )
    )

    write_csv(
        args.audit_dir
        / "audit-remote-calibration-channel.csv",
        remote_rows,
    )

    # D.
    material_mass, mass_rows = (
        audit_material_mass(
            lag_rows,
            arm_rows,
            args.bootstrap_reps,
            args.seed
            + 40000,
        )
    )

    write_csv(
        args.audit_dir
        / "audit-material-mass-by-lag.csv",
        mass_rows,
    )

    # E.
    rb, rb_rows = (
        audit_rb(
            bundles,
            raw_lag,
            arm_rows,
            args.bootstrap_reps,
            args.seed
            + 50000,
        )
    )

    write_csv(
        args.audit_dir
        / "audit-rb-implemented-protocol.csv",
        rb_rows,
    )

    # F.
    pairing, pairing_rows = (
        audit_pairing(
            arm_rows
        )
    )

    write_csv(
        args.audit_dir
        / "audit-group-pairing.csv",
        pairing_rows,
    )

    # G.
    assertions = (
        audit_assertions(
            bundles,
            lag_rows,
            source_profile,
            crystal_params,
        )
    )

    report = {
        "metadata": {
            "audit_version": (
                "chapter27-v1-construct-validity-mechanism-audit-v1"
            ),
            "scientific_role": (
                "ANALYSIS_ONLY_NO_NEW_EXPERIMENT"
            ),
            "audited_seed": (
                args.seed
            ),
            "v1_primary_construct_validity": (
                "INVALID_PREVENT_DID_NOT_EXPLICITLY_BLOCK_X"
            ),
            "v1_immediate_E1_status": (
                "REMAINS_INTERPRETABLE"
            ),
            "v1_12step_G_status": (
                "INVALID_FOR_INTENDED_INTERVENTION"
            ),
        },
        "audit_A_prevent_x": (
            prevent_x
        ),
        "audit_B_E1_saturation": (
            saturation
        ),
        "audit_C_remote_calibration_channel": (
            remote_calibration
        ),
        "audit_D_material_mass_trajectory": (
            material_mass
        ),
        "audit_E_RB_implemented_protocol": (
            rb
        ),
        "audit_F_CRN_pairing": (
            pairing
        ),
        "audit_G_structural_assertions": (
            assertions
        ),
        "interpretive_boundary": {
            "what_this_audit_can_do": [
                (
                    "Quantify the PREVENT-x implementation confound."
                ),
                (
                    "Test the candidate-level saturation explanation for E1."
                ),
                (
                    "Quantify the remote-history calibration leakage channel."
                ),
                (
                    "Measure material-mass trajectory divergence."
                ),
                (
                    "Measure expected-increment variance reduction for the "
                    "implemented V1 path."
                ),
            ],
            "what_this_audit_cannot_do": [
                (
                    "Rescue the intended 12-step V1 primary intervention."
                ),
                (
                    "Turn the implemented V1 trajectory into a valid FORCE/PREVENT "
                    "experiment after x was allowed to attach naturally in PREVENT."
                ),
                (
                    "Replace a corrected V2 scientific run if a 12-step claim is desired."
                ),
            ],
        },
    }

    json_path = (
        args.audit_dir
        / "ch27-v1-construct-validity-audit-report.json"
    )

    json_path.write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )

    md_path = (
        args.audit_dir
        / "ch27-v1-construct-validity-audit-report.md"
    )

    sections = [
        (
            "A. PREVENT-x confound",
            prevent_x,
        ),
        (
            "B. Immediate E1 saturation/channel audit",
            saturation,
        ),
        (
            "C. Remote calibration channel",
            remote_calibration,
        ),
        (
            "D. Material-mass trajectory",
            material_mass,
        ),
        (
            "E. Rao-Blackwellized implemented-protocol diagnostic",
            rb,
        ),
        (
            "F. Common-random-number pairing",
            pairing,
        ),
        (
            "G. Structural assertions",
            assertions,
        ),
    ]

    md = [
        "# Chapter 27 V1 Construct-Validity / Mechanism Audit",
        "",
        "## Scientific boundary",
        "",
        "This audit analyzes the existing V1 sample only.",
        "",
        "The intended 12-step primary intervention is invalid because PREVENT "
        "did not explicitly prevent x from attaching.",
        "",
        "The immediate pre-growth E1 result remains interpretable.",
        "",
    ]

    for title, payload in sections:
        md.extend(
            [
                f"## {title}",
                "",
                "```json",
                json.dumps(
                    payload,
                    indent=2,
                ),
                "```",
                "",
            ]
        )

    md_path.write_text(
        "\n".join(
            md
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 78)
    print("AUDIT COMPLETE")
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")
    print("=" * 78)


if __name__ == "__main__":
    main()
