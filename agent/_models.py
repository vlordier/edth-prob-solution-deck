"""Domain TypedDicts shared across agent modules.

Replaces bare `dict` in function signatures with typed structures.
"""

from __future__ import annotations

from typing import TypedDict


class Problem(TypedDict, total=False):
    id: str
    name: str
    problem: str
    source_row: int
    source_hash: str
    quality_flags: list[str]


class DeckContext(TypedDict, total=False):
    hackathon_name: str
    project_name: str
    team_name: str
    date: str


DECK_CONTEXT_DEFAULTS: DeckContext = {
    "hackathon_name": "EDTH Munich 2025",
    "project_name": "Project X",
    "team_name": "Team",
    "date": "",
}
