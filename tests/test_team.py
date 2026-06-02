"""Tests for agent.team."""

from __future__ import annotations

from pathlib import Path

from agent.team import (
    MemberProfile,
    TeamDynamics,
    TeamProfile,
    word_count,
    write_team_profile,
)


def test_word_count_empty() -> None:
    assert word_count("") == 0
    assert word_count("   ") == 0


def test_word_count_under_50() -> None:
    assert word_count("Hello world this is short") == 5


def test_word_count_over_50() -> None:
    text = "one " * 60
    assert word_count(text) == 60


def test_write_team_profile_creates_file(tmp_path: Path) -> None:
    profile = TeamProfile(
        members=[
            MemberProfile(
                name="Alice",
                intro="I'm a full-stack engineer with 5 years in Python and React. I built a real-time dashboard for a logistics company. For this hackathon I can own the frontend and the deck.",
                skills=["Python", "React", "D3.js"],
                built=["Real-time logistics dashboard", "Internal CLI tool for deployments"],
                experience_years="5 years full-stack",
                self_assessment="Strongest on frontend; weak on ML.",
                blind_spots=["No ML experience", "No defense domain knowledge"],
                quick_answers={"Framework": "React", "Database": "PostgreSQL"},
            ),
            MemberProfile(
                name="Bob",
                intro="I'm a data scientist. I've shipped NLP models to production at a fintech startup. I can handle the ML pipeline — feature engineering, training, deployment on edge.",
                skills=["Python", "PyTorch", "ONNX"],
                built=["NLP pipeline for fintech", "Edge deployment of RL model"],
                experience_years="3 years data science",
            ),
        ],
        dynamics=TeamDynamics(
            pitcher="Alice",
            demo_champion="Bob",
            builder="Alice (frontend) + Bob (ML)",
            deck="Alice",
        ),
        total_members=2,
        strengths_summary=["Frontend + full-stack", "ML production experience"],
        gaps_summary=["No defense domain", "No hardware/IoT", "No UX design"],
    )
    path = write_team_profile(tmp_path, profile)
    raw = path.read_text(encoding="utf-8")

    assert "Alice" in raw
    assert "Bob" in raw
    assert "React" in raw
    assert "PyTorch" in raw
    assert "real-time dashboard" in raw
    assert "No ML experience" in raw
    assert "Team Dynamics" in raw
    assert "Pitcher" in raw
    assert "Team Strengths" in raw
    assert "Team Gaps" in raw


def test_write_team_profile_minimal(tmp_path: Path) -> None:
    profile = TeamProfile(
        members=[MemberProfile(name="Solo", intro="a" * 50, skills=[], built=[])],
        dynamics=TeamDynamics(),
        total_members=1,
        strengths_summary=[],
        gaps_summary=[],
    )
    path = write_team_profile(tmp_path, profile)
    assert path.exists()
