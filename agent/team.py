"""Team discovery helpers — word counting and profile writing."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


def word_count(text: str) -> int:
    """Count words in a string. Splits on whitespace."""
    return len(text.strip().split())


@dataclass
class MemberProfile:
    name: str
    intro: str  # raw self-introduction (≥50 words enforced at interview time)
    skills: list[str]  # extracted: "Python", "React", "signal processing", etc.
    built: list[str]  # things they've built relevant to this hackathon
    experience_years: str = ""
    self_assessment: str = ""  # their own take on what they bring
    blind_spots: list[str] = field(default_factory=list)  # gaps the agent detects
    quick_answers: dict[str, str] = field(default_factory=dict)  # A/B/C answers


@dataclass
class TeamDynamics:
    pitcher: str = ""  # who volunteers for the 3-min pitch
    demo_champion: str = ""  # who drives the live demo
    builder: str = ""  # who writes the code
    deck: str = ""  # who owns the deck / market research
    notes: str = ""


@dataclass
class TeamProfile:
    members: list[MemberProfile]
    dynamics: TeamDynamics
    total_members: int
    strengths_summary: list[str]  # aggregate
    gaps_summary: list[str]  # what's missing


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
