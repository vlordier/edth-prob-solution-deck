"""State management for the EDTH agent.

Loads and saves the state.json file that tracks the agent's progress
through the 9-phase workflow. See spec §8.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def empty_state() -> dict[str, Any]:
    """Return a fresh empty state dict with the schema from spec §8.1."""
    return {
        "version": "0.1.0",
        "started_at": None,
        "updated_at": None,
        "current_phase": 0,
        "config": {
            "input_csv": "input/sample-problems.csv",
            "output_dir": "artefacts",
            "owner_mode": "real",
            "persona": "edth-judge",
            "panel_mode": "expanded",
            "aggregation_mode": "borda",
            "rubric_path": "hackathons/edth.yaml",
        },
        "phases": {
            str(i): {"status": "pending", "artefact": None, "completed_at": None}
            for i in range(9)
        },
        "decisions": {
            "chosen_problem_id": None,
            "chosen_sub_problem_id": None,
            "chosen_solution_id": None,
        },
        "panel": {
            "auto_selected": [],
            "manually_overridden": False,
            "locked": False,
        },
        "branches": {
            "considered_problems": [],
            "considered_sub_problems": [],
            "considered_solutions": [],
        },
    }


def load_state(artefacts_dir: Path) -> dict[str, Any]:
    """Load state.json from artefacts_dir, or return an empty dict if missing."""
    state_path = artefacts_dir / "state.json"
    if not state_path.exists():
        return {}
    with state_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_state(artefacts_dir: Path, state: dict[str, Any]) -> Path:
    """Save state to artefacts_dir/state.json. Creates the dir if missing."""
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = _now_iso()
    if state.get("started_at") is None:
        state["started_at"] = state["updated_at"]
    state_path = artefacts_dir / "state.json"
    with state_path.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, sort_keys=True)
    return state_path


def get_phase_status(state: dict[str, Any], phase: int) -> str:
    """Return the status string ('pending' | 'in_progress' | 'completed') for a phase."""
    if not state:
        return "pending"
    return state["phases"][str(phase)]["status"]


def mark_phase_completed(
    state: dict[str, Any], phase: int, artefact_path: Path
) -> dict[str, Any]:
    """Mark a phase as completed with its artefact path and a timestamp."""
    state["phases"][str(phase)] = {
        "status": "completed",
        "artefact": str(artefact_path),
        "completed_at": _now_iso(),
    }
    state["current_phase"] = max(state.get("current_phase", 0), phase + 1)
    return state


def set_config(state: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    """Update one or more config fields. Returns the updated state."""
    for key, value in kwargs.items():
        if key not in state["config"]:
            raise KeyError(f"Unknown config key: {key!r}")
        state["config"][key] = value
    return state


def set_decision(state: dict[str, Any], key: str, value: Any) -> dict[str, Any]:
    """Record a decision (problem / sub-problem / solution). Returns updated state."""
    if key not in state["decisions"]:
        raise KeyError(f"Unknown decision key: {key!r}")
    state["decisions"][key] = value
    return state


def lock_panel(
    state: dict[str, Any], judge_shorts: list[str], manually_overridden: bool = False
) -> dict[str, Any]:
    """Lock a panel of judges for the current run."""
    state["panel"] = {
        "auto_selected": list(judge_shorts),
        "manually_overridden": manually_overridden,
        "locked": True,
    }
    return state


def mark_phase_in_progress(state: dict[str, Any], phase: int) -> dict[str, Any]:
    """Mark a phase as in_progress. Call before starting any phase work."""
    state["phases"][str(phase)] = {
        "status": "in_progress",
        "artefact": None,
        "started_at": _now_iso(),
        "completed_at": None,
    }
    return state


def rollback_phase(state: dict[str, Any], phase: int) -> dict[str, Any]:
    """Rollback a phase to pending. Use when a phase fails mid-execution."""
    state["phases"][str(phase)] = {
        "status": "pending",
        "artefact": None,
        "started_at": None,
        "completed_at": None,
    }
    return state


def elapsed_minutes(state: dict[str, Any]) -> float | None:
    """Return minutes elapsed since started_at, or None if not started."""
    started = state.get("started_at")
    if not started:
        return None
    started_dt = datetime.fromisoformat(started)
    return (datetime.now(timezone.utc) - started_dt).total_seconds() / 60.0


def expected_phases_remaining(state: dict[str, Any]) -> int:
    """Number of phases still pending (not completed)."""
    completed = sum(
        1 for p in range(9)
        if state.get("phases", {}).get(str(p), {}).get("status") == "completed"
    )
    return max(0, 9 - completed)
