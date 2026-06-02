"""Phase 0 — Onboarding context I/O."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, TypedDict

import yaml

from agent._constants import ARTEFACTS
from agent.rubric import DEFAULT_RUBRIC

log = logging.getLogger(__name__)


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
    path = artefacts_dir / ARTEFACTS.CONTEXT
    if not path.exists():
        return default_context()
    with path.open("r", encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            log.warning("Malformed context YAML in %s: %s — falling back to defaults", path, e)
            return default_context()
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
    path = artefacts_dir / ARTEFACTS.CONTEXT
    try:
        with path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(dict(context), f, sort_keys=False, default_flow_style=False)
    except OSError as exc:
        log.error("Failed to save context to %s: %s", path, exc)
        raise
    return path
