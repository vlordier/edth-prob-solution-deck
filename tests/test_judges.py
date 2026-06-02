from __future__ import annotations

from pathlib import Path

import pytest

from agent.judge_schema import JudgeValidationError
from agent.judges import (
    add_judge,
    list_judges,
    list_judges_full,
    load_judge,
    load_judge_library,
    remove_judge,
    update_judge,
)


def _write(d: Path, s: str, n: str, tags: list[str]) -> None:
    d.mkdir(exist_ok=True)
    (d / f"{s}.yaml").write_text(
        f'name: "{n}"\nshort: "{s}"\ntags: {tags}\nbackground: "bg"\npriorities: ["p"]\nanti_priorities: ["ap"]\ndecision_style: "ds"\nlanguage_patterns: ["lp"]\nscoring_biases:\n  impact: 0.0\n  innovation: 0.0\n  execution: 0.0\n  presentation: 0.0\nknowledge_gaps: ["kg"]\nhard_questions_seed: ["hq"]\n',
        encoding="utf-8",
    )


def test_load_judge_returns_dict(tmp_path: Path) -> None:
    _write(tmp_path, "viper", "Maj.Viper", ["c-uas"])
    j = load_judge(tmp_path, "viper")
    assert j["short"] == "viper"
    assert j["tags"] == ["c-uas"]


def test_load_invalid_raises(tmp_path: Path) -> None:
    tmp_path.mkdir(exist_ok=True)
    (tmp_path / "bad.yaml").write_text("name:bad\n", encoding="utf-8")
    with pytest.raises((FileNotFoundError, JudgeValidationError)):
        load_judge(tmp_path, "bad")


def test_list_judges(tmp_path: Path) -> None:
    _write(tmp_path, "a", "A", [])
    _write(tmp_path, "b", "B", [])
    assert sorted(list_judges(tmp_path)) == ["a", "b"]


def test_load_library_all(tmp_path: Path) -> None:
    _write(tmp_path, "a", "A", [])
    _write(tmp_path, "b", "B", [])
    assert {j["short"] for j in load_judge_library(tmp_path)} == {"a", "b"}


def test_load_library_skips_bad(tmp_path: Path) -> None:
    _write(tmp_path, "a", "A", [])
    (tmp_path / "bad.yaml").write_text("name:bad\n", encoding="utf-8")
    assert [j["short"] for j in load_judge_library(tmp_path)] == ["a"]


def test_select_panel_returns_five(tmp_path: Path) -> None:
    from agent.judges import select_panel

    _write(tmp_path, "tech", "Tech", ["all"])
    _write(tmp_path, "mil", "Mil", ["c-uas"])
    _write(tmp_path, "ew", "EW", ["ew"])
    _write(tmp_path, "ethics", "Ethics", ["autonomy"])
    _write(tmp_path, "ux", "UX", ["c2"])
    panel = select_panel(tmp_path, themes=["c-uas"], tags=["software"])
    assert len(panel) == 5
    assert any(j["short"] == "tech" for j in panel)


def test_select_includes_ethics_for_autonomy(tmp_path: Path) -> None:
    from agent.judges import select_panel

    for s in [
        ("tech", "Tech", ["all"]),
        ("ethics", "Ethics", ["autonomy"]),
        ("ux", "UX", ["c2"]),
        ("red", "Red", ["c-uas"]),
        ("end", "End", ["c-uas"]),
    ]:
        _write(tmp_path, *s)
    panel = select_panel(tmp_path, themes=["autonomy"], tags=[])
    assert any(j["short"] == "ethics" for j in panel) and any(j["short"] == "tech" for j in panel)


def test_select_includes_red_team_for_ew(tmp_path: Path) -> None:
    from agent.judges import select_panel

    for s in [
        ("tech", "Tech", ["all"]),
        ("red", "Red", ["ew"]),
        ("tran", "Tran", ["ew"]),
        ("intel", "Intel", ["ew"]),
        ("acq", "Acq", ["all"]),
    ]:
        _write(tmp_path, *s)
    panel = select_panel(tmp_path, themes=["ew"], tags=[])
    assert any(j["short"] == "red" for j in panel) and any(j["short"] == "tech" for j in panel)


# ── CRUD tests ──


def _full_judge(short: str, name: str, tags: list[str] | None = None) -> dict:
    return {
        "name": name,
        "short": short,
        "tags": tags or ["all"],
        "background": "Experienced in this domain.",
        "priorities": ["accuracy", "speed"],
        "anti_priorities": ["hand-waving"],
        "decision_style": "thorough",
        "language_patterns": ["prove it"],
        "scoring_biases": {
            "impact": 0.05,
            "innovation": 0.0,
            "execution": 0.05,
            "presentation": 0.0,
        },
        "knowledge_gaps": ["consumer_tech"],
        "hard_questions_seed": ["What's the failure mode?"],
    }


def test_add_judge_creates_file(tmp_path: Path) -> None:

    data = _full_judge("custom-judge", "Custom Judge")
    result = add_judge(tmp_path, data)
    assert result["short"] == "custom-judge"
    assert (tmp_path / "custom-judge.yaml").exists()


def test_add_judge_rejects_duplicate(tmp_path: Path) -> None:

    data = _full_judge("dup", "Duplicate")
    add_judge(tmp_path, data)
    with pytest.raises(FileExistsError):
        add_judge(tmp_path, data)


def test_add_judge_rejects_reserved_short(tmp_path: Path) -> None:

    data = _full_judge("readme", "Reserved")
    with pytest.raises(ValueError, match="reserved"):
        add_judge(tmp_path, data)


def test_update_judge_backs_up_and_writes(tmp_path: Path) -> None:

    add_judge(tmp_path, _full_judge("up", "Update Me"))
    updated = update_judge(tmp_path, "up", {"name": "Updated Name", "background": "New bg"})
    assert updated["name"] == "Updated Name"
    assert updated["background"] == "New bg"
    # Backup should exist
    backup_dir = tmp_path / "backups"
    assert backup_dir.exists()
    baks = list(backup_dir.glob("up.yaml.bak.*"))
    assert len(baks) >= 1


def test_remove_judge_moves_to_backup(tmp_path: Path) -> None:

    add_judge(tmp_path, _full_judge("rm", "Remove Me"))
    assert (tmp_path / "rm.yaml").exists()
    remove_judge(tmp_path, "rm")
    assert not (tmp_path / "rm.yaml").exists()
    removed = list((tmp_path / "backups").glob("rm.yaml.removed.*"))
    assert len(removed) == 1


def test_list_judges_full_includes_custom_flag(tmp_path: Path) -> None:

    add_judge(tmp_path, _full_judge("full", "Full Test"))
    lst = list_judges_full(tmp_path)
    assert any(j["short"] == "full" for j in lst)
