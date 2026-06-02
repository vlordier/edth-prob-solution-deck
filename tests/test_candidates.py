from __future__ import annotations
from pathlib import Path
from agent.candidates import Candidate, write_candidate_problem

def test_write_candidate_creates_file(tmp_path: Path) -> None:
    candidates = [Candidate(problem_id="P-028", name="MDO Dashboard", scores={"impact":4.5,"innovation":3.5,"execution":4.0,"presentation":3.5}, panel_picks={"mehta":1,"viper":1}, reasoning="Top pick.")]
    path = write_candidate_problem(tmp_path, candidates)
    raw = path.read_text(); assert "P-028" in raw; assert "mehta" in raw

def test_weighted_score_uses_rubric(tmp_path: Path) -> None:
    candidates = [Candidate(problem_id="P-X", name="Test", scores={"impact":5,"innovation":5,"execution":5,"presentation":5})]
    write_candidate_problem(tmp_path, candidates)
    assert "5.00" in (tmp_path/"02_candidate_problem.md").read_text()
