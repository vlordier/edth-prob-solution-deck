"""Phase 0 — Onboarding context I/O."""

from __future__ import annotations

from pathlib import Path
from typing import Any, TypedDict

import yaml

from agent.rubric import DEFAULT_RUBRIC


class AgentContext(TypedDict, total=False):
    hackathon: dict[str, Any]
    team: dict[str, Any]
    constraints: dict[str, Any]
    agent: dict[str, Any]


def default_context() -> AgentContext:
    return AgentContext(
        hackathon={
            "name": "EDTH Munich 2025",
            "theme": "Defense tech / dual-use",
            "tracks": ["C-UAS", "Autonomy", "EW", "UUV", "USV"],
            "judging_rubric": dict(DEFAULT_RUBRIC),
        },
        team={
            "size": 4,
            "strengths": ["ML/CV", "frontend", "signal_proc"],
            "weaknesses": ["hardware", "maritime domain"],
        },
        constraints={
            "time_budget_hours": 48,
            "deliverable": "deck + thin demo",
        },
        agent={
            "owner_mode": "real",
            "persona": "edth-judge",
            "panel_mode": "expanded",
            "aggregation_mode": "borda",
        },
    )


def load_context(artefacts_dir: Path) -> AgentContext:
    path = artefacts_dir / "00_context.yaml"
    if not path.exists():
        return default_context()
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    default = default_context()
    merged = AgentContext(
        hackathon={**default["hackathon"], **data.get("hackathon", {})},
        team={**default["team"], **data.get("team", {})},
        constraints={**default["constraints"], **data.get("constraints", {})},
        agent={**default["agent"], **data.get("agent", {})},
    )
    return merged


def save_context(artefacts_dir: Path, context: AgentContext) -> Path:
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    path = artefacts_dir / "00_context.yaml"
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(dict(context), f, sort_keys=False, default_flow_style=False)
    return path
