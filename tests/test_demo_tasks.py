"""Tests for agent.demo_tasks."""

from __future__ import annotations

from pathlib import Path

from agent.demo_tasks import DemoTask, DemoTaskPlan, write_demo_tasks


def test_write_demo_tasks_creates_file(tmp_path: Path) -> None:
    plan = DemoTaskPlan(
        tasks=[
            DemoTask(
                id="T1",
                title="Build the real-time feed ingestion pipeline",
                description="Stream simulated multi-domain feeds into the dashboard backend.",
                estimated_hours="8h",
                assigned_to="Bob",
                fit_reasoning="Bob's data science background and PyTorch experience make him the best fit for the ingestion layer.",
            ),
            DemoTask(
                id="T2",
                title="Create the operator-facing dashboard UI",
                description="React dashboard with threat cards, timeline, and 3-second refresh.",
                estimated_hours="10h",
                assigned_to="Alice",
                fit_reasoning="Alice's frontend expertise (React, D3) maps directly to this.",
            ),
            DemoTask(
                id="T3",
                title="Deploy edge inference model",
                description="Export the trained model to ONNX and package for edge deployment.",
                estimated_hours="6h",
                assigned_to="UNASSIGNED",
                fit_reasoning="Bob has edge experience but is already fully loaded on T1. Nobody else has ML ops.",
                gap_flag=True,
            ),
        ],
        total_estimated_hours="24h",
        critical_gaps=["Edge deployment / ML Ops — nobody with production deployment experience"],
        suggested_ordering=["T1", "T2", "T3"],
        notes="Bob and Alice should pair on T3 if time allows. Consider cutting T3 scope to 'API demo' if behind schedule.",
    )
    path = write_demo_tasks(tmp_path, plan)
    raw = path.read_text(encoding="utf-8")

    assert "T1" in raw
    assert "Build the real-time" in raw
    assert "Bob" in raw
    assert "Alice" in raw
    assert "UNASSIGNED" in raw
    assert "GAP" in raw
    assert "Critical Skill Gaps" in raw
    assert "Suggested Build Order" in raw
    assert "24h" in raw
    assert "8h" in raw


def test_demo_tasks_no_gaps(tmp_path: Path) -> None:
    plan = DemoTaskPlan(
        tasks=[
            DemoTask(
                id="T1",
                title="Everything",
                description="One person does it all.",
                estimated_hours="20h",
                assigned_to="Solo",
                fit_reasoning="Only person on the team.",
            ),
        ],
        total_estimated_hours="20h",
        critical_gaps=[],
        suggested_ordering=["T1"],
    )
    path = write_demo_tasks(tmp_path, plan)
    raw = path.read_text(encoding="utf-8")
    assert "Critical Skill Gaps" not in raw  # section omitted when empty
