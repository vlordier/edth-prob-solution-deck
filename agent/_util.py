"""Shared utility helpers used across agent modules.

Extracts repeated patterns: artefact file writing, JSON loading, file slurping,
Jaccard similarity, and timestamp formatting.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)


def now_iso() -> str:
    """ISO 8601 timestamp string in UTC, seconds precision."""
    return datetime.now(UTC).isoformat(timespec="seconds")


def write_artefact(artefacts_dir: Path, filename: str, lines: list[str]) -> Path:
    """Write an artefact markdown file into artefacts_dir.

    Creates the directory if missing. Logs and re-raises OSError on failure.
    Returns the written file path.
    """
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    path = artefacts_dir / filename
    try:
        path.write_text("\n".join(lines), encoding="utf-8")
    except OSError as exc:
        log.error("Failed to write %s: %s", path, exc)
        raise
    return path


def load_json_safe(path: Path) -> dict[str, Any]:
    """Load a JSON file, returning an empty dict on any error.

    Safe for files that may be missing, malformed, or unreadable.
    """
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def slurp_file(artefacts_dir: Path, filename: str) -> str:
    """Read a text file under artefacts_dir. Returns empty string if missing."""
    path = artefacts_dir / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def tokens(text: str, min_length: int = 3) -> set[str]:
    """Return lowercase word tokens from text, filtering short words."""
    return {t.lower() for t in text.split() if len(t) >= min_length}


def jaccard_similarity(a: str | set[str], b: str | set[str]) -> float:
    """Jaccard similarity between two strings or token sets.

    Strings are tokenized before comparison. Returns 0.0-1.0.
    """
    ta = tokens(a) if isinstance(a, str) else a
    tb = tokens(b) if isinstance(b, str) else b
    if not ta and not tb:
        return 1.0
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)
