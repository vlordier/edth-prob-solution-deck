"""Phase 3 — Sub-problem writer and ROI scoring."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

ROI_WEIGHTS = {"impact":0.30,"time_fit":0.30,"demo_ability":0.25,"dependency_risk":0.15}

@dataclass
class SubProblem:
    id: str; title: str; scores: dict[str,float]; description: str = ""
    def roi_score(self) -> float:
        s = dict(self.scores)
        s["dependency_risk"] = max(1.0, min(5.0, 5.0 - s.get("dependency_risk",3.0)))
        return sum(s[k] * w for k, w in ROI_WEIGHTS.items())

def write_sub_problem(artefacts_dir: Path, sub_problems: list[SubProblem]) -> Path:
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# Sub-problem decomposition", ""]
    for sp in sub_problems:
        lines.append(f"## {sp.id}: {sp.title}")
        lines.append(""); lines.append(f"**ROI score: {sp.roi_score():.2f}**"); lines.append("")
        if sp.description: lines.append(sp.description); lines.append("")
        lines.append("**Axis scores (1-5):**")
        for axis, s in sp.scores.items(): lines.append(f"- {axis}: {s:.2f}")
        lines.append("")
    path = artefacts_dir / "03_chosen_sub_problem.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
