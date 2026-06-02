"""Tests for agent.sheet."""

from __future__ import annotations

from pathlib import Path

from agent.sheet import (
    BadQuestion,
    ClusterSheet,
    GoodQuestion,
    QuestionSheet,
    write_question_sheet,
)


def test_write_question_sheet_creates_file(tmp_path: Path) -> None:
    sheet = QuestionSheet(
        clusters=[
            ClusterSheet(
                cluster_name="Counter-UAS",
                good_questions=[
                    GoodQuestion(
                        text="Walk me through the last time a drone threat appeared. What happened step by step?",
                        mom_test_rule="Ask about specific past incidents, not opinions about the future.",
                    ),
                ],
                bad_questions=[
                    BadQuestion(
                        text="Do you think an AI detection system would help?",
                        why_bad="Leading question — asks for opinion, not evidence. They'll say yes to be polite.",
                    ),
                ],
            ),
        ],
        mom_test_rules=[
            "Talk about their life, not your idea.",
            "Ask about specific past incidents.",
        ],
        interviewer_tips=[
            "If they say 'a lot of people have this problem', ask for an introduction.",
        ],
        answer_scoring={
            "Concrete past incident with cost": "Strong — real problem",
            "Vague complaint, no specifics": "Weak — not validated",
        },
    )
    path = write_question_sheet(tmp_path, sheet)
    raw = path.read_text(encoding="utf-8")
    assert "Counter-UAS" in raw
    assert "Walk me through the last time" in raw
    assert "Ask about specific past incidents" in raw
    assert "Leading question" in raw or "leading" in raw.lower()
    assert "The Mom Test" in raw
    assert "Score Answers" in raw


def test_question_sheet_includes_rules_and_tips(tmp_path: Path) -> None:
    sheet = QuestionSheet(
        clusters=[],
        mom_test_rules=["Rule 1", "Rule 2"],
        interviewer_tips=["Tip A", "Tip B"],
        answer_scoring={"Good signal": "Buy"},
    )
    write_question_sheet(tmp_path, sheet)
    raw = (tmp_path / "question_sheet.md").read_text(encoding="utf-8")
    assert "Rule 1" in raw
    assert "Rule 2" in raw
    assert "Tip A" in raw
    assert "Tip B" in raw
