from __future__ import annotations
from pathlib import Path
from agent.ideation import Idea, dedupe_ideas, jaccard_similarity, write_solution_candidates

def test_jaccard_identical() -> None:
    assert jaccard_similarity("a b c", "a b c") == 1.0

def test_jaccard_disjoint() -> None:
    assert jaccard_similarity("alpha", "beta") == 0.0

def test_jaccard_partial() -> None:
    assert jaccard_similarity("alpha beta gamma", "alpha beta delta") == 0.5

def test_dedupe_keeps_first(tmp_path: Path) -> None:
    ideas = [Idea(id="I1", text="radar detection"), Idea(id="I2", text="radar detection with ML"), Idea(id="I3", text="swarm coordination")]
    result = dedupe_ideas(ideas, threshold=0.5)
    assert len(result) == 2; assert result[0].id == "I1"

def test_write_candidates(tmp_path: Path) -> None:
    ideas = [Idea(id="I1", text="Good idea", rating=5.0), Idea(id="I2", text="OK idea", rating=3.0)]
    write_solution_candidates(tmp_path, ideas)
    raw = (tmp_path/"04_solution_candidates.md").read_text()
    assert "I1" in raw; assert "5.00" in raw
