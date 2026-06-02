"""Environment doctor — comprehensive pre-run verification.

Raise errors early, with actionable fix suggestions, before any phase
work begins. Called implicitly by `/edth-agent run` before starting.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Map of check function to name for reporting
_CHECKS: list[tuple[str, callable]] = []


def register(name: str):
    """Decorator to register a check function."""

    def deco(fn):
        _CHECKS.append((name, fn))
        return fn

    return deco


def run_doctor(artefacts_dir: Path) -> tuple[bool, list[str]]:
    """Run all environment checks. Returns (all_pass, issues_list)."""
    issues: list[str] = []
    for name, fn in _CHECKS:
        try:
            result = fn()
            if result:
                issues.append(f"{name}: {result}")
        except Exception as exc:
            issues.append(f"{name}: unexpected error — {exc}")
    return len(issues) == 0, issues


@register("Python version (≥3.12)")
def _check_python() -> str | None:
    if sys.version_info < (3, 12):
        return (
            f"Python {sys.version_info.major}.{sys.version_info.minor} detected. "
            "Install Python 3.12+ from https://python.org. "
            "macOS: brew install python@3.13  |  Linux: sudo apt install python3.13  |  Windows: winget install Python.Python.3.13"
        )
    return None


@register("agent package importable")
def _check_agent_import() -> str | None:
    try:
        import agent  # noqa: F401
    except ImportError:
        return "agent package not found. Run: uv sync --all-groups"
    return None


@register("Required dependencies")
def _check_deps() -> str | None:
    missing = []
    for dep in ("pyyaml", "pptx"):
        try:
            __import__(dep)
        except ImportError:
            missing.append(dep)
    if missing:
        return f"Missing dependencies: {', '.join(missing)}. Run: uv sync --all-groups"
    return None


@register("Sample CSV available")
def _check_csv() -> str | None:
    repo_root = Path(__file__).resolve().parent.parent
    csv_paths = [
        repo_root / "input" / "PB-SOL-EDTH - Sheet1.csv",
        repo_root / "input" / "sample-problems.csv",
    ]
    for p in csv_paths:
        if p.exists():
            return None
    return (
        "No input CSV found. Drop a CSV with columns 'Name' and 'Problem statement' "
        "into input/ and update artefacts/00_context.yaml."
    )


@register("artefacts directory writable")
def _check_artefacts_dir() -> str | None:
    import tempfile

    repo_root = Path(__file__).parent.parent
    artefacts = repo_root / "artefacts"
    try:
        artefacts.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=artefacts, delete=True) as f:
            f.write(b"test")
    except OSError as e:
        return f"Cannot write to artefacts/ directory: {e}"
    return None


@register("Judge library loadable")
def _check_judges() -> str | None:
    try:
        from agent.judges import load_judge_library

        repo_root = Path(__file__).parent.parent
        lib = load_judge_library(repo_root / "judges")
        if len(lib) < 2:
            return (
                f"Only {len(lib)} judges loaded (expected ≥2). "
                "Check judges/*.yaml files for syntax errors."
            )
    except Exception as e:
        return f"Judge library failed to load: {e}"
    return None


@register("Persona default available")
def _check_persona() -> str | None:
    try:
        from agent.personas import load_persona

        repo_root = Path(__file__).parent.parent
        load_persona(repo_root / "personas", "edth-judge")
    except Exception as e:
        return f"Default persona failed to load: {e}"
    return None


@register("Shell tools (marp/graphviz optional)")
def _check_shell_tools() -> str | None:
    import shutil

    missing = []
    if not shutil.which("marp"):
        missing.append("marp (optional — install for PDF output: npm i -g @marp-team/marp-cli)")
    return ("Optional tools missing: " + "; ".join(missing)) if missing else None
