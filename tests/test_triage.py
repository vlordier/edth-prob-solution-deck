"""Tests for agent.triage."""

from __future__ import annotations

from pathlib import Path

from agent.triage import Cluster, TriageReport, write_triage_report


def test_write_triage_creates_file(tmp_path: Path) -> None:
    report = TriageReport(
        clusters=[
            Cluster("Counter-UAV", ["c-uas"], ["P-001", "P-002"],
                    {"impact": 4.5, "innovation": 3.5, "execution": 4.0, "presentation": 3.5},
                    "Active commercial space."),
            Cluster("EW", ["ew"], ["P-003", "P-004"],
                    {"impact": 4.0, "innovation": 4.5, "execution": 3.0, "presentation": 3.5},
                    "Crowded defense primes."),
        ],
        panel_summary="Both judges ranked Counter-UAV top-3.",
    )
    path = write_triage_report(tmp_path, report)
    assert path == tmp_path / "01_triage.md"
    raw = path.read_text(encoding="utf-8")
    assert "# Triage Report" in raw
    assert "Counter-UAV" in raw
    assert "Anduril" not in raw


def test_triage_report_includes_weighted_score(tmp_path: Path) -> None:
    report = TriageReport(
        clusters=[Cluster("Test", [], ["P-1"],
                 {"impact": 5, "innovation": 5, "execution": 5, "presentation": 5}, "")]
    )
    write_triage_report(tmp_path, report)
    raw = (tmp_path / "01_triage.md").read_text(encoding="utf-8")
    assert "5.00" in raw
