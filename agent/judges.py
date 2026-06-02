"""Judge library loader, CRUD, and auto-selection."""

from __future__ import annotations

import logging
import shutil
from datetime import UTC
from pathlib import Path

import yaml

from agent.judge_schema import Judge, JudgeValidationError, validate_judge

log = logging.getLogger(__name__)

_CUSTOM_FILE = "custom.yaml"
_RESERVED_SHORTS = {"readme"}
_BACKUP_DIR = "backups"


def _is_custom(judges_dir: Path, short_name: str) -> bool:
    """Check if a judge is a user-created custom one (in custom.yaml)."""
    return _CUSTOM_FILE in str(_path_for(judges_dir, short_name))


def _path_for(judges_dir: Path, short_name: str) -> Path:
    return judges_dir / f"{short_name}.yaml"


def load_judge(judges_dir: Path, short_name: str) -> Judge:
    path = _path_for(judges_dir, short_name)
    if not path.exists():
        raise FileNotFoundError(f"Judge {short_name!r} not found")
    with path.open("r", encoding="utf-8") as f:
        return validate_judge(yaml.safe_load(f) or {})


def list_judges(judges_dir: Path) -> list[str]:
    if not judges_dir.exists():
        return []
    return sorted(
        p.stem for p in judges_dir.glob("*.yaml") if p.stem.lower() not in _RESERVED_SHORTS
    )


def load_judge_library(judges_dir: Path) -> list[Judge]:
    out: list[Judge] = []
    for short in list_judges(judges_dir):
        try:
            out.append(load_judge(judges_dir, short))
        except (JudgeValidationError, FileNotFoundError, yaml.YAMLError) as exc:
            log.warning("Skipping invalid judge %s: %s", short, exc)
    return out


def add_judge(judges_dir: Path, data: dict) -> Judge:
    """Create a new judge YAML file. Validates before writing.

    Args:
        judges_dir: Path to the judges/ directory.
        data: Dict conforming to the Judge YAML schema. Must include 'short'.

    Returns:
        The validated Judge dict.

    Raises:
        JudgeValidationError: if the data doesn't validate.
        FileExistsError: if a judge with this short name already exists.
        ValueError: if 'short' is missing or reserved.
    """
    short = data.get("short", "").strip()
    if not short:
        raise ValueError("Judge must have a 'short' name")
    if short.lower() in _RESERVED_SHORTS:
        raise ValueError(f"'{short}' is a reserved name — pick another")

    validated = validate_judge(data)
    path = _path_for(judges_dir, short)
    if path.exists():
        raise FileExistsError(f"Judge {short!r} already exists at {path}")

    judges_dir.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(dict(validated), f, sort_keys=False, default_flow_style=False)
    return validated


def update_judge(judges_dir: Path, short_name: str, data: dict) -> Judge:
    """Update an existing judge. Merges provided fields over the existing YAML.

    The existing file is backed up to judges/backups/<short>.yaml.bak.<timestamp>.

    Args:
        judges_dir: Path to the judges/ directory.
        short_name: The judge's short identifier.
        data: Dict of fields to update. Merged over the existing judge's data.

    Returns:
        The updated Judge dict.

    Raises:
        FileNotFoundError: if the judge doesn't exist.
        JudgeValidationError: if the merged data doesn't validate.
    """
    path = _path_for(judges_dir, short_name)
    if not path.exists():
        raise FileNotFoundError(f"Judge {short_name!r} not found at {path}")

    # Back up
    backup_dir = judges_dir / _BACKUP_DIR
    backup_dir.mkdir(parents=True, exist_ok=True)
    from datetime import datetime

    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    shutil.copy2(path, backup_dir / f"{short_name}.yaml.bak.{ts}")

    # Load existing, merge, validate, save
    with path.open("r", encoding="utf-8") as f:
        existing = yaml.safe_load(f) or {}
    merged = {**existing, **data}
    # 'short' must remain the filename
    merged["short"] = short_name
    validated = validate_judge(merged)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(dict(validated), f, sort_keys=False, default_flow_style=False)
    return validated


def remove_judge(judges_dir: Path, short_name: str) -> None:
    """Remove a judge YAML file with a safe rename instead of deletion.

    The file is moved to judges/backups/<short>.yaml.removed.<timestamp>
    rather than being permanently deleted.

    Raises:
        FileNotFoundError: if the judge doesn't exist.
    """
    path = _path_for(judges_dir, short_name)
    if not path.exists():
        raise FileNotFoundError(f"Judge {short_name!r} not found at {path}")

    backup_dir = judges_dir / _BACKUP_DIR
    backup_dir.mkdir(parents=True, exist_ok=True)
    from datetime import datetime

    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    path.rename(backup_dir / f"{short_name}.yaml.removed.{ts}")


def list_judges_full(judges_dir: Path) -> list[dict]:
    """List all judges with metadata: name, short, tags, custom flag, file path."""
    out = []
    for short in list_judges(judges_dir):
        try:
            j = load_judge(judges_dir, short)
            out.append(
                {
                    "short": j["short"],
                    "name": j["name"],
                    "tags": j.get("tags", []),
                    "custom": _is_custom(judges_dir, short),
                    "background": j.get("background", "")[:120],
                }
            )
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
