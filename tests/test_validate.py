"""Tests for agent.validate."""

from __future__ import annotations

import json
from pathlib import Path

from agent.validate import audit_deck_design, preflight_check, run_validation


def test_empty_dir_returns_issues(tmp_path: Path) -> None:
    artefacts = tmp_path / "artefacts"
    artefacts.mkdir()
    passes, _issues = run_validation(artefacts, quiet=True)
    assert not passes  # no state.json at all


def test_minimal_state_passes(tmp_path: Path) -> None:
    artefacts = tmp_path / "artefacts"
    artefacts.mkdir()
    state = {
        "version": "0.1.0",
        "current_phase": 0,
        "phases": {str(i): {"status": "pending"} for i in range(9)},
        "decisions": {
            "chosen_problem_id": None,
            "chosen_sub_problem_id": None,
            "chosen_solution_id": None,
        },
        "panel": {"auto_selected": [], "locked": False, "manually_overridden": False},
        "config": {},
    }
    (artefacts / "state.json").write_text(json.dumps(state))
    passes, _issues = run_validation(artefacts, quiet=True)
    assert passes


def test_phase_marked_complete_but_artefact_missing(tmp_path: Path) -> None:
    artefacts = tmp_path / "artefacts"
    artefacts.mkdir()
    state = {
        "version": "0.1.0",
        "current_phase": 2,
        "phases": {
            "0": {"status": "completed", "artefact": "artefacts/00_context.yaml"},
            "1": {"status": "completed", "artefact": "artefacts/01_triage.md"},
            "2": {"status": "pending"},
        },
        "decisions": {},
        "panel": {"auto_selected": [], "locked": False, "manually_overridden": False},
        "config": {},
    }
    for i in range(3, 9):
        state["phases"][str(i)] = {"status": "pending"}
    (artefacts / "state.json").write_text(json.dumps(state))
    passes, issues = run_validation(artefacts, quiet=True)
    assert not passes
    assert any("00_context.yaml" in i for i in issues)
    assert any("01_triage.md" in i for i in issues)


def test_validate_checks_triage_content(tmp_path: Path) -> None:
    artefacts = tmp_path / "artefacts"
    artefacts.mkdir()
    # valid state
    state = {
        "version": "0.1.0",
        "current_phase": 1,
        "phases": {"0": {"status": "completed", "artefact": str(artefacts / "00_context.yaml")}},
        "decisions": {},
        "panel": {"auto_selected": [], "locked": False},
        "config": {},
    }
    for i in range(1, 9):
        state["phases"][str(i)] = {"status": "pending"}
    (artefacts / "00_context.yaml").write_text("name: test\n")
    (artefacts / "state.json").write_text(json.dumps(state))
    # empty triage
    (artefacts / "01_triage.md").write_text("## Cluster 1\n\nNo scores.\n")
    passes, issues = run_validation(artefacts, quiet=True)
    assert not passes
    assert any("01_triage" in i or "triage" in i.lower() for i in issues)


def test_locked_panel_too_small(tmp_path: Path) -> None:
    artefacts = tmp_path / "artefacts"
    artefacts.mkdir()
    state = {
        "version": "0.1.0",
        "current_phase": 0,
        "phases": {str(i): {"status": "pending"} for i in range(9)},
        "decisions": {},
        "panel": {"auto_selected": ["mehta"], "locked": True},
        "config": {},
    }
    (artefacts / "state.json").write_text(json.dumps(state))
    passes, issues = run_validation(artefacts, quiet=True)
    assert not passes
    assert any("panel" in i.lower() for i in issues)


def test_validate_quiet_no_output_on_success(capsys, tmp_path: Path) -> None:
    artefacts = tmp_path / "artefacts"
    artefacts.mkdir()
    state = {
        "version": "0.1.0",
        "current_phase": 0,
        "phases": {str(i): {"status": "pending"} for i in range(9)},
        "decisions": {},
        "panel": {"auto_selected": [], "locked": False},
        "config": {},
    }
    (artefacts / "state.json").write_text(json.dumps(state))
    passes, _issues = run_validation(artefacts, quiet=True)
    assert passes
    captured = capsys.readouterr()
    assert captured.out == ""


def test_validate_loud_prints_on_success(capsys, tmp_path: Path) -> None:
    artefacts = tmp_path / "artefacts"
    artefacts.mkdir()
    state = {
        "version": "0.1.0",
        "current_phase": 0,
        "phases": {str(i): {"status": "pending"} for i in range(9)},
        "decisions": {},
        "panel": {"auto_selected": [], "locked": False},
        "config": {},
    }
    (artefacts / "state.json").write_text(json.dumps(state))
    passes, _issues = run_validation(artefacts, quiet=False)
    assert passes
    captured = capsys.readouterr()
    assert "✅" in captured.out


def test_preflight_check_no_deps_passes(tmp_path: Path) -> None:
    """Phase 1 has no dependencies — should always pass."""
    artefacts = tmp_path / "artefacts"
    artefacts.mkdir()
    ok, issues = preflight_check(artefacts, 1)
    assert ok
    assert not issues


def test_preflight_check_missing_dep_fails(tmp_path: Path) -> None:
    """Phase 3 depends on 02_candidate_problem.md — fail if missing."""
    artefacts = tmp_path / "artefacts"
    artefacts.mkdir()
    ok, issues = preflight_check(artefacts, 3)
    assert not ok
    assert any("02_candidate_problem" in i for i in issues)


def test_preflight_check_empty_dep_fails(tmp_path: Path) -> None:
    """Phase 3 depends on 02_candidate_problem.md — fail if empty."""
    artefacts = tmp_path / "artefacts"
    artefacts.mkdir()
    (artefacts / "02_candidate_problem.md").write_text("")
    ok, issues = preflight_check(artefacts, 3)
    assert not ok
    assert any("Empty" in i for i in issues)


def test_preflight_check_valid_dep_passes(tmp_path: Path) -> None:
    """Phase 3 — non-empty dep should pass."""
    artefacts = tmp_path / "artefacts"
    artefacts.mkdir()
    (artefacts / "02_candidate_problem.md").write_text("## Candidate 1\nScore: 4.5\n")
    ok, _issues = preflight_check(artefacts, 3)
    assert ok


def test_audit_deck_design_word_density(tmp_path: Path) -> None:
    """Slide with >40 content words gets flagged."""
    artefacts = tmp_path / "artefacts"
    artefacts.mkdir()
    deck = artefacts / "07_deck.md"
    deck.write_text(
        "---\nmarp: true\n---\n\n"
        + "This slide has way too many words it keeps going and going and nobody will read "
        "this because judges scan slides not read them this is terrible design fix it now "
        "forty three words is way past the limit we set of forty get it under control.\n"
    )
    issues: list[str] = []
    audit_deck_design(artefacts, issues)
    assert any("slide 2 has" in i and "words" in i for i in issues)


def test_audit_deck_design_clean_passes(tmp_path: Path) -> None:
    """Short slide with few words passes."""
    artefacts = tmp_path / "artefacts"
    artefacts.mkdir()
    deck = artefacts / "07_deck.md"
    deck.write_text("---\nmarp: true\n---\n\nHello world\n")
    issues: list[str] = []
    audit_deck_design(artefacts, issues)
    assert not issues


def test_audit_deck_design_no_file_skips(tmp_path: Path) -> None:
    """No deck.md exists — skips silently."""
    issues: list[str] = []
    audit_deck_design(tmp_path, issues)
    assert not issues
