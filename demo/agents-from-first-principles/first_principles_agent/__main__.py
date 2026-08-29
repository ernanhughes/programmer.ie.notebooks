from __future__ import annotations

import argparse
import json
from pathlib import Path

from .acceptance import ActionAcceptanceBoundary
from .agent import Agent
from .app import AgentApplication
from .environment import RepositoryEnvironment
from .policy import Stage00Policy, Stage01Policy


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the Agents From First Principles progressive demo."
    )
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--stage", choices=("00", "01", "10"), default="10")
    parser.add_argument(
        "--workspace",
        type=Path,
        help="Optional non-existing destination for the isolated Stage-10 workspace.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.stage == "10":
        result = AgentApplication().run(
            args.task,
            args.repo,
            workspace=args.workspace,
        )
        print(json.dumps(result.as_dict(), indent=2))
        return

    environment = RepositoryEnvironment(args.repo)
    if args.stage == "00":
        agent = Agent(policy=Stage00Policy(), environment=environment)
    else:
        agent = Agent(
            policy=Stage01Policy(),
            environment=environment,
            acceptance=ActionAcceptanceBoundary(args.repo),
        )

    state = agent.run(args.task)
    payload = {
        "stage": args.stage,
        "task": state.task,
        "steps": state.step,
        "termination_reason": state.termination_reason,
        "acceptance_attempts": [
            {
                "accepted": attempt.accepted,
                "stage": attempt.stage.value,
                "reason": attempt.reason,
                "proposal": attempt.proposal_text,
                "action": attempt.action.kind.value if attempt.action is not None else None,
            }
            for attempt in state.acceptance_attempts
        ],
        "transitions": [
            {
                "step": transition.step,
                "action": transition.action.kind.value,
                "target": transition.action.target,
                "reason": transition.action.reason,
                "observation": {
                    "source": transition.observation.source,
                    "ok": transition.observation.ok,
                    "summary": transition.observation.summary,
                    "details": transition.observation.details,
                },
            }
            for transition in state.transitions
        ],
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
