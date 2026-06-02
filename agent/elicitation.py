"""Phase 2 — Owner Q&A artefact writers."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from agent._constants import ARTEFACTS
from agent._util import write_artefact

log = logging.getLogger(__name__)


@dataclass
class OwnerQuestion:
    id: str
    text: str
    asker: str


def write_owner_questions(artefacts_dir: Path, questions: list[OwnerQuestion]) -> Path:
    lines = ["# Owner Questions", ""]
    for q in questions:
        lines.append(f"## {q.id} (asked by: {q.asker})")
        lines.append("")
        lines.append(q.text)
        lines.append("")
    return write_artefact(artefacts_dir, ARTEFACTS.OWNER_QUESTIONS, lines)


def write_owner_answers(artefacts_dir: Path, answers: dict[str, str]) -> Path:
    lines = ["# Owner Answers", ""]
    for qid, answer in answers.items():
        lines.append(f"## {qid}")
        lines.append("")
        lines.append(answer)
        lines.append("")
    return write_artefact(artefacts_dir, ARTEFACTS.OWNER_ANSWERS, lines)
