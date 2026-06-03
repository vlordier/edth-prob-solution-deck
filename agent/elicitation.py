"""Phase 2 — Owner Q&A artefact writers.

Produces owner_questions.md and owner_answers.md from the Mom Test
elicitation interview flow.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from agent._constants import ARTEFACTS
from agent._util import write_artefact

log = logging.getLogger(__name__)


@dataclass
class OwnerQuestion:
    """A question asked to the problem owner during Phase 2 elicitation."""

    id: str
    text: str
    asker: str


def write_owner_questions(artefacts_dir: Path, questions: list[OwnerQuestion]) -> Path:
    """Write `02_owner_questions.md` — Phase 2 elicitation questions."""
    lines = ["# Owner Questions", ""]
    for q in questions:
        lines.append(f"## {q.id} (asked by: {q.asker})")
        lines.append("")
        lines.append(q.text)
        lines.append("")
    return write_artefact(artefacts_dir, ARTEFACTS.OWNER_QUESTIONS, lines)


def write_owner_answers(artefacts_dir: Path, answers: dict[str, str]) -> Path:
    """Write `02_owner_answers.md` — Phase 2 owner's answers to elicitation."""
    lines = ["# Owner Answers", ""]
    for qid, answer in answers.items():
        lines.append(f"## {qid}")
        lines.append("")
        lines.append(answer)
        lines.append("")
    return write_artefact(artefacts_dir, ARTEFACTS.OWNER_ANSWERS, lines)
