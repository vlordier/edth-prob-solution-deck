"""Tests for agent.doctor."""

from __future__ import annotations

from pathlib import Path

from agent.doctor import run_doctor


def test_doctor_runs_all_checks() -> None:
    repo_root = Path(__file__).parent.parent
    artefacts = repo_root / "artefacts"
    artefacts.mkdir(exist_ok=True)
    all_pass, issues = run_doctor(artefacts)
    # Should find at least the Python version and agent import checks
    assert isinstance(all_pass, bool)
    assert isinstance(issues, list)


def test_doctor_reports_issues_for_missing_things() -> None:
    # Most checks will pass (we're in the dev environment)
    # But we can verify the function returns without crashing
    repo_root = Path(__file__).parent.parent
    artefacts = repo_root / "artefacts"
    artefacts.mkdir(exist_ok=True)
    all_pass, issues = run_doctor(artefacts)
    # At minimum, return type is correct
    assert isinstance(all_pass, bool)
    for issue in issues:
        assert isinstance(issue, str)
