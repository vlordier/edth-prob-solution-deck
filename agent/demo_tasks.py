"""Task decomposition and team assignment for the demo phase.

Reads team_profile.md and the chosen solution to produce a concrete
task breakdown with team member assignments, gap flags, and time estimates.

See SKILL.md Phase 6 — Task assignment section.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class DemoTask:
    id: str
    title: str
    description: str
    estimated_hours: str
    assigned_to: str  # team member name, or "UNASSIGNED"
    fit_reasoning: str  # why this person, or why nobody fits
    gap_flag: bool = False  # true if no team member is well-suited


@dataclass
class DemoTaskPlan:
    tasks: list[DemoTask]
    total_estimated_hours: str
    critical_gaps: list[str]  # skills nobody has
    suggested_ordering: list[str]  # task IDs in recommended build order
    notes: str = ""


def write_demo_tasks(artefacts_dir: Path, plan: DemoTaskPlan) -> Path:
    """Write artefacts/demo_tasks.md."""
    artefacts_dir.mkdir(parents=True, exist_ok=True)

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

    path = artefacts_dir / "demo_tasks.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
