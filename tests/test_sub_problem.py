from __future__ import annotations
from pathlib import Path

import pytest

from agent.sub_problem import SubProblem, write_sub_problem


def test_compute_roi_score() -> None:
    sp = SubProblem(id="SP-1", title="Test", scores={"impact":5,"time_fit":4,"demo_ability":3,"dependency_risk":2})
    assert sp.roi_score() == pytest.approx(3.9)

def test_write_sub_problem(tmp_path: Path) -> None:
    subs = [SubProblem(id="SP-1", title="A", scores={"impact":5,"time_fit":4,"demo_ability":3,"dependency_risk":2})]
    path = write_sub_problem(tmp_path, subs)
    assert "SP-1" in path.read_text(); assert "A" in path.read_text()
