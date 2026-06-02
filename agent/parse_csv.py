"""CSV parser for the EDTH agent.

Reads a CSV with columns "Name" and "Problem statement" and returns
a normalized list of problem dicts. Handles multi-line cells, UTF-8 BOM,
and skips rows with empty problem text.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path
from typing import TypedDict

REQUIRED_COLUMNS = {"Name", "Problem statement"}


class ParseError(ValueError):
    """Raised when the CSV is missing required columns."""


class Problem(TypedDict):
    id: str
    name: str
    problem: str
    source_row: int
    source_hash: str


def _short_hash(name: str, problem: str) -> str:
    h = hashlib.sha256()
    h.update(name.strip().encode("utf-8"))
    h.update(b"\x00")
    h.update(problem.strip().encode("utf-8"))
    return h.hexdigest()[:12]


def _make_id(index: int) -> str:
    return f"P-{index:03d}"


def parse_problems_from_string(csv_text: str) -> list[Problem]:
    """Parse CSV content from a string. See parse_problems for details."""
    import io

    text = csv_text
    if text.startswith("\ufeff"):
        text = text[1:]
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        return []
    if not REQUIRED_COLUMNS.issubset(set(reader.fieldnames)):
        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        raise ParseError(f"CSV is missing required columns: {sorted(missing)}")
    out: list[Problem] = []
    for row_index, row in enumerate(reader, start=2):
        name = (row.get("Name") or "").strip()
        problem = (row.get("Problem statement") or "").strip()
        if not problem:
            continue
        out.append(
            Problem(
                id=_make_id(len(out) + 1),
                name=name,
                problem=problem,
                source_row=row_index,
                source_hash=_short_hash(name, problem),
            )
        )
    return out


def parse_problems(csv_path: Path) -> list[Problem]:
    """Parse a CSV file at csv_path and return a list of Problem dicts."""
    text = csv_path.read_text(encoding="utf-8-sig")
    return parse_problems_from_string(text)
