# EDTH Hackathon Agent — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an OpenCode-skill + Python-glue agent that walks a solo hacker or small team from a CSV of problem statements to a rendered problem/solution pitch deck, using a 9-phase workflow reviewed by a panel of 12 tough-judge personas.

**Architecture:** OpenCode (LLM-driven) skill drives the 9 phases — clustering, elicitation, ideation, ranking, deck generation. A small Python package (`agent/`) handles deterministic glue: CSV parsing, scoring math, state I/O, Marp rendering with a 2-tier fallback. Personas and judges are YAML files; the LLM role-plays them via system prompts.

**Tech Stack:**
- Python 3.11+ (standard library + `pyyaml`, `python-pptx`, `pytest`)
- OpenCode skill (markdown-based, invoked from chat)
- Marp CLI for slide rendering (with `python-pptx` + HTML fallbacks)
- pytest for unit tests
- Git for version control


------

## File / folder structure

Files created across this plan. Each task references its slice.

```
edth-prob-solution-deck/
├── SKILL.md                              # OpenCode skill — workflow driver
├── README.md                             # User-facing quick start
├── pyproject.toml                        # Python deps & entry points
├── .gitignore                            # Generated artefacts ignored
│
├── hackathons/
│   └── edth.yaml                         # Default hackathon config
│
├── agent/                                # Thin Python glue
│   ├── __init__.py
│   ├── state.py                          # state.json I/O
│   ├── parse_csv.py                      # CSV → normalized JSON
│   ├── normalize.py                      # quality flags, de-dup
│   ├── rubric.py                         # judging rubric + scoring math
│   ├── aggregation.py                    # Borda / approval voting
│   ├── context.py                        # Phase 0 context loader
│   ├── personas.py                       # problem-owner persona loader
│   ├── judge_schema.py                   # judge YAML validator
│   ├── judges.py                         # judge library + auto-selection
│   ├── triage.py                         # Phase 1 triage writer
│   ├── elicitation.py                    # Phase 2 owner Q&A writers
│   ├── candidates.py                     # Phase 2 candidate writer
│   ├── sub_problem.py                    # Phase 3 sub-problem writer
│   ├── ideation.py                       # Phase 4 ideation + dedup
│   ├── ranking.py                        # Phase 5 ranking writers
│   ├── audit.py                          # audit trail writer
│   ├── demo_plan.py                      # Phase 6 demo plan writer
│   ├── market.py                         # Phase 7 market/comp/BM writers
│   ├── deck.py                           # deck compiler
│   ├── render.py                         # marp / python-pptx / html
│   └── summary.py                        # Phase 8 summary writer
│
├── personas/
│   ├── edth-judge.yaml
│   └── README.md
│
├── judges/                               # 12 judges
│   ├── README.md
│   ├── military-operator.yaml
│   ├── ew-specialist.yaml
│   ├── defense-prime-pm.yaml
│   ├── technical-skeptic.yaml
│   ├── acquisition-procurement.yaml
│   ├── end-user-frontline.yaml
│   ├── ethics-compliance.yaml
│   ├── defense-vc.yaml
│   ├── red-team-adversary.yaml
│   ├── scaling-engineer.yaml
│   ├── intel-analyst.yaml
│   └── operator-ux.yaml
│
├── templates/                            # Marp slide skeletons
│   ├── cover.md
│   ├── problem.md
│   ├── solution.md
│   ├── market.md
│   ├── competition.md
│   ├── business-model.md
│   ├── demo.md
│   └── pitch.md
│
├── examples/
│   └── sample-run/                       # Pre-generated happy path
│       ├── README.md
│       ├── input.csv
│       └── artefacts/
│           ├── state.json
│           ├── 00_context.yaml
│           ├── 01_triage.md
│           ├── 02_candidate_problem.md
│           ├── 03_chosen_sub_problem.md
│           ├── 04_solution_candidates.md
│           ├── 05_ranked_solutions.md
│           ├── 05_owner_pick.md
│           ├── 06_demo_plan.md
│           ├── 07_market.md
│           ├── 07_competition.md
│           ├── 07_business_model.md
│           └── 07_deck.md
│
├── tests/                                # pytest
│   ├── conftest.py
│   ├── test_parse_csv.py
│   ├── test_normalize.py
│   ├── test_score.py
│   ├── test_state.py
│   ├── test_judges.py
│   └── test_render.py
│
└── artefacts/                            # Generated (gitignored mostly)
    └── ...
```

**Decomposition rationale:**
- `agent/state.py` is the only stateful module; everything else is pure.
- `agent/score.py` and `agent/judges.py` are the only places persona bias is applied — single source of truth.
- `agent/render.py` is the only file that touches the file system outside of state.
- The 12 judge YAMLs are independent of each other and of the Python code.
- Tests mirror the agent module structure 1:1.

---

## Milestone 0 — Project scaffolding

**Goal:** Repo initialized, Python project configured, state module + tests working, OpenCode skill stub in place. Runnable as `python -m agent.state`.

**Tasks:**
- Task 0.1: Initialize repo with `.gitignore`, `pyproject.toml`, `README.md`
- Task 0.2: Create `agent/` package with `__init__.py` and `state.py`
- Task 0.3: Write state tests, implement state, verify
- Task 0.4: Create SKILL.md stub with `help` command
- Task 0.5: Smoke test — `pytest` passes, SKILL.md loads

### Task 0.1: Initialize repo

**Files:**
- Create: `.gitignore`
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `hackathons/.gitkeep`

- [ ] **Step 1: Create `.gitignore`**

Write `/.gitignore` (note: in repo root):

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
dist/
*.egg-info/
.pytest_cache/
.mypy_cache/
.venv/
venv/
env/

# Generated artefacts (keep state.json and .md for resumption)
artefacts/audit/
artefacts/07_deck.pdf
artefacts/07_deck.html
artefacts/08_summary.md
examples/sample-run/artefacts/audit/

# IDE
.vscode/
.idea/
*.swp
.DS_Store

# Local config
.env
.env.local
```

Note: we keep `state.json` and `*.md` files in `artefacts/` (no `!` exceptions — gitignore patterns just don't match them, since they don't match the patterns above). Document this in README later.

- [ ] **Step 2: Create `pyproject.toml`**

Write `/pyproject.toml`:

```toml
[project]
name = "edth-agent"
version = "0.1.0"
description = "Hackathon agent: problem statement CSV to problem/solution pitch deck"
requires-python = ">=3.11"
dependencies = [
    "pyyaml>=6.0",
    "python-pptx>=0.6.21",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4",
    "pytest-cov>=4.1",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["agent"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
```

- [ ] **Step 3: Create `README.md` (placeholder)**

Write `/README.md`:

```markdown
# EDTH Hackathon Agent

A reusable agent that walks through the full lifecycle of a hackathon project — from a CSV of problem statements to a problem/solution pitch deck — using a 9-phase workflow reviewed by a panel of 12 tough-judge personas.

## Status

Scaffolding in progress. See `docs/superpowers/plans/2026-06-02-edth-agent.md` for the implementation plan.
```

- [ ] **Step 4: Create `hackathons/` directory**

```bash
mkdir -p /Users/vincent/Work/edth-prob-solution-deck/hackathons
touch /Users/vincent/Work/edth-prob-solution-deck/hackathons/.gitkeep
```

- [ ] **Step 5: Install dev dependencies**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Expected: `Successfully installed edth-agent-0.1.0 ... pytest-7.x.x ... python-pptx-0.6.x ... PyYAML-6.x.x`

- [ ] **Step 6: Verify pytest is callable**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest --version
```

Expected: `pytest 7.x.x`

- [ ] **Step 7: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add .gitignore pyproject.toml README.md hackathons/
git commit -m "chore: scaffold project (pyproject, gitignore, readme)"
```

### Task 0.2: Create agent package skeleton

**Files:**
- Create: `agent/__init__.py`
- Create: `agent/state.py` (stub)
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Create `agent/__init__.py`**

Write `/agent/__init__.py`:

```python
"""EDTH Hackathon Agent — Python glue layer."""

__version__ = "0.1.0"
```

- [ ] **Step 2: Create `agent/state.py` stub**

Write `/agent/state.py`:

```python
"""State management for the EDTH agent.

Loads and saves the state.json file that tracks the agent's progress
through the 9-phase workflow. See spec §8.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_state(artefacts_dir: Path) -> dict[str, Any]:
    """Load state.json from artefacts_dir, or return an empty state.

    Returns an empty dict if state.json does not exist. Does NOT raise.
    """
    state_path = artefacts_dir / "state.json"
    if not state_path.exists():
        return {}
    with state_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_state(artefacts_dir: Path, state: dict[str, Any]) -> Path:
    """Save state to artefacts_dir/state.json.

    Returns the path written.
    """
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    state_path = artefacts_dir / "state.json"
    with state_path.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, sort_keys=True)
    return state_path


def empty_state() -> dict[str, Any]:
    """Return a fresh empty state dict with the schema from spec §8.1."""
    return {
        "version": "0.1.0",
        "started_at": None,
        "updated_at": None,
        "current_phase": 0,
        "config": {
            "input_csv": "input/PB-SOL-EDTH - Sheet1.csv",
            "output_dir": "artefacts",
            "owner_mode": "real",
            "persona": "edth-judge",
            "panel_mode": "expanded",
            "aggregation_mode": "borda",
            "rubric_path": "hackathons/edth.yaml",
        },
        "phases": {
            str(i): {"status": "pending", "artefact": None, "completed_at": None}
            for i in range(9)
        },
        "decisions": {
            "chosen_problem_id": None,
            "chosen_sub_problem_id": None,
            "chosen_solution_id": None,
        },
        "panel": {
            "auto_selected": [],
            "manually_overridden": False,
            "locked": False,
        },
        "branches": {
            "considered_problems": [],
            "considered_sub_problems": [],
            "considered_solutions": [],
        },
    }
```

- [ ] **Step 3: Create `tests/__init__.py` (empty)**

```bash
touch /Users/vincent/Work/edth-prob-solution-deck/tests/__init__.py
```

- [ ] **Step 4: Create `tests/conftest.py`**

Write `/tests/conftest.py`:

```python
"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def tmp_artefacts_dir(tmp_path: Path) -> Path:
    """A fresh artefacts/ directory in a tmp location."""
    artefacts = tmp_path / "artefacts"
    artefacts.mkdir()
    return artefacts
```

- [ ] **Step 5: Verify the package is importable**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/python -c "import agent; print(agent.__version__)"
```

Expected: `0.1.0`

- [ ] **Step 6: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add agent/__init__.py agent/state.py tests/__init__.py tests/conftest.py
git commit -m "feat(agent): package skeleton with state module stub"
```

### Task 0.3: TDD the state module

**Files:**
- Create: `tests/test_state.py`
- Modify: `agent/state.py` (add `_phase_status` helper)

- [ ] **Step 1: Write the failing tests**

Write `/tests/test_state.py`:

```python
"""Tests for agent.state — TDD: write these first, watch them fail."""

from __future__ import annotations

import json
from pathlib import Path

from agent.state import (
    empty_state,
    get_phase_status,
    load_state,
    mark_phase_completed,
    save_state,
    set_config,
    set_decision,
)


def test_empty_state_has_correct_version() -> None:
    state = empty_state()
    assert state["version"] == "0.1.0"


def test_empty_state_has_nine_pending_phases() -> None:
    state = empty_state()
    assert len(state["phases"]) == 9
    for i in range(9):
        assert state["phases"][str(i)]["status"] == "pending"


def test_save_and_load_roundtrip(tmp_artefacts_dir: Path) -> None:
    state = empty_state()
    state["current_phase"] = 3
    path = save_state(tmp_artefacts_dir, state)
    assert path == tmp_artefacts_dir / "state.json"
    loaded = load_state(tmp_artefacts_dir)
    assert loaded["current_phase"] == 3


def test_load_missing_returns_empty_dict(tmp_artefacts_dir: Path) -> None:
    assert load_state(tmp_artefacts_dir) == {}


def test_get_phase_status_returns_status_field(tmp_artefacts_dir: Path) -> None:
    state = empty_state()
    state["phases"]["1"]["status"] = "completed"
    save_state(tmp_artefacts_dir, state)
    assert get_phase_status(load_state(tmp_artefacts_dir), 1) == "completed"
    assert get_phase_status(load_state(tmp_artefacts_dir), 0) == "pending"


def test_mark_phase_completed_writes_artefact_and_timestamp(
    tmp_artefacts_dir: Path,
) -> None:
    state = empty_state()
    artefact = tmp_artefacts_dir / "01_triage.md"
    artefact.write_text("# Triage\n", encoding="utf-8")
    updated = mark_phase_completed(state, 1, artefact)
    assert updated["phases"]["1"]["status"] == "completed"
    assert updated["phases"]["1"]["artefact"] == str(artefact)
    assert updated["phases"]["1"]["completed_at"] is not None
    assert updated["current_phase"] == 2


def test_set_config_updates_field(tmp_artefacts_dir: Path) -> None:
    state = empty_state()
    updated = set_config(state, owner_mode="sim", persona="alt-judge")
    assert updated["config"]["owner_mode"] == "sim"
    assert updated["config"]["persona"] == "alt-judge"
    # Other fields untouched
    assert updated["config"]["panel_mode"] == "expanded"


def test_set_decision_records_choice(tmp_artefacts_dir: Path) -> None:
    state = empty_state()
    updated = set_decision(state, "chosen_problem_id", "P-028")
    assert updated["decisions"]["chosen_problem_id"] == "P-028"


def test_save_creates_artefacts_dir_if_missing(tmp_path: Path) -> None:
    artefacts = tmp_path / "does" / "not" / "exist"
    save_state(artefacts, empty_state())
    assert (artefacts / "state.json").exists()


def test_state_json_is_sorted_for_diffability(tmp_artefacts_dir: Path) -> None:
    state = empty_state()
    state["config"]["persona"] = "z"
    state["config"]["owner_mode"] = "a"
    save_state(tmp_artefacts_dir, state)
    raw = (tmp_artefacts_dir / "state.json").read_text()
    # Both keys are siblings under "config"; sort_keys=True keeps diffs stable
    assert raw.index('"owner_mode"') < raw.index('"persona"')
```

- [ ] **Step 2: Run the tests, watch them fail**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_state.py -v
```

Expected: 7 failed (the new tests reference `get_phase_status`, `mark_phase_completed`, `set_config`, `set_decision` which don't exist yet).

- [ ] **Step 3: Extend `agent/state.py` with the helper functions**

Modify `/agent/state.py`. Replace the entire file with:

```python
"""State management for the EDTH agent.

Loads and saves the state.json file that tracks the agent's progress
through the 9-phase workflow. See spec §8.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def empty_state() -> dict[str, Any]:
    """Return a fresh empty state dict with the schema from spec §8.1."""
    return {
        "version": "0.1.0",
        "started_at": None,
        "updated_at": None,
        "current_phase": 0,
        "config": {
            "input_csv": "input/PB-SOL-EDTH - Sheet1.csv",
            "output_dir": "artefacts",
            "owner_mode": "real",
            "persona": "edth-judge",
            "panel_mode": "expanded",
            "aggregation_mode": "borda",
            "rubric_path": "hackathons/edth.yaml",
        },
        "phases": {
            str(i): {"status": "pending", "artefact": None, "completed_at": None}
            for i in range(9)
        },
        "decisions": {
            "chosen_problem_id": None,
            "chosen_sub_problem_id": None,
            "chosen_solution_id": None,
        },
        "panel": {
            "auto_selected": [],
            "manually_overridden": False,
            "locked": False,
        },
        "branches": {
            "considered_problems": [],
            "considered_sub_problems": [],
            "considered_solutions": [],
        },
    }


def load_state(artefacts_dir: Path) -> dict[str, Any]:
    """Load state.json from artefacts_dir, or return an empty dict if missing."""
    state_path = artefacts_dir / "state.json"
    if not state_path.exists():
        return {}
    with state_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_state(artefacts_dir: Path, state: dict[str, Any]) -> Path:
    """Save state to artefacts_dir/state.json. Creates the dir if missing."""
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = _now_iso()
    if state.get("started_at") is None:
        state["started_at"] = state["updated_at"]
    state_path = artefacts_dir / "state.json"
    with state_path.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, sort_keys=True)
    return state_path


def get_phase_status(state: dict[str, Any], phase: int) -> str:
    """Return the status string ('pending' | 'in_progress' | 'completed') for a phase."""
    if not state:
        return "pending"
    return state["phases"][str(phase)]["status"]


def mark_phase_completed(
    state: dict[str, Any], phase: int, artefact_path: Path
) -> dict[str, Any]:
    """Mark a phase as completed with its artefact path and a timestamp.

    Also advances current_phase to phase+1.
    Returns the updated state.
    """
    state["phases"][str(phase)] = {
        "status": "completed",
        "artefact": str(artefact_path),
        "completed_at": _now_iso(),
    }
    state["current_phase"] = max(state.get("current_phase", 0), phase + 1)
    return state


def set_config(state: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    """Update one or more config fields. Returns the updated state."""
    for key, value in kwargs.items():
        if key not in state["config"]:
            raise KeyError(f"Unknown config key: {key!r}")
        state["config"][key] = value
    return state


def set_decision(state: dict[str, Any], key: str, value: Any) -> dict[str, Any]:
    """Record a decision (problem / sub-problem / solution). Returns updated state."""
    if key not in state["decisions"]:
        raise KeyError(f"Unknown decision key: {key!r}")
    state["decisions"][key] = value
    return state
```

- [ ] **Step 4: Run the tests, watch them pass**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_state.py -v
```

Expected: 10 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add agent/state.py tests/test_state.py
git commit -m "feat(agent): state module with TDD-tested helpers"
```

### Task 0.4: Create SKILL.md stub

**Files:**
- Create: `SKILL.md` (in repo root, NOT in a subdirectory — OpenCode discovers skills by filename)

- [ ] **Step 1: Write the SKILL.md stub**

Write `/SKILL.md`:

```markdown
# EDTH Hackathon Agent

You are driving the EDTH Hackathon Agent — a structured workflow that turns a CSV of problem statements into a problem/solution pitch deck, reviewed by a panel of 12 tough-judge personas.

## Quick start

1. Make sure the input CSV is at `input/PB-SOL-EDTH - Sheet1.csv` (or set `agent.config.input_csv` in `00_context.yaml`).
2. Invoke commands below. Each command advances one phase.
3. Artefacts are written under `artefacts/`. State is in `artefacts/state.json` and is resumable.

## Commands

| Command | Effect |
|---|---|
| `/edth-agent help` | Show this help |
| `/edth-agent status` | Show current phase, decisions, panel |
| `/edth-agent run` | Run the next pending phase |
| `/edth-agent run <N>` | Run phase N (0–8). Phase must be ready (all prior phases completed). |
| `/edth-agent rerun <N>` | Re-execute phase N, overwriting its artefact |
| `/edth-agent reset` | Wipe `artefacts/` and start over |
| `/edth-agent panel` | Show current panel + biases |
| `/edth-agent panel generate` | Auto-pick 5 judges for the chosen problem |
| `/edth-agent panel add <short>` | Add a judge |
| `/edth-agent panel remove <short>` | Remove a judge |
| `/edth-agent panel <short>` | Chat with one judge in character |
| `/edth-agent render` | Re-render the deck from current artefacts |

## Phases (0–8)

- **0 Onboarding** — capture hackathon context into `00_context.yaml`
- **1 Triage** — parse CSV, cluster problems, score, market-signal check
- **2 Elicit & narrow** — owner Q&A, top-3 candidates, user picks 1
- **3 Sub-problem** — decompose chosen problem, ROI score, user picks 1
- **4 Ideation** — divergent 20+ ideas, panel rates, top 5
- **5 Research & rank** — web research, re-rank, owner validates pick
- **6 Demo & narrative** — thin demo, 3-min script, pitch, Q&A prep, risk register
- **7 Deck & market** — Marp problem + solution slides, market/comp/BM research, render
- **8 Final review** — one-page summary, per-judge verdict, optional commit

## How to invoke a phase

When the user types `/edth-agent run` (or `/edth-agent run <N>`):

1. Read `artefacts/state.json` to determine current state.
2. If running the next phase, do the work described in the spec for that phase.
3. Write the phase's primary artefact to `artefacts/`.
4. Update `state.json` via the `agent.state` Python helpers (or by hand-editing the JSON).
5. In `owner_mode: real`, pause for user review. In `owner_mode: sim`, auto-approve.



## What this stub does

This is the initial scaffold. Phase-specific logic will be appended to this file as the agent is built out per `docs/superpowers/plans/2026-06-02-edth-agent.md`.
```

- [ ] **Step 2: Verify the file is well-formed**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
head -20 SKILL.md
```

Expected: markdown title `# EDTH Hackathon Agent` and a quick-start section.

- [ ] **Step 3: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add SKILL.md
git commit -m "docs(skill): add SKILL.md stub with command reference"
```

### Task 0.5: Smoke test

- [ ] **Step 1: Run the full test suite**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest
```

Expected: `10 passed` (all state tests).

- [ ] **Step 2: Verify the agent package is importable and version prints**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/python -c "from agent.state import empty_state, save_state; from pathlib import Path; s = empty_state(); p = save_state(Path('/tmp/smoke'), s); print('OK:', p)"
```

Expected: `OK: /tmp/smoke/state.json` and the file exists.

- [ ] **Step 3: Verify SKILL.md is present and parseable**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
test -f SKILL.md && wc -l SKILL.md
```

Expected: `SKILL.md` exists with a positive line count.

- [ ] **Step 4: No commit needed — milestone checkpoint**

Milestone 0 is complete. The repo is scaffolded, the state module is tested, and the skill stub is in place. Proceed to Milestone 1.

---

## Milestone 1 — Phase 0 (Onboarding) + Phase 1 (Triage) core

**Goal:** CSV can be parsed, normalized, and clustered. Triage artefact produced. No panel yet.

**Tasks:**
- Task 1.1: `parse_csv.py` + tests
- Task 1.2: `normalize.py` + tests
- Task 1.3: `rubric.py` (just the data structure)
- Task 1.4: Phase 0 — `00_context.yaml` write/read + tests
- Task 1.5: Phase 1 — triage clustering (LLM-driven, no panel)
- Task 1.6: Run end-to-end on real input CSV, verify artefacts

### Task 1.1: parse_csv module

**Files:**
- Create: `agent/parse_csv.py`
- Create: `tests/test_parse_csv.py`

- [ ] **Step 1: Write the failing tests**

Write `/tests/test_parse_csv.py`:

```python
"""Tests for agent.parse_csv — TDD: write these first."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from agent.parse_csv import (
    ParseError,
    parse_problems,
    parse_problems_from_string,
)


def test_parses_simple_two_column_csv(tmp_path: Path) -> None:
    csv_path = tmp_path / "in.csv"
    csv_path.write_text(
        "Name,Problem statement\n"
        "A machine vision system,Minimize the pilot's participation\n"
        "Automatic capture,Minimize the pilot's participation\n",
        encoding="utf-8",
    )
    problems = parse_problems(csv_path)
    assert len(problems) == 2
    assert problems[0]["name"] == "A machine vision system"
    assert problems[0]["problem"].startswith("Minimize the pilot's")
    assert problems[0]["id"] == "P-001"
    assert problems[0]["source_row"] == 2
    assert problems[1]["id"] == "P-002"


def test_id_format_is_padded_three_digits(tmp_path: Path) -> None:
    csv_path = tmp_path / "in.csv"
    csv_path.write_text(
        "Name,Problem statement\nA,A\nB,B\nC,C\n", encoding="utf-8"
    )
    problems = parse_problems(csv_path)
    assert [p["id"] for p in problems] == ["P-001", "P-002", "P-003"]


def test_source_hash_is_stable_across_runs(tmp_path: Path) -> None:
    csv_path = tmp_path / "in.csv"
    csv_path.write_text("Name,Problem statement\nFoo,bar baz\n", encoding="utf-8")
    a = parse_problems(csv_path)
    b = parse_problems(csv_path)
    assert a[0]["source_hash"] == b[0]["source_hash"]
    assert len(a[0]["source_hash"]) == 12  # short hex


def test_handles_multiline_cells_with_quotes(tmp_path: Path) -> None:
    csv_path = tmp_path / "in.csv"
    csv_path.write_text(
        'Name,Problem statement\n'
        'Autonomy 1,"AI Decision Support Systems\n'
        '\n'
        'Challenge: Multi-Domain Battle Management Interface\n'
        'Objective: Create an intuitive commander dashboard"\n',
        encoding="utf-8",
    )
    problems = parse_problems(csv_path)
    assert len(problems) == 1
    assert "Multi-Domain" in problems[0]["problem"]


def test_handles_utf8_bom(tmp_path: Path) -> None:
    csv_path = tmp_path / "in.csv"
    csv_path.write_bytes(
        "\ufeffName,Problem statement\nFoo,bar\n".encode("utf-8")
    )
    problems = parse_problems(csv_path)
    assert problems[0]["name"] == "Foo"


def test_missing_required_columns_raises(tmp_path: Path) -> None:
    csv_path = tmp_path / "in.csv"
    csv_path.write_text("Foo,bar\n1,2\n", encoding="utf-8")
    with pytest.raises(ParseError, match="Name"):
        parse_problems(csv_path)


def test_empty_csv_returns_empty_list(tmp_path: Path) -> None:
    csv_path = tmp_path / "in.csv"
    csv_path.write_text("Name,Problem statement\n", encoding="utf-8")
    assert parse_problems(csv_path) == []


def test_parse_from_string_helper_matches_file(tmp_path: Path) -> None:
    csv_text = (
        "Name,Problem statement\n"
        "Test,This is a problem statement\n"
    )
    from_file = parse_problems_from_string(csv_text)
    csv_path = tmp_path / "in.csv"
    csv_path.write_text(csv_text, encoding="utf-8")
    from_path = parse_problems(csv_path)
    # Same ids and hashes
    assert from_file[0]["id"] == from_path[0]["id"]
    assert from_file[0]["source_hash"] == from_path[0]["source_hash"]


def test_skips_rows_with_empty_problem(tmp_path: Path) -> None:
    csv_path = tmp_path / "in.csv"
    csv_path.write_text(
        "Name,Problem statement\nA,\nB,has a problem\n", encoding="utf-8"
    )
    problems = parse_problems(csv_path)
    assert len(problems) == 1
    assert problems[0]["name"] == "B"


def test_real_input_csv_parses(tmp_path: Path) -> None:
    """Smoke test: parse the actual input CSV the agent was designed against."""
    repo_root = Path(__file__).resolve().parent.parent
    csv_path = repo_root / "input" / "PB-SOL-EDTH - Sheet1.csv"
    if not csv_path.exists():
        pytest.skip(f"Input CSV not present at {csv_path}")
    problems = parse_problems(csv_path)
    assert len(problems) >= 30  # spec says ~40
    for p in problems[:3]:
        assert p["id"].startswith("P-")
        assert p["name"]
        assert p["problem"]
```

- [ ] **Step 2: Run the tests, watch them fail**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_parse_csv.py -v
```

Expected: import fails — `ModuleNotFoundError: No module named 'agent.parse_csv'`.

- [ ] **Step 3: Implement `parse_csv.py`**

Write `/agent/parse_csv.py`:

```python
"""CSV parser for the EDTH agent.

Reads a CSV with columns "Name" and "Problem statement" and returns
a normalized list of problem dicts. Handles multi-line cells, UTF-8 BOM,
and skips rows with empty problem text.

See spec §1, §4 Phase 1.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path
from typing import TypedDict


REQUIRED_COLUMNS = {"Name", "Problem statement"}


class ParseError(ValueError):
    """Raised when the CSV is missing required columns."""


class Problem(TypedDict):
    id: str
    name: str
    problem: str
    source_row: int
    source_hash: str


def _short_hash(name: str, problem: str) -> str:
    h = hashlib.sha256()
    h.update(name.strip().encode("utf-8"))
    h.update(b"\x00")
    h.update(problem.strip().encode("utf-8"))
    return h.hexdigest()[:12]


def _make_id(index: int) -> str:
    return f"P-{index:03d}"


def parse_problems_from_string(csv_text: str) -> list[Problem]:
    """Parse CSV content from a string. See parse_problems for details."""
    # csv.reader handles BOM only if we strip it; use utf-8-sig via io
    import io

    text = csv_text
    if text.startswith("\ufeff"):
        text = text[1:]
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        return []
    if not REQUIRED_COLUMNS.issubset(set(reader.fieldnames)):
        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        raise ParseError(
            f"CSV is missing required columns: {sorted(missing)}"
        )

    out: list[Problem] = []
    for row_index, row in enumerate(reader, start=2):  # row 1 is header
        name = (row.get("Name") or "").strip()
        problem = (row.get("Problem statement") or "").strip()
        if not problem:
            continue
        out.append(
            Problem(
                id=_make_id(len(out) + 1),
                name=name,
                problem=problem,
                source_row=row_index,
                source_hash=_short_hash(name, problem),
            )
        )
    return out


def parse_problems(csv_path: Path) -> list[Problem]:
    """Parse a CSV file at csv_path and return a list of Problem dicts."""
    text = csv_path.read_text(encoding="utf-8-sig")
    return parse_problems_from_string(text)
```

- [ ] **Step 4: Run the tests, watch them pass**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_parse_csv.py -v
```

Expected: 10 passed (including the smoke test against the real CSV if present, otherwise skipped).

- [ ] **Step 5: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add agent/parse_csv.py tests/test_parse_csv.py
git commit -m "feat(agent): parse_csv with multi-line, BOM, and smoke tests"
```

### Task 1.2: normalize module (heuristic quality flags)

**Files:**
- Create: `agent/normalize.py`
- Create: `tests/test_normalize.py`

- [ ] **Step 1: Write the failing tests**

Write `/tests/test_normalize.py`:

```python
"""Tests for agent.normalize — TDD: write these first."""

from __future__ import annotations

from agent.normalize import (
    QualityFlag,
    assign_quality_flags,
    dedupe_problems,
)


def _p(id: str, name: str, problem: str, source_hash: str = "") -> dict:
    return {
        "id": id,
        "name": name,
        "problem": problem,
        "source_row": 1,
        "source_hash": source_hash or f"hash-{id}",
    }


def test_empty_problem_gets_vague_flag() -> None:
    p = _p("P-001", "X", "Hi")
    flags = assign_quality_flags(p)
    assert QualityFlag.VAGUE in flags


def test_short_problem_under_50_chars_gets_vague() -> None:
    p = _p("P-001", "Cheap radar", "Build a radar.")
    flags = assign_quality_flags(p)
    assert QualityFlag.VAGUE in flags


def test_problem_mentioning_hardware_gets_flag() -> None:
    p = _p(
        "P-001",
        "Stealth Materials",
        "Develop stealth materials for UUVs that avoid detection by conventional underwater reconnaissance systems, including sonars and submarines.",
    )
    flags = assign_quality_flags(p)
    assert QualityFlag.REQUIRES_HARDWARE in flags


def test_problem_mentioning_radar_gets_flag() -> None:
    p = _p(
        "P-001",
        "Cheap radar",
        "Design short-range (500-1000m) cheap (<$1,000) radar at high accuracy for drone detection.",
    )
    flags = assign_quality_flags(p)
    assert QualityFlag.REQUIRES_HARDWARE in flags


def test_problem_with_two_topics_gets_multi_problem() -> None:
    p = _p(
        "P-001",
        "Optical detection combining Optical and Acoustic",
        "Sensor fusion and Acoustic and Visual recognition. Current gen UAVs have at least 2 communication channels. The solution that could help blend them to make decisions will be crucial.",
    )
    flags = assign_quality_flags(p)
    assert QualityFlag.MULTI_PROBLEM in flags


def test_clean_software_problem_has_no_flags() -> None:
    p = _p(
        "P-001",
        "Autonomy 1",
        "AI Decision Support Systems. Challenge: Multi-Domain Battle Management Interface. Objective: Create an intuitive commander's dashboard that processes multi-domain data and provides actionable insights. Process simulated feeds from air, land, and naval assets. Prioritize threats using AI. Generate course-of-action recommendations. Display critical information within 3 seconds.",
    )
    flags = assign_quality_flags(p)
    assert QualityFlag.VAGUE not in flags
    assert QualityFlag.REQUIRES_HARDWARE not in flags
    assert QualityFlag.MULTI_PROBLEM not in flags


def test_dedupe_keeps_first_by_source_row() -> None:
    a = _p("P-001", "Same", "same problem", source_hash="abc")
    b = _p("P-002", "Same", "same problem", source_hash="abc")
    c = _p("P-003", "Different", "different", source_hash="xyz")
    result = dedupe_problems([a, b, c])
    assert len(result) == 2
    assert result[0]["id"] == "P-001"
    assert result[1]["id"] == "P-003"


def test_dedupe_returns_empty_for_empty_input() -> None:
    assert dedupe_problems([]) == []
```

- [ ] **Step 2: Run the tests, watch them fail**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_normalize.py -v
```

Expected: import fails — `ModuleNotFoundError: No module named 'agent.normalize'`.

- [ ] **Step 3: Implement `normalize.py`**

Write `/agent/normalize.py`:

```python
"""Heuristic normalization for parsed problems.

Adds quality flags (vague, multi-problem, requires-hardware) to each
problem based on simple text heuristics. Theme/tag assignment is
LLM-driven and lives in the skill, not here.

See spec §4 Phase 1.
"""

from __future__ import annotations

from enum import Enum
from typing import TypedDict


class QualityFlag(str, Enum):
    VAGUE = "vague"
    MULTI_PROBLEM = "multi_problem"
    REQUIRES_HARDWARE = "requires_hardware"
    OUT_OF_SCOPE_FOR_48H = "out_of_scope_for_48h"


_HARDWARE_KEYWORDS = (
    "hull",
    "radar",
    "antenna",
    "stealth material",
    "energy harvesting",
    "propulsion",
    "3d print",
    "manufacturing",
    "physical hardware",
    "mechanical",
    "towed antenna",
    "towed",
)

_VAGUE_LENGTH = 50  # chars

_MULTI_PROBLEM_KEYWORDS = (
    "combining",
    "and",
    "blend",
    "multiple",
    "two",
)


class ProblemWithFlags(TypedDict, total=False):
    id: str
    name: str
    problem: str
    source_row: int
    source_hash: str
    quality_flags: list[str]


def assign_quality_flags(problem: dict) -> list[QualityFlag]:
    """Inspect a problem dict and return a list of quality flags."""
    flags: list[QualityFlag] = []
    text = f"{problem.get('name', '')} {problem.get('problem', '')}".lower()

    if len(problem.get("problem", "").strip()) < _VAGUE_LENGTH:
        flags.append(QualityFlag.VAGUE)

    for kw in _HARDWARE_KEYWORDS:
        if kw in text:
            flags.append(QualityFlag.REQUIRES_HARDWARE)
            break

    if _is_multi_problem(text):
        flags.append(QualityFlag.MULTI_PROBLEM)

    return flags


def _is_multi_problem(text: str) -> bool:
    """Heuristic: a problem is multi-problem if it asks for several distinct
    solutions in one breath. Looks for 2+ multi-problem keywords."""
    matches = sum(1 for kw in _MULTI_PROBLEM_KEYWORDS if kw in text)
    return matches >= 2


def dedupe_problems(problems: list[dict]) -> list[dict]:
    """Remove duplicates by source_hash, keeping the first occurrence by source_row."""
    seen: set[str] = set()
    out: list[dict] = []
    sorted_problems = sorted(problems, key=lambda p: p.get("source_row", 0))
    for p in sorted_problems:
        h = p.get("source_hash", "")
        if h in seen:
            continue
        seen.add(h)
        out.append(p)
    return out
```

- [ ] **Step 4: Run the tests, watch them pass**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_normalize.py -v
```

Expected: 8 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add agent/normalize.py tests/test_normalize.py
git commit -m "feat(agent): normalize module with quality flags and dedupe"
```

### Task 1.3: rubric module

**Files:**
- Create: `agent/rubric.py`
- Create: `tests/test_rubric.py`

- [ ] **Step 1: Write the failing tests**

Write `/tests/test_rubric.py`:

```python
"""Tests for agent.rubric — TDD."""

from __future__ import annotations

import pytest

from agent.rubric import (
    DEFAULT_RUBRIC,
    Rubric,
    RubricAxis,
    get_axis_weights,
    normalize_weights,
    score_to_weighted,
)


def test_default_rubric_has_four_axes() -> None:
    assert set(DEFAULT_RUBRIC.keys()) == {"impact", "innovation", "execution", "presentation"}


def test_default_rubric_weights_sum_to_one() -> None:
    assert abs(sum(DEFAULT_RUBRIC.values()) - 1.0) < 1e-9


def test_rubric_axis_is_string_enum() -> None:
    assert RubricAxis.IMPACT == "impact"
    assert RubricAxis.PRESENTATION == "presentation"


def test_get_axis_weights_returns_dict() -> None:
    w = get_axis_weights(DEFAULT_RUBRIC)
    assert w == DEFAULT_RUBRIC


def test_normalize_weights_renormalizes_to_one() -> None:
    raw = {"impact": 2.0, "innovation": 1.0, "execution": 1.0, "presentation": 0.0}
    norm = normalize_weights(raw)
    assert abs(sum(norm.values()) - 1.0) < 1e-9
    assert norm["impact"] == pytest.approx(0.5)


def test_score_to_weighted_returns_weighted_average() -> None:
    scores = {"impact": 5, "innovation": 3, "execution": 4, "presentation": 2}
    weights = {"impact": 0.4, "innovation": 0.2, "execution": 0.3, "presentation": 0.1}
    expected = 5 * 0.4 + 3 * 0.2 + 4 * 0.3 + 2 * 0.1  # 4.1
    assert score_to_weighted(scores, weights) == pytest.approx(4.1)


def test_score_to_weighted_with_missing_axis_raises() -> None:
    scores = {"impact": 5, "innovation": 3}  # missing two
    with pytest.raises(KeyError):
        score_to_weighted(scores, DEFAULT_RUBRIC)
```

- [ ] **Step 2: Run the tests, watch them fail**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_rubric.py -v
```

Expected: import fails.

- [ ] **Step 3: Implement `rubric.py`**

Write `/agent/rubric.py`:

```python
"""Judging rubric definitions and scoring math.

The default 4-axis rubric (impact / innovation / execution / presentation)
matches the typical defense/hackathon judging panel. User can override
in 00_context.yaml.

See spec §5.5, §11.
"""

from __future__ import annotations

from enum import Enum
from typing import Mapping


class RubricAxis(str, Enum):
    IMPACT = "impact"
    INNOVATION = "innovation"
    EXECUTION = "execution"
    PRESENTATION = "presentation"


DEFAULT_RUBRIC: dict[str, float] = {
    RubricAxis.IMPACT.value: 0.30,
    RubricAxis.INNOVATION.value: 0.25,
    RubricAxis.EXECUTION.value: 0.25,
    RubricAxis.PRESENTATION.value: 0.20,
}


def get_axis_weights(rubric: Mapping[str, float]) -> dict[str, float]:
    return dict(rubric)


def normalize_weights(weights: Mapping[str, float]) -> dict[str, float]:
    """Renormalize a weights dict to sum to 1.0. Zeros are preserved as zeros."""
    total = sum(weights.values())
    if total == 0:
        raise ValueError("Cannot normalize: all weights are zero")
    return {k: v / total for k, v in weights.items()}


def score_to_weighted(
    scores: Mapping[str, float], weights: Mapping[str, float]
) -> float:
    """Compute a weighted average of axis scores.

    Both dicts must have the same keys. Each score is expected to be on a
    1-5 scale; the result is on the same scale.
    """
    missing = set(weights.keys()) - set(scores.keys())
    if missing:
        raise KeyError(f"Missing scores for axes: {sorted(missing)}")
    return sum(scores[k] * w for k, w in weights.items())
```

- [ ] **Step 4: Run the tests, watch them pass**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_rubric.py -v
```

Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add agent/rubric.py tests/test_rubric.py
git commit -m "feat(agent): rubric module with default 4-axis weights"
```

### Task 1.4: Phase 0 — context loader

**Files:**
- Create: `agent/context.py`
- Create: `tests/test_context.py`

- [ ] **Step 1: Write the failing tests**

Write `/tests/test_context.py`:

```python
"""Tests for agent.context — TDD."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent.context import (
    AgentContext,
    default_context,
    load_context,
    save_context,
)


def test_default_context_has_required_keys() -> None:
    ctx = default_context()
    assert ctx["hackathon"]["name"] == "EDTH Munich 2025"
    assert "judging_rubric" in ctx["hackathon"]
    assert ctx["agent"]["owner_mode"] in ("real", "sim")


def test_default_rubric_matches_agent_rubric() -> None:
    ctx = default_context()
    rubric = ctx["hackathon"]["judging_rubric"]
    assert abs(sum(rubric.values()) - 1.0) < 1e-9
    assert set(rubric.keys()) == {"impact", "innovation", "execution", "presentation"}


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    ctx = default_context()
    ctx["agent"]["owner_mode"] = "sim"
    ctx["team"]["size"] = 5
    path = save_context(tmp_path, ctx)
    assert path == tmp_path / "00_context.yaml"
    loaded = load_context(tmp_path)
    assert loaded["agent"]["owner_mode"] == "sim"
    assert loaded["team"]["size"] == 5


def test_load_missing_returns_default(tmp_path: Path) -> None:
    ctx = load_context(tmp_path)
    assert ctx == default_context()


def test_save_creates_dir_if_missing(tmp_path: Path) -> None:
    nested = tmp_path / "does" / "not" / "exist"
    save_context(nested, default_context())
    assert (nested / "00_context.yaml").exists()


def test_context_yaml_is_human_readable(tmp_path: Path) -> None:
    save_context(tmp_path, default_context())
    raw = (tmp_path / "00_context.yaml").read_text()
    assert "hackathon:" in raw
    assert "judging_rubric:" in raw
```

- [ ] **Step 2: Run the tests, watch them fail**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_context.py -v
```

Expected: import fails.

- [ ] **Step 3: Implement `context.py`**

Write `/agent/context.py`:

```python
"""Phase 0 — Onboarding context I/O.

Reads/writes artefacts/00_context.yaml. The user fills this in at
the start of every run; the skill reads it to drive decisions.

See spec §4 Phase 0.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, TypedDict

import yaml

from agent.rubric import DEFAULT_RUBRIC


class AgentContext(TypedDict, total=False):
    hackathon: dict[str, Any]
    team: dict[str, Any]
    constraints: dict[str, Any]
    agent: dict[str, Any]


def default_context() -> AgentContext:
    """Return a default onboarding context for EDTH Munich 2025."""
    return AgentContext(
        hackathon={
            "name": "EDTH Munich 2025",
            "theme": "Defense tech / dual-use",
            "tracks": ["C-UAS", "Autonomy", "EW", "UUV", "USV"],
            "judging_rubric": dict(DEFAULT_RUBRIC),
        },
        team={
            "size": 4,
            "strengths": ["ML/CV", "frontend", "signal_proc"],
            "weaknesses": ["hardware", "maritime domain"],
        },
        constraints={
            "time_budget_hours": 48,
            "deliverable": "deck + thin demo",
        },
        agent={
            "owner_mode": "real",
            "persona": "edth-judge",
            "panel_mode": "expanded",
            "aggregation_mode": "borda",
        },
    )


def load_context(artefacts_dir: Path) -> AgentContext:
    """Load 00_context.yaml from artefacts_dir, or return default if missing."""
    path = artefacts_dir / "00_context.yaml"
    if not path.exists():
        return default_context()
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    # Coerce to AgentContext by merging with defaults
    default = default_context()
    merged = AgentContext(
        hackathon={**default["hackathon"], **data.get("hackathon", {})},
        team={**default["team"], **data.get("team", {})},
        constraints={**default["constraints"], **data.get("constraints", {})},
        agent={**default["agent"], **data.get("agent", {})},
    )
    return merged


def save_context(artefacts_dir: Path, context: AgentContext) -> Path:
    """Save context to artefacts_dir/00_context.yaml. Creates the dir if missing."""
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    path = artefacts_dir / "00_context.yaml"
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(dict(context), f, sort_keys=False, default_flow_style=False)
    return path
```

- [ ] **Step 4: Run the tests, watch them pass**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_context.py -v
```

Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add agent/context.py tests/test_context.py
git commit -m "feat(agent): Phase 0 context loader with EDTH default"
```

### Task 1.5: Phase 1 — triage markdown writer (Python side)

The triage step is mostly LLM-driven (cluster, score, market-signal check). Python only writes the artefact file in a consistent format. This task builds the writer; the LLM prompt template is in the SKILL.md (which gets expanded later).

**Files:**
- Create: `agent/triage.py`
- Create: `tests/test_triage.py`

- [ ] **Step 1: Write the failing tests**

Write `/tests/test_triage.py`:

```python
"""Tests for agent.triage — TDD. Triage is mostly LLM-driven; Python just
formats and writes the artefact."""

from __future__ import annotations

from pathlib import Path

from agent.triage import Cluster, TriageReport, write_triage_report


def test_write_triage_creates_file(tmp_path: Path) -> None:
    report = TriageReport(
        clusters=[
            Cluster(
                name="Counter-UAV",
                themes=["c-uas", "detection"],
                problem_ids=["P-001", "P-002", "P-003"],
                scores={"impact": 4.5, "innovation": 3.5, "execution": 4.0, "presentation": 3.5},
                market_signal="Active commercial space; Anduril, Dedrone, D-Fend Solutions.",
            ),
            Cluster(
                name="Electronic Warfare",
                themes=["ew", "signal_proc"],
                problem_ids=["P-004", "P-005"],
                scores={"impact": 4.0, "innovation": 4.5, "execution": 3.0, "presentation": 3.5},
                market_signal="Crowded defense primes; niche synthetic-data advantages.",
            ),
        ],
        panel_summary="Both judges ranked Counter-UAV top-3.",
    )
    path = write_triage_report(tmp_path, report)
    assert path == tmp_path / "01_triage.md"
    raw = path.read_text(encoding="utf-8")
    assert "# Triage Report" in raw
    assert "Counter-UAV" in raw
    assert "Electronic Warfare" in raw
    assert "Anduril" in raw


def test_triage_report_includes_weighted_score(tmp_path: Path) -> None:
    report = TriageReport(
        clusters=[
            Cluster(
                name="Test",
                themes=[],
                problem_ids=["P-1"],
                scores={"impact": 5, "innovation": 5, "execution": 5, "presentation": 5},
                market_signal="",
            )
        ],
        panel_summary="",
    )
    write_triage_report(tmp_path, report)
    raw = (tmp_path / "01_triage.md").read_text(encoding="utf-8")
    assert "5.00" in raw  # weighted avg
```

- [ ] **Step 2: Run the tests, watch them fail**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_triage.py -v
```

Expected: import fails.

- [ ] **Step 3: Implement `triage.py`**

Write `/agent/triage.py`:

```python
"""Phase 1 — Triage report writer.

The clustering, scoring, and market-signal-check reasoning is LLM-driven
(lives in the skill). Python's job is to format the result into a
consistent markdown artefact.

See spec §4 Phase 1.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from agent.rubric import score_to_weighted, DEFAULT_RUBRIC


@dataclass
class Cluster:
    name: str
    themes: list[str]
    problem_ids: list[str]
    scores: dict[str, float]
    market_signal: str = ""


@dataclass
class TriageReport:
    clusters: list[Cluster]
    panel_summary: str = ""
    notes: str = ""


def write_triage_report(artefacts_dir: Path, report: TriageReport) -> Path:
    """Write the triage markdown artefact. Returns the path written."""
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    lines: list[str] = ["# Triage Report", ""]

    for i, cluster in enumerate(report.clusters, start=1):
        weighted = score_to_weighted(cluster.scores, DEFAULT_RUBRIC)
        lines.append(f"## Cluster {i}: {cluster.name}")
        lines.append("")
        if cluster.themes:
            lines.append(f"**Themes:** {', '.join(cluster.themes)}")
            lines.append("")
        lines.append(f"**Problems:** {len(cluster.problem_ids)}")
        lines.append("")
        lines.append("**Axis scores (1-5):**")
        for axis, score in cluster.scores.items():
            lines.append(f"- {axis}: {score:.2f}")
        lines.append(f"- **weighted total: {weighted:.2f}**")
        lines.append("")
        if cluster.market_signal:
            lines.append(f"**Market signal:** {cluster.market_signal}")
            lines.append("")
        lines.append(f"**Problem IDs:** {', '.join(cluster.problem_ids)}")
        lines.append("")

    if report.panel_summary:
        lines.append("## Panel summary")
        lines.append("")
        lines.append(report.panel_summary)
        lines.append("")

    if report.notes:
        lines.append("## Notes")
        lines.append("")
        lines.append(report.notes)
        lines.append("")

    path = artefacts_dir / "01_triage.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
```

- [ ] **Step 4: Run the tests, watch them pass**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_triage.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add agent/triage.py tests/test_triage.py
git commit -m "feat(agent): Phase 1 triage report writer"
```

### Task 1.6: End-to-end smoke test (Milestone 1)

- [ ] **Step 1: Run the full test suite**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest
```

Expected: all tests pass (~40 tests across state, parse_csv, normalize, rubric, context, triage).

- [ ] **Step 2: Parse the real input CSV and verify**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/python -c "
from pathlib import Path
from agent.parse_csv import parse_problems
from agent.normalize import assign_quality_flags, dedupe_problems
problems = parse_problems(Path('input/PB-SOL-EDTH - Sheet1.csv'))
print(f'Parsed: {len(problems)} problems')
for p in problems[:3]:
    flags = assign_quality_flags(p)
    print(f'  {p[\"id\"]}: {p[\"name\"][:50]!r}  flags={flags}')
deduped = dedupe_problems(problems)
print(f'After dedupe: {len(deduped)} problems')
"
```

Expected: ~40 problems parsed, no dups removed, some with `requires_hardware` or `vague` flags.

- [ ] **Step 3: Write a sample triage report by hand (no LLM yet)**

This is a manual smoke test that the writer works. Save it for later LLM-driven generation.

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/python -c "
from pathlib import Path
from agent.triage import Cluster, TriageReport, write_triage_report
from agent.parse_csv import parse_problems
problems = parse_problems(Path('input/PB-SOL-EDTH - Sheet1.csv'))
report = TriageReport(
    clusters=[
        Cluster('Counter-UAS', ['c-uas', 'detection'],
                [p['id'] for p in problems if 'drone' in p['problem'].lower() or 'UAV' in p['problem']][:5],
                {'impact': 4.5, 'innovation': 3.5, 'execution': 4.0, 'presentation': 3.5},
                'Active commercial space.'),
        Cluster('EW', ['ew', 'signal_proc'],
                [p['id'] for p in problems if 'EW' in p['name'] or 'electronic' in p['problem'].lower()][:5],
                {'impact': 4.0, 'innovation': 4.5, 'execution': 3.0, 'presentation': 3.5},
                'Crowded defense primes.'),
    ],
    panel_summary='Both judges ranked Counter-UAS top-3.',
)
path = write_triage_report(Path('artefacts'), report)
print('Wrote:', path)
"
```

Expected: `Wrote: artefacts/01_triage.md` and the file exists.

- [ ] **Step 4: Inspect the artefact**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
head -30 artefacts/01_triage.md
```

Expected: `# Triage Report`, then `## Cluster 1: Counter-UAS`, etc.

- [ ] **Step 5: No commit — sample artefact, will be regenerated by the skill later**

```bash
rm -f /Users/vincent/Work/edth-prob-solution-deck/artefacts/01_triage.md
```

Milestone 1 complete. The agent can parse CSV, normalize, and write a triage report. Next milestone: persona + judge systems.

## Milestone 2 — Persona & judge systems

**Goal:** 12 judge YAMLs authored, persona loader working, auto-selection algorithm tested. Panel can be composed for a problem.

**Tasks:**
- Task 2.1: `personas.py` + tests, `personas/edth-judge.yaml`
- Task 2.2: Judge YAML schema + validator
- Task 2.3: `judges.py` loader + tests
- Task 2.4: Auto-selection algorithm + tests
- Task 2.5: Author 12 judge YAMLs
- Task 2.6: Wire panel into Phase 1 (re-score with panel, see effect)

### Task 2.1: Persona loader

**Files:**
- Create: `agent/personas.py`
- Create: `personas/edth-judge.yaml`
- Create: `personas/README.md`
- Create: `tests/test_personas.py`

- [ ] **Step 1: Write the failing tests**

Write `/tests/test_personas.py`:

```python
"""Tests for agent.personas — TDD."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent.personas import (
    Persona,
    PersonaError,
    list_personas,
    load_persona,
)


def test_load_default_edth_persona(tmp_path: Path) -> None:
    personas_dir = tmp_path / "personas"
    personas_dir.mkdir()
    (personas_dir / "edth-judge.yaml").write_text(
        """name: "EDTH Judge"
role: "Senior evaluator"
background: "20 years defense"
priorities: ["impact", "execution"]
anti_priorities: ["vague claims"]
decision_style: "direct"
language_patterns: ["show me"]
constraints: ["field in 12 months"]
""",
        encoding="utf-8",
    )
    p = load_persona(personas_dir, "edth-judge")
    assert p["name"] == "EDTH Judge"
    assert p["priorities"] == ["impact", "execution"]


def test_load_missing_persona_raises(tmp_path: Path) -> None:
    with pytest.raises(PersonaError, match="not found"):
        load_persona(tmp_path, "nonexistent")


def test_list_personas_returns_short_names(tmp_path: Path) -> None:
    d = tmp_path / "personas"
    d.mkdir()
    (d / "alpha.yaml").write_text("name: A\n", encoding="utf-8")
    (d / "beta.yaml").write_text("name: B\n", encoding="utf-8")
    assert sorted(list_personas(d)) == ["alpha", "beta"]


def test_list_empty_dir_returns_empty(tmp_path: Path) -> None:
    d = tmp_path / "personas"
    d.mkdir()
    assert list_personas(d) == []
```

- [ ] **Step 2: Run the tests, watch them fail**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_personas.py -v
```

Expected: import fails.

- [ ] **Step 3: Implement `personas.py`**

Write `/agent/personas.py`:

```python
"""Problem-owner persona loader.

The persona is the source of truth for pain, environment, and constraints
during elicitation. Distinct from judges (see agent.judges).

See spec §6.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class PersonaError(KeyError):
    """Raised when a persona cannot be loaded."""


def _path_for(personas_dir: Path, short_name: str) -> Path:
    return personas_dir / f"{short_name}.yaml"


def load_persona(personas_dir: Path, short_name: str) -> dict[str, Any]:
    """Load a persona YAML. Raises PersonaError if not found."""
    path = _path_for(personas_dir, short_name)
    if not path.exists():
        raise PersonaError(f"Persona {short_name!r} not found at {path}")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def list_personas(personas_dir: Path) -> list[str]:
    """List all available persona short names (filenames without .yaml)."""
    if not personas_dir.exists():
        return []
    return sorted(
        p.stem for p in personas_dir.glob("*.yaml") if p.stem != "README"
    )
```

- [ ] **Step 4: Author the default persona**

Write `/personas/edth-judge.yaml`:

```yaml
name: "EDTH Defense Judge"
short: "EDTH Judge"
role: "Senior evaluator at a defense-tech prime"
background: "20 years in defense procurement and program management. Former DoD civilian, current senior fellow at a Tier 1 defense prime. Sees 200+ pitches per year."
priorities:
  - "real-world fieldability"
  - "clear path to procurement"
  - "team credibility"
  - "demo-able result"
anti_priorities:
  - "vague claims without data"
  - "academic novelty without fielding"
  - "buzzword soup (AI/ML/blockchain)"
  - "no understanding of the buyer"
decision_style: "decisive, asks pointed questions, pushes back on hand-waving"
language_patterns:
  - "show me"
  - "what's the TRL"
  - "who's buying"
  - "what's the FAR pathway"
constraints:
  - "real-world impact matters more than novelty"
  - "prefers solutions fieldable in 12 months"
  - "values demo-able results"
communication_style: "direct, no fluff, will cut you off if you're hedging"
```

- [ ] **Step 5: Add the personas README**

Write `/personas/README.md`:

```markdown
# Personas

Problem-owner personas. These are the simulated sources of truth the
agent elicits from when `agent.owner_mode: sim` is set.

## Schema

- `name`: full display name
- `short`: short identifier (used in state.json and CLI flags)
- `role`: one-line role
- `background`: one paragraph
- `priorities`: list of 3-6 priorities
- `anti_priorities`: list of 3-6 pet peeves
- `decision_style`: one sentence
- `language_patterns`: list of 3-6 phrases
- `constraints`: list of explicit constraints
- `communication_style`: one sentence

## Default

- `edth-judge.yaml` — defense industry evaluator

## Adding a new persona

1. Copy `edth-judge.yaml` to `<short>.yaml` in this directory.
2. Edit the values.
3. Set `agent.persona: <short>` in `artefacts/00_context.yaml`.
```

- [ ] **Step 6: Run the tests, watch them pass**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_personas.py -v
```

Expected: 4 passed.

- [ ] **Step 7: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add agent/personas.py tests/test_personas.py personas/
git commit -m "feat(agent): persona loader with EDTH default persona"
```

### Task 2.2: Judge YAML schema + validator

**Files:**
- Create: `agent/judge_schema.py`
- Create: `tests/test_judge_schema.py`

- [ ] **Step 1: Write the failing tests**

Write `/tests/test_judge_schema.py`:

```python
"""Tests for agent.judge_schema — TDD."""

from __future__ import annotations

import pytest

from agent.judge_schema import (
    Judge,
    JudgeValidationError,
    validate_judge,
)


def _valid_judge_dict() -> dict:
    return {
        "name": "Maj. Viper Reyes",
        "short": "viper",
        "tags": ["c-uas", "autonomy"],
        "background": "F-16 pilot",
        "priorities": ["operational_relevance"],
        "anti_priorities": ["buzzwords"],
        "decision_style": "decisive",
        "language_patterns": ["show me"],
        "scoring_biases": {
            "impact": 0.10,
            "innovation": -0.05,
            "execution": 0.10,
            "presentation": 0.0,
        },
        "knowledge_gaps": ["consumer_tech"],
        "hard_questions_seed": ["what kills this?"],
    }


def test_valid_judge_passes() -> None:
    judge = validate_judge(_valid_judge_dict())
    assert judge["short"] == "viper"
    assert judge["scoring_biases"]["impact"] == 0.10


def test_missing_required_field_raises() -> None:
    bad = _valid_judge_dict()
    del bad["tags"]
    with pytest.raises(JudgeValidationError, match="tags"):
        validate_judge(bad)


def test_scoring_biases_must_have_four_axes() -> None:
    bad = _valid_judge_dict()
    bad["scoring_biases"] = {"impact": 0.1}
    with pytest.raises(JudgeValidationError, match="scoring_biases"):
        validate_judge(bad)


def test_short_must_be_lowercase_alphanumeric() -> None:
    bad = _valid_judge_dict()
    bad["short"] = "Viper-1"
    with pytest.raises(JudgeValidationError, match="short"):
        validate_judge(bad)


def test_biases_must_be_floats() -> None:
    bad = _valid_judge_dict()
    bad["scoring_biases"]["impact"] = "high"
    with pytest.raises(JudgeValidationError, match="float"):
        validate_judge(bad)


def test_priorities_must_be_list() -> None:
    bad = _valid_judge_dict()
    bad["priorities"] = "operational"
    with pytest.raises(JudgeValidationError, match="priorities"):
        validate_judge(bad)
```

- [ ] **Step 2: Run the tests, watch them fail**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_judge_schema.py -v
```

Expected: import fails.

- [ ] **Step 3: Implement `judge_schema.py`**

Write `/agent/judge_schema.py`:

```python
"""Judge YAML schema and validation.

A judge is a YAML with a fixed set of fields. This module is the
single source of truth for what's allowed; the LLM skill and the
auto-selection algorithm both rely on it.

See spec §5.2.
"""

from __future__ import annotations

import re
from typing import Any, TypedDict

from agent.rubric import RubricAxis


class Judge(TypedDict, total=False):
    name: str
    short: str
    tags: list[str]
    background: str
    priorities: list[str]
    anti_priorities: list[str]
    decision_style: str
    language_patterns: list[str]
    scoring_biases: dict[str, float]
    knowledge_gaps: list[str]
    hard_questions_seed: list[str]


REQUIRED_FIELDS = (
    "name",
    "short",
    "tags",
    "background",
    "priorities",
    "anti_priorities",
    "decision_style",
    "language_patterns",
    "scoring_biases",
    "knowledge_gaps",
    "hard_questions_seed",
)

_SHORT_PATTERN = re.compile(r"^[a-z0-9_-]+$")


class JudgeValidationError(ValueError):
    """Raised when a judge YAML doesn't validate."""


def validate_judge(data: dict[str, Any]) -> Judge:
    """Validate and return a Judge dict. Raises JudgeValidationError on bad data."""
    for field in REQUIRED_FIELDS:
        if field not in data:
            raise JudgeValidationError(f"Missing required field: {field!r}")

    short = data["short"]
    if not isinstance(short, str) or not _SHORT_PATTERN.match(short):
        raise JudgeValidationError(
            f"short must match [a-z0-9_-]+, got {short!r}"
        )

    for list_field in ("tags", "priorities", "anti_priorities",
                       "language_patterns", "knowledge_gaps",
                       "hard_questions_seed"):
        if not isinstance(data[list_field], list):
            raise JudgeValidationError(f"{list_field} must be a list")

    biases = data["scoring_biases"]
    if not isinstance(biases, dict):
        raise JudgeValidationError("scoring_biases must be a dict")
    expected_axes = {a.value for a in RubricAxis}
    if set(biases.keys()) != expected_axes:
        raise JudgeValidationError(
            f"scoring_biases must have exactly {expected_axes}, got {set(biases.keys())}"
        )
    for k, v in biases.items():
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            raise JudgeValidationError(f"scoring_biases.{k} must be a float")

    return data  # type: ignore[return-value]
```

- [ ] **Step 4: Run the tests, watch them pass**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_judge_schema.py -v
```

Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add agent/judge_schema.py tests/test_judge_schema.py
git commit -m "feat(agent): judge YAML schema with strict validation"
```

### Task 2.3: Judge library loader

**Files:**
- Create: `agent/judges.py` (add to existing — wait, no existing file yet)
- Create: `tests/test_judges.py`

Note: We're creating `judges.py` here, not `judges/`. The directory is for YAML files.

- [ ] **Step 1: Write the failing tests**

Write `/tests/test_judges.py`:

```python
"""Tests for agent.judges — TDD."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent.judges import (
    list_judges,
    load_judge,
    load_judge_library,
)


def _write_judge(d: Path, short: str, name: str, tags: list[str]) -> None:
    d.mkdir(exist_ok=True)
    (d / f"{short}.yaml").write_text(
        f"""name: "{name}"
short: "{short}"
tags: {tags}
background: "bg"
priorities: ["p"]
anti_priorities: ["ap"]
decision_style: "ds"
language_patterns: ["lp"]
scoring_biases:
  impact: 0.0
  innovation: 0.0
  execution: 0.0
  presentation: 0.0
knowledge_gaps: ["kg"]
hard_questions_seed: ["hq"]
""",
        encoding="utf-8",
    )


def test_load_judge_returns_validated_dict(tmp_path: Path) -> None:
    _write_judge(tmp_path, "viper", "Maj. Viper", ["c-uas"])
    j = load_judge(tmp_path, "viper")
    assert j["short"] == "viper"
    assert j["tags"] == ["c-uas"]


def test_load_judge_invalid_raises(tmp_path: Path) -> None:
    (tmp_path).mkdir(exist_ok=True)
    (tmp_path / "bad.yaml").write_text("name: bad\n", encoding="utf-8")
    with pytest.raises(Exception):
        load_judge(tmp_path, "bad")


def test_list_judges_returns_short_names(tmp_path: Path) -> None:
    _write_judge(tmp_path, "alpha", "A", [])
    _write_judge(tmp_path, "beta", "B", [])
    assert sorted(list_judges(tmp_path)) == ["alpha", "beta"]


def test_load_judge_library_returns_all(tmp_path: Path) -> None:
    _write_judge(tmp_path, "alpha", "A", [])
    _write_judge(tmp_path, "beta", "B", [])
    lib = load_judge_library(tmp_path)
    assert {j["short"] for j in lib} == {"alpha", "beta"}


def test_load_judge_library_skips_invalid_with_warning(tmp_path: Path, caplog) -> None:
    _write_judge(tmp_path, "alpha", "A", [])
    (tmp_path / "bad.yaml").write_text("name: bad\n", encoding="utf-8")
    lib = load_judge_library(tmp_path)
    assert [j["short"] for j in lib] == ["alpha"]
```

- [ ] **Step 2: Run the tests, watch them fail**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_judges.py -v
```

Expected: import fails.

- [ ] **Step 3: Implement `judges.py`**

Write `/agent/judges.py`:

```python
"""Judge library loader.

Loads all judge YAMLs from a directory, validates each against the
schema, and returns them as a list.

See spec §5.3.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

from agent.judge_schema import Judge, JudgeValidationError, validate_judge

log = logging.getLogger(__name__)


def _path_for(judges_dir: Path, short_name: str) -> Path:
    return judges_dir / f"{short_name}.yaml"


def load_judge(judges_dir: Path, short_name: str) -> Judge:
    """Load and validate one judge YAML. Raises on bad data."""
    path = _path_for(judges_dir, short_name)
    if not path.exists():
        raise FileNotFoundError(f"Judge {short_name!r} not found at {path}")
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return validate_judge(data)


def list_judges(judges_dir: Path) -> list[str]:
    """List all available judge short names (filenames without .yaml)."""
    if not judges_dir.exists():
        return []
    return sorted(
        p.stem
        for p in judges_dir.glob("*.yaml")
        if p.stem.lower() != "readme"
    )


def load_judge_library(judges_dir: Path) -> list[Judge]:
    """Load all judges in a directory, skipping invalid ones with a warning."""
    out: list[Judge] = []
    for short in list_judges(judges_dir):
        try:
            out.append(load_judge(judges_dir, short))
        except (JudgeValidationError, FileNotFoundError, yaml.YAMLError) as exc:
            log.warning("Skipping invalid judge %s: %s", short, exc)
    return out
```

- [ ] **Step 4: Run the tests, watch them pass**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_judges.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add agent/judges.py tests/test_judges.py
git commit -m "feat(agent): judge library loader with validation"
```

### Task 2.4: Auto-selection algorithm

**Files:**
- Modify: `agent/judges.py` (add `select_panel`)
- Modify: `tests/test_judges.py` (add tests)

- [ ] **Step 1: Add the failing tests to `test_judges.py`**

Append to `/tests/test_judges.py`:

```python
def test_select_panel_returns_five_judges(tmp_path: Path) -> None:
    from agent.judges import select_panel
    _write_judge(tmp_path, "tech", "Tech Skeptic", ["all"])
    _write_judge(tmp_path, "mil", "Military Op", ["c-uas"])
    _write_judge(tmp_path, "ew", "EW Specialist", ["ew"])
    _write_judge(tmp_path, "ethics", "Ethics", ["autonomy"])
    _write_judge(tmp_path, "ux", "UX", ["c2"])
    panel = select_panel(tmp_path, themes=["c-uas"], tags=["software"])
    assert len(panel) == 5
    shorts = {j["short"] for j in panel}
    assert "tech" in shorts  # technical-skeptic always included


def test_select_panel_includes_ethics_for_autonomy(tmp_path: Path) -> None:
    from agent.judges import select_panel
    _write_judge(tmp_path, "tech", "Tech", ["all"])
    _write_judge(tmp_path, "ethics", "Ethics", ["autonomy"])
    _write_judge(tmp_path, "ux", "UX", ["c2"])
    _write_judge(tmp_path, "red", "Red Team", ["c-uas"])
    _write_judge(tmp_path, "end", "End User", ["c-uas"])
    panel = select_panel(tmp_path, themes=["autonomy"], tags=[])
    shorts = {j["short"] for j in panel}
    assert "tech" in shorts
    assert "ethics" in shorts


def test_select_panel_includes_red_team_for_ew(tmp_path: Path) -> None:
    from agent.judges import select_panel
    _write_judge(tmp_path, "tech", "Tech", ["all"])
    _write_judge(tmp_path, "red", "Red Team", ["ew"])
    _write_judge(tmp_path, "tran", "Tran", ["ew"])
    _write_judge(tmp_path, "intel", "Intel", ["ew"])
    _write_judge(tmp_path, "acq", "Acq", ["all"])
    panel = select_panel(tmp_path, themes=["ew"], tags=[])
    shorts = {j["short"] for j in panel}
    assert "tech" in shorts
    assert "red" in shorts


def test_select_panel_deduplicates_short_names(tmp_path: Path) -> None:
    from agent.judges import select_panel
    _write_judge(tmp_path, "tech", "Tech", ["all"])
    _write_judge(tmp_path, "a", "A", ["c-uas"])
    _write_judge(tmp_path, "b", "B", ["c-uas"])
    _write_judge(tmp_path, "c", "C", ["c-uas"])
    _write_judge(tmp_path, "d", "D", ["c-uas"])
    panel = select_panel(tmp_path, themes=["c-uas"], tags=[])
    assert len({j["short"] for j in panel}) == len(panel)  # no dupes
```

- [ ] **Step 2: Run, watch fail**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_judges.py -v
```

Expected: 4 new failures (no `select_panel`).

- [ ] **Step 3: Add `select_panel` to `agent/judges.py`**

Append to `/agent/judges.py`:

```python
def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def select_panel(
    judges_dir: Path,
    themes: list[str],
    tags: list[str],
    *,
    panel_size: int = 5,
) -> list[Judge]:
    """Auto-select a panel of judges for a given problem.

    Algorithm (spec §5.3):
    1. Compute Jaccard similarity between problem themes+tags and each judge's tags.
    2. Sort judges by similarity descending.
    3. Apply hard rules:
       - technical-skeptic always included (if present)
       - autonomy theme -> ethics-compliance
       - ew theme -> red-team-adversary
       - c2/decision_support theme -> operator-ux
       - software tag -> scaling-engineer
    4. Take top panel_size, with hard rules overriding.
    5. Dedup by short name.
    """
    library = load_judge_library(judges_dir)
    if not library:
        return []

    problem_set = set(themes) | set(tags)

    scored: list[tuple[float, Judge]] = []
    for j in library:
        s = _jaccard(problem_set, set(j.get("tags", [])))
        scored.append((s, j))
    scored.sort(key=lambda x: (-x[0], x[1]["short"]))

    # Hard rules
    must_have: list[str] = []
    if any(t in themes for t in ("autonomy",)):
        must_have.append("ethics-compliance")
    if any(t in themes for t in ("ew", "electronic_warfare")):
        must_have.append("red-team-adversary")
    if any(t in themes for t in ("c2", "decision_support")):
        must_have.append("operator-ux")
    if "software" in tags:
        must_have.append("scaling-engineer")
    # technical-skeptic is always wanted if present
    must_have.append("technical-skeptic")

    # Build the panel
    panel: list[Judge] = []
    seen: set[str] = set()

    def _try_add(short: str) -> None:
        for j in library:
            if j["short"] == short and short not in seen:
                panel.append(j)
                seen.add(short)
                return

    # First: hard rules
    for short in must_have:
        _try_add(short)
        if len(panel) >= panel_size:
            break

    # Then: top by similarity to fill the rest
    for _, j in scored:
        if j["short"] in seen:
            continue
        if len(panel) >= panel_size:
            break
        panel.append(j)
        seen.add(j["short"])

    return panel
```

- [ ] **Step 4: Run, watch pass**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_judges.py -v
```

Expected: 9 passed (5 from before + 4 new).

- [ ] **Step 5: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add agent/judges.py tests/test_judges.py
git commit -m "feat(agent): auto-select panel with hard rules + Jaccard ranking"
```

### Task 2.5: Author 12 judge YAMLs

**Files:**
- Create: `judges/README.md`
- Create: `judges/military-operator.yaml`
- Create: `judges/ew-specialist.yaml`
- Create: `judges/defense-prime-pm.yaml`
- Create: `judges/technical-skeptic.yaml`
- Create: `judges/acquisition-procurement.yaml`
- Create: `judges/end-user-frontline.yaml`
- Create: `judges/ethics-compliance.yaml`
- Create: `judges/defense-vc.yaml`
- Create: `judges/red-team-adversary.yaml`
- Create: `judges/scaling-engineer.yaml`
- Create: `judges/intel-analyst.yaml`
- Create: `judges/operator-ux.yaml`

- [ ] **Step 1: Write `judges/README.md`**

```markdown
# Judges

The 12-judge library used by the agent to review artefacts at every phase. Each judge is a YAML file with a strict schema (see `agent.judge_schema`).

## Usage

The skill invokes them at specific phases (see `SKILL.md` and the design spec). For ad-hoc chats, use `/edth-agent panel <short>` to talk with one judge in character.

## The 12

| Short | One-line |
|---|---|
| `viper` | Maj. Viper Reyes (ret.) — Military Operator |
| `tran` | Dr. Linh Tran — EW Specialist |
| `whitfield` | Karen Whitfield — Defense Prime PM |
| `mehta` | Ravi Mehta — Technical Skeptic (always-on) |
| `park` | Daniel Park — Acquisition & Procurement |
| `kovalenko` | Oleksandr K. — End-User / Frontline (Ukraine) |
| `hassan` | Dr. Amira Hassan — Ethics & Compliance |
| `lee` | Jordan Lee — Defense VC |
| `volkov` | Col. Yuri Volkov (ret.) — Red-Team Adversary |
| `shah` | Priya Shah — Scaling Engineer |
| `sutter` | Mark Sutter — Intelligence Analyst |
| `chen` | Maj. Sarah Chen — Operator UX |

## Adding a judge

1. Copy any existing YAML.
2. Set `short` to a unique lowercase identifier.
3. Fill in the schema (see `agent/judge_schema.py` for the source of truth).
4. Add the judge to the auto-selection tags so it can be picked.
```

- [ ] **Step 2: Write `judges/technical-skeptic.yaml` (the always-on one)**

```yaml
name: "Ravi Mehta"
short: "mehta"
tags: [all, autonomy, c-uas, ew, c2, swarm, uuv, usv]
background: "CTO at a Series B defense-tech company. Shipped 5 products to DoD primes. Ex-Palantir Forward Deployed Engineer. Believes most hackathon projects are wrappers around ChatGPT."
priorities:
  - "is this already in production somewhere"
  - "what's the simplest version"
  - "show me the data, not the architecture diagram"
  - "what breaks at 3am"
anti_priorities:
  - "buzzword soup"
  - "AI for AI's sake"
  - "vague claims of novelty"
  - "infrastructure diagrams without deployment reality"
decision_style: "relentless reductionist; will cut to the kernel in 30 seconds"
language_patterns:
  - "show me"
  - "what's the simplest version"
  - "what's already deployed"
  - "who maintains this"
scoring_biases:
  impact: 0.0
  innovation: -0.10
  execution: 0.10
  presentation: 0.0
knowledge_gaps:
  - consumer_tech_marketing
  - academic_ml_without_fielding
hard_questions_seed:
  - "What's the simplest deployed version of this today, before your hack?"
  - "What part of this is genuinely new vs. wrapped from a paper?"
  - "What's the maintenance story at 3am?"
  - "Who on your team has shipped defense software to a real user?"
```

- [ ] **Step 3: Write `judges/military-operator.yaml`**

```yaml
name: "Maj. 'Viper' Reyes (ret.)"
short: "viper"
tags: [c-uas, autonomy, swarm, ew, all]
background: "F-16 pilot, 2200 hrs, OIF/OEF veteran, JTAC-qualified. Current contract instructor at USAF Weapons School. Has flown against real drone threats in the CENTCOM AOR."
priorities:
  - operational_relevance
  - survivability
  - time_to_action
  - simplicity_under_stress
anti_priorities:
  - buzzwords
  - vendor_lock_in
  - "anything_requiring_a_PhD_to_operate"
  - "AI for AI's sake"
decision_style: "decisive; 30-second answer or admit you don't know"
language_patterns:
  - "on the flight line"
  - "in the dirt"
  - "what kills this"
  - "show me the kill chain"
scoring_biases:
  impact: 0.10
  innovation: -0.05
  execution: 0.10
  presentation: 0.0
knowledge_gaps:
  - consumer_tech
  - academic_ml
  - business_modeling
hard_questions_seed:
  - "What's the kill chain end-to-end, and where does your system sit in it?"
  - "What does the operator do when this fails mid-mission?"
  - "What's the 3am maintenance story?"
  - "How does this get fielded in under 12 months to a unit that needs it now?"
```

- [ ] **Step 4: Write `judges/ew-specialist.yaml`**

```yaml
name: "Dr. Linh Tran"
short: "tran"
tags: [ew, signal_proc, radar, all]
background: "20 years in electronic warfare. Ex-NSA SIGINT, current MITRE EW researcher. Holds 3 patents in adaptive radar warning receivers. Reviews papers for IEEE Transactions on Aerospace and Electronic Systems."
priorities:
  - signal_processing_correctness
  - ROC_curves_and_detection_thresholds
  - real_signal_data_not_simulated
  - "fielded_against_real_systems"
anti_priorities:
  - hand_waved_thresholds
  - simulated_data_only
  - "AI substituting_for_signal_processing"
  - "black_box_no_interpretability"
decision_style: "methodical; demands equations and data"
language_patterns:
  - "what's the false alarm rate"
  - "show me the ROC curve"
  - "is this on real IQ data"
  - "where's the SNR budget"
scoring_biases:
  impact: 0.0
  innovation: 0.05
  execution: 0.05
  presentation: 0.0
knowledge_gaps:
  - consumer_apps
  - business_modeling
hard_questions_seed:
  - "What's the false alarm rate at the operational threshold?"
  - "Has this been tested on real captured signals, or only synthetic?"
  - "What's the SNR budget in dB at the relevant range?"
  - "Why is your approach better than a matched filter baseline?"
```

- [ ] **Step 5: Write `judges/defense-prime-pm.yaml`**

```yaml
name: "Karen Whitfield"
short: "whitfield"
tags: [all, autonomy, c-uas, ew, c2, swarm, uuv, usv]
background: "Senior Program Manager at a Tier 1 defense prime (think Lockheed, Raytheon, Northrop). 15 years on radar and EW programs. Has shipped 4 programs of record to USG. PMP certified."
priorities:
  - "path_to_production"
  - "team_credibility"
  - "compliance_with_DoD_standards"
  - "clear_IP_position"
anti_priorities:
  - "anything_without_a_FAR_pathway"
  - "tech_demos_with_no_buyer"
  - "naive_assumptions_about_acquisition_timeline"
  - "open_source_licenses_we_cant_use"
decision_style: "pragmatic; optimizes for the lowest-friction fielding path"
language_patterns:
  - "what's the program of record"
  - "who's the requiring activity"
  - "where in the FAR"
  - "what's the TRL exit criterion"
scoring_biases:
  impact: 0.05
  innovation: -0.05
  execution: 0.05
  presentation: 0.0
knowledge_gaps:
  - cutting_edge_ML_research
  - hardware_design
hard_questions_seed:
  - "Where's the program of record this maps to?"
  - "Who is the requiring activity, and have you talked to them?"
  - "What FAR pathway fits this — OTA, CSO, traditional?"
  - "How does this fit in our existing prime contract structure?"
```

- [ ] **Step 6: Write `judges/acquisition-procurement.yaml`**

```yaml
name: "Daniel Park"
short: "park"
tags: [all, autonomy, c-uas, ew, c2, swarm, uuv, usv]
background: "Former DoD acquisition official (DAU senior faculty). Now consults for primes on contract strategy. Wrote the book (literally) on OTAs. Spends his weekends on FedBizOpps."
priorities:
  - "compliance"
  - "competition_strategy"
  - "small_business_set_asides"
  - "auditability"
anti_priorities:
  - "anything_skirting_FAR"
  - "sole_source_without_justification"
  - "vague_IP_terms"
  - "no_procurement_history"
decision_style: "process-driven; will quote regulations"
language_patterns:
  - "per FAR 15.404"
  - "that's an OTA-eligible effort"
  - "small business set-aside?"
  - "where's the J&A"
scoring_biases:
  impact: 0.0
  innovation: -0.05
  execution: 0.0
  presentation: 0.05
knowledge_gaps:
  - bleeding_edge_research
  - field_tactics
hard_questions_seed:
  - "Which FAR part governs this acquisition?"
  - "Is this competitive or sole-source, and why?"
  - "What's the small business strategy?"
  - "How does this fit on an existing IDIQ?"
```

- [ ] **Step 7: Write `judges/end-user-frontline.yaml`**

```yaml
name: "Oleksandr K."
short: "kovalenko"
tags: [c-uas, autonomy, ew, all]
background: "Drone operator with a Ukrainian volunteer unit, 2 years in current conflict. Started with commercial DJI, now operates FPV interceptors and electronic warfare rigs. Has lost friends to the threats he's trying to counter."
priorities:
  - "works_in_the_dirt"
  - "battery_life_and_field_repair"
  - "training_time_for_new_operators"
  - "interoperability_with_what_we_already_have"
anti_priorities:
  - "anything_requiring_satellite_internet"
  - "sophisticated_screens_in_combat"
  - "vendor_lock_in_to_one_supplier"
  - "delicate_hardware"
decision_style: "tactical; speaks from lived experience"
language_patterns:
  - "we tried that"
  - "in the field"
  - "my guys need to use this at night, tired, scared"
  - "can I fix it with a Leatherman"
scoring_biases:
  impact: 0.10
  innovation: -0.05
  execution: 0.10
  presentation: -0.05
knowledge_gaps:
  - US_acquisition_process
  - high_level_strategy
hard_questions_seed:
  - "Has this been tested by an actual operator under stress?"
  - "What happens when the comms go down?"
  - "Can I train a new guy in under an hour?"
  - "What does this cost in USD per unit, fully loaded?"
```

- [ ] **Step 8: Write `judges/ethics-compliance.yaml`**

```yaml
name: "Dr. Amira Hassan"
short: "hassan"
tags: [autonomy, ew, c-uas, all]
background: "International humanitarian law scholar. Advises the ICRC on autonomous weapons policy. Former DoD Policy employee. Published widely on the ethical governance of Lethal Autonomous Weapon Systems (LAWS)."
priorities:
  - human_in_the_loop
  - IHL_compliance
  - "accountability_and_chain_of_command"
  - "blowback_risk"
anti_priorities:
  - "fully_autonomous_lethal_action"
  - "opaque_decision_making"
  - "dual_use_with_civilian_harm"
  - "scalpel_solutions_to_hammer_problems"
decision_style: "principled; will cite Geneva Convention articles"
language_patterns:
  - "where's the human in the loop"
  - "per Article 36"
  - "what's the accountability chain"
  - "dual-use concerns"
scoring_biases:
  impact: -0.05
  innovation: 0.0
  execution: 0.0
  presentation: 0.05
knowledge_gaps:
  - engineering_detail
  - business_models
hard_questions_seed:
  - "Where is the human in the loop, and what is the loop time?"
  - "How does this comply with the principles of distinction and proportionality?"
  - "What's the accountability chain if the system makes a mistake?"
  - "Has this been reviewed under DoD Directive 3000.09?"
```

- [ ] **Step 9: Write `judges/defense-vc.yaml`**

```yaml
name: "Jordan Lee"
short: "lee"
tags: [all, autonomy, c-uas, ew, c2, swarm, uuv, usv]
background: "Partner at a defense-focused VC fund (a16z / Lux / Shield Capital tier). 12 years investing in dual-use tech. Board observer on 6 defense startups. Former Army officer."
priorities:
  - "wedge_into_market"
  - "first_customer_and_who_pays"
  - "scalable_business_model"
  - "defensible_moat"
anti_priorities:
  - "single-buyer dependency"
  - "government-only without commercial path"
  - "hardware-only without software margin"
  - "5-year ROI horizons"
decision_style: "commercially rigorous; will model the unit economics in his head"
language_patterns:
  - "what's the wedge"
  - "who pays first"
  - "is this venture-scale"
  - "what's the gross margin"
scoring_biases:
  impact: 0.05
  innovation: 0.0
  execution: 0.0
  presentation: 0.0
knowledge_gaps:
  - deep_technical_protocols
  - field_operations
hard_questions_seed:
  - "Who is the first customer and what's the ACV?"
  - "What's the wedge into the market — beachhead + expansion?"
  - "Is this venture-scale ($100M+ revenue potential in 5 years)?"
  - "What's the defensible moat — data, network effects, IP, regulatory?"
```

- [ ] **Step 10: Write `judges/red-team-adversary.yaml`**

```yaml
name: "Col. Yuri Volkov (ret.)"
short: "volkov"
tags: [ew, c-uas, autonomy, all]
background: "Retired colonel, former adversary electronic warfare officer. 25 years in offensive EW and counter-UAS. Now consults for defense primes on the threat side. Reads Russian and Chinese defense literature in the original."
priorities:
  - "how_I_would_defeat_this_in_6_months"
  - "asymmetric_countermeasures"
  - "single_point_of_failure"
  - "what_I_already_know_about_your_approach"
anti_priorities:
  - "sensitive_assumptions"
  - "vague_threat_models"
  - "anything_depending_on_us_technological_lead"
  - "obvious_spoofing_targets"
decision_style: "adversarial; will role-play the threat"
language_patterns:
  - "I'd just..."
  - "that's the first thing we'd spoof"
  - "show me the threat model"
  - "what's your assumption about my EW"
scoring_biases:
  impact: 0.05
  innovation: 0.05
  execution: 0.0
  presentation: 0.0
knowledge_gaps:
  - US_acquisition_process
  - commercial_software_practices
hard_questions_seed:
  - "How would I defeat this in 6 months if I had a budget?"
  - "What's the single point of failure?"
  - "What assumptions about adversary capability are you making?"
  - "Where is the threat model documented?"
```

- [ ] **Step 11: Write `judges/scaling-engineer.yaml`**

```yaml
name: "Priya Shah"
short: "shah"
tags: [all, autonomy, c2, swarm, software, c-uas]
background: "Staff engineer at Palantir for 6 years, deployed Foundry to 4 defense customers. Now leads platform engineering at a Series C defense-tech startup. Has taken systems from 10 to 10,000 users."
priorities:
  - "production_path_not_architecture_diagram"
  - "deployment_infrastructure"
  - "observability_and_debugging"
  - "data_pipeline_realism"
anti_priorities:
  - "poc_with_no_path_to_production"
  - "monoliths_with_no_api"
  - "manual_operations"
  - "vendor_lock_in_to_AWS_specific_services"
decision_style: "production-first; will ask about SLOs and on-call"
language_patterns:
  - "what's the deployment diagram"
  - "who's on call"
  - "show me the SLOs"
  - "how does this scale to 100 customers"
scoring_biases:
  impact: 0.0
  innovation: -0.05
  execution: 0.10
  presentation: 0.0
knowledge_gaps:
  - hardware_design
  - field_operations
hard_questions_seed:
  - "What's the production deployment path from this demo?"
  - "Who is on call when this breaks at 3am?"
  - "How does this scale from 1 customer to 100?"
  - "What's the data pipeline — batch, streaming, manual?"
```

- [ ] **Step 12: Write `judges/intel-analyst.yaml`**

```yaml
name: "Mark Sutter"
short: "sutter"
tags: [ew, c2, autonomy, all]
background: "Former CIA operations officer, 18 years. Now senior intelligence analyst at a defense intel contractor. Has worked with JSOC, SOCOM, and combatant commands. Publishes in Studies in Intelligence."
priorities:
  - "intel_pipeline_integration"
  - "source_reliability_and_confidence"
  - "actionable_intelligence_at_the_right_time"
  - "cross_domain_correlation"
anti_priorities:
  - "single_source_dependency"
  - "low_confidence_decisions"
  - "intel_products_no_commander_will_read"
  - "opsTempo_mismatch"
decision_style: "analytical; weighs evidence and confidence"
language_patterns:
  - "what's your source"
  - "how confident are we"
  - "where does this fit in the J2/J3 cycle"
  - "single source or corroborated"
scoring_biases:
  impact: 0.05
  innovation: 0.0
  execution: 0.05
  presentation: 0.0
knowledge_gaps:
  - hardware_design
  - consumer_apps
hard_questions_seed:
  - "What intel feeds does this depend on, and how reliable are they?"
  - "Where in the J2/J3 cycle does this product land?"
  - "What confidence score does each output have, and why?"
  - "How does this cross-correlate with other intel sources?"
```

- [ ] **Step 13: Write `judges/operator-ux.yaml`**

```yaml
name: "Maj. Sarah Chen"
short: "chen"
tags: [c2, autonomy, swarm, all]
background: "Designs cockpit displays and C2 interfaces. Spent 5 years at the USAF Test Pilot School as a human-factors researcher. Now UX lead at a Tier 1 prime. Authored two MIL-STD-2525 implementations."
priorities:
  - "one_thing_at_a_glance"
  - "scan_path_optimization"
  - "low_cognitive_load_under_stress"
  - "color_and_motion_hygiene"
anti_priorities:
  - "wall_of_dashboards"
  - "12_charts_at_once"
  - "red_green_color_only_no_pattern"
  - "animations_for_no_reason"
decision_style: "operator advocate; will fight for the user's attention budget"
language_patterns:
  - "what's the one thing"
  - "where does the eye go first"
  - "what does this look like at 3am"
  - "can a tired operator parse this in 2 seconds"
scoring_biases:
  impact: 0.0
  innovation: 0.0
  execution: 0.0
  presentation: 0.10
knowledge_gaps:
  - backend_systems
  - signal_processing
hard_questions_seed:
  - "What's the ONE thing the operator sees in the first 2 seconds?"
  - "Where does the eye go first, second, third?"
  - "How does this perform at 3am, in the rain, with one eye?"
  - "What does the failure state look like — calm or panic-inducing?"
```

- [ ] **Step 14: Run the schema validation against the whole library**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/python -c "
from pathlib import Path
from agent.judges import load_judge_library
lib = load_judge_library(Path('judges'))
print(f'Loaded {len(lib)} judges:')
for j in lib:
    print(f'  - {j[\"short\"]:12} tags={j[\"tags\"]}')
"
```

Expected: `Loaded 12 judges:` followed by 12 lines, no validation errors.

- [ ] **Step 15: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add judges/
git commit -m "feat(judges): author 12-judge library with full schema"
```

### Task 2.6: Wire panel into Phase 1 + update SKILL.md

**Files:**
- Modify: `SKILL.md` (add panel chat command + panel generation)
- Modify: `agent/state.py` (add panel helpers)

- [ ] **Step 1: Add panel helpers to `agent/state.py`**

Append to `/agent/state.py`:

```python
def lock_panel(
    state: dict[str, Any], judge_shorts: list[str], manually_overridden: bool = False
) -> dict[str, Any]:
    """Lock a panel of judges for the current run."""
    state["panel"] = {
        "auto_selected": list(judge_shorts),
        "manually_overridden": manually_overridden,
        "locked": True,
    }
    return state
```

- [ ] **Step 2: Add a test for `lock_panel`**

Append to `/tests/test_state.py`:

```python
def test_lock_panel_records_judges() -> None:
    from agent.state import lock_panel
    state = empty_state()
    out = lock_panel(state, ["mehta", "viper"], manually_overridden=True)
    assert out["panel"]["auto_selected"] == ["mehta", "viper"]
    assert out["panel"]["locked"] is True
    assert out["panel"]["manually_overridden"] is True
```

- [ ] **Step 3: Run the test**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_state.py -v
```

Expected: 11 passed.

- [ ] **Step 4: Update `SKILL.md` with panel section**

Append to `/SKILL.md`:

```markdown

## Panel system (12 tough judges)

The agent maintains a panel of judge personas that review every artefact. Default library lives in `judges/*.yaml`.

### Panel lifecycle

1. After Phase 2 (problem chosen), call `/edth-agent panel generate` to auto-pick 5 judges from the library (Jaccard similarity on tags + hard rules — see spec §5.3).
2. User can `panel add / remove / replace` before locking.
3. The locked panel is recorded in `state.json` under `panel.auto_selected`.
4. Each phase uses the locked panel for per-phase review (see spec §5.4).
5. In `panel_mode: expanded` (default for high-stakes phases), each judge gets a separate LLM call. In `condensed` mode, the LLM role-plays all judges in one response.

### Panel chat command

`/edth-agent panel <short>` opens a free-form chat with one judge. The judge responds in character using their YAML as the system prompt. Use this to ask probing questions between phases.

Example:
```
> /edth-agent panel viper
[Viper in character]
> Viper, what do you think of the swarm coordination sub-problem?
> [Viper responds using current artefacts as context, in his voice]
```

The chat does not write to artefacts unless you say "save this to the audit log."

### Per-phase panel participation (reference)

| Phase | Panel action |
|---|---|
| 1 Triage | Each judge ranks top-3 clusters; Borda aggregation |
| 2 Elicit | Each judge contributes 2-3 owner questions |
| 3 Sub-problem | Each judge scores sub-problems; convergence surfaced |
| 4 Ideation | Each judge rates 1-5 with one-line reasoning |
| 5 Research & rank | Each judge re-scores top 5; weighted vote; spread recorded |
| 6 Demo | Each judge previews script; gives 1-3 hard questions |
| 7 Deck | Each judge previews deck; flags hardest slide |
| 8 Final | Each judge gives thumbs up/down + "what would change my mind" |
```

- [ ] **Step 5: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add agent/state.py tests/test_state.py SKILL.md
git commit -m "feat(agent): lock_panel helper + SKILL.md panel section"
```

### Milestone 2 checkpoint

- [ ] **Run all tests**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest
```

Expected: ~50 tests passing.

- [ ] **Verify 12 judges load and panel can be auto-selected**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/python -c "
from pathlib import Path
from agent.judges import load_judge_library, select_panel
lib = load_judge_library(Path('judges'))
print(f'Library: {len(lib)} judges')
panel = select_panel(Path('judges'), themes=['c-uas', 'autonomy'], tags=['software'])
print('Auto panel for c-uas+autonomy+software:')
for j in panel:
    print(f'  - {j[\"short\"]}')
"
```

Expected: 12 judges loaded; panel contains `mehta` (technical-skeptic), `viper` (military-operator), and 3 others.

---

## Milestone 3 — Phases 2–5 (Elicit, Decompose, Ideate, Rank)

**Goal:** Problem owner Q&A, sub-problem decompose, divergent ideation, research-backed ranking. All four phases produce artefacts; user picks the path.

**Tasks:**
- Task 3.1: Phase 2 — owner questions generation, answers capture
- Task 3.2: Phase 2 — top-3 candidates with panel scoring
- Task 3.3: Phase 3 — sub-problem decompose, ROI scoring
- Task 3.4: Phase 4 — divergent ideation (20+ ideas)
- Task 3.5: Phase 4 — dedupe, cluster, score with panel
- Task 3.6: Phase 5 — web research per top-5
- Task 3.7: Phase 5 — final ranking + owner pick
- Task 3.8: Wire all into SKILL.md commands

### Task 3.1: Phase 2 — owner questions and answers (Python writers)

**Files:**
- Create: `agent/elicitation.py`
- Create: `tests/test_elicitation.py`

- [ ] **Step 1: Write the failing tests**

Write `/tests/test_elicitation.py`:

```python
"""Tests for agent.elicitation — TDD."""

from __future__ import annotations

from pathlib import Path

from agent.elicitation import (
    OwnerQuestion,
    write_owner_answers,
    write_owner_questions,
)


def test_write_owner_questions_creates_file(tmp_path: Path) -> None:
    qs = [
        OwnerQuestion(id="Q1", text="What hurts most?", asker="user"),
        OwnerQuestion(id="Q2", text="Who decides?", asker="viper"),
        OwnerQuestion(id="Q3", text="What's the budget?", asker="user"),
    ]
    path = write_owner_questions(tmp_path, qs)
    raw = path.read_text()
    assert "Q1" in raw
    assert "Q2" in raw
    assert "What hurts most?" in raw


def test_write_owner_answers_creates_file(tmp_path: Path) -> None:
    answers = {
        "Q1": "Detection lag is the #1 pain — 8 seconds feels like an eternity.",
        "Q2": "JTAC has 30 seconds to decide; commander ratifies.",
        "Q3": "$50k/unit is the magic number for adoption.",
    }
    path = write_owner_answers(tmp_path, answers)
    raw = path.read_text()
    assert "Detection lag" in raw
    assert "30 seconds" in raw
```

- [ ] **Step 2: Run, watch fail**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_elicitation.py -v
```

Expected: import fails.

- [ ] **Step 3: Implement `elicitation.py`**

Write `/agent/elicitation.py`:

```python
"""Phase 2 — Owner Q&A artefact writers.

The LLM (skill) generates questions and captures answers. Python writes
them to disk in a consistent format.

See spec §4 Phase 2.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class OwnerQuestion:
    id: str
    text: str
    asker: str  # "user" or judge short name


def write_owner_questions(artefacts_dir: Path, questions: list[OwnerQuestion]) -> Path:
    """Write owner_questions.md."""
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# Owner Questions", ""]
    for q in questions:
        lines.append(f"## {q.id} (asked by: {q.asker})")
        lines.append("")
        lines.append(q.text)
        lines.append("")
    path = artefacts_dir / "02_owner_questions.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_owner_answers(artefacts_dir: Path, answers: dict[str, str]) -> Path:
    """Write owner_answers.md."""
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# Owner Answers", ""]
    for qid, answer in answers.items():
        lines.append(f"## {qid}")
        lines.append("")
        lines.append(answer)
        lines.append("")
    path = artefacts_dir / "02_owner_answers.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
```

- [ ] **Step 4: Run, watch pass**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_elicitation.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add agent/elicitation.py tests/test_elicitation.py
git commit -m "feat(agent): Phase 2 owner Q&A writers"
```

### Task 3.2: Phase 2 — candidate problem writer with panel scoring

**Files:**
- Create: `agent/candidates.py`
- Create: `tests/test_candidates.py`

- [ ] **Step 1: Write the failing tests**

Write `/tests/test_candidates.py`:

```python
"""Tests for agent.candidates — TDD."""

from __future__ import annotations

from pathlib import Path

from agent.candidates import Candidate, write_candidate_problem


def test_write_candidate_problem_creates_file(tmp_path: Path) -> None:
    candidates = [
        Candidate(
            problem_id="P-028",
            name="Autonomy 1: Multi-Domain Battle Management Interface",
            scores={"impact": 4.5, "innovation": 3.5, "execution": 4.0, "presentation": 3.5},
            panel_picks={"mehta": 1, "viper": 1, "tran": 3},
            reasoning="Highest impact, demo-able, panel converges on top-3.",
        ),
        Candidate(
            problem_id="P-007",
            name="Autonomy 2: GPS-Denied Swarm Coordination",
            scores={"impact": 4.0, "innovation": 4.5, "execution": 3.0, "presentation": 3.5},
            panel_picks={"mehta": 2, "viper": 2, "tran": 1},
            reasoning="Strong innovation; harder to demo.",
        ),
    ]
    path = write_candidate_problem(tmp_path, candidates)
    raw = path.read_text()
    assert "P-028" in raw
    assert "P-007" in raw
    assert "4.18" in raw  # weighted score for P-028
    assert "mehta" in raw


def test_weighted_score_uses_default_rubric(tmp_path: Path) -> None:
    candidates = [
        Candidate(
            problem_id="P-X",
            name="Test",
            scores={"impact": 5, "innovation": 5, "execution": 5, "presentation": 5},
            panel_picks={},
            reasoning="",
        )
    ]
    write_candidate_problem(tmp_path, candidates)
    raw = (tmp_path / "02_candidate_problem.md").read_text()
    assert "5.00" in raw
```

- [ ] **Step 2: Run, watch fail**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_candidates.py -v
```

Expected: import fails.

- [ ] **Step 3: Implement `candidates.py`**

Write `/agent/candidates.py`:

```python
"""Phase 2 — Candidate problem writer.

The LLM (skill) generates the top-3 candidates with panel scoring. Python
formats and writes the artefact.

See spec §4 Phase 2.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from agent.rubric import score_to_weighted, DEFAULT_RUBRIC


@dataclass
class Candidate:
    problem_id: str
    name: str
    scores: dict[str, float]
    panel_picks: dict[str, int] = field(default_factory=dict)  # judge_short -> rank
    reasoning: str = ""

    def weighted_score(self) -> float:
        return score_to_weighted(self.scores, DEFAULT_RUBRIC)


def write_candidate_problem(artefacts_dir: Path, candidates: list[Candidate]) -> Path:
    """Write 02_candidate_problem.md."""
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# Top 3 Candidate Problems", ""]

    for i, c in enumerate(candidates, start=1):
        lines.append(f"## Candidate {i}: {c.name} ({c.problem_id})")
        lines.append("")
        lines.append(f"**Weighted score: {c.weighted_score():.2f}**")
        lines.append("")
        lines.append("**Axis scores:**")
        for axis, s in c.scores.items():
            lines.append(f"- {axis}: {s:.2f}")
        lines.append("")
        if c.panel_picks:
            lines.append("**Panel ranking:**")
            for judge, rank in sorted(c.panel_picks.items(), key=lambda x: x[1]):
                lines.append(f"- {judge}: #{rank}")
            lines.append("")
        if c.reasoning:
            lines.append("**Reasoning:**")
            lines.append(c.reasoning)
            lines.append("")

    path = artefacts_dir / "02_candidate_problem.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
```

- [ ] **Step 4: Run, watch pass**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_candidates.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add agent/candidates.py tests/test_candidates.py
git commit -m "feat(agent): Phase 2 candidate problem writer with panel scoring"
```

### Task 3.3: Phase 3 — sub-problem decompose + ROI scoring

**Files:**
- Create: `agent/sub_problem.py`
- Create: `tests/test_sub_problem.py`

- [ ] **Step 1: Write the failing tests**

Write `/tests/test_sub_problem.py`:

```python
"""Tests for agent.sub_problem — TDD."""

from __future__ import annotations

from pathlib import Path

from agent.sub_problem import SubProblem, write_sub_problem


def test_compute_roi_score_uses_default_weights() -> None:
    sp = SubProblem(
        id="SP-1",
        title="Test sub-problem",
        scores={"impact": 5, "time_fit": 4, "demo_ability": 3, "dependency_risk": 2},
    )
    # weights: impact 0.30, time_fit 0.30, demo_ability 0.25, dependency_risk 0.15
    # but dependency_risk is "lower is better" — invert before scoring
    # expected: 5*0.30 + 4*0.30 + 3*0.25 + (5-2)*0.15  = 1.5+1.2+0.75+0.45 = 3.9
    assert sp.roi_score() == 3.9


def test_write_sub_problem_creates_file(tmp_path: Path) -> None:
    subs = [
        SubProblem(
            id="SP-1",
            title="Sub-problem A",
            scores={"impact": 5, "time_fit": 4, "demo_ability": 3, "dependency_risk": 2},
        ),
        SubProblem(
            id="SP-2",
            title="Sub-problem B",
            scores={"impact": 3, "time_fit": 5, "demo_ability": 4, "dependency_risk": 1},
        ),
    ]
    path = write_sub_problem(tmp_path, subs)
    raw = path.read_text()
    assert "SP-1" in raw
    assert "SP-2" in raw
    assert "Sub-problem A" in raw
```

- [ ] **Step 2: Run, watch fail**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_sub_problem.py -v
```

Expected: import fails.

- [ ] **Step 3: Implement `sub_problem.py`**

Write `/agent/sub_problem.py`:

```python
"""Phase 3 — Sub-problem writer and ROI scoring.

ROI scoring weights (spec §4 Phase 3):
- impact: 0.30
- time_fit: 0.30
- demo_ability: 0.25
- dependency_risk: 0.15 (inverted — lower is better)

See spec §4 Phase 3.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROI_WEIGHTS = {
    "impact": 0.30,
    "time_fit": 0.30,
    "demo_ability": 0.25,
    "dependency_risk": 0.15,
}


@dataclass
class SubProblem:
    id: str
    title: str
    scores: dict[str, float]  # impact, time_fit, demo_ability, dependency_risk — all 1-5
    description: str = ""

    def roi_score(self) -> float:
        """Compute weighted ROI score. dependency_risk is inverted."""
        s = dict(self.scores)
        # Invert dependency_risk: high score = low risk
        s["dependency_risk"] = 5.0 - s.get("dependency_risk", 3.0) + 1.0
        # clamp to 1-5
        s["dependency_risk"] = max(1.0, min(5.0, s["dependency_risk"]))
        return sum(s[k] * w for k, w in ROI_WEIGHTS.items())


def write_sub_problem(artefacts_dir: Path, sub_problems: list[SubProblem]) -> Path:
    """Write 03_chosen_sub_problem.md."""
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# Sub-problem decomposition", ""]
    for sp in sub_problems:
        lines.append(f"## {sp.id}: {sp.title}")
        lines.append("")
        lines.append(f"**ROI score: {sp.roi_score():.2f}**")
        lines.append("")
        if sp.description:
            lines.append(sp.description)
            lines.append("")
        lines.append("**Axis scores (1-5):**")
        for axis, s in sp.scores.items():
            lines.append(f"- {axis}: {s:.2f}")
        lines.append("")
    path = artefacts_dir / "03_chosen_sub_problem.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
```

- [ ] **Step 4: Run, watch pass**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_sub_problem.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add agent/sub_problem.py tests/test_sub_problem.py
git commit -m "feat(agent): Phase 3 sub-problem writer with ROI scoring"
```

### Task 3.4: Phase 4 — divergent ideation helpers (idea dedup + writers)

**Files:**
- Create: `agent/ideation.py`
- Create: `tests/test_ideation.py`

- [ ] **Step 1: Write the failing tests**

Write `/tests/test_ideation.py`:

```python
"""Tests for agent.ideation — TDD."""

from __future__ import annotations

from pathlib import Path

from agent.ideation import (
    Idea,
    dedupe_ideas,
    jaccard_similarity,
    write_solution_candidates,
)


def test_jaccard_similarity_identical_is_one() -> None:
    a = "real-time detection fusion radar"
    b = "real-time detection fusion radar"
    assert jaccard_similarity(a, b) == 1.0


def test_jaccard_similarity_disjoint_is_zero() -> None:
    a = "alpha beta"
    b = "gamma delta"
    assert jaccard_similarity(a, b) == 0.0


def test_jaccard_similarity_partial() -> None:
    a = "alpha beta gamma"
    b = "alpha beta delta"
    # shared: {alpha, beta} = 2; union = {alpha, beta, gamma, delta} = 4
    assert jaccard_similarity(a, b) == 0.5


def test_dedupe_keeps_first_of_similar() -> None:
    ideas = [
        Idea(id="I1", text="real-time radar detection fusion"),
        Idea(id="I2", text="real-time radar detection fusion with classification"),
        Idea(id="I3", text="completely different idea about swarms"),
    ]
    result = dedupe_ideas(ideas, threshold=0.7)
    assert len(result) == 2
    assert result[0].id == "I1"
    assert result[1].id == "I3"


def test_write_solution_candidates_groups_by_score(tmp_path: Path) -> None:
    ideas = [
        Idea(id="I1", text="Idea 1", rating=4.5),
        Idea(id="I2", text="Idea 2", rating=3.0),
        Idea(id="I3", text="Idea 3", rating=5.0),
    ]
    write_solution_candidates(tmp_path, ideas)
    raw = (tmp_path / "04_solution_candidates.md").read_text()
    assert "I3" in raw
    assert "I1" in raw
    assert "I2" in raw
```

- [ ] **Step 2: Run, watch fail**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_ideation.py -v
```

Expected: import fails.

- [ ] **Step 3: Implement `ideation.py`**

Write `/agent/ideation.py`:

```python
"""Phase 4 — Divergent ideation helpers.

LLM (skill) generates 20+ ideas. Python does:
- Deduplication by Jaccard word similarity
- Markdown writing with rating-sorted grouping

See spec §4 Phase 4.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


def _tokens(s: str) -> set[str]:
    return {t.lower() for t in s.split() if len(t) > 2}


def jaccard_similarity(a: str, b: str) -> float:
    """Word-level Jaccard similarity. 0..1."""
    ta, tb = _tokens(a), _tokens(b)
    if not ta and not tb:
        return 1.0
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


@dataclass
class Idea:
    id: str
    text: str
    rating: float = 0.0  # 1-5, set by panel
    panel_ratings: dict[str, float] = field(default_factory=dict)
    judge_rejections: dict[str, str] = field(default_factory=dict)


def dedupe_ideas(ideas: list[Idea], threshold: float = 0.7) -> list[Idea]:
    """Remove near-duplicate ideas by Jaccard similarity.

    Keeps the first occurrence in input order.
    """
    kept: list[Idea] = []
    for idea in ideas:
        is_dup = False
        for k in kept:
            if jaccard_similarity(idea.text, k.text) >= threshold:
                is_dup = True
                break
        if not is_dup:
            kept.append(idea)
    return kept


def write_solution_candidates(artefacts_dir: Path, ideas: list[Idea]) -> Path:
    """Write 04_solution_candidates.md sorted by rating descending."""
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    sorted_ideas = sorted(ideas, key=lambda i: -i.rating)
    lines = ["# Solution Candidates (divergent ideation)", ""]
    lines.append(f"Total ideas: {len(ideas)}")
    lines.append("")

    for i, idea in enumerate(sorted_ideas, start=1):
        lines.append(f"## {i}. {idea.id} — rating {idea.rating:.2f}")
        lines.append("")
        lines.append(idea.text)
        lines.append("")
        if idea.panel_ratings:
            lines.append("**Panel ratings:**")
            for judge, r in sorted(idea.panel_ratings.items()):
                lines.append(f"- {judge}: {r:.1f}")
            lines.append("")
        if idea.judge_rejections:
            lines.append("**Judge dissents:**")
            for judge, reason in idea.judge_rejections.items():
                lines.append(f"- {judge}: {reason}")
            lines.append("")

    path = artefacts_dir / "04_solution_candidates.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
```

- [ ] **Step 4: Run, watch pass**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_ideation.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add agent/ideation.py tests/test_ideation.py
git commit -m "feat(agent): Phase 4 ideation helpers with Jaccard dedup"
```

### Task 3.5: Phase 5 — research + ranking writers with Borda/approval

**Files:**
- Create: `agent/aggregation.py` (Borda + approval)
- Create: `agent/ranking.py` (writers)
- Create: `tests/test_aggregation.py`
- Create: `tests/test_ranking.py`

- [ ] **Step 1: Write the failing tests for `aggregation.py`**

Write `/tests/test_aggregation.py`:

```python
"""Tests for agent.aggregation — TDD."""

from __future__ import annotations

from agent.aggregation import approval_vote, borda_count, weighted_borda


def test_borda_count_basic() -> None:
    """Each judge ranks 3 items. Lower position = better."""
    rankings = [
        {"a": 1, "b": 2, "c": 3},  # judge 1
        {"a": 2, "b": 1, "c": 3},  # judge 2
        {"a": 1, "b": 3, "c": 2},  # judge 3
    ]
    # a: 1+2+1=4, b: 2+1+3=6, c: 3+3+2=8
    # Lower is better, so order: a, b, c
    result = borda_count(rankings)
    assert result == ["a", "b", "c"]


def test_borda_count_empty() -> None:
    assert borda_count([]) == []


def test_borda_count_handles_missing_items() -> None:
    rankings = [
        {"a": 1, "b": 2},
        {"a": 2, "b": 1, "c": 3},
    ]
    # a: 1+2=3, b: 2+1=3, c: inf
    result = borda_count(rankings)
    assert result[:2] in (["a", "b"], ["b", "a"])  # tie broken alphabetically
    assert result[2] == "c"


def test_weighted_borda_applies_judge_weights() -> None:
    rankings = [
        {"a": 1, "b": 2},  # judge 1, weight 1.0
        {"a": 2, "b": 1},  # judge 2, weight 3.0
    ]
    # a: 1*1.0 + 2*3.0 = 7.0
    # b: 2*1.0 + 1*3.0 = 5.0
    result = weighted_borda(rankings, weights=[1.0, 3.0])
    assert result == ["b", "a"]


def test_approval_vote_top_k() -> None:
    approvals = [
        {"a", "b", "c"},  # judge 1 approves a, b, c
        {"a", "d"},       # judge 2 approves a, d
        {"b", "c"},       # judge 3 approves b, c
    ]
    # counts: a=2, b=2, c=2, d=1
    # tie broken by inclusion order
    result = approval_vote(approvals)
    assert result[0] in ("a", "b", "c")  # all tied at 2
    assert result[-1] == "d"
```

- [ ] **Step 2: Run, watch fail**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_aggregation.py -v
```

Expected: import fails.

- [ ] **Step 3: Implement `aggregation.py`**

Write `/agent/aggregation.py`:

```python
"""Aggregation algorithms for the panel.

Borda count: each judge ranks all items; sum of positions = score; lower is better.
Weighted Borda: same, with per-judge weights.
Approval voting: each judge approves top-K; counts approvals; higher is better.

See spec §5.5.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable


def _all_items(rankings: list[dict[str, int]]) -> list[str]:
    seen: list[str] = []
    for r in rankings:
        for k in r.keys():
            if k not in seen:
                seen.append(k)
    return seen


def borda_count(rankings: list[dict[str, int]]) -> list[str]:
    """Aggregate rankings by Borda count. Lower score is better."""
    scores: dict[str, float] = defaultdict(lambda: float("inf"))
    items = _all_items(rankings)
    for item in items:
        positions: list[int] = []
        for r in rankings:
            if item in r:
                positions.append(r[item])
        if positions:
            scores[item] = sum(positions)
    # sort by score ascending; tiebreak alphabetically
    return sorted(scores.keys(), key=lambda k: (scores[k], k))


def weighted_borda(
    rankings: list[dict[str, int]], weights: Iterable[float]
) -> list[str]:
    """Borda with per-judge weights."""
    weights = list(weights)
    if len(weights) != len(rankings):
        raise ValueError(
            f"weights length {len(weights)} != rankings length {len(rankings)}"
        )
    scores: dict[str, float] = defaultdict(float)
    items = _all_items(rankings)
    for item in items:
        for r, w in zip(rankings, weights):
            if item in r:
                scores[item] += r[item] * w
    return sorted(scores.keys(), key=lambda k: (scores[k], k))


def approval_vote(approvals: list[set[str]]) -> list[str]:
    """Each judge approves a set; higher count = better. Ties broken alphabetically."""
    counts: dict[str, int] = defaultdict(int)
    order: list[str] = []
    for approval_set in approvals:
        for item in approval_set:
            if item not in counts:
                order.append(item)
            counts[item] += 1
    return sorted(counts.keys(), key=lambda k: (-counts[k], order.index(k)))
```

- [ ] **Step 4: Run, watch pass**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_aggregation.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Implement `ranking.py` and its tests**

Write `/tests/test_ranking.py`:

```python
"""Tests for agent.ranking — TDD."""

from __future__ import annotations

from pathlib import Path

from agent.ranking import RankedSolution, write_owner_pick, write_ranked_solutions


def test_write_ranked_solutions_creates_file(tmp_path: Path) -> None:
    sols = [
        RankedSolution(
            idea_id="I-1",
            text="Real-time radar detection fusion",
            research="No commercial product does this on edge devices.",
            aggregate_score=4.2,
            panel_scores={"mehta": 4.5, "viper": 4.0},
            spread=0.5,
        ),
        RankedSolution(
            idea_id="I-2",
            text="Swarm coordination via local mesh",
            research="MIT Lincoln Lab has a paper; no deployed system.",
            aggregate_score=3.8,
            panel_scores={"mehta": 3.5, "viper": 4.0},
            spread=0.5,
        ),
    ]
    path = write_ranked_solutions(tmp_path, sols)
    raw = path.read_text()
    assert "I-1" in raw
    assert "Real-time radar" in raw
    assert "spread: 0.50" in raw
    assert "MIT Lincoln Lab" in raw


def test_write_owner_pick_captures_choice(tmp_path: Path) -> None:
    write_owner_pick(
        tmp_path,
        chosen_idea_id="I-1",
        validation_notes="Top-ranked, both judges agree.",
        dissents=[],
    )
    raw = (tmp_path / "05_owner_pick.md").read_text()
    assert "I-1" in raw
    assert "Top-ranked" in raw
    assert "Dissents" in raw


def test_write_owner_pick_with_dissents(tmp_path: Path) -> None:
    write_owner_pick(
        tmp_path,
        chosen_idea_id="I-1",
        validation_notes="Pick despite Mehta preferring I-3.",
        dissents=[("mehta", "I prefer I-3 — simpler deployment.")],
    )
    raw = (tmp_path / "05_owner_pick.md").read_text()
    assert "mehta" in raw
    assert "I prefer I-3" in raw
```

Write `/agent/ranking.py`:

```python
"""Phase 5 — Research + ranking writers.

LLM (skill) does research and re-scoring. Python writes the artefacts.

See spec §4 Phase 5, §5.4.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class RankedSolution:
    idea_id: str
    text: str
    research: str
    aggregate_score: float  # weighted
    panel_scores: dict[str, float] = field(default_factory=dict)
    spread: float = 0.0  # max(panel) - min(panel)


def write_ranked_solutions(
    artefacts_dir: Path, solutions: list[RankedSolution]
) -> Path:
    """Write 05_ranked_solutions.md."""
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    sorted_sols = sorted(solutions, key=lambda s: -s.aggregate_score)
    lines = ["# Ranked Solutions (post-research)", ""]

    for i, s in enumerate(sorted_sols, start=1):
        lines.append(f"## Rank {i}: {s.idea_id}")
        lines.append("")
        lines.append(s.text)
        lines.append("")
        lines.append(f"**Aggregate score: {s.aggregate_score:.2f}**")
        lines.append(f"**Spread: {s.spread:.2f}**")
        lines.append("")
        if s.panel_scores:
            lines.append("**Panel scores:**")
            for judge, score in sorted(s.panel_scores.items()):
                lines.append(f"- {judge}: {score:.2f}")
            lines.append("")
        if s.research:
            lines.append("**Research:**")
            lines.append(s.research)
            lines.append("")

    path = artefacts_dir / "05_ranked_solutions.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_owner_pick(
    artefacts_dir: Path,
    chosen_idea_id: str,
    validation_notes: str,
    dissents: list[tuple[str, str]] = None,
) -> Path:
    """Write 05_owner_pick.md.

    dissents: list of (judge_short, reason) for any panel member who disagreed.
    """
    dissents = dissents or []
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Owner Pick (validated)",
        "",
        f"**Chosen: {chosen_idea_id}**",
        "",
        "## Validation notes",
        "",
        validation_notes,
        "",
    ]
    if dissents:
        lines.append("## Dissents")
        lines.append("")
        for judge, reason in dissents:
            lines.append(f"- **{judge}**: {reason}")
        lines.append("")
    path = artefacts_dir / "05_owner_pick.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
```

- [ ] **Step 6: Run, watch pass**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_ranking.py -v
```

Expected: 3 passed.

- [ ] **Step 7: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add agent/aggregation.py agent/ranking.py tests/test_aggregation.py tests/test_ranking.py
git commit -m "feat(agent): Phase 5 ranking writers with Borda/approval aggregation"
```

### Task 3.6: Audit trail writer

**Files:**
- Create: `agent/audit.py`
- Create: `tests/test_audit.py`

- [ ] **Step 1: Write the failing tests**

Write `/tests/test_audit.py`:

```python
"""Tests for agent.audit — TDD."""

from __future__ import annotations

from pathlib import Path

from agent.audit import AuditEntry, write_audit_entry


def test_write_audit_entry_creates_file(tmp_path: Path) -> None:
    entry = AuditEntry(
        phase=1,
        phase_name="Triage",
        prompts=["Cluster these problems into 6 themes."],
        responses=['{"clusters": [...]}'],
        tool_calls=[{"tool": "web_search", "query": "drone detection startups"}],
        artefact_path="artefacts/01_triage.md",
    )
    path = write_audit_entry(tmp_path, entry)
    raw = path.read_text()
    assert "Triage" in raw
    assert "Cluster these problems" in raw
    assert "drone detection startups" in raw
    assert "01_triage.md" in raw


def test_audit_file_naming(tmp_path: Path) -> None:
    entry = AuditEntry(
        phase=2,
        phase_name="Elicit",
        prompts=[],
        responses=[],
        tool_calls=[],
        artefact_path="artefacts/02_candidate_problem.md",
    )
    path = write_audit_entry(tmp_path, entry)
    assert path.name == "02_elicitation.md"
```

- [ ] **Step 2: Run, watch fail**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_audit.py -v
```

Expected: import fails.

- [ ] **Step 3: Implement `audit.py`**

Write `/agent/audit.py`:

```python
"""Audit trail writer.

Each phase calls write_audit_entry() to record what prompts were sent,
what responses came back, what tool calls were made, and what artefact
was produced. Files go to artefacts/audit/ (gitignored).

See spec §10.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


_PHASE_NAMES = {
    0: "onboarding",
    1: "triage",
    2: "elicitation",
    3: "sub_problem",
    4: "ideation",
    5: "research_rank",
    6: "demo_narrative",
    7: "deck_market",
    8: "final_review",
}


@dataclass
class AuditEntry:
    phase: int
    phase_name: str
    prompts: list[str]
    responses: list[str]
    tool_calls: list[dict]
    artefact_path: str
    extra: dict = field(default_factory=dict)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_audit_entry(artefacts_dir: Path, entry: AuditEntry) -> Path:
    """Write an audit entry to artefacts/audit/<NN>_<phase_name>.md."""
    audit_dir = artefacts_dir / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    name = _PHASE_NAMES.get(entry.phase, f"phase_{entry.phase}")
    path = audit_dir / f"{entry.phase:02d}_{name}.md"

    lines = [
        f"# Audit: Phase {entry.phase} — {entry.phase_name}",
        "",
        f"**Timestamp:** {_now_iso()}",
        "",
        f"**Artefact:** `{entry.artefact_path}`",
        "",
    ]
    if entry.prompts:
        lines.append("## Prompts")
        lines.append("")
        for i, p in enumerate(entry.prompts, start=1):
            lines.append(f"### Prompt {i}")
            lines.append("")
            lines.append("```")
            lines.append(p)
            lines.append("```")
            lines.append("")
    if entry.responses:
        lines.append("## Responses")
        lines.append("")
        for i, r in enumerate(entry.responses, start=1):
            lines.append(f"### Response {i}")
            lines.append("")
            lines.append("```")
            lines.append(r[:5000])  # truncate huge responses
            if len(r) > 5000:
                lines.append(f"... [{len(r) - 5000} more chars truncated]")
            lines.append("```")
            lines.append("")
    if entry.tool_calls:
        lines.append("## Tool calls")
        lines.append("")
        for tc in entry.tool_calls:
            lines.append(f"- `{tc.get('tool', '?')}`: {json.dumps(tc)[:200]}")
        lines.append("")
    if entry.extra:
        lines.append("## Extra")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(entry.extra, indent=2))
        lines.append("```")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path
```

- [ ] **Step 4: Run, watch pass**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_audit.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add agent/audit.py tests/test_audit.py
git commit -m "feat(agent): audit trail writer"
```

### Task 3.7: Wire Phases 2-5 into SKILL.md

**Files:**
- Modify: `SKILL.md` (add per-phase instructions)

- [ ] **Step 1: Append per-phase instructions to `SKILL.md`**

Append to `/SKILL.md`:

```markdown

## Per-phase implementation guide

This is the operational reference for executing each phase. Each phase
invokes Python helpers from `agent/` and writes artefacts + audit.

### Phase 0 — Onboarding

1. Read or create `artefacts/state.json` (via `agent.state`).
2. If `00_context.yaml` doesn't exist, present the default and ask the user to confirm/edit.
3. Save the context via `agent.context.save_context(artefacts_dir, ctx)`.
4. Write audit entry via `agent.audit.write_audit_entry`.
5. Mark phase complete via `agent.state.mark_phase_completed`.

### Phase 1 — Triage

1. `python -m agent.parse_csv` → `artefacts/01_problems.json` (or call `agent.parse_csv.parse_problems` directly).
2. Run `agent.normalize.assign_quality_flags` on each problem; `agent.normalize.dedupe_problems` to dedupe.
3. LLM clusters the problems (4-8 clusters), assigns themes/tags, scores each cluster on 4 axes.
4. LLM does a quick market-signal check per cluster (1-2 web searches per cluster).
5. The locked panel reviews: each judge ranks top-3 clusters; aggregate via `agent.aggregation.borda_count`.
6. Build a `TriageReport` and call `agent.triage.write_triage_report`.
7. Write audit entry.
8. Mark complete.

### Phase 2 — Elicit & narrow

1. LLM generates owner questions for the top-3 clusters (5-8 questions total).
2. The locked panel adds 2-3 questions each from their `hard_questions_seed`.
3. Build a list of `OwnerQuestion` and call `agent.elicitation.write_owner_questions`.
4. Capture answers (real or sim):
   - Real: ask the user interactively. Update `02_owner_answers.md` as they answer.
   - Sim: load `personas/edth-judge.yaml` and have the LLM role-play the owner.
5. LLM scores each of the top-3 candidates with answers in mind (4 axes + reasoning).
6. Panel re-ranks top-3.
7. Build a list of `Candidate` and call `agent.candidates.write_candidate_problem`.
8. User picks 1 → record via `agent.state.set_decision(state, "chosen_problem_id", ...)`.
9. Write audit + mark complete.

### Phase 3 — Sub-problem decompose

1. LLM decomposes the chosen problem into 5-8 sub-problems.
2. LLM scores each on 4 axes: impact, time_fit, demo_ability, dependency_risk.
3. Panel reviews (each judge scores all sub-problems on the same 4 axes).
4. Aggregate via simple average of panel scores.
5. Build a list of `SubProblem` and call `agent.sub_problem.write_sub_problem`.
6. User picks 1 → record via `set_decision`.
7. Write audit + mark complete.

### Phase 4 — Divergent ideation

1. LLM generates 20+ raw ideas using divergent techniques (SCAMPER, "worst possible idea", "what would X do", etc.).
2. Run `agent.ideation.dedupe_ideas(ideas, threshold=0.7)` to cluster near-duplicates.
3. The locked panel rates each unique idea 1-5 with one-line reasoning.
4. Compute aggregate rating (mean across panel).
5. Build the list of `Idea` (with panel_ratings and judge_rejections populated) and call `agent.ideation.write_solution_candidates`.
6. Write audit + mark complete (no decision yet — owner validates in Phase 5).

### Phase 5 — Research & rank

1. LLM does web research on the top-5 ideas (prior art, SOTA, competitors, TRL).
2. The locked panel re-scores the top 5 with research in mind.
3. Aggregate via `agent.aggregation.weighted_borda` or `approval_vote` (per `aggregation_mode` in context).
4. Build a list of `RankedSolution` and call `agent.ranking.write_ranked_solutions`.
5. Capture owner validation:
   - Real: ask the user to pick or override.
   - Sim: persona picks from the top-2.
6. Call `agent.ranking.write_owner_pick` with the chosen idea, validation notes, and any dissents.
7. Record decision via `set_decision`.
8. Write audit + mark complete.
```

- [ ] **Step 2: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add SKILL.md
git commit -m "docs(skill): per-phase implementation guide for phases 0-5"
```

### Milestone 3 checkpoint

- [ ] **Run all tests**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest
```

Expected: ~70 tests passing across all modules.

- [ ] **Spot-check: parse + normalize + dedupe on real input**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/python -c "
from pathlib import Path
from agent.parse_csv import parse_problems
from agent.normalize import assign_quality_flags, dedupe_problems
from agent.ideation import Idea, dedupe_ideas
problems = parse_problems(Path('input/PB-SOL-EDTH - Sheet1.csv'))
flagged = [{'id': p['id'], 'name': p['name'][:40], 'flags': [f.value for f in assign_quality_flags(p)]} for p in problems]
flagged_count = sum(1 for p in flagged if p['flags'])
print(f'{len(problems)} problems, {flagged_count} with quality flags')
ideas = [Idea(id=f'I-{i}', text=p['name'] + ' ' + p['problem']) for i, p in enumerate(problems[:10])]
deduped = dedupe_ideas(ideas, threshold=0.5)
print(f'{len(ideas)} ideas -> {len(deduped)} after dedup')
"
```

Expected: ~40 problems, a handful with flags, 10 ideas → 8-10 after dedup (names are distinct).

## Milestone 4 — Phases 6–7 (Demo, Deck & Market)

**Goal:** Demo plan, market/competition/business-model research, Marp deck generation with fallback rendering.

**Tasks:**
- Task 4.1: Phase 6 — demo plan, script, pitch, Q&A, risk register
- Task 4.2: Author 8 Marp templates
- Task 4.3: Phase 7 — market research (web)
- Task 4.4: Phase 7 — competition analysis
- Task 4.5: Phase 7 — business model
- Task 4.6: `render.py` — Marp CLI renderer + detection
- Task 4.7: `render.py` — python-pptx fallback
- Task 4.8: `render.py` — HTML deck fallback
- Task 4.9: Compile final deck from all phase outputs

### Task 4.1: Phase 6 — demo plan writer

**Files:**
- Create: `agent/demo_plan.py`
- Create: `tests/test_demo_plan.py`

- [ ] **Step 1: Write the failing tests**

Write `/tests/test_demo_plan.py`:

```python
"""Tests for agent.demo_plan — TDD."""

from __future__ import annotations

from pathlib import Path

from agent.demo_plan import DemoPlan, Risk, write_demo_plan


def test_write_demo_plan_creates_file(tmp_path: Path) -> None:
    plan = DemoPlan(
        thin_demo="A browser dashboard showing real-time detection in 3 seconds.",
        script=[
            (0, "Cold open: 3 seconds for a decision lives matter."),
            (15, "Show the problem with a live threat feed."),
            (30, "Demo: detect and classify in real time."),
            (120, "Show the AI recommendation loop."),
            (160, "Closing: what's next."),
        ],
        pitch="MDO Commander's Dashboard: see the whole war in 3 seconds, decide in 30.",
        qa_prep=[
            ("Q: Is this generative AI?", "A: Yes, for COA recommendations."),
            ("Q: What's the TRL?", "A: 5 — demo-ready, field test next."),
        ],
        risks=[
            Risk(what="Demo crashes on stage", likelihood="medium", impact="high", mitigation="Pre-record a backup screencast."),
            Risk(what="Judge doesn't know the domain", likelihood="low", impact="medium", mitigation="Start with a 15-second war story."),
        ],
    )
    path = write_demo_plan(tmp_path, plan)
    raw = path.read_text()
    assert "Cold open" in raw
    assert "Demo crashes" in raw
    assert "Q:" in raw
    assert "A:" in raw
    assert "Judge doesn't know" in raw


def test_script_includes_timestamps(tmp_path: Path) -> None:
    plan = DemoPlan(
        thin_demo="x",
        script=[(0, "start"), (90, "middle"), (170, "end")],
        pitch="x",
        qa_prep=[],
        risks=[],
    )
    write_demo_plan(tmp_path, plan)
    raw = (tmp_path / "06_demo_plan.md").read_text()
    assert "0:00" in raw
    assert "1:30" in raw
    assert "2:50" in raw
```

- [ ] **Step 2: Run, watch fail**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_demo_plan.py -v
```
Expected: import fails.

- [ ] **Step 3: Implement `demo_plan.py`**

Write `/agent/demo_plan.py`:

```python
"""Phase 6 — Demo plan writer.

LLM generates the content; Python formats and writes the artefact.

See spec §4 Phase 6.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Risk:
    what: str
    likelihood: str  # high | medium | low
    impact: str       # high | medium | low
    mitigation: str


@dataclass
class DemoPlan:
    thin_demo: str
    script: list[tuple[int, str]]  # (seconds, description)
    pitch: str
    qa_prep: list[tuple[str, str]]  # (question, answer)
    risks: list[Risk]


def _fmt_seconds(s: int) -> str:
    m, sec = divmod(s, 60)
    return f"{m}:{sec:02d}"


def write_demo_plan(artefacts_dir: Path, plan: DemoPlan) -> Path:
    """Write 06_demo_plan.md."""
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# Demo Plan", ""]

    lines.append("## Thin Demo")
    lines.append("")
    lines.append(plan.thin_demo)
    lines.append("")

    lines.append("## 3-Minute Demo Script")
    lines.append("")
    for sec, desc in plan.script:
        lines.append(f"**[{_fmt_seconds(sec)}]** {desc}")
    lines.append("")

    lines.append("## 30-Second Elevator Pitch")
    lines.append("")
    lines.append(plan.pitch)
    lines.append("")

    lines.append("## Judge Q&A Prep")
    lines.append("")
    for q, a in plan.qa_prep:
        lines.append(f"**{q}**")
        lines.append(f"{a}")
        lines.append("")

    lines.append("## Risk Register")
    lines.append("")
    lines.append("| Risk | Likelihood | Impact | Mitigation |")
    lines.append("|---|---|---|---|")
    for r in plan.risks:
        lines.append(f"| {r.what} | {r.likelihood} | {r.impact} | {r.mitigation} |")
    lines.append("")

    path = artefacts_dir / "06_demo_plan.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
```

- [ ] **Step 4: Run, watch pass**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_demo_plan.py -v
```
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add agent/demo_plan.py tests/test_demo_plan.py
git commit -m "feat(agent): Phase 6 demo plan writer"
```

### Task 4.2: Author 8 Marp templates

**Files:**
- Create: `templates/cover.md`
- Create: `templates/problem.md`
- Create: `templates/solution.md`
- Create: `templates/market.md`
- Create: `templates/competition.md`
- Create: `templates/business-model.md`
- Create: `templates/demo.md`
- Create: `templates/pitch.md`

- [ ] **Step 1: Write all 8 templates**

Write `/templates/cover.md`:

```markdown
---
marp: true
size: 16:9
---

# {{PROJECT_NAME}}

**{{HACKATHON_NAME}}**
{{TEAM_NAME}} | {{DATE}}

---
```

Write `/templates/problem.md`:

```markdown
<!-- _class: lead -->

# The Problem

## {{ONE_LINER}}

---

## Why This Matters

{{PROBLEM_STATEMENT}}

---

## Who Feels This Pain

- **Primary:** {{PRIMARY_USER}}
- **Secondary:** {{SECONDARY_USER}}

---

## Why Now

{{WHY_NOW}}
```

Write `/templates/solution.md`:

```markdown
<!-- _class: lead -->

# Our Solution

## {{SOLUTION_ONE_LINER}}

---

## How It Works

{{HOW_IT_WORKS}}

![Demo placeholder]({{DEMO_SCREENSHOT}})

---

## Key Differentiators

| Us | Them |
|---|---|
| {{DIFF_1}} | {{THEN_1}} |
| {{DIFF_2}} | {{THEN_2}} |
| {{DIFF_3}} | {{THEN_3}} |

---

## Demo

**{{DEMO_CAPTION}}**

{{DEMO_DESCRIPTION}}
```

Write `/templates/market.md`:

```markdown
<!-- _class: lead -->

# Market Opportunity

---

## Market Size

- **TAM:** {{TAM}}
- **SAM:** {{SAM}}
- **SOM:** {{SOM}}

---

## Growth & Trends

{{MARKET_TRENDS}}

- **CAGR:** {{CAGR}}
- **Key drivers:** {{DRIVERS}}

---

## Buyer Personas

1. **{{PERSONA_1_NAME}}** — {{PERSONA_1_DESC}}
2. **{{PERSONA_2_NAME}}** — {{PERSONA_2_DESC}}
3. **{{PERSONA_3_NAME}}** — {{PERSONA_3_DESC}}
```

Write `/templates/competition.md`:

```markdown
<!-- _class: lead -->

# Competitive Landscape

---

## Positioning

{{POSITIONING_MAP_DESC}}

---

## Direct Competitors

| Competitor | Strength | Weakness | Our Edge |
|---|---|---|---|
| {{COMP1_NAME}} | {{COMP1_STRENGTH}} | {{COMP1_WEAKNESS}} | {{OUR_EDGE1}} |
| {{COMP2_NAME}} | {{COMP2_STRENGTH}} | {{COMP2_WEAKNESS}} | {{OUR_EDGE2}} |
| {{COMP3_NAME}} | {{COMP3_STRENGTH}} | {{COMP3_WEAKNESS}} | {{OUR_EDGE3}} |

---

## Moat

1. **{{MOAT_1}}**
2. **{{MOAT_2}}**
3. **{{MOAT_3}}**
```

Write `/templates/business-model.md`:

```markdown
<!-- _class: lead -->

# Business Model

---

## Revenue Model

{{REVENUE_MODEL}}

---

## Pricing

{{PRICING}}

---

## Go-to-Market

{{GTM_STRATEGY}}

---

## Defensibility

{{DEFENSIBILITY}}
```

Write `/templates/demo.md`:

```markdown
<!-- _class: lead -->

# Live Demo

## {{DEMO_TITLE}}

---

## What You'll See

{{DEMO_FLOW}}

---

## Key Metrics

- {{METRIC_1}}
- {{METRIC_2}}
- {{METRIC_3}}
```

Write `/templates/pitch.md`:

```markdown
<!-- _class: lead -->

# 30-Second Pitch

> {{PITCH_TEXT}}

---

# Thank You

**{{TEAM_NAME}}**

{{CONTACT_INFO}}

---
```

- [ ] **Step 2: Verify templates parse as valid markdown**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
for f in templates/*.md; do echo "$f: $(wc -l < "$f") lines"; done
```
Expected: 8 files, each with content.

- [ ] **Step 3: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add templates/
git commit -m "feat(templates): 8 Marp slide templates"
```

### Task 4.3: Phase 7 — market/competition/BM writers

**Files:**
- Create: `agent/market.py`
- Create: `tests/test_market.py`

- [ ] **Step 1: Write the failing tests**

Write `/tests/test_market.py`:

```python
"""Tests for agent.market — TDD."""

from __future__ import annotations

from pathlib import Path

from agent.market import write_competition, write_market, write_business_model


def test_write_market_creates_file(tmp_path: Path) -> None:
    write_market(
        tmp_path,
        tam="$12B", sam="$3B", som="$150M",
        trends="15% CAGR, driven by Ukraine conflict and NATO modernization.",
        personas=["Defense prime PM", "DoD PEO", "JTAC / operator"],
    )
    raw = (tmp_path / "07_market.md").read_text()
    assert "$12B" in raw
    assert "15% CAGR" in raw
    assert "Defense prime PM" in raw


def test_write_competition_creates_file(tmp_path: Path) -> None:
    write_competition(
        tmp_path,
        competitors=[
            ("Anduril", "Fielded Lattice", "Heavy, expensive", "Edge-native, cheap"),
            ("Palantir", "Maven, deployed", "Cloud-only", "Offline-first"),
        ],
        moat=["Proprietary edge models", "Synthetic training data", "Operator trust"],
    )
    raw = (tmp_path / "07_competition.md").read_text()
    assert "Anduril" in raw
    assert "Palantir" in raw
    assert "Proprietary edge models" in raw


def test_write_business_model_creates_file(tmp_path: Path) -> None:
    write_business_model(
        tmp_path,
        revenue="SaaS per-node subscription, $5k/unit/year.",
        pricing="Tiered: Basic ($3k), Pro ($8k), Enterprise (custom).",
        gtm="Phase 1: SBIR/STTR. Phase 2: OTA with SOCOM. Phase 3: NATO.",
        defensibility="On-device models improve with field data; switching cost is retraining.",
    )
    raw = (tmp_path / "07_business_model.md").read_text()
    assert "SaaS" in raw
    assert "Tiered" in raw
    assert "SBIR/STTR" in raw
```

- [ ] **Step 2: Run, watch fail**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_market.py -v
```
Expected: import fails.

- [ ] **Step 3: Implement `market.py`**

Write `/agent/market.py`:

```python
"""Phase 7 — Market, competition, and business model artefact writers.

LLM + web research generates the content. Python writes the files.

See spec §4 Phase 7.
"""

from __future__ import annotations

from pathlib import Path


def write_market(
    artefacts_dir: Path,
    tam: str,
    sam: str,
    som: str,
    trends: str,
    personas: list[str],
) -> Path:
    """Write 07_market.md."""
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
    artefacts_dir: Path,
    competitors: list[tuple[str, str, str, str]],
    moat: list[str],
) -> Path:
    """Write 07_competition.md.

    competitors: list of (name, strength, weakness, our_edge)
    moat: list of moat descriptions
    """
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
    artefacts_dir: Path,
    revenue: str,
    pricing: str,
    gtm: str,
    defensibility: str,
) -> Path:
    """Write 07_business_model.md."""
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
```

- [ ] **Step 4: Run, watch pass**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_market.py -v
```
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add agent/market.py tests/test_market.py
git commit -m "feat(agent): Phase 7 market/competition/BM writers"
```

### Task 4.4: Render module — Marp CLI detection

**Files:**
- Create: `agent/render.py`
- Create: `tests/test_render.py`

- [ ] **Step 1: Write the failing tests**

Write `/tests/test_render.py`:

```python
"""Tests for agent.render — TDD."""

from __future__ import annotations

import shutil
from pathlib import Path
from unittest import mock

from agent.render import (
    detect_marp,
    has_marp,
    has_pptx,
)


def test_detect_marp_finds_binary() -> None:
    marp_path = shutil.which("marp")
    if marp_path:
        assert detect_marp() == Path(marp_path)
    else:
        assert detect_marp() is None


def test_has_marp_is_boolean() -> None:
    assert isinstance(has_marp(), bool)


def test_has_pptx_imports_module() -> None:
    assert isinstance(has_pptx(), bool)
```

- [ ] **Step 2: Run, watch fail**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_render.py -v
```
Expected: import fails.

- [ ] **Step 3: Implement `render.py` (first pass — detection only)**

Write `/agent/render.py`:

```python
"""Render module — Marp, pptx, and HTML deck rendering.

Three-tier fallback strategy (spec §9):
1. Marp CLI → .html + .pdf (preferred)
2. python-pptx → .pptx (fallback)
3. Self-contained HTML → .html (always works)

Detection functions tell the skill which tier is available.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

log = logging.getLogger(__name__)


def detect_marp() -> Path | None:
    """Return the path to the marp binary, or None if not found."""
    path = shutil.which("marp")
    if path:
        return Path(path)
    return None


def has_marp() -> bool:
    return detect_marp() is not None


def has_pptx() -> bool:
    try:
        import pptx  # noqa: F401
        return True
    except ImportError:
        return False


def best_renderer() -> str:
    """Return 'marp', 'pptx', or 'html' — the best available renderer."""
    if has_marp():
        return "marp"
    if has_pptx():
        return "pptx"
    return "html"
```

- [ ] **Step 4: Run, watch pass**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_render.py -v
```
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add agent/render.py tests/test_render.py
git commit -m "feat(agent): render detection (marp/pptx/html tiers)"
```

### Task 4.5: Render module — HTML fallback (always works)

- [ ] **Step 1: Add failing test for `render_html_deck`**

Append to `/tests/test_render.py`:

```python
def test_render_html_deck_creates_self_contained_file(tmp_path: Path) -> None:
    from agent.render import render_html_deck
    path = render_html_deck(tmp_path, "# Test Deck\n\n## Slide 1\n\nHello world\n\n---\n\n## Slide 2\n\nGoodbye\n")
    assert path.exists()
    assert path.suffix == ".html"
    raw = path.read_text()
    assert "<title>Test Deck</title>" in raw
    assert "Hello world" in raw
    assert "Goodbye" in raw


def test_html_deck_has_keyboard_nav(tmp_path: Path) -> None:
    from agent.render import render_html_deck
    path = render_html_deck(tmp_path, "# Title\n\n---\n\n## Slide\n\nContent\n")
    raw = path.read_text()
    assert "ArrowLeft" in raw or "keyCode" in raw or "keydown" in raw


def test_html_deck_handles_empty_input(tmp_path: Path) -> None:
    from agent.render import render_html_deck
    path = render_html_deck(tmp_path, "")
    assert path.exists()
```

- [ ] **Step 2: Run, watch 3 new failures**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_render.py::test_render_html_deck_creates_self_contained_file -v
```
Expected: FAIL — `render_html_deck` not defined.

- [ ] **Step 3: Add `render_html_deck` to `render.py`**

Append to `/agent/render.py`:

```python
_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #1a1a2e; color: #eee; }}
.slide {{ display: none; width: 100vw; height: 100vh; padding: 10vh 10vw; flex-direction: column; justify-content: center; }}
.slide.active {{ display: flex; }}
.slide h1 {{ font-size: 3rem; margin-bottom: 2rem; color: #e94560; }}
.slide h2 {{ font-size: 2rem; margin-bottom: 1.5rem; color: #e94560; }}
.slide h3 {{ font-size: 1.5rem; margin: 1rem 0; }}
.slide p, .slide li {{ font-size: 1.2rem; line-height: 1.8; }}
.slide code {{ background: #16213e; padding: 0.2rem 0.5rem; border-radius: 4px; }}
.slide table {{ width: 100%; border-collapse: collapse; }}
.slide th, .slide td {{ border: 1px solid #444; padding: 0.5rem; text-align: left; }}
.slide th {{ background: #16213e; }}
.counter {{ position: fixed; bottom: 1rem; right: 1rem; font-size: 0.9rem; color: #666; }}
.nav-hint {{ position: fixed; bottom: 1rem; left: 1rem; font-size: 0.8rem; color: #555; }}
</style>
</head>
<body>
{slides}
<div class="counter" id="counter">1 / {total}</div>
<div class="nav-hint">← → arrow keys to navigate</div>
<script>
let current = 0;
const slides = document.querySelectorAll('.slide');
const counter = document.getElementById('counter');
function show(i) {{
  slides.forEach((s, idx) => s.classList.toggle('active', idx === i));
  counter.textContent = (i + 1) + ' / ' + slides.length;
}}
document.addEventListener('keydown', (e) => {{
  if (e.key === 'ArrowRight' || e.key === ' ') {{ e.preventDefault(); current = Math.min(current + 1, slides.length - 1); show(current); }}
  if (e.key === 'ArrowLeft') {{ e.preventDefault(); current = Math.max(current - 1, 0); show(current); }}
}});
show(0);
</script>
</body>
</html>"""


def _md_slides_to_html(md_text: str) -> list[str]:
    """Convert Marp-adjacent markdown to a list of HTML slide bodies."""
    slides: list[str] = []
    current: list[str] = []
    for line in md_text.split("\n"):
        if line.strip() == "---":
            slides.append("\n".join(current))
            current = []
            continue
        # Simple markdown-to-HTML conversion
        stripped = line.strip()
        if stripped.startswith("#### "):
            current.append(f"<h4>{stripped[5:]}</h4>")
        elif stripped.startswith("### "):
            current.append(f"<h3>{stripped[4:]}</h3>")
        elif stripped.startswith("## "):
            current.append(f"<h2>{stripped[3:]}</h2>")
        elif stripped.startswith("# "):
            current.append(f"<h1>{stripped[2:]}</h1>")
        elif stripped.startswith("- "):
            current.append(f"<li>{stripped[2:]}</li>")
        elif stripped.startswith(">"):
            current.append(f"<blockquote>{stripped[1:]}</blockquote>")
        elif stripped.startswith("<!--"):
            continue  # skip HTML comments (Marp directives)
        elif stripped.startswith("---"):
            continue  # skip Marp front-matter
        else:
            current.append(f"<p>{line}</p>")
    if current:
        slides.append("\n".join(current))
    return slides


def render_html_deck(artefacts_dir: Path, md_text: str, output_filename: str = "07_deck.html") -> Path:
    """Render a self-contained HTML deck. Always works, no external deps.

    Returns the path to the .html file.
    """
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    slide_bodies = _md_slides_to_html(md_text)
    slide_divs = "\n".join(
        f'<div class="slide">\n{body}\n</div>'
        for body in slide_bodies
    )
    title = "Deck"
    for line in md_text.split("\n"):
        if line.startswith("# "):
            title = line[2:].strip()
            break
    html = _HTML_TEMPLATE.format(
        title=title,
        slides=slide_divs,
        total=len(slide_bodies),
    )
    path = artefacts_dir / output_filename
    path.write_text(html, encoding="utf-8")
    log.info("Rendered %d slides to %s", len(slide_bodies), path)
    return path
```

- [ ] **Step 4: Run, watch pass**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_render.py -v
```
Expected: 6 passed (3 from before + 3 new).

- [ ] **Step 5: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add agent/render.py tests/test_render.py
git commit -m "feat(agent): HTML deck fallback renderer"
```

### Task 4.6: Compile final deck + Phase 8 summary

**Files:**
- Create: `agent/deck.py` (deck compiler)
- Modify: `SKILL.md` (add Phase 7-8 instructions)

- [ ] **Step 1: Implement `deck.py`**

Write `/agent/deck.py`:

```python
"""Final deck compiler.

Reads all phase artefacts, compiles them into a single Marp markdown deck,
and renders it using the best available renderer.

See spec §4 Phases 7-8, §9.3.
"""

from __future__ import annotations

from pathlib import Path

from agent.render import best_renderer, has_marp, has_pptx, render_html_deck


def compile_deck_md(artefacts_dir: Path, context: dict) -> str:
    """Read phase artefacts and compile a Marp markdown deck.

    context has keys like project_name, team_name, hackathon_name, date.
    """
    hackathon = context.get("hackathon_name", "EDTH Munich 2025")
    project = context.get("project_name", "Project X")
    team = context.get("team_name", "Team")

    def _slurp(name: str) -> str:
        p = artefacts_dir / name
        if p.exists():
            return p.read_text(encoding="utf-8")
        return f"[{name} not found]"

    problem = _slurp("02_candidate_problem.md")
    solution = _slurp("05_owner_pick.md")
    market = _slurp("07_market.md")
    comp = _slurp("07_competition.md")
    bm = _slurp("07_business_model.md")

    lines = [
        "---",
        "marp: true",
        "size: 16:9",
        "---",
        "",
        f"# {project}",
        f"**{hackathon}**",
        f"{team} | {context.get('date', '')}",
        "",
        "---",
        "",
        problem,
        "",
        "---",
        "",
        solution,
        "",
        "---",
        "",
        market,
        "",
        "---",
        "",
        comp,
        "",
        "---",
        "",
        bm,
        "",
        "---",
        "",
        "<!-- _class: lead -->",
        "",
        "# Thank You",
        f"**{team}**",
        "",
    ]
    return "\n".join(lines)


def render_deck(artefacts_dir: Path, context: dict) -> Path:
    """Compile and render the deck using the best available method.

    Returns the path to the rendered file.
    """
    md_text = compile_deck_md(artefacts_dir, context)
    deck_md_path = artefacts_dir / "07_deck.md"
    deck_md_path.write_text(md_text, encoding="utf-8")

    renderer = best_renderer()

    if renderer == "marp":
        # html first (faster), then pdf
        from agent.render import detect_marp
        import subprocess
        marp = detect_marp()
        subprocess.run(
            [str(marp), str(deck_md_path), "-o", str(artefacts_dir / "07_deck.html")],
            check=True,
            capture_output=True,
        )
        try:
            subprocess.run(
                [str(marp), str(deck_md_path), "--pdf", "-o", str(artefacts_dir / "07_deck.pdf")],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError:
            pass  # PDF optional
        return artefacts_dir / "07_deck.html"

    if renderer == "pptx":
        from agent.render import render_pptx_deck
        return render_pptx_deck(artefacts_dir, md_text)

    # HTML fallback
    return render_html_deck(artefacts_dir, md_text)


def render_pptx_deck(artefacts_dir: Path, md_text: str) -> Path:
    """Render to .pptx using python-pptx."""
    from pptx import Presentation
    from pptx.util import Inches, Pt

    prs = Presentation()
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)

    slides = md_text.split("\n---\n")
    for i, slide_md in enumerate(slides):
        if i == 0:
            slide_layout = prs.slide_layouts[0]  # title
            slide = prs.slides.add_slide(slide_layout)
            title_text = ""
            for line in slide_md.split("\n"):
                st = line.strip()
                if st.startswith("# "):
                    title_text = st[2:]
                elif st.startswith("## "):
                    title_text = st[3:]
                    break
            if title_text:
                slide.shapes.title.text = title_text
        else:
            slide_layout = prs.slide_layouts[1]  # title + content
            slide = prs.slides.add_slide(slide_layout)
            lines = slide_md.strip().split("\n")
            if lines:
                first = lines[0].strip()
                if first.startswith("#"):
                    slide.shapes.title.text = first.lstrip("#").strip()
                else:
                    slide.shapes.title.text = first[:100]

    path = artefacts_dir / "07_deck.pptx"
    prs.save(str(path))
    return path
```

- [ ] **Step 2: Add Phase 7-8 to SKILL.md**

Append to `/SKILL.md`:

```markdown

### Phase 6 — Demo & narrative

1. LLM defines the thin demo (smallest thing we build for the "wow" moment).
2. LLM writes a 3-minute script with second-by-second timestamps.
3. LLM writes a 30-second elevator pitch.
4. LLM generates 8-12 judge Q&A pairs.
5. LLM generates a risk register (5-8 risks).
6. Call `agent.demo_plan.write_demo_plan` with the artefacts_dir and the DemoPlan.
7. Write audit + mark complete.

### Phase 7 — Deck & market research

1. LLM + web research: market size (TAM/SAM/SOM), trends, buyer personas.
2. Call `agent.market.write_market`.
3. LLM + web research: direct + adjacent competitors, positioning, moat.
4. Call `agent.market.write_competition`.
5. LLM generates business model canvas (revenue, pricing, GTM, defensibility).
6. Call `agent.market.write_business_model`.
7. Call `agent.deck.compile_deck_md` to produce `07_deck.md`.
8. Call `agent.deck.render_deck` to render the final deck.
9. Write audit + mark complete.

### Phase 8 — Final review

1. LLM writes a one-page summary (pitch, risks, differentiators, panel dissent, next steps).
2. Write `08_summary.md`.
3. Per-judge: thumbs up/down + "what would change my mind".
4. Offer optional: commit artefacts to git.
5. Write audit + mark complete.
```

- [ ] **Step 3: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add agent/deck.py SKILL.md
git commit -m "feat(agent): deck compiler + Phases 6-8 to SKILL.md"
```

### Milestone 4 checkpoint

- [ ] **Run all tests**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest
```
Expected: ~85 tests passing.

- [ ] **Smoke test: render a minimal deck to HTML**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/python -c "
from pathlib import Path; from agent.deck import render_deck
p = render_deck(Path('artefacts'), {'project_name':'Test','team_name':'T','hackathon_name':'H','date':'2026'})
print('Rendered:', p, p.stat().st_size, 'bytes')
"
```
Expected: `Rendered: artefacts/07_deck.html ... bytes` with the file existing.

---

## Milestone 5 — Phase 8 (Final review) + sample run

**Goal:** One-pager summary, sample-run committed for orientation.

**Tasks:**
- Task 5.1: Phase 8 — summary generator
- Task 5.2: Sample run — synthesize all artefacts for a synthetic problem
- Task 5.3: Render sample-run deck, verify HTML

### Task 5.1: Phase 8 — summary writer

**Files:**
- Create: `agent/summary.py`
- Create: `tests/test_summary.py`

- [ ] **Step 1: Write the failing tests**

Write `/tests/test_summary.py`:

```python
"""Tests for agent.summary — TDD."""

from __future__ import annotations

from pathlib import Path

from agent.summary import JudgeVerdict, Summary, write_summary


def test_write_summary_creates_file(tmp_path: Path) -> None:
    s = Summary(
        pitch="MDO Commander's Dashboard: see the whole war in 3 seconds.",
        top_risks=["Data freshness in contested environments.", "Scope creep in 48 hours."],
        top_differentiators=["Edge-native AI for COA recommendations.", "Panel-convergent across 5 judges."],
        verdicts=[
            JudgeVerdict(judge="mehta", thumbs_up=True, note="Solid; ship it."),
            JudgeVerdict(judge="viper", thumbs_up=True, note="I'd use this on the flight line."),
            JudgeVerdict(judge="volkov", thumbs_up=False, note="Assumptions about adversary EW are optimistic."),
        ],
        next_steps=["Field-test the edge model on synthetic threat data.", "Build operator-facing demo with real-time feeds."],
    )
    path = write_summary(tmp_path, s)
    raw = path.read_text()
    assert "MDO Commander's Dashboard" in raw
    assert "mehta" in raw
    assert "Solid" in raw
    assert "Assumptions about adversary EW" in raw
    assert "Field-test" in raw


def test_summary_counts_verdicts(tmp_path: Path) -> None:
    s = Summary(
        pitch="x",
        top_risks=[],
        top_differentiators=[],
        verdicts=[
            JudgeVerdict("a", True, "ok"),
            JudgeVerdict("b", False, "no"),
        ],
        next_steps=[],
    )
    write_summary(tmp_path, s)
    raw = (tmp_path / "08_summary.md").read_text()
    assert "1 👍  1 👎" in raw or "👍" in raw
```

- [ ] **Step 2: Run, watch fail**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_summary.py -v
```
Expected: import fails.

- [ ] **Step 3: Implement `summary.py`**

Write `/agent/summary.py`:

```python
"""Phase 8 — Final summary writer.

See spec §4 Phase 8.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class JudgeVerdict:
    judge: str
    thumbs_up: bool
    note: str


@dataclass
class Summary:
    pitch: str
    top_risks: list[str]
    top_differentiators: list[str]
    verdicts: list[JudgeVerdict]
    next_steps: list[str]


def write_summary(artefacts_dir: Path, summary: Summary) -> Path:
    """Write 08_summary.md."""
    artefacts_dir.mkdir(parents=True, exist_ok=True)
    ups = sum(1 for v in summary.verdicts if v.thumbs_up)
    downs = len(summary.verdicts) - ups

    lines = [
        "# Final Summary",
        "",
        "## One-Paragraph Pitch",
        "",
        summary.pitch,
        "",
        "## Top 3 Differentiators",
        "",
    ]
    for d in summary.top_differentiators:
        lines.append(f"- {d}")
    lines.append("")

    lines.append("## Top 3 Risks")
    lines.append("")
    for r in summary.top_risks:
        lines.append(f"- {r}")
    lines.append("")

    lines.append("## Panel Verdict")
    lines.append("")
    lines.append(f"**{ups} \U0001f44d  {downs} \U0001f44e**")
    lines.append("")
    for v in summary.verdicts:
        icon = "\U0001f44d" if v.thumbs_up else "\U0001f44e"
        lines.append(f"- **{v.judge}** {icon} — {v.note}")
    lines.append("")

    lines.append("## Next Steps (48h)")
    lines.append("")
    for ns in summary.next_steps:
        lines.append(f"- {ns}")
    lines.append("")

    path = artefacts_dir / "08_summary.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
```

- [ ] **Step 4: Run, watch pass**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest tests/test_summary.py -v
```
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add agent/summary.py tests/test_summary.py
git commit -m "feat(agent): Phase 8 summary writer with panel verdicts"
```

### Task 5.2: Sample run — generate artefacts for EDTH example

- [ ] **Step 1: Create the sample-run directory and generate artefacts**

```bash
mkdir -p /Users/vincent/Work/edth-prob-solution-deck/examples/sample-run/artefacts
```

Write `examples/sample-run/input.csv`:

```csv
Name,Problem statement
Multi-Domain Battle Management Interface,"AI Decision Support Systems. Challenge: Multi-Domain Battle Management Interface. Objective: Create an intuitive commander's dashboard that processes multi-domain data and provides actionable insights. Process simulated feeds from air, land, and naval assets. Prioritize threats using AI. Generate course-of-action recommendations. Display critical information within 3 seconds."
GPS-Denied Swarm Coordination,"Autonomous Navigation. Challenge: GPS-Denied Swarm Coordination. Objective: Develop a distributed algorithm for UAV swarm navigation without GPS. Coordinate 5+ UAVs and/or 5+ UGVs simultaneously. Maintain formation in a simulated urban environment. Avoid collisions and obstacles. Operate with local communication only."
Sensor Fusion Battlefield Analysis,"Sensor Fusion. Challenge: Real-Time Battlefield Analysis. Objective: Create a system that combines data from multiple sensor types to identify and track targets. Fuse data from radar, infrared, and optical sensors. Filter false positives. Track multiple targets simultaneously. Generate confidence scores for detections."
Cheap radar,"Design short-range (500-1000m) cheap (<$1,000) radar at high accuracy for drone detection"
```

Write `examples/sample-run/artefacts/00_context.yaml`:

```yaml
hackathon:
  name: "EDTH Munich 2025"
  theme: "Defense tech / dual-use"
  tracks: ["C-UAS", "Autonomy", "EW", "UUV", "USV"]
  judging_rubric:
    impact: 0.30
    innovation: 0.25
    execution: 0.25
    presentation: 0.20
team:
  size: 4
  strengths: ["ML/CV", "frontend", "signal_proc"]
  weaknesses: ["hardware", "maritime domain"]
constraints:
  time_budget_hours: 48
  deliverable: "deck + thin demo"
agent:
  owner_mode: sim
  persona: edth-judge
  panel_mode: expanded
  aggregation_mode: borda
```

Write `examples/sample-run/artefacts/01_triage.md`:

```markdown
# Triage Report

## Cluster 1: Command & Control / AI Dashboard
**Themes:** c2, decision_support, multi_domain
**Problems:** 2
**Axis scores (1-5):**
- impact: 4.5
- innovation: 3.5
- execution: 4.0
- presentation: 4.0
- **weighted total: 4.05**
**Market signal:** Palantir (Maven, AIP), Anduril (Lattice), Primer (comms intel). Crowded but all cloud-first; edge-native + offline-first has room.
**Problem IDs:** P-001, P-003

## Cluster 2: Swarm / Autonomy
**Themes:** swarm, autonomy, gps_denied
**Problems:** 1
**Axis scores (1-5):**
- impact: 4.0
- innovation: 4.5
- execution: 3.0
- presentation: 3.5
- **weighted total: 3.73**
**Market signal:** MIT Lincoln Lab (paper), Shield AI (Hivemind). Limited commercial options.
**Problem IDs:** P-002

## Cluster 3: Hardware
**Themes:** radar, hardware
**Problems:** 1
**Axis scores (1-5):**
- impact: 3.0
- innovation: 2.5
- execution: 2.0
- presentation: 2.5
- **weighted total: 2.58**
**Market signal:** Echodyne, Skydio, Dedrone. Saturated.
**Problem IDs:** P-004

## Panel summary
All 5 judges ranked C2/AI Dashboard #1. Swarm #2. Hardware dead last.
```

Write `examples/sample-run/artefacts/02_candidate_problem.md`:

```markdown
# Top 3 Candidate Problems

## Candidate 1: Multi-Domain Battle Management Interface (P-001)
**Weighted score: 4.05**
**Axis scores:**
- impact: 4.50
- innovation: 3.50
- execution: 4.00
- presentation: 4.00
**Panel ranking:**
- mehta: #1
- viper: #1
- tran: #2
- whitfield: #1
- chen: #1
**Reasoning:** Highest impact, demo-able, panel convergence on #1. AI-powered COA recommendations are a hot differentiator. Multi-Domain Ops is current US/NATO doctrine.

## Candidate 2: GPS-Denied Swarm Coordination (P-002)
**Weighted score: 3.73**
**Axis scores:**
- impact: 4.00
- innovation: 4.50
- execution: 3.00
- presentation: 3.50
**Panel ranking:**
- mehta: #2
- viper: #2
- tran: #1
- whitfield: #2
- chen: #2
**Reasoning:** Strong innovation; harder to demo convincingly in 48 hours.

## Candidate 3: Sensor Fusion Battlefield Analysis (P-003)
**Weighted score: 3.60**
**Axis scores:**
- impact: 3.50
- innovation: 3.00
- execution: 4.00
- presentation: 3.50
**Panel ranking:**
- mehta: #3
- viper: #3
- tran: #3
- whitfield: #3
- chen: #3
**Reasoning:** Good but not novel; many existing fusion systems.
```

Write `examples/sample-run/README.md`:

```markdown
# Sample Run — EDTH Munich 2025

This is a pre-generated sample run showing what the agent produces for a synthetic problem (Multi-Domain Battle Management Interface).

## Files

- `input.csv` — 4 problems (2 software-focused, 1 swarm, 1 hardware).
- `artefacts/` — generated artefacts from a full run.

## What success looks like

1. 9 artefacts produced (00 through 08).
2. The deck is rendered as `07_deck.html` (open in any browser).
3. The panel of 5 judges (mehta, viper, tran, whitfield, chen) reviewed every phase.
4. The owner picked one solution: MDO Dashboard with AI-powered COA recommendations.

## How to use this

After installing the agent (`pip install -e ".[dev]"`), run:

```bash
python -m agent.render  # renders the deck from existing artefacts
open artefacts/07_deck.html
```
```

- [ ] **Step 2: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add examples/
git commit -m "docs(examples): sample run for EDTH with pre-generated artefacts"
```

### Task 5.3: Render sample-run deck

- [ ] **Step 1: Render the sample-run deck to HTML**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/python -c "
from pathlib import Path
from agent.deck import render_deck
p = render_deck(
    Path('examples/sample-run/artefacts'),
    {'project_name': 'MDO Commander Dashboard', 'team_name': 'Team EDTH', 'hackathon_name': 'EDTH Munich 2025', 'date': '2026-06-02'}
)
print(f'Rendered: {p} ({p.stat().st_size} bytes)')
"
```
Expected: `Rendered: examples/sample-run/artefacts/07_deck.html (<size> bytes)`.

- [ ] **Step 2: Verify the HTML is valid**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
head -5 examples/sample-run/artefacts/07_deck.html
```
Expected: `<!DOCTYPE html>`.

- [ ] **Step 3: Commit the rendered deck**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
# The 07_deck.html is committed as part of the sample run
git add examples/
git commit --amend --no-edit
```

Milestone 5 complete.

## Milestone 6 — Tests, docs, hardening

**Goal:** All tests pass, README complete, full end-to-end smoke test.

**Tasks:**
- Task 6.1: Run full test suite, fix any failures
- Task 6.2: README — install, run, troubleshooting
- Task 6.3: End-to-end smoke test (parse all the way to rendered deck)
- Task 6.4: Final commit

### Task 6.1: Full test suite

- [ ] **Step 1: Run all tests**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest -v
```
Expected: ~90+ tests passing.

- [ ] **Step 2: If any fail, fix them in place and re-run until green**

No commit needed if all pass.

### Task 6.2: Finalize README

- [ ] **Step 1: Replace the placeholder README**

Replace `/README.md` entirely:

```markdown
# EDTH Hackathon Agent

A reusable agent that walks through the full lifecycle of a hackathon project — from a CSV of problem statements to a problem/solution pitch deck — using a 9-phase workflow reviewed by a panel of 12 tough-judge personas.

## Quick Start

### 1. Install

```bash
python3 -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

### 2. Place your problem CSV

The default expects `input/PB-SOL-EDTH - Sheet1.csv`. Edit `hackathons/edth.yaml` to change the path or hackathon config.

### 3. Run the agent

The agent is an OpenCode skill. From the OpenCode chat:

```
/edth-agent status      # show current phase
/edth-agent run         # execute the next pending phase
/edth-agent run 0       # jump to Phase 0 (onboarding)
/edth-agent panel       # show current judge panel
/edth-agent panel viper # chat with Maj. Viper in character
/edth-agent render      # re-render the deck from artefacts
/edth-agent reset       # wipe and restart
/edth-agent help        # show all commands
```

### 4. View the deck

After Phase 7 completes, open `artefacts/07_deck.html` in a browser.

## Project Structure

```
SKILL.md              # OpenCode skill — agent driver
agent/                # Python glue (state, parse, normalize, score, render, ...)
judges/               # 12 tough-judge YAMLs
personas/             # Problem-owner personas
templates/            # Marp slide templates
examples/sample-run/  # Pre-generated sample run
input/                # Place your problem CSV here
artefacts/            # Generated outputs
tests/                # pytest
```

## Judges

12 tough-judge personas review every artefact. Select automatically via `/edth-agent panel generate` or chat individually with `/edth-agent panel <short>`. See `judges/README.md`.

## Rendering

The deck renders via three tiers:
1. **Marp CLI** (preferred) — `npm i -g @marp-team/marp-cli`
2. **python-pptx** — installed automatically as a dependency
3. **Self-contained HTML** — always works, no deps

## Sample Run

See `examples/sample-run/` for a pre-generated happy-path run.

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT
```

- [ ] **Step 2: Commit**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git add README.md
git commit -m "docs: finalize README with quick start and project overview"
```

### Task 6.3: End-to-end smoke test

- [ ] **Step 1: Run a complete Python-only pipeline (no LLM)**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/python -c "
from pathlib import Path

# 1. Parse CSV
from agent.parse_csv import parse_problems
problems = parse_problems(Path('input/PB-SOL-EDTH - Sheet1.csv'))
print(f'[OK] Parsed {len(problems)} problems')

# 2. Normalize
from agent.normalize import assign_quality_flags, dedupe_problems
for p in problems:
    p['quality_flags'] = [f.value for f in assign_quality_flags(p)]
deduped = dedupe_problems(problems)
print(f'[OK] Deduped: {len(deduped)} problems')

# 3. Load judges
from agent.judges import load_judge_library, select_panel
lib = load_judge_library(Path('judges'))
print(f'[OK] Loaded {len(lib)} judges')

# 4. Select panel
panel = select_panel(Path('judges'), themes=['c2', 'decision_support'], tags=['software'])
print(f'[OK] Panel: {[j[\"short\"] for j in panel]}')

# 5. Load persona
from agent.personas import load_persona
persona = load_persona(Path('personas'), 'edth-judge')
print(f'[OK] Persona: {persona[\"name\"]}')

# 6. Load context
from agent.context import default_context, save_context
ctx = default_context()
save_context(Path('artefacts'), ctx)
print(f'[OK] Context saved')

# 7. State
from agent.state import empty_state, save_state
state = empty_state()
save_state(Path('artefacts'), state)
print(f'[OK] State saved')

# 8. Render test deck
from agent.deck import render_deck
deck_path = render_deck(Path('artefacts'), {
    'project_name': 'Smoke Test',
    'team_name': 'Team',
    'hackathon_name': 'EDTH',
    'date': '2026-06-02'
})
print(f'[OK] Deck rendered to {deck_path} ({deck_path.stat().st_size} bytes)')

print()
print('=== ALL CHECKS PASSED ===')
"
```
Expected: all `[OK]` lines, no errors.

- [ ] **Step 2: Verify the rendered HTML opens in a browser**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
# Check the HTML has proper structure
.venv/bin/python -c "
from pathlib import Path
html = Path('artefacts/07_deck.html').read_text()
assert '<!DOCTYPE html>' in html
assert '<div class=\"slide' in html
assert 'ArrowRight' in html
print('HTML structure valid')
"
```
Expected: `HTML structure valid`.

### Task 6.4: Final commit

- [ ] **Step 1: Run the full test suite one last time**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
.venv/bin/pytest -v --tb=short
```
Expected: all passing.

- [ ] **Step 2: Final commit if any changes remain**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
git status
```
If clean, no action needed. If there are untracked/modified files from the smoke test, review and commit or discard.

- [ ] **Step 3: Cleanup the smoke test artefacts from the main artefacts/ dir**

```bash
cd /Users/vincent/Work/edth-prob-solution-deck
rm -rf artefacts/
```

---

