"""Tests for agent._util — shared utility functions."""

from __future__ import annotations

from pathlib import Path

from agent._util import (
    jaccard_similarity,
    load_json_safe,
    now_iso,
    slurp_file,
    tokens,
    write_artefact,
)


def test_now_iso_returns_iso_string() -> None:
    ts = now_iso()
    assert isinstance(ts, str)
    assert "T" in ts
    assert ts.endswith(("+00:00", "Z")) or ts[-1:].isdigit()


def test_write_artefact_creates_file(tmp_path: Path) -> None:
    path = write_artefact(tmp_path, "test.md", ["# Hello", "", "world"])
    assert path == tmp_path / "test.md"
    content = path.read_text()
    assert "# Hello" in content
    assert "world" in content


def test_write_artefact_creates_parent_dirs(tmp_path: Path) -> None:
    deep = tmp_path / "deep" / "nested"
    path = write_artefact(deep, "out.md", ["line 1", "line 2"])
    assert path.exists()
    assert path.read_text() == "line 1\nline 2"


def test_load_json_safe_loads_valid_json(tmp_path: Path) -> None:
    path = tmp_path / "data.json"
    path.write_text('{"key": "value"}')
    assert load_json_safe(path) == {"key": "value"}


def test_load_json_safe_returns_empty_on_missing(tmp_path: Path) -> None:
    assert load_json_safe(tmp_path / "nonexistent.json") == {}


def test_load_json_safe_returns_empty_on_corrupt(tmp_path: Path) -> None:
    path = tmp_path / "corrupt.json"
    path.write_text("{not valid json")
    assert load_json_safe(path) == {}


def test_slurp_file_reads_content(tmp_path: Path) -> None:
    (tmp_path / "data.md").write_text("content", encoding="utf-8")
    assert slurp_file(tmp_path, "data.md") == "content"


def test_slurp_file_returns_empty_on_missing(tmp_path: Path) -> None:
    assert slurp_file(tmp_path, "missing.md") == ""


def test_tokens_extracts_words() -> None:
    assert tokens("hello world this") == {"hello", "world", "this"}
    assert tokens("ab cd ef") == set()  # min_length=3 filters short words
    assert tokens("") == set()


def test_jaccard_identical() -> None:
    assert jaccard_similarity("hello world", "hello world") == 1.0


def test_jaccard_disjoint() -> None:
    assert jaccard_similarity("alpha beta", "gamma delta") == 0.0


def test_jaccard_partial() -> None:
    s = jaccard_similarity("alpha beta gamma", "alpha beta delta")
    assert 0.4 < s < 0.7


def test_jaccard_empty_both() -> None:
    assert jaccard_similarity("", "") == 1.0


def test_jaccard_one_empty() -> None:
    assert jaccard_similarity("hello world", "") == 0.0
    assert jaccard_similarity("", "hello world") == 0.0


def test_jaccard_with_sets() -> None:
    assert jaccard_similarity({"alpha", "beta"}, {"beta", "gamma"}) == 1 / 3
