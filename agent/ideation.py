"""Phase 4 — Divergent ideation helpers."""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from pathlib import Path

from agent._constants import ARTEFACTS
from agent._util import jaccard_similarity, write_artefact

log = logging.getLogger(__name__)


@dataclass
class Idea:
    """A divergent solution idea with panel ratings and dissents."""

    id: str
    text: str
    rating: float = 0.0
    panel_ratings: dict[str, float] = field(default_factory=dict)
    judge_rejections: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.rating = _safe_float(self.rating)


def dedupe_ideas(ideas: list[Idea], threshold: float = 0.7) -> list[Idea]:
    """Remove near-duplicate ideas using Jaccard similarity on tokenized text."""
    kept: list[Idea] = []
    for idea in ideas:
        is_dup = any(jaccard_similarity(idea.text, k.text) >= threshold for k in kept)
        if not is_dup:
            kept.append(idea)
    return kept


def write_solution_candidates(artefacts_dir: Path, ideas: list[Idea]) -> Path:
    """Write `04_solution_candidates.md` — Phase 4 divergent ideation output."""
    for idea in ideas:
        idea.rating = _safe_float(idea.rating)
    sorted_ideas = sorted(ideas, key=lambda i: i.rating, reverse=True)
    lines = [
        "# Solution Candidates (divergent ideation)",
        "",
        f"Total ideas: {len(ideas)}",
        "",
    ]
    for i, idea in enumerate(sorted_ideas, start=1):
        lines.append(f"## {i}. {idea.id} — rating {idea.rating:.2f}")
        lines.append("")
        lines.append(idea.text)
        lines.append("")
        if idea.panel_ratings:
            lines.append("**Panel ratings:**")
            for judge, r in sorted(idea.panel_ratings.items()):
                lines.append(f"- {judge}: {r:.1f}")
            lines.append("")
        if idea.judge_rejections:
            lines.append("**Judge dissents:**")
            for judge, reason in idea.judge_rejections.items():
                lines.append(f"- {judge}: {reason}")
            lines.append("")
    return write_artefact(artefacts_dir, ARTEFACTS.SOLUTION_CANDIDATES, lines)


def _safe_float(value: object) -> float:
    """Coerce any value to a finite float, defaulting NaN/inf/errors to 0.0."""
    try:
        f = float(value)  # type: ignore[arg-type]
        if math.isnan(f) or math.isinf(f):
            return 0.0
        return f
    except (TypeError, ValueError):
        return 0.0
