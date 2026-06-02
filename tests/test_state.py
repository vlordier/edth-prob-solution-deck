"""Tests for agent.state."""

from __future__ import annotations

from pathlib import Path

from agent.state import (
    empty_state,
    get_phase_status,
    load_state,
    lock_panel,
    mark_phase_completed,
    save_state,
    set_config,
    set_decision,
)


def test_empty_state_has_correct_version() -> None:
    state = empty_state()
    assert state["version"] == "0.1.0"


def test_empty_state_has_nine_pending_phases() -> None:
    state = empty_state()
    assert len(state["phases"]) == 9
    for i in range(9):
        assert state["phases"][str(i)]["status"] == "pending"


def test_save_and_load_roundtrip(tmp_artefacts_dir: Path) -> None:
    state = empty_state()
    state["current_phase"] = 3
    path = save_state(tmp_artefacts_dir, state)
    assert path == tmp_artefacts_dir / "state.json"
    loaded = load_state(tmp_artefacts_dir)
    assert loaded["current_phase"] == 3


def test_load_missing_returns_empty_dict(tmp_artefacts_dir: Path) -> None:
    assert load_state(tmp_artefacts_dir) == {}


def test_get_phase_status_returns_status_field(tmp_artefacts_dir: Path) -> None:
    state = empty_state()
    state["phases"]["1"]["status"] = "completed"
    save_state(tmp_artefacts_dir, state)
    assert get_phase_status(load_state(tmp_artefacts_dir), 1) == "completed"
    assert get_phase_status(load_state(tmp_artefacts_dir), 0) == "pending"


def test_mark_phase_completed_writes_artefact_and_timestamp(
    tmp_artefacts_dir: Path,
) -> None:
    state = empty_state()
    artefact = tmp_artefacts_dir / "01_triage.md"
    artefact.write_text("# Triage\n", encoding="utf-8")
    updated = mark_phase_completed(state, 1, artefact)
    assert updated["phases"]["1"]["status"] == "completed"
    assert updated["phases"]["1"]["artefact"] == str(artefact)
    assert updated["phases"]["1"]["completed_at"] is not None
    assert updated["current_phase"] == 2


def test_set_config_updates_field() -> None:
    state = empty_state()
    updated = set_config(state, owner_mode="sim", persona="alt-judge")
    assert updated["config"]["owner_mode"] == "sim"
    assert updated["config"]["persona"] == "alt-judge"
    assert updated["config"]["panel_mode"] == "expanded"


def test_set_decision_records_choice() -> None:
    state = empty_state()
    updated = set_decision(state, "chosen_problem_id", "P-028")
    assert updated["decisions"]["chosen_problem_id"] == "P-028"


def test_save_creates_artefacts_dir_if_missing(tmp_path: Path) -> None:
    artefacts = tmp_path / "does" / "not" / "exist"
    save_state(artefacts, empty_state())
    assert (artefacts / "state.json").exists()


def test_state_json_is_sorted_for_diffability(tmp_artefacts_dir: Path) -> None:
    state = empty_state()
    state["config"]["persona"] = "z"
    state["config"]["owner_mode"] = "a"
    save_state(tmp_artefacts_dir, state)
    raw = (tmp_artefacts_dir / "state.json").read_text()
    assert raw.index('"owner_mode"') < raw.index('"persona"')


def test_lock_panel_records_judges() -> None:
    state = empty_state()
    out = lock_panel(state, ["mehta", "viper"], manually_overridden=True)
    assert out["panel"]["auto_selected"] == ["mehta", "viper"]
    assert out["panel"]["locked"] is True
    assert out["panel"]["manually_overridden"] is True


def test_set_config_unknown_key_raises_key_error() -> None:
    state = empty_state()
    import pytest
    with pytest.raises(KeyError, match="nope"):
        set_config(state, nope="value")


def test_set_decision_unknown_key_raises_key_error() -> None:
    state = empty_state()
    import pytest
    with pytest.raises(KeyError, match="nope"):
        set_decision(state, "nope", "value")


def test_mark_phase_completed_guards_against_phase_9() -> None:
    state = empty_state()
    updated = mark_phase_completed(state, 8, Path("unused.md"))
    assert updated["current_phase"] == 9
    assert updated["phases"]["8"]["status"] == "completed"


def test_mark_phase_in_progress() -> None:
    from agent.state import mark_phase_in_progress
    state = empty_state()
    out = mark_phase_in_progress(state, 3)
    assert out["phases"]["3"]["status"] == "in_progress"
    assert out["phases"]["3"]["started_at"] is not None


def test_rollback_phase() -> None:
    from agent.state import mark_phase_in_progress, rollback_phase
    state = empty_state()
    mark_phase_in_progress(state, 3)
    out = rollback_phase(state, 3)
    assert out["phases"]["3"]["status"] == "pending"


def test_expected_phases_remaining() -> None:
    from agent.state import expected_phases_remaining
    state = empty_state()
    assert expected_phases_remaining(state) == 9
    state["phases"]["0"]["status"] = "completed"
    state["phases"]["1"]["status"] = "completed"
    assert expected_phases_remaining(state) == 7
