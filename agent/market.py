"""Phase 7 — Market, competition, and business model artefact writers."""

from __future__ import annotations

from pathlib import Path


def write_market(
    artefacts_dir: Path, tam: str, sam: str, som: str, trends: str, personas: list[str]
) -> Path:
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Market Research",
        "",
        "## Market Size",
        "",
        f"- **TAM:** {tam}",
        f"- **SAM:** {sam}",
        f"- **SOM:** {som}",
        "",
        "## Growth & Trends",
        "",
        trends,
        "",
        "## Buyer Personas",
        "",
    ]
    for i, p in enumerate(personas, start=1):
        lines.append(f"{i}. {p}")
    lines.append("")
    path = artefacts_dir / "07_market.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_competition(
    artefacts_dir: Path, competitors: list[tuple[str, str, str, str]], moat: list[str]
) -> Path:
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Competition Analysis",
        "",
        "## Direct Competitors",
        "",
        "| Competitor | Strength | Weakness | Our Edge |",
        "|---|---|---|---|",
    ]
    for name, strength, weakness, edge in competitors:
        lines.append(f"| {name} | {strength} | {weakness} | {edge} |")
    lines.append("")
    lines.append("## Moat")
    lines.append("")
    for i, m in enumerate(moat, start=1):
        lines.append(f"{i}. {m}")
    lines.append("")
    path = artefacts_dir / "07_competition.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_business_model(
    artefacts_dir: Path, revenue: str, pricing: str, gtm: str, defensibility: str
) -> Path:
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Business Model",
        "",
        "## Revenue Model",
        "",
        revenue,
        "",
        "## Pricing",
        "",
        pricing,
        "",
        "## Go-to-Market",
        "",
        gtm,
        "",
        "## Defensibility",
        "",
        defensibility,
        "",
    ]
    path = artefacts_dir / "07_business_model.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
