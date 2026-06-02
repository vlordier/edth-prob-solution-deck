"""Phase 2 — Owner Q&A artefact writers."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

@dataclass
class OwnerQuestion:
    id: str
    text: str
    asker: str

def write_owner_questions(artefacts_dir: Path, questions: list[OwnerQuestion]) -> Path:
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# Owner Questions", ""]
    for q in questions:
        lines.append(f"## {q.id} (asked by: {q.asker})")
        lines.append(""); lines.append(q.text); lines.append("")
    path = artefacts_dir / "02_owner_questions.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path

def write_owner_answers(artefacts_dir: Path, answers: dict[str, str]) -> Path:
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# Owner Answers", ""]
    for qid, answer in answers.items():
        lines.append(f"## {qid}"); lines.append(""); lines.append(answer); lines.append("")
    path = artefacts_dir / "02_owner_answers.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
