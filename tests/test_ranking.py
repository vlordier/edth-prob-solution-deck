from __future__ import annotations
from pathlib import Path
from agent.ranking import RankedSolution, write_owner_pick, write_ranked_solutions

def test_write_ranked_solutions(tmp_path: Path) -> None:
    sols = [RankedSolution(idea_id="I-1", text="A solution", research="No prior art.", aggregate_score=4.2, panel_scores={"mehta":4.5,"viper":4.0}, spread=0.5)]
    path = write_ranked_solutions(tmp_path, sols)
    raw = path.read_text(); assert "I-1" in raw; assert "4.20" in raw; assert "0.50" in raw

def test_write_owner_pick(tmp_path: Path) -> None:
    write_owner_pick(tmp_path, "I-1", "Top choice.", [("mehta","Prefer I-3.")])
    raw = (tmp_path/"05_owner_pick.md").read_text()
    assert "I-1" in raw; assert "mehta" in raw
