from __future__ import annotations
from agent.aggregation import approval_vote, borda_count, weighted_borda

def test_borda_basic() -> None:
    rankings = [{"a":1,"b":2,"c":3},{"a":2,"b":1,"c":3},{"a":1,"b":3,"c":2}]
    assert borda_count(rankings) == ["a","b","c"]

def test_borda_empty() -> None:
    assert borda_count([]) == []

def test_borda_missing_items() -> None:
    rankings = [{"a":1,"b":2},{"a":2,"b":1,"c":3}]
    result = borda_count(rankings)
    assert result[2] == "c"

def test_weighted_borda() -> None:
    rankings = [{"a":1,"b":2},{"a":2,"b":1}]
    result = weighted_borda(rankings, weights=[1.0, 3.0])
    assert result == ["b","a"]

def test_approval_vote() -> None:
    approvals = [{"a","b","c"},{"a","d"},{"b","c"}]
    result = approval_vote(approvals)
    assert result[-1] == "d"
