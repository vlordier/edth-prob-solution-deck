"""Phase 1 — Triage report writer."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from agent.rubric import score_to_weighted, DEFAULT_RUBRIC


@dataclass
class Cluster:
    name: str
    themes: list[str]
    problem_ids: list[str]
    scores: dict[str, float]
    market_signal: str = ""


@dataclass
class TriageReport:
    clusters: list[Cluster]
    panel_summary: str = ""
    notes: str = ""


def write_triage_report(artefacts_dir: Path, report: TriageReport) -> Path:
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    lines: list[str] = ["# Triage Report", ""]
    for i, cluster in enumerate(report.clusters, start=1):
        weighted = score_to_weighted(cluster.scores, DEFAULT_RUBRIC)
        lines.append(f"## Cluster {i}: {cluster.name}")
        lines.append("")
        if cluster.themes:
            lines.append(f"**Themes:** {', '.join(cluster.themes)}")
            lines.append("")
        lines.append(f"**Problems:** {len(cluster.problem_ids)}")
        lines.append("")
        lines.append("**Axis scores (1-5):**")
        for axis, score in cluster.scores.items():
            lines.append(f"- {axis}: {score:.2f}")
        lines.append(f"- **weighted total: {weighted:.2f}**")
        lines.append("")
        if cluster.market_signal:
            lines.append(f"**Market signal:** {cluster.market_signal}")
            lines.append("")
        lines.append(f"**Problem IDs:** {', '.join(cluster.problem_ids)}")
        lines.append("")
    if report.panel_summary:
        lines.append("## Panel summary")
        lines.append("")
        lines.append(report.panel_summary)
        lines.append("")
    if report.notes:
        lines.append("## Notes")
        lines.append("")
        lines.append(report.notes)
        lines.append("")
    path = artefacts_dir / "01_triage.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
