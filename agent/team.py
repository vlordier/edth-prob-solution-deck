"""Team discovery helpers — word counting and profile writing."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


def word_count(text: str) -> int:
    """Count words in a string. Splits on whitespace."""
    return len(text.strip().split())


class MemberProfile(BaseModel):
    name: str
    intro: str  # raw self-introduction (≥50 words enforced at interview time)
    skills: list[str] = Field(default_factory=list)  # "Python", "React", etc.
    built: list[str] = Field(default_factory=list)  # things they've built
    experience_years: str = ""
    self_assessment: str = ""  # their own take
    blind_spots: list[str] = Field(default_factory=list)  # gaps the agent detects
    quick_answers: dict[str, str] = Field(default_factory=dict)  # A/B/C answers


class TeamDynamics(BaseModel):
    pitcher: str = ""  # 3-min pitch
    demo_champion: str = ""  # live demo
    builder: str = ""  # core code
    deck: str = ""  # deck / market research
    notes: str = ""


class TeamEquipment(BaseModel):
    available: list[str] = Field(default_factory=list)  # what they have
    accessible: list[str] = Field(default_factory=list)  # can get in 2h
    gaps: list[str] = Field(default_factory=list)  # critical — can't solve without
    notes: str = ""


class TeamProfile(BaseModel):
    members: list[MemberProfile]
    dynamics: TeamDynamics = Field(default_factory=TeamDynamics)
    equipment: TeamEquipment = Field(default_factory=TeamEquipment)
    total_members: int = 0
    strengths_summary: list[str] = Field(default_factory=list)
    gaps_summary: list[str] = Field(default_factory=list)


def write_team_profile(artefacts_dir: Path, profile: TeamProfile) -> Path:
    """Write artefacts/team_profile.md — committed to git as team memory."""
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Team Profile",
        "",
        f"**Team size:** {profile.total_members}",
        "",
        "---",
        "",
    ]

    for i, m in enumerate(profile.members, start=1):
        lines.append(f"## Member {i}: {m.name}")
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

    lines.append("## Team Dynamics")
    lines.append("")
    if profile.dynamics.pitcher:
        lines.append(f"- **Pitcher (3-min pitch):** {profile.dynamics.pitcher}")
    if profile.dynamics.demo_champion:
        lines.append(f"- **Demo champion (live demo):** {profile.dynamics.demo_champion}")
    if profile.dynamics.builder:
        lines.append(f"- **Builder (core code):** {profile.dynamics.builder}")
    if profile.dynamics.deck:
        lines.append(f"- **Deck & market:** {profile.dynamics.deck}")
    if profile.dynamics.notes:
        lines.append(f"- **Notes:** {profile.dynamics.notes}")
    lines.append("")

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

    path = artefacts_dir / "team_profile.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
