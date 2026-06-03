from __future__ import annotations

from pathlib import Path

from agent.render import (
    best_renderer,
    detect_marp,
    has_marp,
    has_pptx,
    render_html_deck,
    render_pptx_deck,
)


def test_detect_marp() -> None:
    result = detect_marp()
    if result is not None:
        assert result.exists()


def test_has_marp() -> None:
    assert isinstance(has_marp(), bool)


def test_has_pptx() -> None:
    assert isinstance(has_pptx(), bool)


def test_best_renderer_returns_string() -> None:
    assert best_renderer() in ("marp", "pptx", "html")


def test_render_pptx_deck_creates_file(tmp_path: Path) -> None:
    md_text = "# Title\n\nContent\n\n---\n\n## Slide 2\n\nMore\n"
    path = render_pptx_deck(tmp_path, md_text)
    assert path.exists()
    assert path.stat().st_size > 0
    assert path.suffix == ".pptx"


def test_render_pptx_deck_empty_content(tmp_path: Path) -> None:
    path = render_pptx_deck(tmp_path, "")
    assert path.exists()
    assert path.stat().st_size > 0


def test_render_pptx_deck_nested_artefacts_dir(tmp_path: Path) -> None:
    nested = tmp_path / "a" / "b" / "c"
    path = render_pptx_deck(nested, "# Hello\n\n---\n\n## World\n")
    assert path.exists()
    assert path.stat().st_size > 0


def test_render_pptx_deck_correct_number_of_slides(tmp_path: Path) -> None:
    from pptx import Presentation

    md_text = "# One\n\n---\n\n## Two\n\n---\n\n## Three\n"
    path = render_pptx_deck(tmp_path, md_text)
    prs = Presentation(str(path))
    assert len(prs.slides) == 3


def test_render_html_deck(tmp_path: Path) -> None:
    path = render_html_deck(tmp_path, "# Test\n\n## Slide 1\n\nHello\n\n---\n\n## Slide 2\n\nBye\n")
    assert path.exists()
    assert path.suffix == ".html"
    raw = path.read_text()
    assert "<title>Test</title>" in raw
    assert "Hello" in raw


def test_html_deck_keyboard_nav(tmp_path: Path) -> None:
    path = render_html_deck(tmp_path, "# T\n\n---\n\n## S\n\nContent\n")
    raw = path.read_text()
    assert "ArrowLeft" in raw


def test_html_deck_empty_input(tmp_path: Path) -> None:
    path = render_html_deck(tmp_path, "")
    assert path.exists()
