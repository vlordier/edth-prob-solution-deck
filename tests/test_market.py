from __future__ import annotations

from pathlib import Path

from agent.market import write_business_model, write_competition, write_market


def test_write_market(tmp_path: Path) -> None:
    write_market(tmp_path, "$12B", "$3B", "$150M", "15% CAGR.", ["PM", "PEO", "JTAC"])
    raw = (tmp_path / "07_market.md").read_text()
    assert "$12B" in raw
    assert "15% CAGR" in raw


def test_write_competition(tmp_path: Path) -> None:
    write_competition(tmp_path, [("Anduril", "Lattice", "Heavy", "Edge")], ["Edge models"])
    raw = (tmp_path / "07_competition.md").read_text()
    assert "Anduril" in raw
    assert "Edge models" in raw


def test_write_business_model(tmp_path: Path) -> None:
    write_business_model(tmp_path, "SaaS", "Tiered", "SBIR", "Switching cost")
    raw = (tmp_path / "07_business_model.md").read_text()
    assert "SaaS" in raw
    assert "SBIR" in raw
