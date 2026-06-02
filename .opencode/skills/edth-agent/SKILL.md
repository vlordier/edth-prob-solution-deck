---
name: edth-agent
description: >
  Turn a CSV of defense-tech problem statements into a winning pitch deck —
  problem selection, Mom Test elicitation (operator-adapted), 12-judge validation,
  solution ideation, ranking, and Marp deck generation. Includes team discovery,
  kill chain mapping, one-sentence clarity, subagent-based pitch review.
  Subcommands: team, dry-run, run, validate, panel, sheet, skip-to, judge, review, setup.
disable-model-invocation: true
compatibility: opencode claude gemini
metadata:
  audience: hackathon
  workflow: edth
  domain: defense-tech
  phases: 9
  judges: 12
---

# EDTH Hackathon Agent

You are driving the EDTH Hackathon Agent — a structured workflow that turns a CSV of problem statements into a problem/solution pitch deck, reviewed by a panel of 12 tough-judge personas.

**This file is the workflow spine.** Prompt templates are in `references/prompts/`.
The agent reads each prompt template only when executing that phase — keeping context lean.

## Setup (run once)

**First invocation:** silently run `uv run python -c "import agent"`. If it fails:
```bash
bash setup.sh   # cross-platform: macOS / Linux / Windows-WSL
```
Verify: `uv run python -c "import agent; print('agent ready')"`

For PDF output: `npm install -g @marp-team/marp-cli || brew install marp-cli` (HTML fallback always works).

## Behavior rules

- **Idempotency:** Check `agent.state.get_phase_status(state, N)`. If `"completed"`, skip and advance. If `"in_progress"`, rollback and re-run.
- **Timebox:** After each phase check elapsed time. At 6h → force-pick problem. At 12h → skip to ranking. At 24h → skip to deck.
- **Environment doctor:** On `/edth-agent run`, run `agent.doctor.run_doctor()` first. Print issues, ask "Continue? (y/n)".
- **First-run check:** Before every command, silently `uv run python -c "import agent"`. If it fails, print "Run `bash setup.sh`" and stop.
- **Pre-flight:** `agent.validate.preflight_check(artefacts_dir, phase)` before starting any phase. Abort if issues.
- **Post-write verification:** After every artefact write, verify file exists AND `st_size > 0`. If not, abort.
- **Progress echo:** `⚙️  Phase N — Name: substep...`
- **Lint after code changes:** `uv run ruff check agent/ tests/ --fix && uv run ruff format agent/ tests/`
- **Mark in_progress:** `mark_phase_in_progress(state, N)` → `save_state()` before work. On failure: `rollback_phase(state, N)`.
- **Validate after each phase:** `agent.validate.run_validation(artefacts_dir, quiet=True)`.
- **Time tracking:** `⏱  {elapsed:.0f} min, {remaining} phases remaining.`
- **Rerun snapshots:** Before overwriting, copy to `artefacts/snapshots/<file>.bak.<timestamp>`.
- **Shell safety:** Always single-quote file paths.
- In `owner_mode: real`, ask "Approve? (y/edit/redo)". In `owner_mode: sim`, auto-continue.
- Every phase writes `agent.audit.write_audit_entry()`.

## Quick start

```
/edth-agent dry-run    → 30s smoke test
/edth-agent team       → interview your team
/edth-agent            → start/resume the workflow
```

Artefacts under `artefacts/`. State resumable via `artefacts/state.json`.

## Commands

| Command | Effect |
|---|---|
| `/edth-agent` | **Default** — resume or start the workflow |
| `/edth-agent help` | Show this help |
| `/edth-agent status` | Show current phase, decisions, panel |
| `/edth-agent run` / `run <N>` | Run next or specific phase |
| `/edth-agent rerun <N>` | Re-execute phase N (snapshots old artefact) |
| `/edth-agent dry-run` | Auto-run phases 0–7 with sim owner + condensed panel |
| `/edth-agent skip-to <N>` | Generate stubs for phases 0..N-1, jump to N |
| `/edth-agent team` | Interview each team member → `artefacts/team_profile.md` |
| `/edth-agent team --skip` | Skip team discovery with minimal stub |
| `/edth-agent validate` | Scan all artefacts for issues |
| `/edth-agent validate --quiet` | Same, but only report if issues found |
| `/edth-agent reset` | Wipe `artefacts/` and start over |
| `/edth-agent panel <short>` | Chat with one judge in character |
| `/edth-agent panel generate` | Auto-pick 5 judges for the chosen problem |
| `/edth-agent sheet` | Generate a printable Mom Test question sheet |
| `/edth-agent judge add` | Create a new custom judge persona |
| `/edth-agent judge edit <short>` | Edit a judge's YAML (auto-backup) |
| `/edth-agent judge remove <short>` | Safe-delete (moves to backups/) |
| `/edth-agent judge reset <short>` | Restore from git |
| `/edth-agent judge list` | List all judges with tags |
| `/edth-agent review` | Submit a deck to all 12 judges as subagents |
| `/edth-agent setup` | Guided first-time setup (uv, pre-commit, Exa MCP) |
| `/edth-agent render` | Re-render the deck from current artefacts |

## Phases (0–8)

| # | Phase | Primary artefact |
|---|---|---|
| 0 | Onboarding | `artefacts/00_context.yaml` |
| 1 | Triage | `artefacts/01_triage.md` |
| 2 | Elicit & narrow | `artefacts/02_candidate_problem.md` + q/a |
| 3 | Sub-problem | `artefacts/03_chosen_sub_problem.md` |
| 4 | Ideation | `artefacts/04_solution_candidates.md` |
| 5 | Research & rank | `artefacts/05_ranked_solutions.md` + owner pick |
| 6 | Demo & narrative | `artefacts/06_demo_plan.md` |
| 7 | Deck & market | `artefacts/07_deck.md` + market/comp/BM + rendered |
| 8 | Final review | `artefacts/08_summary.md` |

**Special stages (between phases):**
- Kill Chain Mapping — after Phase 3. See `references/prompts/kill-chain.md`.
- One-Sentence Clarity — after Phase 5. See `references/prompts/clarity.md`.
- Pitch Review — after Phase 7 or ad-hoc. See `references/prompts/review.md`.

## Panel system

Panel of 5 judge personas reviews every artefact. Library: `judges/*.yaml`.
See `references/judges.md` for judge profiles and prompt templates.

After Phase 2, call `/edth-agent panel generate` to auto-pick 5 judges.
Judges run as subagents. Relevance gate applied — off-topic judges stay quiet.
Panel lifecycle, per-phase actions, and CRUD commands at `references/judges.md`.

## MCP tools

- **Exa** — web search. `https://mcp.exa.ai/mcp`. Free, no API key.
  Use for Phase 1 market signals, Phase 5 web research, Phase 7 market sizing.
- **Context7** — library docs. `https://mcp.context7.com/mcp`. Free account at context7.com.
  Use when solutions reference specific frameworks/libraries.

## Linting

`uv run ruff check agent/ tests/ --fix && uv run ruff format agent/ tests/`
Run after any code change. Pre-commit hooks auto-run on `git commit`.

---

## Per-Phase Execution

Each phase has:
- A prompt template in `references/prompts/phase-{N}.md`
- Implementation steps below
- Quality rules

When executing a phase:
1. Read the prompt template from `references/prompts/phase-{N}.md`
2. Execute it verbatim — do not improvise
3. Follow the implementation steps below for Python glue
4. Validate, track time, ask approve

### Phase 0 — Onboarding

Read `references/prompts/phase-0.md`, then:

1. `⚙️  Phase 0 — Onboarding: loading defaults...`
2. `mark_phase_in_progress(state, 0)`. Save state.
3. `agent.state.load_state()` + `agent.context.default_context()`.
4. Execute prompt. Save via `agent.context.save_context(artefacts_dir, ctx)`.
5. `✅ Phase 0 — Onboarding: context saved.`
6. `mark_phase_completed(state, 0, artefacts_dir / "00_context.yaml")`. Save state.
7. Validate, time, audit, approve.

### Phase 1 — Triage

Read `references/prompts/phase-1.md`, then:

1. `⚙️  Phase 1 — Triage: loading state...`
2. `preflight_check(artefacts_dir, 1)`. `mark_phase_in_progress(state, 1)`. Save state.
3. Parse CSV via `agent.parse_csv.parse_problems_safe(csv_path)`. If error, abort with `rollback_phase`. Save `01_problems.json`. Verify exists + size > 0.
4. `agent.normalize.assign_quality_flags()` on each. `agent.normalize.dedupe_problems()`.
5. Execute prompt template. If panel locked, run Borda aggregation.
6. Build `agent.triage.TriageReport`. Write via `agent.triage.write_triage_report()`. Post-write verify.
7. `✅ Phase 1 — Triage: {N} clusters written.`
8. `mark_phase_completed(state, 1, artefacts_dir / "01_triage.md")`. Save state.
9. Validate, time + timebox, audit, approve.

### Phase 2 — Elicit & narrow

Read `references/prompts/phase-2.md`, then:

1. `⚙️  Phase 2 — Elicit: generating owner questions...`
2. `mark_phase_in_progress(state, 2)`. Save state.
3. Load `01_triage.md`. Execute prompt template.
4. Build `OwnerQuestion` objects. Write via `agent.elicitation.write_owner_questions()`.
5. Capture answers. Write via `agent.elicitation.write_owner_answers()`.
6. Re-score candidates. Write via `agent.candidates.write_candidate_problem()`.
7. User picks 1. Record via `set_decision(state, "chosen_problem_id", ...)`.
8. **Second team check:** Cross-reference `team_profile.md` against chosen problem. Print capability gaps.
   **Adjacent problem suggestion:** Look for high-execution, lower-impact clusters the team *could* easily build. Print: `💡 Adjacent consideration: {problem} scored {scores}. Reconsider? (y/n)`.
9. Auto-pick panel: `agent.judges.select_panel()`. Store in state.
10. `✅ Phase 2 — Elicit: problem {pid} chosen.`
11. `mark_phase_completed(state, 2, artefacts_dir / "02_candidate_problem.md")`. Save state.
12. Validate, time + timebox, audit, approve.

### Phase 3 — Sub-problem decompose

Read `references/prompts/phase-3.md`, then:

1. `⚙️  Phase 3 — Sub-problem: decomposing...`
2. `mark_phase_in_progress(state, 3)`. Save state.
3. Load chosen problem from state + `02_candidate_problem.md`. Execute prompt.
4. Panel: each judge scores sub-problems on 4 ROI axes.
5. Write via `agent.sub_problem.write_sub_problem()`. `✅ Phase 3 — Sub-problem: {N} sub-problems written.`
6. User picks 1. Record via `set_decision("chosen_sub_problem_id", ...)`.
7. `mark_phase_completed(state, 3, artefacts_dir / "03_chosen_sub_problem.md")`. Save state.
8. Validate, time + timebox, audit, approve.

#### Kill Chain Mapping

Runs after Phase 3 completes. Read `references/prompts/kill-chain.md`, then:
1. `⚙️  Kill Chain — mapping to F2T2EA + European defense context...`
2. Execute prompt. Append output to `03_chosen_sub_problem.md`.
3. `✅ Kill chain mapping appended.`

### Phase 4 — Divergent ideation

Read `references/prompts/phase-4.md`, then:

1. `⚙️  Phase 4 — Ideation: generating ideas with 7 techniques...`
2. `mark_phase_in_progress(state, 4)`. Save state.
3. Load `03_chosen_sub_problem.md`. Execute prompt.
4. Dedupe via `agent.ideation.dedupe_ideas()`.
5. In real mode: offer user to add 1-3 ideas.
6. Panel: rate every idea 1-5.
7. Sort, surface top 5 + "judges hated this".
8. Write via `agent.ideation.write_solution_candidates()`. `✅ Phase 4 — Ideation: {N} ideas written.`
9. `mark_phase_completed(state, 4, artefacts_dir / "04_solution_candidates.md")`. Save state.
10. Validate, time + timebox, audit, approve.

### Phase 5 — Research & rank

Read `references/prompts/phase-5.md`, then:

1. `⚙️  Phase 5 — Research: web searching top 5 ideas...`
2. `mark_phase_in_progress(state, 5)`. Save state.
3. Load `04_solution_candidates.md`. Extract top 5. Execute prompt.
4. Web research per idea. Panel re-scores.
5. Aggregate, write `05_ranked_solutions.md`.
6. Owner validates, write `05_owner_pick.md`. `✅ Phase 5 — Research: solution {id} chosen.`
7. Record decision. `mark_phase_completed(state, 5, artefacts_dir / "05_ranked_solutions.md")`. Save state.
8. Validate, time + timebox, audit, approve.

#### One-Sentence Clarity

Runs after Phase 5. Read `references/prompts/clarity.md`, then:
1. `⚙️  One-Sentence Clarity — stating the project...`
2. Execute prompt. Interactive check only — no file written.
3. Record the final sentence in the audit entry.

### Phase 6 — Demo & narrative

Read `references/prompts/phase-6.md` (demo plan) and `references/prompts/task-assignment.md`, then:

1. `⚙️  Phase 6 — Demo: writing plan...`
2. `mark_phase_in_progress(state, 6)`. Save state.
3. Load `05_owner_pick.md`. Execute demo prompt.
4. Panel: previews script, gives Q&A questions.
5. Write via `agent.demo_plan.write_demo_plan()`. `✅ Phase 6 — Demo: demo plan written.`
6. Execute task assignment prompt. Writes `artefacts/demo_tasks.md`.
7. `mark_phase_completed(state, 6, artefacts_dir / "06_demo_plan.md")`. Save state.
8. Validate, time + timebox, audit, approve.

### Phase 7 — Deck & market research

Read `references/prompts/phase-7.md`, then:

1. `⚙️  Phase 7 — Deck: researching market...`
2. `mark_phase_in_progress(state, 7)`. Save state.
3. Load all prior artefacts. Execute prompt.
4. Write `07_market.md`, `07_competition.md`, `07_business_model.md`.
5. Compile deck via `agent.deck.compile_deck_md()`. Render via `agent.deck.render_deck()`.
6. `✅ Phase 7 — Deck: rendered to artefacts/07_deck.html.`
7. Panel reviews slides.
8. `mark_phase_completed(state, 7, artefacts_dir / "07_deck.md")`. Save state.
9. Validate, time + timebox, audit, approve.

### Phase 8 — Final review

Read `references/prompts/phase-8.md`, then:

1. `⚙️  Phase 8 — Final: writing summary...`
2. `mark_phase_in_progress(state, 8)`. Save state.
3. Load all artefacts. Execute prompt.
4. Write `08_summary.md` via `agent.summary.write_summary()`.
5. Panel: final verdicts. Record dissent.
6. Final deck re-render check.
7. `mark_phase_completed(state, 8, artefacts_dir / "08_summary.md")`. Save state.
8. Validate. Print: `⏱  Total: {elapsed:.0f} min across 9 phases.`
9. Audit. Mark run complete.

---

## Special Commands

### Team Discovery (`/edth-agent team`)

Read `references/prompts/team-discovery.md`, then:
1. `⚙️  Team Discovery — interviewing the team...`
2. Ask how many members. Go person by person: intro → word count (≥50) → 5 A/B/C questions → blind spots → profile.
3. After all: team dynamics (pitcher, demo, builder, deck).
4. Write via `agent.team.write_team_profile()`. `✅ Team profile saved.`

### Question Sheet (`/edth-agent sheet`)

Read `references/prompts/sheet.md`, then:
1. `⚙️  Question Sheet — generating...`
2. Verify Phase 1 completed (`01_triage.md` exists).
3. Execute prompt. Write via `agent.sheet.write_question_sheet()`.
4. `✅ Question sheet saved to artefacts/question_sheet.md.`

### Pitch Review (`/edth-agent review`)

Read `references/prompts/review.md`, then:
1. `⚙️  Pitch Review — reading deck...`
2. Ask for deck (PDF, HTML, or `artefacts/07_deck.md`). Extract text.
3. `⚙️  Pitch Review — dispatching 12 judge subagents...`
4. Dispatch one subagent per judge. Collect results.
5. Compile review. Write `artefacts/pitch_review.md`.
6. `✅ Pitch review complete. {N} judges contributed, {M} stayed quiet.`
7. If Signal Quality is weak: `⚠️  Only {N} of 12 judges found this relevant.`

### Guided Setup (`/edth-agent setup`)

Read `references/prompts/setup.md`, then:
1. `⚙️  Guided Setup — let's get you running.`
2. Execute prompt: bash setup.sh → pre-commit → Exa MCP → optional Context7 → verify.

### Judge Management

Read `references/judges.md` for the full judge prompt templates.
Commands: `/edth-agent judge add | edit | remove | reset | list | panel generate`.
Python: `agent.judges.add_judge() | update_judge() | remove_judge() | list_judges_full()`.

## Dry-run mode

1. `⚙️  Dry-run: starting with sim owner + condensed panel...`
2. Fresh state via `agent.state.empty_state()`. Set `owner_mode: sim`, `panel_mode: condensed`.
3. Phase 0 through 7 auto-executed. **BAIL at** parse failure, <2 clusters, <5 ideas.
4. `✅ Dry-run complete. Deck: artefacts/07_deck.html.`
5. Validate. Print: "Start over? `/edth-agent reset` then `/edth-agent run`."

## Skip-to mode

1. `⚙️  Skip-to: generating stub artefacts for phases 0 to {N-1}...`
2. Fresh state. Generate minimal stubs for each phase 0..N-1. Mark `[STUB]`.
3. All stubs: `mark_phase_completed(state, p, stub_path)`. Set `current_phase = N`.
4. `✅ Stubs generated. Ready for phase {N}.`
5. `⚠️  Stubs are marked [STUB]. Replace with real data via /edth-agent rerun <N>.`

## Validate command

Run `agent.validate.run_validation(artefacts_dir, quiet=True/False)`. Checks:
state.json integrity, artefact presence + size, content quality (cluster count,
slide count, research sections, html keyboard nav), panel consistency,
cross-phase decision tracking. Prints `✅ All {N} checks passed.` or `⚠️  {N} issue(s):`
