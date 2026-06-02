"""Tests for agent.parse_csv — TDD."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent.parse_csv import (
    EmptyCsvError,
    ParseError,
    parse_problems,
    parse_problems_from_string,
    parse_problems_safe,
)


def test_empty_csv_raises(tmp_path: Path) -> None:
    csv_path = tmp_path / "in.csv"
    csv_path.write_text("Name,Problem statement\n", encoding="utf-8")
    with pytest.raises(EmptyCsvError):
        parse_problems(csv_path)


def test_parse_from_string_helper_matches_file(tmp_path: Path) -> None:
    csv_text = "Name,Problem statement\nTest,This is a problem statement\n"
    from_file = parse_problems_from_string(csv_text)
    csv_path = tmp_path / "in.csv"
    csv_path.write_text(csv_text, encoding="utf-8")
    from_path = parse_problems(csv_path)
    assert from_file[0]["id"] == from_path[0]["id"]
    assert from_file[0]["source_hash"] == from_path[0]["source_hash"]


def test_skips_rows_with_empty_problem(tmp_path: Path) -> None:
    csv_path = tmp_path / "in.csv"
    csv_path.write_text("Name,Problem statement\nA,\nB,has a problem\n", encoding="utf-8")
    problems = parse_problems(csv_path)
    assert len(problems) == 1
    assert problems[0]["name"] == "B"


def test_real_input_csv_parses(tmp_path: Path) -> None:
    """Smoke test: parse a real input CSV (sample-problems or the EDTH original)."""
    repo_root = Path(__file__).resolve().parent.parent
    csv_path = repo_root / "input" / "PB-SOL-EDTH - Sheet1.csv"
    if not csv_path.exists():
        csv_path = repo_root / "input" / "sample-problems.csv"
    if not csv_path.exists():
        pytest.skip(f"No input CSV found at {csv_path}")
    problems = parse_problems(csv_path)
    assert len(problems) >= 4


def test_fuzzy_column_suggestion(tmp_path: Path) -> None:
    csv_path = tmp_path / "in.csv"
    csv_path.write_text("name,problem description\nFoo,bar\n", encoding="utf-8")
    with pytest.raises(ParseError, match="Name"):
        parse_problems(csv_path)


def test_parse_safe_returns_error_on_bad_csv(tmp_path: Path) -> None:
    csv_path = tmp_path / "in.csv"
    csv_path.write_text("Name,Problem statement\n", encoding="utf-8")
    result, error = parse_problems_safe(csv_path)
    assert result is None
    assert error is not None


def test_parse_safe_returns_problems_on_good_csv(tmp_path: Path) -> None:
    csv_path = tmp_path / "in.csv"
    csv_path.write_text("Name,Problem statement\nA,B\n", encoding="utf-8")
    result, error = parse_problems_safe(csv_path)
    assert result is not None
    assert error is None
    assert len(result) == 1


def test_missing_file_returns_error(tmp_path: Path) -> None:
    csv_path = tmp_path / "does_not_exist.csv"
    result, error = parse_problems_safe(csv_path)
    assert result is None
    assert error is not None


def test_parses_simple_two_column_csv(tmp_path: Path) -> None:
    csv_path = tmp_path / "in.csv"
    csv_path.write_text(
        "Name,Problem statement\n"
        "Capture drones,Minimize participation\n"
        "Auto Shaheds,Minimize participation\n",
        encoding="utf-8",
    )
    problems = parse_problems(csv_path)
    assert len(problems) == 2
    assert problems[0]["name"] == "Capture drones"
    assert problems[0]["id"] == "P-001"
    assert problems[0]["source_row"] == 2
    assert problems[1]["id"] == "P-002"


def test_id_format_is_padded_three_digits(tmp_path: Path) -> None:
    csv_path = tmp_path / "in.csv"
    csv_path.write_text("Name,Problem statement\nA,A\nB,B\nC,C\n", encoding="utf-8")
    problems = parse_problems(csv_path)
    assert [p["id"] for p in problems] == ["P-001", "P-002", "P-003"]


def test_source_hash_is_stable_across_runs(tmp_path: Path) -> None:
    csv_path = tmp_path / "in.csv"
    csv_path.write_text("Name,Problem statement\nFoo,bar baz\n", encoding="utf-8")
    a = parse_problems(csv_path)
    b = parse_problems(csv_path)
    assert a[0]["source_hash"] == b[0]["source_hash"]
    assert len(a[0]["source_hash"]) == 12


def test_handles_multiline_cells_with_quotes(tmp_path: Path) -> None:
    csv_path = tmp_path / "in.csv"
    csv_path.write_text(
        'Name,Problem statement\nAutonomy 1,"AI Decision Support\n\nMulti-Domain"\n',
        encoding="utf-8",
    )
    problems = parse_problems(csv_path)
    assert len(problems) == 1
    assert "Multi-Domain" in problems[0]["problem"]


def test_handles_utf8_bom(tmp_path: Path) -> None:
    csv_path = tmp_path / "in.csv"
    csv_path.write_bytes("\ufeffName,Problem statement\nFoo,bar\n".encode())
    problems = parse_problems(csv_path)
    assert problems[0]["name"] == "Foo"


def test_missing_required_columns_raises(tmp_path: Path) -> None:
    csv_path = tmp_path / "in.csv"
    csv_path.write_text("Foo,bar\n1,2\n", encoding="utf-8")
    with pytest.raises(ParseError, match="Name"):
        parse_problems(csv_path)
