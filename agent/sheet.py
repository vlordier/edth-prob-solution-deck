"""Question sheet writer — a printable Mom Test interview guide.

Called by `/edth-agent sheet` to generate a standalone document of
structured questions for the problem owner, separate from the interactive
Phase 2 Q&A flow.

See SKILL.md "Question sheet" section.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class BadQuestion:
    text: str
    why_bad: str


@dataclass
class GoodQuestion:
    text: str
    mom_test_rule: str  # which Mom Test principle it follows


@dataclass
class ClusterSheet:
    cluster_name: str
    good_questions: list[GoodQuestion]
    bad_questions: list[BadQuestion]  # what NOT to ask for this cluster


@dataclass
class QuestionSheet:
    clusters: list[ClusterSheet]
    mom_test_rules: list[str]
    interviewer_tips: list[str]
    answer_scoring: dict[str, str]  # signal type -> score weight


def write_question_sheet(artefacts_dir: Path, sheet: QuestionSheet) -> Path:
    """Write artefacts/question_sheet.md."""
    artefacts_dir.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Problem Owner Question Sheet",
        "",
        "> Inspired by **The Mom Test** (Rob Fitzpatrick).",
        "> Talk about their life, not your idea. Ask about specific past incidents.",
        "",
        "---",
        "",
        "## The Mom Test — Rules",
        "",
    ]
    for i, rule in enumerate(sheet.mom_test_rules, start=1):
        lines.append(f"{i}. {rule}")
    lines.append("")

    lines.append("## Interviewer Tips")
    lines.append("")
    for tip in sheet.interviewer_tips:
        lines.append(f"- {tip}")
    lines.append("")

    lines.append("---")
    lines.append("")

    for ci, cluster in enumerate(sheet.clusters, start=1):
        lines.append(f"## Cluster {ci}: {cluster.cluster_name}")
        lines.append("")

        lines.append("### ✅ Ask These")
        lines.append("")
        for i, q in enumerate(cluster.good_questions, start=1):
            lines.append(f"**Q{ci}.{i}** — {q.text}")
            lines.append(f"  *Mom Test rule: {q.mom_test_rule}*")
            lines.append("")

        lines.append("### ❌ Avoid These")
        lines.append("")
        for bq in cluster.bad_questions:
            lines.append(f'- *"{bq.text}"* — {bq.why_bad}')
        lines.append("")

        lines.append("---")
        lines.append("")

    lines.append("## How to Score Answers")
    lines.append("")
    lines.append("| Answer type | Signal strength | Example |")
    lines.append("|---|---|---|")
    for signal_type, desc in sheet.answer_scoring.items():
        lines.append(f"| {signal_type} | {desc} | |")
    lines.append("")
    lines.append(
        "**After the interview:** score each cluster 1-5 on purchase intent signal. No signal = no problem."
    )
    lines.append("")

    path = artefacts_dir / "question_sheet.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
