"""Artefact validation — checks completeness, consistency, and integrity.

Called by `/edth-agent validate` or internally after each phase.
Reports issues at file-level granularity.

See SKILL.md "Validate command" section.
"""

from __future__ import annotations

from pathlib import Path

from agent._constants import ARTEFACTS, MIN_SIZES, PHASE_COUNT, PHASE_DEPENDENCIES
from agent._util import load_json_safe, slurp_file


def run_validation(artefacts_dir: Path, quiet: bool = False) -> tuple[bool, list[str]]:
    """Run all validation checks across every phase's artefacts.

    Returns (all_pass, issues_list). Prints results unless quiet=True.
    """
    issues: list[str] = []
    state = load_json_safe(artefacts_dir / ARTEFACTS.STATE)

    _check_state(state, issues)
    _validate_phase_1(artefacts_dir, issues)
    _validate_phase_2(artefacts_dir, issues)
    _validate_phase_3(artefacts_dir, issues)
    _validate_phase_4(artefacts_dir, issues)
    _validate_phase_5(artefacts_dir, issues)
    _validate_phase_6(artefacts_dir, issues)
    _validate_phase_7(artefacts_dir, issues)
    _validate_phase_8(artefacts_dir, issues)
    _validate_file_sizes(artefacts_dir, issues)
    _validate_cross_phase(state, artefacts_dir, issues)

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
    deps = PHASE_DEPENDENCIES.get(phase, [])
    for dep in deps:
        path = artefacts_dir / dep
        if not path.exists():
            issues.append(f"Missing input: {dep} \u2014 run prior phase first.")
        elif path.stat().st_size == 0:
            issues.append(f"Empty input: {dep} \u2014 re-run prior phase.")
    return len(issues) == 0, issues


# ── Per-phase validators ─────────────────────────────────────────────


def _validate_phase_1(artefacts_dir: Path, issues: list[str]) -> None:
    """Phase 1 — Triage report."""
    if not (artefacts_dir / ARTEFACTS.TRIAGE).exists():
        return
    text = slurp_file(artefacts_dir, ARTEFACTS.TRIAGE)
    cluster_count = text.count("## Cluster ")
    if cluster_count < 2:
        issues.append(f"{ARTEFACTS.TRIAGE}: only {cluster_count} clusters found (expected \u22652)")
    if "weighted total" not in text:
        issues.append(f"{ARTEFACTS.TRIAGE}: no weighted score found")
    if "Market signal" not in text:
        issues.append(f"{ARTEFACTS.TRIAGE}: no market signal section found")


def _validate_phase_2(artefacts_dir: Path, issues: list[str]) -> None:
    """Phase 2 — Candidate problem and owner elicitation."""
    if (artefacts_dir / ARTEFACTS.CANDIDATE).exists():
        text = slurp_file(artefacts_dir, ARTEFACTS.CANDIDATE)
        cand_count = text.count("## Candidate ")
        if cand_count < 2:
            issues.append(f"{ARTEFACTS.CANDIDATE}: only {cand_count} candidates (expected \u22652)")
        if "Weighted score" not in text:
            issues.append(f"{ARTEFACTS.CANDIDATE}: no weighted score found")

    if (artefacts_dir / ARTEFACTS.OWNER_QUESTIONS).exists():
        text = slurp_file(artefacts_dir, ARTEFACTS.OWNER_QUESTIONS)
        q_count = text.count("## Q-")
        if q_count < 3:
            issues.append(
                f"{ARTEFACTS.OWNER_QUESTIONS}: only {q_count} questions (expected \u22654)"
            )

    if (artefacts_dir / ARTEFACTS.OWNER_ANSWERS).exists():
        text = slurp_file(artefacts_dir, ARTEFACTS.OWNER_ANSWERS)
        if len(text.strip()) < 100:
            issues.append(f"{ARTEFACTS.OWNER_ANSWERS}: very short \u2014 maybe missing answers")


def _validate_phase_3(artefacts_dir: Path, issues: list[str]) -> None:
    """Phase 3 — Sub-problem decomposition."""
    if not (artefacts_dir / ARTEFACTS.SUB_PROBLEM).exists():
        return
    text = slurp_file(artefacts_dir, ARTEFACTS.SUB_PROBLEM)
    sp_count = text.count("## SP-")
    if sp_count < 3:
        issues.append(f"{ARTEFACTS.SUB_PROBLEM}: only {sp_count} sub-problems (expected \u22653)")
    if "ROI score" not in text:
        issues.append(f"{ARTEFACTS.SUB_PROBLEM}: no ROI scores found")


def _validate_phase_4(artefacts_dir: Path, issues: list[str]) -> None:
    """Phase 4 — Divergent ideation."""
    if not (artefacts_dir / ARTEFACTS.SOLUTION_CANDIDATES).exists():
        return
    text = slurp_file(artefacts_dir, ARTEFACTS.SOLUTION_CANDIDATES)
    idea_count = text.count("## ")
    if idea_count < 5:
        issues.append(
            f"{ARTEFACTS.SOLUTION_CANDIDATES}: only {idea_count} ideas (expected \u22655)"
        )
    if "rating" not in text.lower() and "Rating" not in text:
        issues.append(f"{ARTEFACTS.SOLUTION_CANDIDATES}: no ratings found")


def _validate_phase_5(artefacts_dir: Path, issues: list[str]) -> None:
    """Phase 5 — Research ranking and owner pick."""
    if (artefacts_dir / ARTEFACTS.RANKED_SOLUTIONS).exists():
        text = slurp_file(artefacts_dir, ARTEFACTS.RANKED_SOLUTIONS)
        if "Research" not in text and "research" not in text.lower():
            issues.append(f"{ARTEFACTS.RANKED_SOLUTIONS}: no research section found")
        if "Aggregate score" not in text and "aggregate" not in text.lower():
            issues.append(f"{ARTEFACTS.RANKED_SOLUTIONS}: no aggregate scores found")
        if "http" not in text and "." not in text.split("Research")[-1][:500]:
            issues.append(f"{ARTEFACTS.RANKED_SOLUTIONS}: no URLs or references in research")

    if (artefacts_dir / ARTEFACTS.OWNER_PICK).exists():
        text = slurp_file(artefacts_dir, ARTEFACTS.OWNER_PICK)
        if len(text.strip()) < 50:
            issues.append(f"{ARTEFACTS.OWNER_PICK}: very short \u2014 may be incomplete")
        if "Chosen" not in text and "chosen" not in text.lower():
            issues.append(f"{ARTEFACTS.OWNER_PICK}: no chosen solution ID found")


def _validate_phase_6(artefacts_dir: Path, issues: list[str]) -> None:
    """Phase 6 — Demo plan."""
    if not (artefacts_dir / ARTEFACTS.DEMO_PLAN).exists():
        return
    text = slurp_file(artefacts_dir, ARTEFACTS.DEMO_PLAN)
    beat_count = text.count("**[")
    if beat_count < 5:
        issues.append(f"{ARTEFACTS.DEMO_PLAN}: only {beat_count} timed beats (expected \u22655)")
    if "Risk Register" not in text and "risk" not in text.lower():
        issues.append(f"{ARTEFACTS.DEMO_PLAN}: no risk register found")


def _validate_phase_7(artefacts_dir: Path, issues: list[str]) -> None:
    """Phase 7 — Market, competition, business model, and deck."""
    _check_min_length(artefacts_dir, ARTEFACTS.MARKET, 100, issues)
    _check_min_length(artefacts_dir, ARTEFACTS.BUSINESS_MODEL, 100, issues)

    if (artefacts_dir / ARTEFACTS.COMPETITION).exists():
        text = slurp_file(artefacts_dir, ARTEFACTS.COMPETITION)
        if "|" not in text:
            issues.append(
                f"{ARTEFACTS.COMPETITION}: no table found \u2014 expected competitor table"
            )

    if (artefacts_dir / ARTEFACTS.DECK_MD).exists():
        text = slurp_file(artefacts_dir, ARTEFACTS.DECK_MD)
        slide_count = text.count("\n---\n") + 1
        if slide_count < 3:
            issues.append(f"{ARTEFACTS.DECK_MD}: only {slide_count} slides (expected \u22653)")
        if "---" not in text:
            issues.append(f"{ARTEFACTS.DECK_MD}: no slide separators found")

    if (artefacts_dir / ARTEFACTS.DECK_HTML).exists():
        try:
            html = slurp_file(artefacts_dir, ARTEFACTS.DECK_HTML)
            if "ArrowRight" not in html and "keydown" not in html:
                issues.append(
                    f"{ARTEFACTS.DECK_HTML}: no keyboard navigation \u2014 may be incomplete"
                )
        except OSError:
            issues.append(f"{ARTEFACTS.DECK_HTML}: could not be read")


def _validate_phase_8(artefacts_dir: Path, issues: list[str]) -> None:
    """Phase 8 — Final summary."""
    if not (artefacts_dir / ARTEFACTS.SUMMARY).exists():
        return
    text = slurp_file(artefacts_dir, ARTEFACTS.SUMMARY)
    if "## One-Paragraph Pitch" not in text:
        issues.append(f"{ARTEFACTS.SUMMARY}: missing 'One-Paragraph Pitch' section")
    if "## Panel Verdict" not in text:
        issues.append(f"{ARTEFACTS.SUMMARY}: missing 'Panel Verdict' section")


def _validate_file_sizes(artefacts_dir: Path, issues: list[str]) -> None:
    for fname, min_size in MIN_SIZES.items():
        path = artefacts_dir / fname
        if path.exists() and path.stat().st_size < min_size:
            issues.append(
                f"{fname}: only {path.stat().st_size} bytes "
                f"(expected \u2265{min_size}) \u2014 may be truncated"
            )


def _validate_cross_phase(state: dict, artefacts_dir: Path, issues: list[str]) -> None:
    if not state:
        return
    pid = state.get("decisions", {}).get("chosen_problem_id")
    if pid:
        cand_text = slurp_file(artefacts_dir, ARTEFACTS.CANDIDATE)
        if cand_text and pid not in cand_text:
            issues.append(
                f"Consistency: chosen_problem_id '{pid}' not found in {ARTEFACTS.CANDIDATE}"
            )


def _check_min_length(artefacts_dir: Path, fname: str, min_chars: int, issues: list[str]) -> None:
    if (artefacts_dir / fname).exists():
        text = slurp_file(artefacts_dir, fname)
        if len(text.strip()) < min_chars:
            issues.append(f"{fname}: very short \u2014 may be incomplete")


# ── State file integrity ─────────────────────────────────────────────


def _check_state(state: dict, issues: list[str]) -> None:
    if not state:
        issues.append(f"{ARTEFACTS.STATE} is missing or invalid JSON")
        return

    cp = state.get("current_phase")
    if cp is None:
        issues.append(f"{ARTEFACTS.STATE}: missing current_phase")
    elif not isinstance(cp, int):
        issues.append(f"{ARTEFACTS.STATE}: current_phase must be an integer")
    elif cp < 0 or cp > PHASE_COUNT:
        issues.append(f"{ARTEFACTS.STATE}: current_phase out of range: {cp}")

    _check_state_phases(state, issues)
    _check_state_panel(state, issues)
    _check_state_decisions(state, issues)


def _check_state_phases(state: dict, issues: list[str]) -> None:
    if "phases" not in state:
        issues.append(f"{ARTEFACTS.STATE}: missing phases dict")
        return
    for p in range(PHASE_COUNT):
        ps = state["phases"].get(str(p))
        if ps is None:
            continue
        if ps.get("status") != "completed":
            continue
        artefact = ps.get("artefact", "")
        if not artefact:
            continue
        check_path = Path(artefact)
        if not check_path.exists():
            issues.append(
                f"{ARTEFACTS.STATE}: phase {p} marked completed but artefact missing: {artefact}"
            )
        elif check_path.stat().st_size == 0:
            issues.append(f"{ARTEFACTS.STATE}: phase {p} artefact is empty: {artefact}")


def _check_state_panel(state: dict, issues: list[str]) -> None:
    panel = state.get("panel", {})
    if not panel.get("locked"):
        return
    panel_size = len(panel.get("auto_selected", []))
    if panel_size < 2 or panel_size > 12:
        issues.append(
            f"{ARTEFACTS.STATE}: locked panel has {panel_size} judges (expected 3-5, max 12)"
        )


def _check_state_decisions(state: dict, issues: list[str]) -> None:
    for dkey, dval in state.get("decisions", {}).items():
        if dval and not isinstance(dval, str):
            issues.append(f"{ARTEFACTS.STATE}: decisions.{dkey} is not a string: {dval}")


# ── Helpers ──────────────────────────────────────────────────────────


def _count_checks(artefacts_dir: Path) -> int:
    count = 4
    for fname in MIN_SIZES:
        if (artefacts_dir / fname).exists():
            count += 1
    return count
