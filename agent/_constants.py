"""Constants shared across agent modules.

Eliminates magic strings: artefact file names, phase statuses, render
modes, phase count, audit limits, and default config values.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class PhaseStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class RenderMode(StrEnum):
    MARP = "marp"
    PPTX = "pptx"
    HTML = "html"


PHASE_COUNT: Final[int] = 9

MAX_AUDIT_RESPONSE: Final[int] = 5000

MIN_PANEL_SIZE: Final[int] = 2
MAX_PANEL_SIZE: Final[int] = 12

# ── Artefact file names ──────────────────────────────────────────────
# Single source of truth for every artefact filename used by both
# producers (write_* functions) and consumers (validate.py checks).
# Usage: ARTEFACTS.TRIAGE, ARTEFACTS.DECK, etc.
ARTEFACTS = type(
    "_Artefacts",
    (),
    {
        "TRIAGE": "01_triage.md",
        "CANDIDATE": "02_candidate_problem.md",
        "OWNER_QUESTIONS": "02_owner_questions.md",
        "OWNER_ANSWERS": "02_owner_answers.md",
        "SUB_PROBLEM": "03_chosen_sub_problem.md",
        "SOLUTION_CANDIDATES": "04_solution_candidates.md",
        "RANKED_SOLUTIONS": "05_ranked_solutions.md",
        "OWNER_PICK": "05_owner_pick.md",
        "DEMO_PLAN": "06_demo_plan.md",
        "MARKET": "07_market.md",
        "COMPETITION": "07_competition.md",
        "BUSINESS_MODEL": "07_business_model.md",
        "DECK_MD": "07_deck.md",
        "DECK_HTML": "07_deck.html",
        "DECK_PDF": "07_deck.pdf",
        "DECK_PPTX": "07_deck.pptx",
        "SUMMARY": "08_summary.md",
        "STATE": "state.json",
        "CONTEXT": "00_context.yaml",
        "TEAM_PROFILE": "team_profile.md",
        "QUESTION_SHEET": "question_sheet.md",
        "DEMO_TASKS": "demo_tasks.md",
    },
)

# ── Validation config ────────────────────────────────────────────────
# Minimum expected file sizes (bytes) per artefact
MIN_SIZES: Final[dict[str, int]] = {
    ARTEFACTS.TRIAGE: 500,
    ARTEFACTS.CANDIDATE: 300,
    ARTEFACTS.OWNER_QUESTIONS: 200,
    ARTEFACTS.OWNER_ANSWERS: 200,
    ARTEFACTS.SUB_PROBLEM: 300,
    ARTEFACTS.SOLUTION_CANDIDATES: 500,
    ARTEFACTS.RANKED_SOLUTIONS: 300,
    ARTEFACTS.OWNER_PICK: 100,
    ARTEFACTS.DEMO_PLAN: 400,
    ARTEFACTS.MARKET: 300,
    ARTEFACTS.COMPETITION: 300,
    ARTEFACTS.BUSINESS_MODEL: 300,
    ARTEFACTS.DECK_MD: 500,
    ARTEFACTS.SUMMARY: 300,
}

# Artefacts each phase depends on (inputs that must exist and be non-empty)
PHASE_DEPENDENCIES: Final[dict[int, list[str]]] = {
    1: [],
    2: [ARTEFACTS.TRIAGE],
    3: [ARTEFACTS.CANDIDATE],
    4: [ARTEFACTS.SUB_PROBLEM],
    5: [ARTEFACTS.SOLUTION_CANDIDATES],
    6: [ARTEFACTS.OWNER_PICK],
    7: [ARTEFACTS.CANDIDATE, ARTEFACTS.OWNER_PICK, ARTEFACTS.DEMO_PLAN],
    8: [],
}


# ── Default state config ─────────────────────────────────────────────
DEFAULT_STATE_CONFIG: Final[dict[str, object]] = {
    "csv_file": "input/sample-problems.csv",
    "artefacts_dir": "artefacts",
    "persona_file": "hackathons/edth.yaml",
    "owner_mode": "real",
    "persona": "edth-judge",
    "panel_mode": "expanded",
    "aggregation_mode": "borda",
}
