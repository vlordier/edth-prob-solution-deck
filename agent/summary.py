"""Phase 8 — Final summary writer."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from agent._constants import ARTEFACTS
from agent._util import write_artefact

log = logging.getLogger(__name__)


@dataclass
class JudgeVerdict:
    judge: str
    thumbs_up: bool
    note: str


@dataclass
class Summary:
    pitch: str
    top_risks: list[str]
    top_differentiators: list[str]
    verdicts: list[JudgeVerdict]
    next_steps: list[str]


def write_summary(artefacts_dir: Path, summary: Summary) -> Path:
    ups = sum(1 for v in summary.verdicts if v.thumbs_up)
    downs = len(summary.verdicts) - ups
    lines = [
        "# Final Summary",
        "",
        "## One-Paragraph Pitch",
        "",
        summary.pitch,
        "",
        "## Top 3 Differentiators",
        "",
    ]
    for d in summary.top_differentiators:
        lines.append(f"- {d}")
    lines.append("")
    lines.append("## Top 3 Risks")
    lines.append("")
    for r in summary.top_risks:
        lines.append(f"- {r}")
    lines.append("")
    lines.append("## Panel Verdict")
    lines.append("")
    lines.append(f"**{ups} \u2611  {downs} \u2612**")
    lines.append("")
    for v in summary.verdicts:
        icon = "\u2611" if v.thumbs_up else "\u2612"
        lines.append(f"- **{v.judge}** {icon} — {v.note}")
    lines.append("")
    lines.append("## Next Steps (48h)")
    lines.append("")
    for ns in summary.next_steps:
        lines.append(f"- {ns}")
    lines.append("")
    return write_artefact(artefacts_dir, ARTEFACTS.SUMMARY, lines)
