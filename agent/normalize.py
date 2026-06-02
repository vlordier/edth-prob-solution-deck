"""Heuristic normalization for parsed problems."""

from __future__ import annotations

from enum import Enum
from typing import TypedDict


class QualityFlag(str, Enum):
    VAGUE = "vague"
    MULTI_PROBLEM = "multi_problem"
    REQUIRES_HARDWARE = "requires_hardware"
    OUT_OF_SCOPE_FOR_48H = "out_of_scope_for_48h"


_HARDWARE_KEYWORDS = (
    "hull", "radar", "antenna", "stealth material", "energy harvesting",
    "propulsion", "3d print", "manufacturing", "physical hardware",
    "mechanical", "towed antenna", "towed",
)

_VAGUE_LENGTH = 50

_MULTI_PROBLEM_KEYWORDS = ("combining", "and", "blend", "multiple", "two")


class ProblemWithFlags(TypedDict, total=False):
    id: str
    name: str
    problem: str
    source_row: int
    source_hash: str
    quality_flags: list[str]


def assign_quality_flags(problem: dict) -> list[QualityFlag]:
    """Inspect a problem dict and return a list of quality flags."""
    flags: list[QualityFlag] = []
    text = f"{problem.get('name', '')} {problem.get('problem', '')}".lower()
    if len(problem.get("problem", "").strip()) < _VAGUE_LENGTH:
        flags.append(QualityFlag.VAGUE)
    for kw in _HARDWARE_KEYWORDS:
        if kw in text:
            flags.append(QualityFlag.REQUIRES_HARDWARE)
            break
    if _is_multi_problem(text):
        flags.append(QualityFlag.MULTI_PROBLEM)
    return flags


def _is_multi_problem(text: str) -> bool:
    matches = sum(1 for kw in _MULTI_PROBLEM_KEYWORDS if kw in text)
    return matches >= 2


def dedupe_problems(problems: list[dict]) -> list[dict]:
    """Remove duplicates by source_hash, keeping the first occurrence."""
    seen: set[str] = set()
    out: list[dict] = []
    sorted_problems = sorted(problems, key=lambda p: p.get("source_row", 0))
    for p in sorted_problems:
        h = p.get("source_hash", "")
        if h in seen:
            continue
        seen.add(h)
        out.append(p)
    return out
