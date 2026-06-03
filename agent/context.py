"""Phase 0 — Onboarding context I/O.

Loads and merges hackathon context from artefacts/00_context.yaml
with built-in defaults. Saves updated context back.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, TypedDict

import yaml

from agent._constants import ARTEFACTS
from agent.rubric import DEFAULT_RUBRIC

log = logging.getLogger(__name__)


class AgentContext(TypedDict, total=False):
    """Onboarding context — hackathon metadata, team profile, constraints, agent config."""

    hackathon: dict[str, Any]
    team: dict[str, Any]
    constraints: dict[str, Any]
    agent: dict[str, Any]


def default_context() -> AgentContext:
    """Return a context dict with sensible EDTH defaults."""
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
    """Load 00_context.yaml, falling back to defaults if missing or malformed."""
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
    """Persist context to 00_context.yaml. Creates artefacts dir if needed."""
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    path = artefacts_dir / ARTEFACTS.CONTEXT
    try:
        with path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(dict(context), f, sort_keys=False, default_flow_style=False)
    except OSError as exc:
        log.error("Failed to save context to %s: %s", path, exc)
        raise
    return path
