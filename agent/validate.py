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
    issues: list[str] = []
    state = load_json_safe(artefacts_dir / ARTEFACTS.STATE)

    _check_state(state, issues)

    # 1. Phase 1: Triage
    if (artefacts_dir / ARTEFACTS.TRIAGE).exists():
        text = slurp_file(artefacts_dir, ARTEFACTS.TRIAGE)
        cluster_count = text.count("## Cluster ")
        if cluster_count < 2:
            issues.append(
                f"{ARTEFACTS.TRIAGE}: only {cluster_count} clusters found (expected \u22652)"
            )
        if "weighted total" not in text:
            issues.append(f"{ARTEFACTS.TRIAGE}: no weighted score found")
        if "Market signal" not in text:
            issues.append(f"{ARTEFACTS.TRIAGE}: no market signal section found")

    # 2. Phase 2: Candidate problem
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

    # 3. Phase 3: Sub-problem
    if (artefacts_dir / ARTEFACTS.SUB_PROBLEM).exists():
        text = slurp_file(artefacts_dir, ARTEFACTS.SUB_PROBLEM)
        sp_count = text.count("## SP-")
        if sp_count < 3:
            issues.append(
                f"{ARTEFACTS.SUB_PROBLEM}: only {sp_count} sub-problems (expected \u22653)"
            )
        if "ROI score" not in text:
            issues.append(f"{ARTEFACTS.SUB_PROBLEM}: no ROI scores found")

    # 4. Phase 4: Ideation
    if (artefacts_dir / ARTEFACTS.SOLUTION_CANDIDATES).exists():
        text = slurp_file(artefacts_dir, ARTEFACTS.SOLUTION_CANDIDATES)
        idea_count = text.count("## ")
        if idea_count < 5:
            issues.append(
                f"{ARTEFACTS.SOLUTION_CANDIDATES}: only {idea_count} ideas (expected \u22655)"
            )
        if "rating" not in text.lower() and "Rating" not in text:
            issues.append(f"{ARTEFACTS.SOLUTION_CANDIDATES}: no ratings found")

    # 5. Phase 5: Ranking
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

    # 6. Phase 6: Demo plan
    if (artefacts_dir / ARTEFACTS.DEMO_PLAN).exists():
        text = slurp_file(artefacts_dir, ARTEFACTS.DEMO_PLAN)
        beat_count = text.count("**[")
        if beat_count < 5:
            issues.append(
                f"{ARTEFACTS.DEMO_PLAN}: only {beat_count} timed beats (expected \u22655)"
            )
        if "Risk Register" not in text and "risk" not in text.lower():
            issues.append(f"{ARTEFACTS.DEMO_PLAN}: no risk register found")

    # 7. Phase 7: Deck + market
    if (artefacts_dir / ARTEFACTS.MARKET).exists():
        text = slurp_file(artefacts_dir, ARTEFACTS.MARKET)
        if len(text.strip()) < 100:
            issues.append(f"{ARTEFACTS.MARKET}: very short \u2014 may be incomplete")

    if (artefacts_dir / ARTEFACTS.COMPETITION).exists():
        text = slurp_file(artefacts_dir, ARTEFACTS.COMPETITION)
        if "|" not in text:
            issues.append(
                f"{ARTEFACTS.COMPETITION}: no table found \u2014 expected competitor table"
            )

    if (artefacts_dir / ARTEFACTS.BUSINESS_MODEL).exists():
        text = slurp_file(artefacts_dir, ARTEFACTS.BUSINESS_MODEL)
        if len(text.strip()) < 100:
            issues.append(f"{ARTEFACTS.BUSINESS_MODEL}: very short")

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

    # 8. Phase 8: Summary
    if (artefacts_dir / ARTEFACTS.SUMMARY).exists():
        text = slurp_file(artefacts_dir, ARTEFACTS.SUMMARY)
        if "## One-Paragraph Pitch" not in text:
            issues.append(f"{ARTEFACTS.SUMMARY}: missing 'One-Paragraph Pitch' section")
        if "## Panel Verdict" not in text:
            issues.append(f"{ARTEFACTS.SUMMARY}: missing 'Panel Verdict' section")

    # 9. File size minimums
    for fname, min_size in MIN_SIZES.items():
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
            cand_text = slurp_file(artefacts_dir, ARTEFACTS.CANDIDATE)
            if cand_text and pid not in cand_text:
                issues.append(
                    f"Consistency: chosen_problem_id '{pid}' not found in {ARTEFACTS.CANDIDATE}"
                )

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
    issues: list[str] = []
    deps = PHASE_DEPENDENCIES.get(phase, [])
    for dep in deps:
        path = artefacts_dir / dep
        if not path.exists():
            issues.append(f"Missing input: {dep} \u2014 run prior phase first.")
        elif path.stat().st_size == 0:
            issues.append(f"Empty input: {dep} \u2014 re-run prior phase.")
    return len(issues) == 0, issues


def _check_state(state: dict, issues: list[str]) -> None:
    if not state:
        issues.append(f"{ARTEFACTS.STATE} is missing or invalid JSON")
    else:
        cp = state.get("current_phase")
        if cp is None:
            issues.append(f"{ARTEFACTS.STATE}: missing current_phase")
        elif not isinstance(cp, int):
            issues.append(f"{ARTEFACTS.STATE}: current_phase must be an integer")
        else:
            if cp < 0 or cp > PHASE_COUNT:
                issues.append(f"{ARTEFACTS.STATE}: current_phase out of range: {cp}")

        if "phases" not in state:
            issues.append(f"{ARTEFACTS.STATE}: missing phases dict")
        else:
            for p in range(PHASE_COUNT):
                ps = state["phases"].get(str(p))
                if ps is None:
                    continue
                status = ps.get("status", "")
                artefact = ps.get("artefact", "")
                if status == "completed":
                    check_path = Path(artefact) if artefact else None
                    if not check_path or not check_path.exists():
                        issues.append(
                            f"{ARTEFACTS.STATE}: phase {p} marked completed but "
                            f"artefact missing: {artefact}"
                        )
                    elif check_path.stat().st_size == 0:
                        issues.append(f"{ARTEFACTS.STATE}: phase {p} artefact is empty: {artefact}")

        panel = state.get("panel", {})
        if panel.get("locked"):
            panel_size = len(panel.get("auto_selected", []))
            if panel_size < 2 or panel_size > 12:
                issues.append(
                    f"{ARTEFACTS.STATE}: locked panel has {panel_size} judges "
                    f"(expected 3-5, max 12)"
                )

        for dkey, dval in state.get("decisions", {}).items():
            if dval and not isinstance(dval, str):
                issues.append(f"{ARTEFACTS.STATE}: decisions.{dkey} is not a string: {dval}")


def _count_checks(artefacts_dir: Path) -> int:
    count = 4
    for fname in MIN_SIZES:
        if (artefacts_dir / fname).exists():
            count += 1
    return count
