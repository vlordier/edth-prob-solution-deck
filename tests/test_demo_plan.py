from __future__ import annotations

from pathlib import Path

from agent.demo_plan import DemoPlan, Risk, write_demo_plan


def test_write_demo_plan(tmp_path: Path) -> None:
    plan = DemoPlan(
        thin_demo="A dashboard.",
        script=[(0, "Cold open"), (120, "Demo")],
        pitch="See the war in 3 seconds.",
        qa_prep=[("Q:Is this AI?", "A:Yes, for COA.")],
        risks=[
            Risk(what="Demo crashes", likelihood="medium", impact="high", mitigation="Pre-record")
        ],
    )
    path = write_demo_plan(tmp_path, plan)
    raw = path.read_text()
    assert "Cold open" in raw
    assert "0:00" in raw
    assert "2:00" in raw
    assert "Demo crashes" in raw
