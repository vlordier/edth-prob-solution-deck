from __future__ import annotations
from pathlib import Path
from agent.audit import AuditEntry, write_audit_entry

def test_write_audit(tmp_path: Path) -> None:
    entry = AuditEntry(phase=1, phase_name="Triage", prompts=["Cluster these."], responses=['{"clusters":[]}'], tool_calls=[{"tool":"web_search","query":"drones"}], artefact_path="artefacts/01_triage.md")
    path = write_audit_entry(tmp_path, entry)
    raw = path.read_text()
    assert "Triage" in raw; assert "Cluster these" in raw; assert "drones" in raw

def test_audit_naming(tmp_path: Path) -> None:
    entry = AuditEntry(phase=2, phase_name="Elicit", prompts=[], responses=[], tool_calls=[], artefact_path="02.md")
    path = write_audit_entry(tmp_path, entry)
    assert path.name == "02_elicitation.md"
