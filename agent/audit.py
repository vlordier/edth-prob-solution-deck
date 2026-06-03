"""Audit trail writer.

Records every agent interaction — prompts, responses, tool calls — as
timestamped markdown files in artefacts/audit/. Truncates long responses
at MAX_AUDIT_RESPONSE characters.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from agent._constants import MAX_AUDIT_RESPONSE
from agent._util import now_iso, write_artefact

log = logging.getLogger(__name__)

_PHASE_NAMES = {
    0: "onboarding",
    1: "triage",
    2: "elicitation",
    3: "sub_problem",
    4: "ideation",
    5: "research_rank",
    6: "demo_narrative",
    7: "deck_market",
    8: "final_review",
}


@dataclass
class AuditEntry:
    """A single agent interaction — prompts, responses, and tool calls for one phase."""

    phase: int
    phase_name: str
    prompts: list[str]
    responses: list[str]
    tool_calls: list[dict]
    artefact_path: str
    extra: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not (0 <= self.phase <= 8):
            log.warning("AuditEntry phase %d is outside 0-8 range", self.phase)


def write_audit_entry(artefacts_dir: Path, entry: AuditEntry) -> Path:
    """Write a numbered audit markdown file for an agent interaction phase."""
    name = _PHASE_NAMES.get(entry.phase, f"phase_{entry.phase}")
    filename = f"{entry.phase:02d}_{name}.md"
    lines = [
        f"# Audit: Phase {entry.phase} — {entry.phase_name}",
        "",
        f"**Timestamp:** {now_iso()}",
        "",
        f"**Artefact:** `{entry.artefact_path}`",
        "",
    ]
    if entry.prompts:
        lines.append("## Prompts")
        lines.append("")
        for i, p in enumerate(entry.prompts, start=1):
            lines.append(f"### Prompt {i}")
            lines.append("")
            lines.append("```")
            lines.append(p)
            lines.append("```")
            lines.append("")
    if entry.responses:
        lines.append("## Responses")
        lines.append("")
        for i, r in enumerate(entry.responses, start=1):
            lines.append(f"### Response {i}")
            lines.append("")
            r_truncated = r[:MAX_AUDIT_RESPONSE]
            if len(r) > MAX_AUDIT_RESPONSE:
                r_truncated += " (truncated)"
            lines.append("```")
            lines.append(r_truncated)
            lines.append("```")
            lines.append("")
    if entry.tool_calls:
        lines.append("## Tool calls")
        lines.append("")
        for tc in entry.tool_calls:
            lines.append(f"- `{tc.get('tool', '?')}`: {json.dumps(tc)[:200]}")
        lines.append("")
    return write_artefact(artefacts_dir, filename, lines)
