"""Final deck compiler.

Orchestrates deck content assembly and renderer dispatch.
Content → compile_deck_md; rendering → render.py.
"""

from __future__ import annotations

import logging
import subprocess
from contextlib import suppress
from pathlib import Path

from agent._constants import ARTEFACTS, RenderMode
from agent._models import DECK_CONTEXT_DEFAULTS, DeckContext
from agent._util import slurp_file, write_artefact

log = logging.getLogger(__name__)


def compile_deck_md(artefacts_dir: Path, context: DeckContext | None = None) -> str:
    """Produce a single Marp-flavoured markdown string from artefacts.

    Accepts a DeckContext or None (falls back to defaults).
    """
    ctx: DeckContext = dict(DECK_CONTEXT_DEFAULTS, **(context or {}))
    hackathon = ctx.get("hackathon_name", DECK_CONTEXT_DEFAULTS["hackathon_name"])
    project = ctx.get("project_name", DECK_CONTEXT_DEFAULTS["project_name"])
    team = ctx.get("team_name", DECK_CONTEXT_DEFAULTS["team_name"])

    problem = slurp_file(artefacts_dir, ARTEFACTS.CANDIDATE)
    solution = slurp_file(artefacts_dir, ARTEFACTS.OWNER_PICK)
    market = slurp_file(artefacts_dir, ARTEFACTS.MARKET)
    comp = slurp_file(artefacts_dir, ARTEFACTS.COMPETITION)
    bm = slurp_file(artefacts_dir, ARTEFACTS.BUSINESS_MODEL)

    return "\n".join(
        [
            "---",
            "marp: true",
            "size: 16:9",
            "---",
            "",
            f"# {project}",
            f"**{hackathon}**",
            f"{team} | {ctx.get('date', '')}",
            "",
            "---",
            "",
            problem,
            "",
            "---",
            "",
            solution,
            "",
            "---",
            "",
            market,
            "",
            "---",
            "",
            comp,
            "",
            "---",
            "",
            bm,
            "",
            "---",
            "",
            "<!-- _class: lead -->",
            "",
            "# Thank You",
            f"**{team}**",
            "",
        ]
    )


def render_deck(artefacts_dir: Path, context: DeckContext | None = None) -> Path:
    """Compile the deck markdown, write it, and render to the best available format.

    Render order: Marp > pptx > HTML fallback.
    """
    from agent.render import best_renderer, detect_marp, render_html_deck, render_pptx_deck

    md_text = compile_deck_md(artefacts_dir, context)
    write_artefact(artefacts_dir, ARTEFACTS.DECK_MD, [md_text])

    renderer = best_renderer()
    if renderer == RenderMode.MARP:
        marp_path = detect_marp()
        deck_md_path = artefacts_dir / ARTEFACTS.DECK_MD
        try:
            subprocess.run(
                [
                    str(marp_path),
                    str(deck_md_path),
                    "-o",
                    str(artefacts_dir / ARTEFACTS.DECK_HTML),
                ],
                check=True,
                capture_output=True,
                timeout=60,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            log.warning("Marp HTML render failed: %s. Falling back.", exc)
            return render_html_deck(artefacts_dir, md_text)

        with suppress(subprocess.CalledProcessError, subprocess.TimeoutExpired):
            subprocess.run(
                [
                    str(marp_path),
                    str(deck_md_path),
                    "--pdf",
                    "-o",
                    str(artefacts_dir / ARTEFACTS.DECK_PDF),
                ],
                check=True,
                capture_output=True,
                timeout=60,
            )
        return artefacts_dir / ARTEFACTS.DECK_HTML

    if renderer == RenderMode.PPTX:
        return render_pptx_deck(artefacts_dir, md_text)

    return render_html_deck(artefacts_dir, md_text)
