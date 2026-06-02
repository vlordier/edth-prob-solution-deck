"""Phase 3 — Sub-problem writer and ROI scoring."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from agent._constants import ARTEFACTS
from agent._util import write_artefact

log = logging.getLogger(__name__)

ROI_WEIGHTS = {"impact": 0.30, "time_fit": 0.30, "demo_ability": 0.25, "dependency_risk": 0.15}


@dataclass
class SubProblem:
    id: str
    title: str
    scores: dict[str, float]
    description: str = ""

    def roi_score(self) -> float:
        """Weighted ROI score clamped to [1.0, 5.0].

        dependency_risk is inverted (higher risk = lower score).
        Missing weight axes default to 0.0 contribution.
        """
        s = dict(self.scores)
        dep = s.get("dependency_risk", 3.0)
        s["dependency_risk"] = max(1.0, min(5.0, 5.0 - dep))
        return sum(s.get(k, 0.0) * w for k, w in ROI_WEIGHTS.items())


def write_sub_problem(artefacts_dir: Path, sub_problems: list[SubProblem]) -> Path:
    lines = ["# Sub-problem decomposition", ""]
    for sp in sub_problems:
        lines.append(f"## {sp.id}: {sp.title}")
        lines.append("")
        lines.append(f"**ROI score: {sp.roi_score():.2f}**")
        lines.append("")
        if sp.description:
            lines.append(sp.description)
            lines.append("")
        lines.append("**Axis scores (1-5):**")
        for axis, s in sp.scores.items():
            lines.append(f"- {axis}: {s:.2f}")
        lines.append("")
    return write_artefact(artefacts_dir, ARTEFACTS.SUB_PROBLEM, lines)
