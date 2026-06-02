"""Test skill integrity — verifies that all Python functions and modules
referenced in SKILL.md actually exist and are importable.

This is a build-time safety check. If the SKILL.md tells the LLM to call
`agent.foo.bar()` and `bar()` doesn't exist, the agent will fail at runtime.
This test catches that before it happens.
"""

from __future__ import annotations

from pathlib import Path

import pytest

SKILL_PATHS = [
    ".opencode/skills/edth-agent/SKILL.md",
    ".claude/skills/edth-agent/SKILL.md",
]

# Functions the SKILL.md references as `agent.<module>.<function>()`
EXPECTED_CALLS = [
    ("state", "empty_state"),
    ("state", "load_state"),
    ("state", "save_state"),
    ("state", "get_phase_status"),
    ("state", "mark_phase_completed"),
    ("state", "mark_phase_in_progress"),
    ("state", "rollback_phase"),
    ("state", "set_config"),
    ("state", "set_decision"),
    ("state", "lock_panel"),
    ("state", "elapsed_minutes"),
    ("state", "expected_phases_remaining"),
    ("parse_csv", "parse_problems"),
    ("parse_csv", "parse_problems_safe"),
    ("parse_csv", "parse_problems_from_string"),
    ("normalize", "assign_quality_flags"),
    ("normalize", "dedupe_problems"),
    ("rubric", "score_to_weighted"),
    ("rubric", "get_axis_weights"),
    ("triage", "write_triage_report"),
    ("triage", "TriageReport"),
    ("triage", "Cluster"),
    ("elicitation", "write_owner_questions"),
    ("elicitation", "write_owner_answers"),
    ("elicitation", "OwnerQuestion"),
    ("candidates", "write_candidate_problem"),
    ("candidates", "Candidate"),
    ("sub_problem", "write_sub_problem"),
    ("sub_problem", "SubProblem"),
    ("ideation", "dedupe_ideas"),
    ("ideation", "write_solution_candidates"),
    ("ideation", "Idea"),
    ("aggregation", "borda_count"),
    ("aggregation", "weighted_borda"),
    ("aggregation", "approval_vote"),
    ("ranking", "write_ranked_solutions"),
    ("ranking", "write_owner_pick"),
    ("ranking", "RankedSolution"),
    ("demo_plan", "write_demo_plan"),
    ("demo_plan", "DemoPlan"),
    ("demo_tasks", "write_demo_tasks"),
    ("demo_tasks", "DemoTask"),
    ("demo_tasks", "DemoTaskPlan"),
    ("market", "write_market"),
    ("market", "write_competition"),
    ("market", "write_business_model"),
    ("deck", "compile_deck_md"),
    ("deck", "render_deck"),
    ("render", "render_html_deck"),
    ("summary", "write_summary"),
    ("summary", "Summary"),
    ("summary", "JudgeVerdict"),
    ("sheet", "write_question_sheet"),
    ("sheet", "QuestionSheet"),
    ("sheet", "GoodQuestion"),
    ("sheet", "BadQuestion"),
    ("sheet", "ClusterSheet"),
    ("team", "word_count"),
    ("team", "write_team_profile"),
    ("team", "MemberProfile"),
    ("team", "TeamProfile"),
    ("team", "TeamDynamics"),
    ("audit", "write_audit_entry"),
    ("audit", "AuditEntry"),
    ("context", "default_context"),
    ("context", "save_context"),
    ("context", "load_context"),
    ("judges", "load_judge_library"),
    ("judges", "select_panel"),
    ("personas", "load_persona"),
    ("validate", "run_validation"),
    ("validate", "preflight_check"),
]


def _find_skill_md() -> Path:
    """Find an existing SKILL.md — try .opencode then .claude."""
    for sp in SKILL_PATHS:
        path = Path(__file__).parent.parent / sp
        if path.exists():
            return path
    return Path(".")


def test_skill_md_exists() -> None:
    path = _find_skill_md()
    assert path.exists(), f"SKILL.md not found at any of {SKILL_PATHS}"
    assert path.name == "SKILL.md"


def test_skill_md_is_well_formed_markdown() -> None:
    path = _find_skill_md()
    content = path.read_text()
    assert content.startswith("---"), "SKILL.md must start with YAML frontmatter"
    assert "name:" in content[:200], "SKILL.md frontmatter must include name"


@pytest.mark.parametrize("module_name,attr_name", EXPECTED_CALLS)
def test_all_skill_referenced_modules_exist(module_name: str, attr_name: str) -> None:
    """Every function/dataclass referenced as agent.X.Y in SKILL.md must import."""
    mod = __import__(f"agent.{module_name}", fromlist=[attr_name])
    assert hasattr(mod, attr_name), f"agent.{module_name}.{attr_name} does not exist"


def test_skill_md_has_required_sections() -> None:
    path = _find_skill_md()
    content = path.read_text()
    required = [
        "## Behavior rules",
        "## Commands",
        "## Phase 1 — Triage",
        "## Phase 2 — Elicit",
        "## Phase 3 — Sub-problem",
        "## Phase 4 — Divergent ideation",
        "## Phase 5 — Research",
        "## Phase 6 — Demo",
        "## Phase 7 — Deck",
        "## Phase 8 — Final",
        "## Phase 0 — Onboarding",
        "## Team Discovery",
        "## Dry-run mode",
        "## Skip-to mode",
        "## Validate command",
    ]
    for section in required:
        assert section in content, f"SKILL.md missing section: {section}"
