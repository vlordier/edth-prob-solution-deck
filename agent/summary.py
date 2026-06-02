"""Phase 8 — Final summary writer."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class JudgeVerdict:
    judge: str; thumbs_up: bool; note: str

@dataclass
class Summary:
    pitch: str; top_risks: list[str]; top_differentiators: list[str]
    verdicts: list[JudgeVerdict]; next_steps: list[str]

def write_summary(artefacts_dir: Path, summary: Summary) -> Path:
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    ups = sum(1 for v in summary.verdicts if v.thumbs_up)
    downs = len(summary.verdicts) - ups
    lines = ["# Final Summary", "", "## One-Paragraph Pitch", "", summary.pitch, "", "## Top 3 Differentiators", ""]
    for d in summary.top_differentiators: lines.append(f"- {d}")
    lines.append("")
    lines.append("## Top 3 Risks"); lines.append("")
    for r in summary.top_risks: lines.append(f"- {r}")
    lines.append("")
    lines.append("## Panel Verdict"); lines.append("")
    lines.append(f"**{ups} \U0001f44d  {downs} \U0001f44e**"); lines.append("")
    for v in summary.verdicts:
        icon = "\U0001f44d" if v.thumbs_up else "\U0001f44e"
        lines.append(f"- **{v.judge}** {icon} — {v.note}")
    lines.append("")
    lines.append("## Next Steps (48h)"); lines.append("")
    for ns in summary.next_steps: lines.append(f"- {ns}")
    lines.append("")
    path = artefacts_dir / "08_summary.md"; path.write_text("\n".join(lines), encoding="utf-8")
    return path
