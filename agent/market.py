"""Phase 7 — Market, competition, and business model artefact writers."""

from __future__ import annotations

import logging
from pathlib import Path

from agent._constants import ARTEFACTS
from agent._util import write_artefact

log = logging.getLogger(__name__)


def write_market(
    artefacts_dir: Path, tam: str, sam: str, som: str, trends: str, personas: list[str]
) -> Path:
    """Write `07_market.md` — market size, growth trends, and buyer personas."""
    lines = [
        "# Market Research",
        "",
        "## Market Size",
        "",
        f"- **TAM:** {tam or '(not estimated)'}",
        f"- **SAM:** {sam or '(not estimated)'}",
        f"- **SOM:** {som or '(not estimated)'}",
        "",
        "## Growth & Trends",
        "",
        trends or "(not researched)",
        "",
        "## Buyer Personas",
        "",
    ]
    for i, p in enumerate(personas, start=1):
        lines.append(f"{i}. {p}")
    lines.append("")
    return write_artefact(artefacts_dir, ARTEFACTS.MARKET, lines)


def write_competition(
    artefacts_dir: Path, competitors: list[tuple[str, str, str, str]], moat: list[str]
) -> Path:
    """Write `07_competition.md` — competitor table and defensive moat analysis."""
    lines = [
        "# Competition Analysis",
        "",
        "## Direct Competitors",
        "",
        "| Competitor | Strength | Weakness | Our Edge |",
        "|---|---|---|---|",
    ]
    for entry in competitors:
        if len(entry) != 4:
            log.warning("Skipping malformed competitor entry: %r", entry)
            continue
        name, strength, weakness, edge = entry
        lines.append(f"| {name} | {strength} | {weakness} | {edge} |")
    lines.append("")
    lines.append("## Moat")
    lines.append("")
    for i, m in enumerate(moat, start=1):
        lines.append(f"{i}. {m}")
    lines.append("")
    return write_artefact(artefacts_dir, ARTEFACTS.COMPETITION, lines)


def write_business_model(
    artefacts_dir: Path, revenue: str, pricing: str, gtm: str, defensibility: str
) -> Path:
    """Write `07_business_model.md` — revenue, pricing, GTM, and defensibility."""
    lines = [
        "# Business Model",
        "",
        "## Revenue Model",
        "",
        revenue or "(not specified)",
        "",
        "## Pricing",
        "",
        pricing or "(not specified)",
        "",
        "## Go-to-Market",
        "",
        gtm or "(not specified)",
        "",
        "## Defensibility",
        "",
        defensibility or "(not specified)",
        "",
    ]
    return write_artefact(artefacts_dir, ARTEFACTS.BUSINESS_MODEL, lines)
