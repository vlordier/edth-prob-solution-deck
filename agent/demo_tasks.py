"""Task decomposition and team assignment for the demo phase.

Reads team_profile.md and the chosen solution to produce a concrete
task breakdown with team member assignments, gap flags, and time estimates.

See SKILL.md Phase 6 — Task assignment section.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from agent._constants import ARTEFACTS
from agent._util import write_artefact

log = logging.getLogger(__name__)


@dataclass
class DemoTask:
    """A single build task assigned to a team member."""

    id: str
    title: str
    description: str
    estimated_hours: str
    assigned_to: str
    fit_reasoning: str
    gap_flag: bool = False


@dataclass
class DemoTaskPlan:
    """Task breakdown with team assignments, gaps, and build order."""

    tasks: list[DemoTask]
    total_estimated_hours: str
    critical_gaps: list[str]
    suggested_ordering: list[str]
    notes: str = ""


def write_demo_tasks(artefacts_dir: Path, plan: DemoTaskPlan) -> Path:
    """Write `demo_tasks.md` — Phase 6 task breakdown with team assignments."""
    lines = [
        "# Demo Task Breakdown & Team Assignment",
        "",
        f"**Total estimated hours:** {plan.total_estimated_hours}",
        "",
        "---",
        "",
        "## Tasks",
        "",
    ]
    for i, task in enumerate(plan.tasks, start=1):
        lines.append(f"### {i}. {task.id}: {task.title}")
        lines.append("")
        lines.append(task.description)
        lines.append("")
        lines.append(f"**Estimated:** {task.estimated_hours}")
        lines.append("")
        if task.gap_flag:
            lines.append("**⚠️ GAP — nobody on the team is well-suited**")
            lines.append("")
        lines.append(f"**Assigned to:** {task.assigned_to}")
        if task.fit_reasoning:
            lines.append(f"  *{task.fit_reasoning}*")
        lines.append("")
        lines.append("---")
        lines.append("")

    if plan.critical_gaps:
        lines.append("## ⚠️ Critical Skill Gaps")
        lines.append("")
        lines.append("Nobody on the team has strong fit for these tasks:")
        lines.append("")
        for gap in plan.critical_gaps:
            lines.append(f"- {gap}")
        lines.append("")
        lines.append("---")
        lines.append("")

    if plan.suggested_ordering:
        lines.append("## Suggested Build Order")
        lines.append("")
        for j, task_id in enumerate(plan.suggested_ordering, start=1):
            lines.append(f"{j}. {task_id}")
        lines.append("")
        lines.append("---")
        lines.append("")

    if plan.notes:
        lines.append("## Notes")
        lines.append("")
        lines.append(plan.notes)
        lines.append("")

    return write_artefact(artefacts_dir, ARTEFACTS.DEMO_TASKS, lines)
