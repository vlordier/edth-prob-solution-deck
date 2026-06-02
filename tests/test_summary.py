from __future__ import annotations

from pathlib import Path

from agent.summary import JudgeVerdict, Summary, write_summary


def test_write_summary(tmp_path: Path) -> None:
    s = Summary(
        pitch="MDO Dashboard.",
        top_risks=["Data freshness."],
        top_differentiators=["Edge-native AI."],
        verdicts=[JudgeVerdict("mehta", True, "Solid."), JudgeVerdict("viper", True, "Use this.")],
        next_steps=["Field-test"],
    )
    path = write_summary(tmp_path, s)
    raw = path.read_text()
    assert "MDO Dashboard" in raw
    assert "mehta" in raw
    assert "Field-test" in raw
