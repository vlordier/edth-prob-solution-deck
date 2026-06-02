"""Render module — Marp, pptx, and HTML deck rendering with fallback tiers."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

log = logging.getLogger(__name__)


def detect_marp() -> Path | None:
    path = shutil.which("marp")
    return Path(path) if path else None


def has_marp() -> bool:
    return detect_marp() is not None


def has_pptx() -> bool:
    try:
        import pptx  # noqa: F401

        return True
    except ImportError:
        return False


def best_renderer() -> str:
    if has_marp():
        return "marp"
    if has_pptx():
        return "pptx"
    return "html"


_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #1a1a2e; color: #eee; }}
.slide {{ display: none; width: 100vw; height: 100vh; padding: 10vh 10vw; flex-direction: column; justify-content: center; }}
.slide.active {{ display: flex; }}
.slide h1 {{ font-size: 3rem; margin-bottom: 2rem; color: #e94560; }}
.slide h2 {{ font-size: 2rem; margin-bottom: 1.5rem; color: #e94560; }}
.slide h3 {{ font-size: 1.5rem; margin: 1rem 0; }}
.slide p, .slide li {{ font-size: 1.2rem; line-height: 1.8; }}
.slide code {{ background: #16213e; padding: 0.2rem 0.5rem; border-radius: 4px; }}
.slide table {{ width: 100%; border-collapse: collapse; }}
.slide th, .slide td {{ border: 1px solid #444; padding: 0.5rem; text-align: left; }}
.slide th {{ background: #16213e; }}
.counter {{ position: fixed; bottom: 1rem; right: 1rem; font-size: 0.9rem; color: #666; }}
.nav-hint {{ position: fixed; bottom: 1rem; left: 1rem; font-size: 0.8rem; color: #555; }}
</style>
</head>
<body>
{slides}
<div class="counter" id="counter">1 / {total}</div>
<div class="nav-hint">← → arrow keys to navigate</div>
<script>
let current = 0;
const slides = document.querySelectorAll('.slide');
const counter = document.getElementById('counter');
function show(i) {{
  slides.forEach((s, idx) => s.classList.toggle('active', idx === i));
  counter.textContent = (i + 1) + ' / ' + slides.length;
}}
document.addEventListener('keydown', (e) => {{
  if (e.key === 'ArrowRight' || e.key === ' ') {{ e.preventDefault(); current = Math.min(current + 1, slides.length - 1); show(current); }}
  if (e.key === 'ArrowLeft') {{ e.preventDefault(); current = Math.max(current - 1, 0); show(current); }}
}});
show(0);
</script>
</body>
</html>"""


def _md_slides_to_html(md_text: str) -> list[str]:
    slides: list[str] = []
    current: list[str] = []
    for line in md_text.split("\n"):
        st = line.strip()
        if st == "---":
            slides.append("\n".join(current))
            current = []
            continue
        if st.startswith("#### "):
            current.append(f"<h4>{st[5:]}</h4>")
        elif st.startswith("### "):
            current.append(f"<h3>{st[4:]}</h3>")
        elif st.startswith("## "):
            current.append(f"<h2>{st[3:]}</h2>")
        elif st.startswith("# "):
            current.append(f"<h1>{st[2:]}</h1>")
        elif st.startswith("- "):
            current.append(f"<li>{st[2:]}</li>")
        elif st.startswith(">"):
            current.append(f"<blockquote>{st[1:]}</blockquote>")
        elif st.startswith("<!--") or st.startswith("---"):
            continue
        else:
            current.append(f"<p>{line}</p>")
    if current:
        slides.append("\n".join(current))
    return slides


def render_html_deck(
    artefacts_dir: Path, md_text: str, output_filename: str = "07_deck.html"
) -> Path:
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    slide_bodies = _md_slides_to_html(md_text)
    slide_divs = "\n".join(f'<div class="slide">\n{body}\n</div>' for body in slide_bodies)
    title = "Deck"
    for line in md_text.split("\n"):
        if line.startswith("# "):
            title = line[2:].strip()
            break
    html = _HTML_TEMPLATE.format(title=title, slides=slide_divs, total=len(slide_bodies))
    path = artefacts_dir / output_filename
    path.write_text(html, encoding="utf-8")
    log.info("Rendered %d slides to %s", len(slide_bodies), path)
    return path
