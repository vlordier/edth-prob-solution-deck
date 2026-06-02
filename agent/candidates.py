"""Phase 2 — Candidate problem writer."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from agent.rubric import DEFAULT_RUBRIC, score_to_weighted


@dataclass
class Candidate:
    problem_id: str
    name: str
    scores: dict[str, float]
    panel_picks: dict[str, int] = field(default_factory=dict)
    reasoning: str = ""

    def weighted_score(self) -> float:
        return score_to_weighted(self.scores, DEFAULT_RUBRIC)


def write_candidate_problem(artefacts_dir: Path, candidates: list[Candidate]) -> Path:
    artefacts_dir.mkdir(parents=True, exist_ok=True)
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
    path = artefacts_dir / "02_candidate_problem.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
