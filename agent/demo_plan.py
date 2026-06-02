"""Phase 6 — Demo plan writer."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class Risk:
    what: str; likelihood: str; impact: str; mitigation: str

@dataclass
class DemoPlan:
    thin_demo: str; script: list[tuple[int,str]]; pitch: str
    qa_prep: list[tuple[str,str]]; risks: list[Risk]

def _fmt_seconds(s: int) -> str:
    m, sec = divmod(s, 60); return f"{m}:{sec:02d}"

def write_demo_plan(artefacts_dir: Path, plan: DemoPlan) -> Path:
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# Demo Plan", "", "## Thin Demo", "", plan.thin_demo, "", "## 3-Minute Demo Script", ""]
    for sec, desc in plan.script:
        lines.append(f"**[{_fmt_seconds(sec)}]** {desc}")
    lines.append(""); lines.append("## 30-Second Elevator Pitch"); lines.append(""); lines.append(plan.pitch); lines.append("")
    lines.append("## Judge Q&A Prep"); lines.append("")
    for q, a in plan.qa_prep:
        lines.append(f"**{q}**"); lines.append(f"{a}"); lines.append("")
    lines.append("## Risk Register"); lines.append("")
    lines.append("| Risk | Likelihood | Impact | Mitigation |")
    lines.append("|---|---|---|---|")
    for r in plan.risks:
        lines.append(f"| {r.what} | {r.likelihood} | {r.impact} | {r.mitigation} |")
    lines.append("")
    path = artefacts_dir / "06_demo_plan.md"; path.write_text("\n".join(lines), encoding="utf-8")
    return path
