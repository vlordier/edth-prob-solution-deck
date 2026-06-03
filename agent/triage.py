"""Phase 1 — Triage report writer."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from agent._constants import ARTEFACTS
from agent._util import write_artefact
from agent.rubric import DEFAULT_RUBRIC, score_to_weighted

log = logging.getLogger(__name__)


@dataclass
class Cluster:
    """A cluster of related problems scored against the judging rubric axes."""

    name: str
    themes: list[str]
    problem_ids: list[str]
    scores: dict[str, float]
    market_signal: str = ""

    def __post_init__(self) -> None:
        missing = set(DEFAULT_RUBRIC) - self.scores.keys()
        if missing:
            log.warning("Cluster '%s' missing rubric axes: %s", self.name, sorted(missing))


@dataclass
class TriageReport:
    """The output of Phase 1 triage — clustered problems with panel summary."""

    clusters: list[Cluster]
    panel_summary: str = ""
    notes: str = ""


def write_triage_report(artefacts_dir: Path, report: TriageReport) -> Path:
    """Write `01_triage.md` — Phase 1 triage output with cluster scores."""
    lines: list[str] = ["# Triage Report", ""]
    for i, cluster in enumerate(report.clusters, start=1):
        try:
            weighted = score_to_weighted(cluster.scores, DEFAULT_RUBRIC)
        except KeyError:
            log.warning(
                "Cluster '%s': missing rubric axes in scores — weighted total set to 0",
                cluster.name,
            )
            weighted = 0.0
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
    return write_artefact(artefacts_dir, ARTEFACTS.TRIAGE, lines)
