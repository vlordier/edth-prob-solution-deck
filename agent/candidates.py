"""Phase 2 — Candidate problem writer."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from agent._constants import ARTEFACTS
from agent._util import write_artefact
from agent.rubric import DEFAULT_RUBRIC, score_to_weighted

log = logging.getLogger(__name__)


@dataclass
class Candidate:
    """A shortlisted problem scored against the judging rubric."""

    problem_id: str
    name: str
    scores: dict[str, float]
    panel_picks: dict[str, int] = field(default_factory=dict)
    reasoning: str = ""

    def __post_init__(self) -> None:
        missing = set(DEFAULT_RUBRIC) - self.scores.keys()
        if missing:
            log.warning("Candidate '%s' missing rubric axes: %s", self.problem_id, sorted(missing))

    def weighted_score(self) -> float:
        """Aggregate score weighted by rubric axis weights."""
        return score_to_weighted(self.scores, DEFAULT_RUBRIC)


def write_candidate_problem(artefacts_dir: Path, candidates: list[Candidate]) -> Path:
    """Write `02_candidate_problem.md` — Phase 2 candidate shortlist with panel picks."""
    lines = ["# Top 3 Candidate Problems", ""]
    for i, c in enumerate(candidates, start=1):
        lines.append(f"## Candidate {i}: {c.name} ({c.problem_id})")
        lines.append("")
        lines.append(f"**Weighted score: {c.weighted_score():.2f}**")
        lines.append("")
        lines.append("**Axis scores:**")
        for axis, s in c.scores.items():
            lines.append(f"- {axis}: {s:.2f}")
        lines.append("")
        if c.panel_picks:
            lines.append("**Panel ranking:**")
            for judge, rank in sorted(c.panel_picks.items(), key=lambda x: x[1]):
                lines.append(f"- {judge}: #{rank}")
            lines.append("")
        if c.reasoning:
            lines.append("**Reasoning:**")
            lines.append(c.reasoning)
            lines.append("")
    return write_artefact(artefacts_dir, ARTEFACTS.CANDIDATE, lines)
