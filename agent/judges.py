"""Judge library loader."""
from __future__ import annotations
import logging
from pathlib import Path
from typing import Any
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
    return sorted(p.stem for p in judges_dir.glob("*.yaml") if p.stem.lower()!="readme")

def load_judge_library(judges_dir: Path) -> list[Judge]:
    out: list[Judge] = []
    for short in list_judges(judges_dir):
        try:
            out.append(load_judge(judges_dir, short))
        except (JudgeValidationError, FileNotFoundError, yaml.YAMLError) as exc:
            log.warning("Skipping invalid judge %s: %s", short, exc)
    return out
