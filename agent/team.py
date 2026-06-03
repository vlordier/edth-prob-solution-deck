"""Team discovery helpers — word counting and profile writing.

Produces artefacts/team_profile.md from structured team discovery interviews.
Uses pydantic v2 models for schema enforcement.
"""

from __future__ import annotations

import logging
from pathlib import Path

from pydantic import BaseModel, Field

from agent._constants import ARTEFACTS
from agent._util import write_artefact

log = logging.getLogger(__name__)


def word_count(text: str) -> int:
    """Count whitespace-delimited words in a string."""
    return len(text.strip().split())


class MemberProfile(BaseModel):
    """A team member's profile from the discovery interview."""

    name: str
    intro: str
    skills: list[str] = Field(default_factory=list)
    built: list[str] = Field(default_factory=list)
    experience_years: str = ""
    self_assessment: str = ""
    blind_spots: list[str] = Field(default_factory=list)
    quick_answers: dict[str, str] = Field(default_factory=dict)


class TeamDynamics(BaseModel):
    """Role assignments for the 48h sprint."""

    pitcher: str = ""
    demo_champion: str = ""
    builder: str = ""
    deck: str = ""
    notes: str = ""


class TeamEquipment(BaseModel):
    """Hardware/software inventory — what the team has, can get, or critically needs."""

    available: list[str] = Field(default_factory=list)
    accessible: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    notes: str = ""


class TeamProfile(BaseModel):
    """Complete team profile — members, dynamics, equipment, and gap analysis."""

    members: list[MemberProfile]
    dynamics: TeamDynamics = Field(default_factory=TeamDynamics)
    equipment: TeamEquipment = Field(default_factory=TeamEquipment)
    total_members: int = 0
    strengths_summary: list[str] = Field(default_factory=list)
    gaps_summary: list[str] = Field(default_factory=list)


def write_team_profile(artefacts_dir: Path, profile: TeamProfile) -> Path:
    """Write `team_profile.md` — committed team memory for the hackathon."""
    lines = [
        "# Team Profile",
        "",
        f"**Team size:** {profile.total_members}",
        "",
        "---",
        "",
    ]
    for i, m in enumerate(profile.members, start=1):
        _render_member(m, i, lines)

    _render_dynamics(profile, lines)
    _render_equipment(profile, lines)

    lines.append("## Team Strengths")
    lines.append("")
    for s in profile.strengths_summary:
        lines.append(f"- {s}")
    lines.append("")

    lines.append("## Team Gaps")
    lines.append("")
    for g in profile.gaps_summary:
        lines.append(f"- {g}")
    lines.append("")

    return write_artefact(artefacts_dir, ARTEFACTS.TEAM_PROFILE, lines)


def _render_member(m: MemberProfile, idx: int, lines: list[str]) -> None:
    lines.append(f"## Member {idx}: {m.name}")
    lines.append("")
    lines.append("### Self-introduction")
    lines.append("")
    lines.append(m.intro)
    lines.append("")
    if m.skills:
        lines.append(f"**Declared skills:** {', '.join(m.skills)}")
        lines.append("")
    if m.built:
        lines.append("**Things they've built:**")
        for b in m.built:
            lines.append(f"- {b}")
        lines.append("")
    if m.experience_years:
        lines.append(f"**Experience:** {m.experience_years}")
        lines.append("")
    if m.self_assessment:
        lines.append(f"**Self-assessment:** {m.self_assessment}")
        lines.append("")
    if m.blind_spots:
        lines.append("**Detected gaps / blind spots:**")
        for bs in m.blind_spots:
            lines.append(f"- {bs}")
        lines.append("")
    if m.quick_answers:
        lines.append("**Quick-fire answers:**")
        for q, a in m.quick_answers.items():
            lines.append(f"- **{q}** → {a}")
        lines.append("")
    lines.append("---")
    lines.append("")


def _render_dynamics(profile: TeamProfile, lines: list[str]) -> None:
    lines.append("## Team Dynamics")
    lines.append("")
    d = profile.dynamics
    if d.pitcher:
        lines.append(f"- **Pitcher (3-min pitch):** {d.pitcher}")
    if d.demo_champion:
        lines.append(f"- **Demo champion (live demo):** {d.demo_champion}")
    if d.builder:
        lines.append(f"- **Builder (core code):** {d.builder}")
    if d.deck:
        lines.append(f"- **Deck & market:** {d.deck}")
    if d.notes:
        lines.append(f"- **Notes:** {d.notes}")
    lines.append("")


def _render_equipment(profile: TeamProfile, lines: list[str]) -> None:
    lines.append("## Team Equipment")
    lines.append("")
    eq = profile.equipment
    lines.append("### Available")
    lines.append("")
    for a in eq.available or ["(none listed)"]:
        lines.append(f"- {a}")
    lines.append("")
    lines.append("### Accessible (within 2 hours)")
    lines.append("")
    for a in eq.accessible or ["(none listed)"]:
        lines.append(f"- {a}")
    lines.append("")
    lines.append("### Critical Gaps")
    lines.append("")
    for g in eq.gaps or ["(none flagged)"]:
        lines.append(f"- {g}")
    if eq.notes:
        lines.append("")
        lines.append(eq.notes)
    lines.append("")
