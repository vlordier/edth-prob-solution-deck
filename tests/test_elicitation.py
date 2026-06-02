from __future__ import annotations

from pathlib import Path

from agent.elicitation import OwnerQuestion, write_owner_answers, write_owner_questions


def test_write_questions_creates_file(tmp_path: Path) -> None:
    qs = [
        OwnerQuestion(id="Q1", text="What hurts?", asker="user"),
        OwnerQuestion(id="Q2", text="Who decides?", asker="viper"),
    ]
    path = write_owner_questions(tmp_path, qs)
    raw = path.read_text()
    assert "Q1" in raw
    assert "What hurts?" in raw


def test_write_answers_creates_file(tmp_path: Path) -> None:
    answers = {"Q1": "Detection lag.", "Q2": "JTAC decides."}
    path = write_owner_answers(tmp_path, answers)
    raw = path.read_text()
    assert "Detection lag" in raw
