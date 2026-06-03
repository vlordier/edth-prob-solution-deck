"""Phase 5 — Research + ranking writers."""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from pathlib import Path

from agent._constants import ARTEFACTS
from agent._util import write_artefact

log = logging.getLogger(__name__)


@dataclass
class RankedSolution:
    """A solution ranked after three-salvo research with aggregate + panel scores."""

    idea_id: str
    text: str
    research: str
    aggregate_score: float
    panel_scores: dict[str, float] = field(default_factory=dict)
    spread: float = 0.0

    def __post_init__(self) -> None:
        self.aggregate_score = _safe_score(self.aggregate_score)


def _safe_score(score: float) -> float:
    """Coerce NaN/inf to 0.0 so sorting is stable."""
    if math.isnan(score) or math.isinf(score):
        return 0.0
    return score


def write_ranked_solutions(artefacts_dir: Path, solutions: list[RankedSolution]) -> Path:
    """Write `05_ranked_solutions.md` — Phase 5 post-research ranking."""
    for s in solutions:
        s.aggregate_score = _safe_score(s.aggregate_score)
    sorted_sols = sorted(solutions, key=lambda s: -s.aggregate_score)
    lines = ["# Ranked Solutions (post-research)", ""]
    for i, s in enumerate(sorted_sols, start=1):
        lines.append(f"## Rank {i}: {s.idea_id}")
        lines.append("")
        lines.append(s.text)
        lines.append("")
        lines.append(f"**Aggregate score: {s.aggregate_score:.2f}**")
        lines.append(f"**Spread: {s.spread:.2f}**")
        lines.append("")
        if s.panel_scores:
            lines.append("**Panel scores:**")
            for judge, score in sorted(s.panel_scores.items()):
                lines.append(f"- {judge}: {score:.2f}")
            lines.append("")
        if s.research:
            lines.append("**Research:**")
            lines.append(s.research)
            lines.append("")
    return write_artefact(artefacts_dir, ARTEFACTS.RANKED_SOLUTIONS, lines)


def write_owner_pick(
    artefacts_dir: Path,
    chosen_idea_id: str,
    validation_notes: str,
    dissents: list[tuple[str, str]] | None = None,
) -> Path:
    """Write `05_owner_pick.md` — Phase 5 owner's validated solution choice."""
    dissents = dissents or []
    lines = [
        "# Owner Pick (validated)",
        "",
        f"**Chosen: {chosen_idea_id}**",
        "",
        "## Validation notes",
        "",
        validation_notes,
        "",
    ]
    if dissents:
        lines.append("## Dissents")
        lines.append("")
        for entry in dissents:
            if len(entry) != 2:
                log.warning("Skipping malformed dissent entry: %r", entry)
                continue
            judge, reason = entry
            lines.append(f"- **{judge}**: {reason}")
        lines.append("")
    return write_artefact(artefacts_dir, ARTEFACTS.OWNER_PICK, lines)
