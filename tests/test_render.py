from __future__ import annotations
from pathlib import Path
from agent.render import best_renderer, detect_marp, has_marp, has_pptx, render_html_deck

def test_detect_marp() -> None:
    result = detect_marp()
    if result is not None: assert result.exists()

def test_has_marp() -> None:
    assert isinstance(has_marp(), bool)

def test_has_pptx() -> None:
    assert isinstance(has_pptx(), bool)

def test_best_renderer_returns_string() -> None:
    assert best_renderer() in ("marp","pptx","html")

def test_render_html_deck(tmp_path: Path) -> None:
    path = render_html_deck(tmp_path, "# Test\n\n## Slide 1\n\nHello\n\n---\n\n## Slide 2\n\nBye\n")
    assert path.exists(); assert path.suffix == ".html"
    raw = path.read_text()
    assert "<title>Test</title>" in raw; assert "Hello" in raw

def test_html_deck_keyboard_nav(tmp_path: Path) -> None:
    path = render_html_deck(tmp_path, "# T\n\n---\n\n## S\n\nContent\n")
    raw = path.read_text()
    assert "ArrowLeft" in raw

def test_html_deck_empty_input(tmp_path: Path) -> None:
    path = render_html_deck(tmp_path, "")
    assert path.exists()
