"""Phase 5 — Research + ranking writers."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class RankedSolution:
    idea_id: str
    text: str
    research: str
    aggregate_score: float
    panel_scores: dict[str, float] = field(default_factory=dict)
    spread: float = 0.0


def write_ranked_solutions(artefacts_dir: Path, solutions: list[RankedSolution]) -> Path:
    artefacts_dir.mkdir(parents=True, exist_ok=True)
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
    path = artefacts_dir / "05_ranked_solutions.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_owner_pick(
    artefacts_dir: Path,
    chosen_idea_id: str,
    validation_notes: str,
    dissents: list[tuple[str, str]] | None = None,
) -> Path:
    dissents = dissents or []
    artefacts_dir.mkdir(parents=True, exist_ok=True)
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
        for judge, reason in dissents:
            lines.append(f"- **{judge}**: {reason}")
        lines.append("")
    path = artefacts_dir / "05_owner_pick.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
