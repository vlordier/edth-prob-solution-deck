"""State management for the EDTH agent.

Loads and saves the state.json file that tracks the agent's progress
through the 9-phase workflow. See spec §8.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from agent._constants import ARTEFACTS, PHASE_COUNT

log = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def empty_state() -> dict[str, Any]:
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
            for i in range(PHASE_COUNT)
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
    state_path = artefacts_dir / ARTEFACTS.STATE
    if not state_path.exists():
        return {}
    mtime = state_path.stat().st_mtime
    try:
        with state_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        log.warning(
            "state.json is corrupted (%s). Backup saved to state.json.corrupt. "
            "Consider /edth-agent reset.",
            e,
        )
        corrupt_path = artefacts_dir / "state.json.corrupt"
        try:
            state_path.rename(corrupt_path)
            log.warning("Moved corrupt state.json to %s", corrupt_path)
        except OSError as exc:
            log.warning("Could not create corruption backup: %s", exc)
        return {}
    except OSError as e:
        log.warning("Could not read state.json: %s", e)
        return {}

    if state_path.stat().st_mtime != mtime:
        log.warning(
            "state.json was modified during load — another process may be writing. "
            "Avoid running two agents on the same repo simultaneously."
        )
    return data


def save_state(artefacts_dir: Path, state: dict[str, Any]) -> Path:
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = _now_iso()
    if state.get("started_at") is None:
        state["started_at"] = state["updated_at"]
    state_path = artefacts_dir / ARTEFACTS.STATE
    tmp_path = artefacts_dir / "state.json.tmp"
    try:
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, sort_keys=True)
        tmp_path.rename(state_path)
    except OSError:
        with state_path.open("w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, sort_keys=True)
    return state_path


def get_phase_status(state: dict[str, Any], phase: int) -> str:
    if not state:
        return "pending"
    return state["phases"][str(phase)]["status"]


def mark_phase_completed(state: dict[str, Any], phase: int, artefact_path: Path) -> dict[str, Any]:
    state["phases"][str(phase)] = {
        "status": "completed",
        "artefact": str(artefact_path),
        "completed_at": _now_iso(),
    }
    state["current_phase"] = max(state.get("current_phase", 0), phase + 1)
    return state


def set_config(state: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    for key, value in kwargs.items():
        if key not in state["config"]:
            raise KeyError(f"Unknown config key: {key!r}")
        state["config"][key] = value
    return state


def set_decision(state: dict[str, Any], key: str, value: Any) -> dict[str, Any]:
    if key not in state["decisions"]:
        raise KeyError(f"Unknown decision key: {key!r}")
    state["decisions"][key] = value
    return state


def lock_panel(
    state: dict[str, Any], judge_shorts: list[str], manually_overridden: bool = False
) -> dict[str, Any]:
    state["panel"] = {
        "auto_selected": list(judge_shorts),
        "manually_overridden": manually_overridden,
        "locked": True,
    }
    return state


def mark_phase_in_progress(state: dict[str, Any], phase: int) -> dict[str, Any]:
    state["phases"][str(phase)] = {
        "status": "in_progress",
        "artefact": None,
        "started_at": _now_iso(),
        "completed_at": None,
    }
    return state


def rollback_phase(state: dict[str, Any], phase: int) -> dict[str, Any]:
    state["phases"][str(phase)] = {
        "status": "pending",
        "artefact": None,
        "started_at": None,
        "completed_at": None,
    }
    return state


def elapsed_minutes(state: dict[str, Any]) -> float | None:
    started = state.get("started_at")
    if not started:
        return None
    started_dt = datetime.fromisoformat(started)
    return (datetime.now(UTC) - started_dt).total_seconds() / 60.0


def expected_phases_remaining(state: dict[str, Any]) -> int:
    completed = sum(
        1
        for p in range(PHASE_COUNT)
        if state.get("phases", {}).get(str(p), {}).get("status") == "completed"
    )
    return max(0, PHASE_COUNT - completed)
