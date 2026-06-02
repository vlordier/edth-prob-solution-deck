from __future__ import annotations

from pathlib import Path

import pytest

from agent.personas import PersonaError, list_personas, load_persona


def test_load_default_persona_passes(tmp_path: Path) -> None:
    d = tmp_path / "personas"
    d.mkdir()
    (d / "edth-judge.yaml").write_text(
        'name: "EDTH Judge"\nrole: "Senior evaluator"\nbackground: "20 years"\npriorities: ["impact"]\nanti_priorities: ["vague"]\ndecision_style: "direct"\nlanguage_patterns: ["show me"]\nconstraints: ["field in 12"]\n',
        encoding="utf-8",
    )
    p = load_persona(d, "edth-judge")
    assert p["name"] == "EDTH Judge"


def test_load_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(PersonaError, match="not found"):
        load_persona(tmp_path, "nonexistent")


def test_list_personas(tmp_path: Path) -> None:
    d = tmp_path / "personas"
    d.mkdir()
    (d / "a.yaml").write_text("name: A\n", encoding="utf-8")
    (d / "b.yaml").write_text("name: B\n", encoding="utf-8")
    assert sorted(list_personas(d)) == ["a", "b"]


def test_list_empty(tmp_path: Path) -> None:
    d = tmp_path / "personas"
    d.mkdir()
    assert list_personas(d) == []
