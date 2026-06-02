"""Tests for agent.deck — compile_deck_md and render_deck edge cases."""

from __future__ import annotations

from pathlib import Path

from agent.deck import compile_deck_md


def test_compile_deck_with_empty_artefacts(tmp_path: Path) -> None:
    """All artefacts missing → renders skeleton with defaults."""
    result = compile_deck_md(tmp_path)
    assert "# Project X" in result
    assert "---" in result
    assert "Thank You" in result


def test_compile_deck_with_context_override(tmp_path: Path) -> None:
    """Context dict overrides project name."""
    ctx = {"project_name": "Ghost Fleet", "team_name": "Neptune", "date": "2026-06-03"}
    result = compile_deck_md(tmp_path, ctx)
    assert "Ghost Fleet" in result
    assert "Neptune" in result
    assert "2026-06-03" in result


def test_compile_deck_with_none_context(tmp_path: Path) -> None:
    """None context falls back to defaults without crashing."""
    result = compile_deck_md(tmp_path, None)
    assert "# Project X" in result
    assert "Thank You" in result


def test_compile_deck_with_partial_artefacts(tmp_path: Path) -> None:
    """Some artefacts present, some missing — renders what's available."""
    (tmp_path / "02_candidate_problem.md").write_text("## Candidate 1: Radar\nScore: 5", encoding="utf-8")
    (tmp_path / "05_owner_pick.md").write_text("## Owner Choice\nChose SAR", encoding="utf-8")

    result = compile_deck_md(tmp_path)
    assert "Candidate 1" in result
    assert "Owner Choice" in result
    assert "Thank You" in result


def test_compile_deck_with_all_artefacts(tmp_path: Path) -> None:
    """Full artefacts → no placeholder text."""
    (tmp_path / "02_candidate_problem.md").write_text("## C1: Radar", encoding="utf-8")
    (tmp_path / "05_owner_pick.md").write_text("## Pick: Radar", encoding="utf-8")
    (tmp_path / "07_market.md").write_text("## Market: $5B", encoding="utf-8")
    (tmp_path / "07_competition.md").write_text("## Comp: None", encoding="utf-8")
    (tmp_path / "07_business_model.md").write_text("## BM: SaaS", encoding="utf-8")

    result = compile_deck_md(tmp_path)
    assert "C1: Radar" in result
    assert "Thank You" in result


def test_compile_deck_structure(tmp_path: Path) -> None:
    """Result has Marp front-matter and slide separators."""
    result = compile_deck_md(tmp_path)
    assert result.startswith("---\nmarp: true\nsize: 16:9\n---\n")
    assert "<!-- _class: lead -->" in result


def test_render_deck_writes_md_file(tmp_path: Path) -> None:
    """render_deck writes the deck markdown file to disk."""
    from agent.deck import render_deck

    render_deck(tmp_path)
    assert (tmp_path / "07_deck.md").exists()
    content = (tmp_path / "07_deck.md").read_text()
    assert "Thank You" in content


def test_render_deck_html_fallback(tmp_path: Path) -> None:
    """render_deck produces HTML output file (fallback when no marp/pptx)."""
    from agent.deck import render_deck

    render_deck(tmp_path)
    html_files = list(tmp_path.glob("*.html"))
    assert len(html_files) >= 1


def test_render_deck_with_context(tmp_path: Path) -> None:
    """Context flows through to rendered deck."""
    from agent.deck import render_deck

    render_deck(tmp_path, {"project_name": "Iron Dome"})
    content = (tmp_path / "07_deck.md").read_text()
    assert "Iron Dome" in content


def test_compile_deck_empty_context_dict(tmp_path: Path) -> None:
    """Empty context dict uses all defaults."""
    result = compile_deck_md(tmp_path, {})
    assert "# Project X" in result
