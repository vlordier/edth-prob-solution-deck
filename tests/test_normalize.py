"""Tests for agent.normalize."""

from __future__ import annotations

from agent.normalize import (
    QualityFlag,
    assign_quality_flags,
    dedupe_problems,
)


def _p(id: str, name: str, problem: str, source_hash: str = "") -> dict:
    return {
        "id": id,
        "name": name,
        "problem": problem,
        "source_row": 1,
        "source_hash": source_hash or f"hash-{id}",
    }


def test_empty_problem_gets_vague_flag() -> None:
    p = _p("P-001", "X", "Hi")
    assert QualityFlag.VAGUE in assign_quality_flags(p)


def test_short_problem_under_50_chars_gets_vague() -> None:
    p = _p("P-001", "Cheap radar", "Build a radar.")
    assert QualityFlag.VAGUE in assign_quality_flags(p)


def test_problem_mentioning_hardware_gets_flag() -> None:
    p = _p(
        "P-001",
        "Stealth Materials",
        "Develop stealth materials for UUVs that avoid detection by conventional underwater reconnaissance systems, including sonars and submarines.",
    )
    assert QualityFlag.REQUIRES_HARDWARE in assign_quality_flags(p)


def test_problem_mentioning_radar_gets_flag() -> None:
    p = _p("P-001", "Cheap radar", "Design short-range radar at high accuracy for drone detection.")
    assert QualityFlag.REQUIRES_HARDWARE in assign_quality_flags(p)


def test_problem_with_two_topics_gets_multi_problem() -> None:
    p = _p(
        "P-001",
        "Optical detection combining Optical and Acoustic",
        "Sensor fusion and Acoustic and Visual recognition.",
    )
    assert QualityFlag.MULTI_PROBLEM in assign_quality_flags(p)


def test_clean_software_problem_has_no_flags() -> None:
    p = _p(
        "P-001",
        "Autonomy 1",
        "AI Decision Support Systems. Challenge: Multi-Domain Battle Management Interface. Create an intuitive commander's dashboard. Process simulated feeds from air, land, and naval assets. Prioritize threats. Generate COA recommendations within 3 seconds.",
    )
    flags = assign_quality_flags(p)
    assert QualityFlag.VAGUE not in flags
    assert QualityFlag.REQUIRES_HARDWARE not in flags
    assert QualityFlag.MULTI_PROBLEM not in flags


def test_dedupe_keeps_first_by_source_row() -> None:
    a = _p("P-001", "Same", "same", source_hash="abc")
    b = _p("P-002", "Same", "same", source_hash="abc")
    c = _p("P-003", "Different", "diff", source_hash="xyz")
    result = dedupe_problems([a, b, c])
    assert len(result) == 2
    assert result[0]["id"] == "P-001"
    assert result[1]["id"] == "P-003"


def test_dedupe_returns_empty_for_empty_input() -> None:
    assert dedupe_problems([]) == []
