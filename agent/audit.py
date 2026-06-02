"""Audit trail writer."""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

_PHASE_NAMES = {0:"onboarding",1:"triage",2:"elicitation",3:"sub_problem",4:"ideation",5:"research_rank",6:"demo_narrative",7:"deck_market",8:"final_review"}

@dataclass
class AuditEntry:
    phase: int; phase_name: str; prompts: list[str]; responses: list[str]; tool_calls: list[dict]; artefact_path: str
    extra: dict = field(default_factory=dict)

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def write_audit_entry(artefacts_dir: Path, entry: AuditEntry) -> Path:
    audit_dir = artefacts_dir / "audit"; audit_dir.mkdir(parents=True, exist_ok=True)
    name = _PHASE_NAMES.get(entry.phase, f"phase_{entry.phase}")
    path = audit_dir / f"{entry.phase:02d}_{name}.md"
    lines = [f"# Audit: Phase {entry.phase} — {entry.phase_name}", "", f"**Timestamp:** {_now_iso()}", "", f"**Artefact:** `{entry.artefact_path}`", ""]
    if entry.prompts:
        lines.append("## Prompts"); lines.append("")
        for i, p in enumerate(entry.prompts, start=1): lines.append(f"### Prompt {i}"); lines.append(""); lines.append("```"); lines.append(p); lines.append("```"); lines.append("")
    if entry.responses:
        lines.append("## Responses"); lines.append("")
        for i, r in enumerate(entry.responses, start=1): lines.append(f"### Response {i}"); lines.append(""); lines.append("```"); lines.append(r[:5000]); lines.append("```"); lines.append("")
    if entry.tool_calls:
        lines.append("## Tool calls"); lines.append("")
        for tc in entry.tool_calls: lines.append(f"- `{tc.get('tool','?')}`: {json.dumps(tc)[:200]}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
