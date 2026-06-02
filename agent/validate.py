"""Artefact validation — checks completeness, consistency, and integrity.

Called by `/edth-agent validate` or internally after each phase.
Reports issues at file-level granularity.

See SKILL.md "Validate command" section.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

# Minimum expected file sizes in bytes for each artefact
_MIN_SIZES: dict[str, int] = {
    "01_triage.md": 500,  # at least a few clusters
    "02_candidate_problem.md": 300,
    "02_owner_questions.md": 200,
    "02_owner_answers.md": 200,
    "03_chosen_sub_problem.md": 300,
    "04_solution_candidates.md": 500,
    "05_ranked_solutions.md": 300,
    "05_owner_pick.md": 100,
    "06_demo_plan.md": 400,
    "07_market.md": 300,
    "07_competition.md": 300,
    "07_business_model.md": 300,
    "07_deck.md": 500,
    "08_summary.md": 300,
}

# Artefacts each phase depends on (inputs that must exist and be non-empty)
_PHASE_DEPENDENCIES: dict[int, list[str]] = {
    1: [],  # Phase 1: no dependencies
    2: ["01_triage.md"],
    3: ["02_candidate_problem.md"],
    4: ["03_chosen_sub_problem.md"],
    5: ["04_solution_candidates.md"],
    6: ["05_owner_pick.md"],
    7: ["02_candidate_problem.md", "05_owner_pick.md", "06_demo_plan.md"],
    8: [],  # reads all, checked per-phase
}


def run_validation(artefacts_dir: Path, quiet: bool = False) -> tuple[bool, list[str]]:
    """Run all validation checks. Returns (passes, issues_list).

    If quiet=True, returns without printing. If quiet=False, prints results.
    """
    issues: list[str] = []
    state = _load_json_safe(artefacts_dir / "state.json")

    # 0. State file integrity
    _check_state(state, issues)

    # 1. Phase 1: Triage
    if (artefacts_dir / "01_triage.md").exists():
        text = _slurp(artefacts_dir, "01_triage.md")
        cluster_count = text.count("## Cluster ")
        if cluster_count < 2:
            issues.append(f"01_triage.md: only {cluster_count} clusters found (expected \u22652)")
        if "weighted total" not in text:
            issues.append("01_triage.md: no weighted score found")
        if "Market signal" not in text:
            issues.append("01_triage.md: no market signal section found")

    # 2. Phase 2: Candidate problem
    if (artefacts_dir / "02_candidate_problem.md").exists():
        text = _slurp(artefacts_dir, "02_candidate_problem.md")
        cand_count = text.count("## Candidate ")
        if cand_count < 2:
            issues.append(
                f"02_candidate_problem.md: only {cand_count} candidates (expected \u22652)"
            )
        if "Weighted score" not in text:
            issues.append("02_candidate_problem.md: no weighted score found")

    if (artefacts_dir / "02_owner_questions.md").exists():
        text = _slurp(artefacts_dir, "02_owner_questions.md")
        q_count = text.count("## Q-")
        if q_count < 3:
            issues.append(f"02_owner_questions.md: only {q_count} questions (expected \u22654)")

    if (artefacts_dir / "02_owner_answers.md").exists():
        text = _slurp(artefacts_dir, "02_owner_answers.md")
        if len(text.strip()) < 100:
            issues.append("02_owner_answers.md: very short \u2014 maybe missing answers")

    # 3. Phase 3: Sub-problem
    if (artefacts_dir / "03_chosen_sub_problem.md").exists():
        text = _slurp(artefacts_dir, "03_chosen_sub_problem.md")
        sp_count = text.count("## SP-")
        if sp_count < 3:
            issues.append(
                f"03_chosen_sub_problem.md: only {sp_count} sub-problems (expected \u22653)"
            )
        if "ROI score" not in text:
            issues.append("03_chosen_sub_problem.md: no ROI scores found")

    # 4. Phase 4: Ideation
    if (artefacts_dir / "04_solution_candidates.md").exists():
        text = _slurp(artefacts_dir, "04_solution_candidates.md")
        idea_count = text.count("## ")
        if idea_count < 5:
            issues.append(f"04_solution_candidates.md: only {idea_count} ideas (expected \u22655)")
        if "rating" not in text.lower() and "Rating" not in text:
            issues.append("04_solution_candidates.md: no ratings found")

    # 5. Phase 5: Ranking
    if (artefacts_dir / "05_ranked_solutions.md").exists():
        text = _slurp(artefacts_dir, "05_ranked_solutions.md")
        if "Research" not in text and "research" not in text.lower():
            issues.append("05_ranked_solutions.md: no research section found")
        if "Aggregate score" not in text and "aggregate" not in text.lower():
            issues.append("05_ranked_solutions.md: no aggregate scores found")
        # At least one URL or company reference in research
        if "http" not in text and "." not in text.split("Research")[-1][:500]:
            issues.append("05_ranked_solutions.md: no URLs or references in research")

    if (artefacts_dir / "05_owner_pick.md").exists():
        text = _slurp(artefacts_dir, "05_owner_pick.md")
        if len(text.strip()) < 50:
            issues.append("05_owner_pick.md: very short \u2014 may be incomplete")
        if "Chosen" not in text and "chosen" not in text.lower():
            issues.append("05_owner_pick.md: no chosen solution ID found")

    # 6. Phase 6: Demo plan
    if (artefacts_dir / "06_demo_plan.md").exists():
        text = _slurp(artefacts_dir, "06_demo_plan.md")
        beat_count = text.count("**[")
        if beat_count < 5:
            issues.append(f"06_demo_plan.md: only {beat_count} timed beats (expected \u22655)")
        if "Risk Register" not in text and "risk" not in text.lower():
            issues.append("06_demo_plan.md: no risk register found")

    # 7. Phase 7: Deck + market
    if (artefacts_dir / "07_market.md").exists():
        text = _slurp(artefacts_dir, "07_market.md")
        if len(text.strip()) < 100:
            issues.append("07_market.md: very short \u2014 may be incomplete")

    if (artefacts_dir / "07_competition.md").exists():
        text = _slurp(artefacts_dir, "07_competition.md")
        if "|" not in text:
            issues.append("07_competition.md: no table found \u2014 expected competitor table")

    if (artefacts_dir / "07_business_model.md").exists():
        text = _slurp(artefacts_dir, "07_business_model.md")
        if len(text.strip()) < 100:
            issues.append("07_business_model.md: very short")

    if (artefacts_dir / "07_deck.md").exists():
        text = _slurp(artefacts_dir, "07_deck.md")
        slide_count = text.count("\n---\n") + 1
        if slide_count < 3:
            issues.append(f"07_deck.md: only {slide_count} slides (expected \u22653)")
        if "---" not in text:
            issues.append("07_deck.md: no slide separators found")

    if (artefacts_dir / "07_deck.html").exists():
        try:
            html = _slurp(artefacts_dir, "07_deck.html")
            if "ArrowRight" not in html and "keydown" not in html:
                issues.append("07_deck.html: no keyboard navigation \u2014 may be incomplete")
        except Exception:
            issues.append("07_deck.html: could not be read")

    # 8. Phase 8: Summary
    if (artefacts_dir / "08_summary.md").exists():
        text = _slurp(artefacts_dir, "08_summary.md")
        if "## One-Paragraph Pitch" not in text:
            issues.append("08_summary.md: missing 'One-Paragraph Pitch' section")
        if "## Panel Verdict" not in text:
            issues.append("08_summary.md: missing 'Panel Verdict' section")

    # 9. File size minimums
    for fname, min_size in _MIN_SIZES.items():
        path = artefacts_dir / fname
        if path.exists() and path.stat().st_size < min_size:
            issues.append(
                f"{fname}: only {path.stat().st_size} bytes "
                f"(expected \u2265{min_size}) \u2014 may be truncated"
            )

    # 10. Cross-phase consistency
    if state:
        pid = state.get("decisions", {}).get("chosen_problem_id")
        if pid:
            cand_text = _slurp(artefacts_dir, "02_candidate_problem.md")
            if cand_text and pid not in cand_text:
                issues.append(
                    f"Consistency: chosen_problem_id '{pid}' not found in 02_candidate_problem.md"
                )

    # Report
    if not quiet:
        if issues:
            print(f"\u26a0\ufe0f  {len(issues)} issue(s):")
            for issue in issues:
                print(f"  - {issue}")
        else:
            n_checks = _count_checks(artefacts_dir)
            print(f"\u2705 All {n_checks} checks passed.")

    return len(issues) == 0, issues


def preflight_check(artefacts_dir: Path, phase: int) -> tuple[bool, list[str]]:
    """Verify that all input artefacts for a phase exist and are non-empty.

    Call before starting any phase work. Returns (ok, issues).
    """
    issues: list[str] = []
    deps = _PHASE_DEPENDENCIES.get(phase, [])
    for dep in deps:
        path = artefacts_dir / dep
        if not path.exists():
            issues.append(f"Missing input: {dep} \u2014 run prior phase first.")
        elif path.stat().st_size == 0:
            issues.append(f"Empty input: {dep} \u2014 re-run prior phase.")
    return len(issues) == 0, issues


def _check_state(state: dict, issues: list[str]) -> None:
    if not state:
        issues.append("state.json is missing or invalid JSON")
    else:
        if "current_phase" not in state:
            issues.append("state.json: missing current_phase")
        elif not isinstance(state.get("current_phase"), int):
            issues.append("state.json: current_phase must be an integer")
        else:
            phase = state["current_phase"]
            if phase < 0 or phase > 9:
                issues.append(f"state.json: current_phase out of range: {phase}")

        if "phases" not in state:
            issues.append("state.json: missing phases dict")
        else:
            for p in range(9):
                ps = state["phases"].get(str(p))
                if ps is None:
                    continue
                status = ps.get("status", "")
                artefact = ps.get("artefact", "")
                if status == "completed":
                    check_path = Path(artefact) if artefact else None
                    if not check_path or not check_path.exists():
                        issues.append(
                            f"state.json: phase {p} marked completed but "
                            f"artefact missing: {artefact}"
                        )
                    elif check_path.stat().st_size == 0:
                        issues.append(f"state.json: phase {p} artefact is empty: {artefact}")

        if state.get("panel", {}).get("locked"):
            panel_size = len(state["panel"].get("auto_selected", []))
            if panel_size < 2 or panel_size > 12:
                issues.append(
                    f"state.json: locked panel has {panel_size} judges (expected 3-5, max 12)"
                )

        for dkey, dval in state.get("decisions", {}).items():
            if dval and not isinstance(dval, str):
                issues.append(f"state.json: decisions.{dkey} is not a string: {dval}")


def _count_checks(artefacts_dir: Path) -> int:
    """Rough count of checks for display."""
    count = 4  # state.json checks
    for fname in [
        "01_triage.md",
        "02_candidate_problem.md",
        "02_owner_questions.md",
        "02_owner_answers.md",
        "03_chosen_sub_problem.md",
        "04_solution_candidates.md",
        "05_ranked_solutions.md",
        "05_owner_pick.md",
        "06_demo_plan.md",
        "07_market.md",
        "07_competition.md",
        "07_business_model.md",
        "07_deck.md",
        "08_summary.md",
    ]:
        if (artefacts_dir / fname).exists():
            count += 1
    return count


def _load_json_safe(path: Path) -> dict[str, Any]:
    import json

    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _slurp(artefacts_dir: Path, filename: str) -> str:
    path = artefacts_dir / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""
