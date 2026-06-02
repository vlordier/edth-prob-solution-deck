"""CSV parser for the EDTH agent.

Reads a CSV with columns "Name" and "Problem statement" and returns
a normalized list of problem dicts. Handles multi-line cells, UTF-8 BOM,
skips rows with empty problem text, and warns on large inputs.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path
from typing import TypedDict

REQUIRED_COLUMNS = {"Name", "Problem statement"}
MAX_PROBLEMS = 1000
WARN_PROBLEMS = 500

COLUMN_SUGGESTIONS = {
    "name": "Name",
    "problem": "Problem statement",
    "title": "Name",
    "description": "Problem statement",
    "challenge": "Problem statement",
    "issue": "Problem statement",
    "problem_description": "Problem statement",
    "problem_name": "Name",
    "topic": "Name",
    "statement": "Problem statement",
}


class ParseError(ValueError):
    """Raised when the CSV is missing required columns."""


class EmptyCsvError(ParseError):
    """Raised when the CSV has no data rows."""


class TooManyProblemsError(ParseError):
    """Raised when the CSV has more than MAX_PROBLEMS rows."""


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


def _suggest_columns(fieldnames: list[str]) -> str:
    """If the CSV has similar but wrong column names, suggest fixes."""
    hints = []
    for fn in fieldnames:
        key = fn.strip().lower().replace(" ", "_")
        if key in COLUMN_SUGGESTIONS:
            hints.append(f'  Found "{fn}" — did you mean "{COLUMN_SUGGESTIONS[key]}"?')
    return "\n".join(hints) if hints else ""


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
        suggestions = _suggest_columns(list(reader.fieldnames))
        msg = f"CSV is missing required columns: {sorted(missing)}"
        if suggestions:
            msg += f"\n{suggestions}"
        raise ParseError(msg)
    out: list[Problem] = []
    for row_index, row in enumerate(reader, start=2):
        name = (row.get("Name") or "").strip()
        problem = (row.get("Problem statement") or "").strip()
        if not problem:
            continue
        if len(out) >= MAX_PROBLEMS:
            raise TooManyProblemsError(
                f"CSV has more than {MAX_PROBLEMS} problem rows. Please reduce the input size."
            )
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
    """Parse a CSV file at csv_path.

    Returns the problem list. Raises EmptyCsvError if no data rows.
    Warns (via print) if the row count exceeds WARN_PROBLEMS.
    Raises TooManyProblemsError if row count exceeds MAX_PROBLEMS.
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    text = csv_path.read_text(encoding="utf-8-sig")
    problems = parse_problems_from_string(text)

    if not problems:
        raise EmptyCsvError(
            f"No valid problem rows found in {csv_path}. "
            f"Check that the CSV has a header row with "
            f"'{sorted(REQUIRED_COLUMNS)}' and at least one data row."
        )

    if len(problems) > WARN_PROBLEMS:
        print(
            f"⚠️  Warning: {len(problems)} problems parsed. "
            f"Consider reducing the CSV to improve clustering quality."
        )

    return problems


def parse_problems_safe(csv_path: Path) -> tuple[list[Problem] | None, str | None]:
    """Parse problems, returning (problems, None) on success or (None, message) on failure."""
    try:
        return parse_problems(csv_path), None
    except ParseError as e:
        return None, str(e)
    except FileNotFoundError as e:
        return None, str(e)
    except Exception as e:
        return None, f"Unexpected error parsing CSV: {e}"
