"""Judge library loader."""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from agent.judge_schema import Judge, JudgeValidationError, validate_judge

log = logging.getLogger(__name__)


def load_judge(judges_dir: Path, short_name: str) -> Judge:
    path = judges_dir / f"{short_name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Judge {short_name!r} not found")
    with path.open("r", encoding="utf-8") as f:
        return validate_judge(yaml.safe_load(f) or {})


def list_judges(judges_dir: Path) -> list[str]:
    if not judges_dir.exists():
        return []
    return sorted(p.stem for p in judges_dir.glob("*.yaml") if p.stem.lower() != "readme")


def load_judge_library(judges_dir: Path) -> list[Judge]:
    out: list[Judge] = []
    for short in list_judges(judges_dir):
        try:
            out.append(load_judge(judges_dir, short))
        except (JudgeValidationError, FileNotFoundError, yaml.YAMLError) as exc:
            log.warning("Skipping invalid judge %s: %s", short, exc)
    return out


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def select_panel(
    judges_dir: Path, themes: list[str], tags: list[str], *, panel_size: int = 5
) -> list[Judge]:
    """Auto-select a panel of judges for a given problem using Jaccard similarity + hard rules."""
    library = load_judge_library(judges_dir)
    if not library:
        return []
    problem_set = set(themes) | set(tags)
    scored = sorted(
        [(_jaccard(problem_set, set(j.get("tags", []))), j) for j in library],
        key=lambda x: (-x[0], x[1]["short"]),
    )
    must_have: list[str] = []
    if any(t in themes for t in ("autonomy",)):
        must_have.append("ethics-compliance")
    if any(t in themes for t in ("ew", "electronic_warfare")):
        must_have.append("red-team-adversary")
    if any(t in themes for t in ("c2", "decision_support")):
        must_have.append("operator-ux")
    if "software" in tags:
        must_have.append("scaling-engineer")
    must_have.append("technical-skeptic")

    panel: list[Judge] = []
    seen: set[str] = set()

    def _try_add(short: str) -> None:
        for j in library:
            if j["short"] == short and short not in seen:
                panel.append(j)
                seen.add(short)
                return

    for short in must_have:
        _try_add(short)
        if len(panel) >= panel_size:
            break

    for _, j in scored:
        if j["short"] in seen:
            continue
        if len(panel) >= panel_size:
            break
        panel.append(j)
        seen.add(j["short"])

    return panel
