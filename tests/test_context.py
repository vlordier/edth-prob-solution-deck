"""Tests for agent.context."""

from __future__ import annotations

from pathlib import Path

from agent.context import default_context, load_context, save_context


def test_default_context_has_required_keys() -> None:
    ctx = default_context()
    assert ctx["hackathon"]["name"] == "EDTH Munich 2025"
    assert "judging_rubric" in ctx["hackathon"]
    assert ctx["agent"]["owner_mode"] in ("real", "sim")


def test_default_rubric_matches_agent_rubric() -> None:
    ctx = default_context()
    rubric = ctx["hackathon"]["judging_rubric"]
    assert abs(sum(rubric.values()) - 1.0) < 1e-9
    assert set(rubric.keys()) == {"impact", "innovation", "execution", "presentation"}


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    ctx = default_context()
    ctx["agent"]["owner_mode"] = "sim"
    ctx["team"]["size"] = 5
    path = save_context(tmp_path, ctx)
    assert path == tmp_path / "00_context.yaml"
    loaded = load_context(tmp_path)
    assert loaded["agent"]["owner_mode"] == "sim"
    assert loaded["team"]["size"] == 5


def test_load_missing_returns_default(tmp_path: Path) -> None:
    ctx = load_context(tmp_path)
    assert ctx == default_context()


def test_save_creates_dir_if_missing(tmp_path: Path) -> None:
    nested = tmp_path / "does" / "not" / "exist"
    save_context(nested, default_context())
    assert (nested / "00_context.yaml").exists()


def test_context_yaml_is_human_readable(tmp_path: Path) -> None:
    save_context(tmp_path, default_context())
    raw = (tmp_path / "00_context.yaml").read_text()
    assert "hackathon:" in raw
    assert "judging_rubric:" in raw
