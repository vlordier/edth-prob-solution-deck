"""Phase 4 — Divergent ideation helpers."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path

def _tokens(s: str) -> set[str]:
    return {t.lower() for t in s.split() if len(t) > 2}

def jaccard_similarity(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta and not tb: return 1.0
    if not ta or not tb: return 0.0
    return len(ta & tb) / len(ta | tb)

@dataclass
class Idea:
    id: str; text: str; rating: float = 0.0
    panel_ratings: dict[str,float] = field(default_factory=dict)
    judge_rejections: dict[str,str] = field(default_factory=dict)

def dedupe_ideas(ideas: list[Idea], threshold: float = 0.7) -> list[Idea]:
    kept: list[Idea] = []
    for idea in ideas:
        is_dup = any(jaccard_similarity(idea.text, k.text) >= threshold for k in kept)
        if not is_dup: kept.append(idea)
    return kept

def write_solution_candidates(artefacts_dir: Path, ideas: list[Idea]) -> Path:
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    sorted_ideas = sorted(ideas, key=lambda i: -i.rating)
    lines = ["# Solution Candidates (divergent ideation)", "", f"Total ideas: {len(ideas)}", ""]
    for i, idea in enumerate(sorted_ideas, start=1):
        lines.append(f"## {i}. {idea.id} — rating {idea.rating:.2f}")
        lines.append(""); lines.append(idea.text); lines.append("")
        if idea.panel_ratings:
            lines.append("**Panel ratings:**")
            for judge, r in sorted(idea.panel_ratings.items()): lines.append(f"- {judge}: {r:.1f}")
            lines.append("")
        if idea.judge_rejections:
            lines.append("**Judge dissents:**")
            for judge, reason in idea.judge_rejections.items(): lines.append(f"- {judge}: {reason}")
            lines.append("")
    path = artefacts_dir / "04_solution_candidates.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
