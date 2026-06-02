"""Problem-owner persona loader."""
from __future__ import annotations
from pathlib import Path
from typing import Any
import yaml

class PersonaError(KeyError):
    pass

def load_persona(personas_dir: Path, short_name: str) -> dict[str, Any]:
    path = personas_dir / f"{short_name}.yaml"
    if not path.exists():
        raise PersonaError(f"Persona {short_name!r} not found at {path}")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def list_personas(personas_dir: Path) -> list[str]:
    if not personas_dir.exists():
        return []
    return sorted(p.stem for p in personas_dir.glob("*.yaml") if p.stem.lower() != "readme")
