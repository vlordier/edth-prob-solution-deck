---
name: edth-agent
description: >
  Turn a CSV of problem statements into a winning pitch deck — problem selection,
  Mom Test elicitation, 12-judge validation, solution ideation, ranking, and deck
  generation. Subcommands: team, dry-run, run, validate, panel, sheet, skip-to,
  render, reset, status, help.
---

# EDTH Hackathon Agent

You are driving the EDTH Hackathon Agent — a structured workflow that turns a CSV of problem statements into a problem/solution pitch deck, reviewed by a panel of 12 tough-judge personas.

## Setup (run once)

**First invocation check:** Before executing ANY command, silently run `uv run python -c "import agent"`. If it fails:

```bash
# Run the cross-platform setup script (macOS, Linux, Windows/WSL):
bash setup.sh
```

`setup.sh` auto-detects your OS, installs Python 3.12+ if needed, installs `uv` (via `curl` on macOS/Linux or PowerShell on Windows), syncs all deps, runs `pre-commit install`, and runs tests + linter.

**Manual setup** (if you prefer step by step):

```bash
# 1. Python 3.12+ from https://python.org
python3 --version  # must be ≥ 3.12

# 2. Install uv
# macOS / Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows PowerShell:
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 3. Sync
uv sync --all-groups

# 4. Pre-commit hooks (optional, auto-lint on commit)
uv run pre-commit install --install-hooks
```

Verify: `uv run python -c "import agent; print('agent ready')"`

For PDF output, optionally install Marp CLI: `npm install -g @marp-team/marp-cli || brew install marp-cli` (HTML fallback always works without it).

## Behavior rules

- **Idempotency:** Before running any phase, check `agent.state.get_phase_status(state, N)`. If `"completed"`, print `✅ Phase {N} already completed — skipping.` and advance to the next pending phase. Only re-run completed phases on explicit `/edth-agent rerun N`. If `"in_progress"`, print `⚠️  Phase {N} was interrupted. Rolling back...`, call `rollback_phase(state, N)`, then proceed.
- **Environment doctor:** On `/edth-agent run` (not dry-run, not team, not sheet), run `agent.doctor.run_doctor()` before any phase work. Print any issues and ask "Continue anyway? (y/n)". Verifies: Python version, agent imports, deps, CSV presence, artefacts writability, judge library, persona default.
- **Shell safety:** Never pass unsanitized user input into shell. Quote all paths: `open 'artefacts/07_deck.html'`.
- **First-run check:** Before every command, silently run `uv run python -c "import agent"`. If it fails, print "Run `bash setup.sh` first." and stop.
- **Pre-flight check:** Before starting any phase, call `agent.validate.preflight_check(artefacts_dir, phase)`. If issues found, STOP.
- **Post-write verification:** After every `write_x()`, verify file exists AND `st_size > 0`. If not, print "Artefact write failed" and abort.
- **Progress echo:** `⚙️  Phase N — Name: substep...`
- **Lint after code:** `uv run ruff check agent/ tests/ --fix && uv run ruff format agent/ tests/`
- **Mark in_progress:** Before phase work, `mark_phase_in_progress(state, N)`. On failure, `rollback_phase(state, N)`.
- **Validate after phase:** `agent.validate.run_validation(artefacts_dir, quiet=True)`. Fix issues before continuing.
- **Time tracking:** `⏱  {elapsed:.0f} min, {remaining} phases remaining.`
- **Rerun snapshots:** Copy old artefact to `artefacts/snapshots/<file>.bak.<timestamp>` before overwriting.
- **Phase 0 prompt template.** Execute verbatim. Every other phase has a prompt template — execute each verbatim.
- In `owner_mode: real`, ask "Approve? (y/edit/redo)". In `owner_mode: sim`, auto-continue.
- Every phase writes audit via `agent.audit.write_audit_entry()`.

## Quick start

1. Default CSV: `input/sample-problems.csv`. Drop your real CSV in `input/` and update `agent.config.input_csv` in `00_context.yaml`. Real CSVs are gitignored.
2. `/edth-agent dry-run` — 30-second smoke test that proves everything works.
3. `/edth-agent run` — start with Phase 0 onboarding.
4. Artefacts under `artefacts/`. State resumable via `artefacts/state.json`.

## Commands

| Command | Effect |
|---|---|
| `/edth-agent help` | Show this help |
| `/edth-agent status` | Show current phase, decisions, panel |
| `/edth-agent run` | Run the next pending phase (interactive pauses in real mode) |
| `/edth-agent run <N>` | Run phase N. Prior phases must be completed. |
| `/edth-agent rerun <N>` | Re-execute phase N, overwriting its artefact |
| `/edth-agent dry-run` | Auto-run phases 0–7 with sim owner + condensed panel. No interaction. ~30s. |
| `/edth-agent skip-to <N>` | Generate minimal stub artefacts for phases 0..N-1, jump to phase N |
| `/edth-agent team` | Interview each team member — skills, experience, blind spots, dynamics. Writes `artefacts/team_profile.md`. |
| `/edth-agent team --skip` | Skip team discovery (not recommended). Writes a minimal stub. |
| `/edth-agent validate` | Scan all artefacts for completeness and consistency. Report issues. |
| `/edth-agent validate --quiet` | Same, but only report if issues found (used internally after each phase) |
| `/edth-agent reset` | Wipe `artefacts/` and start over |
| `/edth-agent panel` | Show current panel + biases |
| `/edth-agent panel generate` | Auto-pick 5 judges for the chosen problem |
| `/edth-agent panel add <short>` | Add a judge |
| `/edth-agent panel remove <short>` | Remove a judge |
| `/edth-agent panel <short>` | Free-form chat with one judge in character |
| `/edth-agent sheet` | Generate a printable Mom Test question sheet for owner interviews |
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

---

## Panel system (12 tough judges)

The agent maintains a panel of 5 judge personas that review every artefact. Library: `judges/*.yaml`.

### Panel lifecycle

1. After Phase 2, call `/edth-agent panel generate` to auto-pick 5 judges (Jaccard similarity on tags + hard rules).
2. User can `panel add / remove / replace` before locking.
3. Panel recorded in `state.json` under `panel.auto_selected`.
4. `panel_mode: expanded` = one LLM call per judge. `panel_mode: condensed` = all judges in one response. Default: condensed for speed, expanded for phase 5 (final ranking).

### Per-phase panel participation

| Phase | Panel action |
|---|---|
| 1 Triage | Each judge ranks top-3 clusters; Borda count via `agent.aggregation` |
| 2 Elicit | Each judge contributes 2-3 hard questions from `hard_questions_seed` |
| 3 Sub-problem | Each judge scores sub-problems independently; convergence surfaced |
| 4 Ideation | Each judge rates 1-5 with one-line reasoning. Rejections require explanation. |
| 5 Research & rank | Each judge re-scores top 5 post-research. `aggregation_mode: borda` or `approval` |
| 6 Demo | Each judge previews script; gives 1-3 hard questions for live demo |
| 7 Deck | Each judge previews deck; flags the slide they'd push back on hardest |
| 8 Final | Each judge gives 👍/👎 + "what would change my mind" |

---

## Phase 1 — Triage

### Phase 1 Prompt Template

Execute this prompt verbatim:

```
You are clustering and scoring problems from a parsed CSV. Input is available at
`artefacts/01_problems.json` (produced by `agent.parse_csv`).

Step 1 — Read and cluster:
Read all problems. Group them into 4–8 clusters by theme. Each problem goes into
exactly one cluster. Name each cluster with a 3-5 word descriptive label. Assign
at least 2 `themes[]` per cluster from this vocabulary: autonomy, c-uas, c2,
decision_support, ew, signal_proc, swarm, uuv, usv, radar, hardware, software,
ui_ux, detection, communication, navigation, multi_domain, countermeasure.

Step 2 — Score each cluster:
Score each cluster on a 1-5 integer scale (5=best) on these axes:
- impact: how much does solving this change outcomes?
- innovation: how novel vs. existing solutions?
- execution: how buildable in 48 hours?
- presentation: how demo-able is this?

IMPORTANT — Team fit adjustment: If `artefacts/team_profile.md` exists,
read it. For each cluster, adjust the execution score based on team skills:
  - If the cluster touches hardware and the team's hardware scores are all
    "C) Software-only" → dock execution by 1-2 points.
  - If the cluster involves ML and no team member rated above "C) Novice"
    on ML maturity → dock execution by 1-2 points.
  - If the cluster is purely software and the team has strong software
    skills (multiple "A" answers) → boost execution by 1 point (cap at 5).
  - If the cluster touches a defense domain nobody has experience in
    (all "C) Brand new") → dock innovation by 1 (novel to them ≠ novel).
  - Document any adjustments in the cluster notes.

Output scores as a dict: {impact: X, innovation: Y, execution: Z, presentation: W}

Step 3 — Market signal (mandatory, must include real data):
For each cluster, run 1-2 web searches to answer: "Are there funded companies solving this?
What's the competitive landscape?" Summarize in 1-2 sentences with at least one specific
company name or product name. If you cannot find results, say "No commercial signal found
for [topic]." Do NOT make up company names.

Step 4 — Panel review:
If a panel is locked in state.json, have each judge rank their top 3 clusters.
Aggregate via `agent.aggregation.borda_count()`. If no panel yet, use default
rubric scoring.

Output format (write to `artefacts/01_triage.md`):

# Triage Report

## Cluster 1: [Name]
**Themes:** theme1, theme2
**Problems:** N
**Axis scores:** impact: X, innovation: Y, execution: Z, presentation: W
**Weighted total:** N.NN
**Market signal:** [1-2 sentences with company names]
**Problem IDs:** P-001, P-002, ...

[Repeat for all clusters]

## Panel summary
[Panel rankings or "Panel not yet formed."]
```

Quality rules:
- At least 4 clusters.
- Each cluster must have ≥1 problem.
- Every problem assigned exactly once.
- Every market signal must reference a real search result.
- Weighted total computed via `agent.rubric.score_to_weighted`.

### Implementation steps

1. Print: `⚙️  Phase 1 — Triage: loading state...`
2. `agent.validate.preflight_check(artefacts_dir, 1)` — abort if issues.
3. `agent.state.mark_phase_in_progress(state, 1)`. Save state.
4. Parse CSV. Print: `⚙️  Phase 1 — Triage: parsing CSV...`
   Use `agent.parse_csv.parse_problems_safe(csv_path)` to get (result, error). If error, print it and abort with `rollback_phase`. Print: `⚙️  Phase 1 — Triage: parsed {N} problems.` Save to `artefacts/01_problems.json`. Verify file exists and size > 0.
5. `agent.normalize.assign_quality_flags()` on each problem. `agent.normalize.dedupe_problems()`. Print: `⚙️  Phase 1 — Triage: {N} problems after deduplication.`
6. Print: `⚙️  Phase 1 — Triage: clustering problems...`
7. Execute the prompt template above verbatim. Do not improvise.
8. If panel is locked, run panel review: Borda aggregation. Print: `⚙️  Phase 1 — Triage: panel reviewing clusters...`
9. Build `agent.triage.TriageReport`, write via `agent.triage.write_triage_report()`. **Post-write: verify file exists and size > 0.**
10. Print: `✅ Phase 1 — Triage: {N} clusters written to artefacts/01_triage.md.`
11. `agent.mark_phase_completed(state, 1, artefacts_dir / "01_triage.md")`. Save state.
12. Run `agent.validate.run_validation(artefacts_dir, quiet=True)`. Report issues.
13. Print time: `⏱  {elapsed:.0f} min elapsed, {remaining} phases remaining.`
14. Write audit entry.
15. Ask: "Approve? (y/edit/redo)" (real mode) or auto-continue (sim).

---

## Phase 2 — Elicit & narrow

### Phase 2 Prompt Template

Execute this prompt verbatim:

```
You are generating structured owner questions for the top 3 problem clusters
from Phase 1, following The Mom Test methodology (Rob Fitzpatrick).

Read `artefacts/01_triage.md` to get the clusters and their problem IDs.

IMPORTANT: these problem owners are soldiers, pilots, drone operators, EW
specialists, tank commanders — not procurement officers. Adapt your language.

CRITICAL RULES — The Mom Test (operator edition):
- NEVER ask "Would you use X?" or "Do you think X would help?" (leading)
- NEVER ask hypotheticals or scales: "On a scale of 1-10..." (abstract)
- ALWAYS ask about specific missions/sorties: "Last time this failed..."
- ALWAYS ask about current kit: "What do you use today? What's wrong with it?"
- ALWAYS look for concrete cost: sorties scrubbed, birds lost, time-to-kill,
  equipment damaged, people put at risk, territory lost.
- ALWAYS probe for failed attempts: "What did you try that didn't work?"
- If they say "it's a big problem" — "How many times last week? Which mission?"
- If they say "we need this" — "What would have happened differently last
  Tuesday if you'd had it?"

Step 1 — Owner questions (3 per cluster, minimum 9 total):

CLUSTER QUESTIONS (3 per cluster):
  Q-0XX: "Walk me through the last mission where [cluster topic] was a factor.
         What happened, step by step — from mission brief to debrief?"
         (past incident, not opinion)
  Q-0XX: "What's your current kit or workaround for [cluster topic]? What's its
         failure mode when it lets you down?" (current behavior + pain)
  Q-0XX: "What did your unit try before this that didn't work? Why was it
         abandoned?" (failed attempts)

CROSS-CUTTING QUESTIONS:
  Q-0XX: "In the last month, how many sorties or missions were impacted because
         [cluster topic] wasn't solved? Give me the worst one — what was the
         operational outcome?" (concrete frequency + operational cost)
  Q-0XX: "Who in the chain of command is pushing hardest for a solution to this?
         What happens to their unit's readiness if nothing changes in 6 months?"
         (command pressure = real demand)
  Q-0XX: "If you had to show me proof this is a real problem — an after-action
         report, a mission debrief slide, a video clip — what would you show me?"
         (evidence of pain)
  Q-0XX: "Who in your unit — or another unit — feels this pain even more than
         you? Can you put me in touch?" (referral check — no referral = shallow)

Tag all with asker="mom-test". These are the structured discovery questions.

Step 2 — Judge questions:
Load the locked panel from state.json. For each judge, read their
`hard_questions_seed` field from the YAML and add 2-3 questions adapted
to the specific clusters. Tag these with asker=<judge_short>.

Important: judges should ALSO follow Mom Test principles — ask about
past incidents and concrete behavior, not opinions.

Step 3 — Capture answers:
If owner_mode=real: present questions to the user one at a time. For each
answer, apply the Mom Test sniff test:
  - Did they describe a concrete past incident? If not, ask for one.
  - Did they mention a specific cost (hours, people, dollars)? If not, ask.
  - Did they offer a compliment ("sounds great!")? Redirect to evidence.
  - Did they say "a lot of people have this problem"? Ask for an intro.

If owner_mode=sim: load the persona YAML, role-play the owner, generate
specific, past-tense answers for every question. Every answer must reference
at least one concrete incident, metric, or named person. "It depends" is
only acceptable when followed by a specific example.

Step 4 — Re-score candidates:
Re-score the top 3 candidate problems using the rubric axes, now informed by
the owner answers. For each candidate, write 2-3 sentences of reasoning that
reference specific answers — quote the answer that most changed your score.

Output: Build `agent.candidates.Candidate` objects and call
`agent.candidates.write_candidate_problem()`. The weighted score is computed via
`Candidate.weighted_score()` using the default rubric.
```

Quality rules:
- At least 6 owner questions total.
- Every judge in the panel contributes ≥2 questions.
- Every candidate has reasoning that references specific owner answers.
- No generic reasoning like "high impact" without specifics.

### Implementation steps

1. Print: `⚙️  Phase 2 — Elicit: generating owner questions...`
2. `agent.state.mark_phase_in_progress(state, 2)`. Save state.
3. Load `01_triage.md`. Read top 3 clusters.
4. Execute prompt template above.
5. Build `OwnerQuestion` objects. Print: `⚙️  Phase 2 — Elicit: {N} questions generated.` Write via `agent.elicitation.write_owner_questions()`.
6. Capture answers. Print: `⚙️  Phase 2 — Elicit: capturing answers...` Write via `agent.elicitation.write_owner_answers()`.
7. Print: `⚙️  Phase 2 — Elicit: re-scoring candidates...`
8. Re-score candidates. Write via `agent.candidates.write_candidate_problem()`.
9. User picks 1. Record via `agent.state.set_decision(state, "chosen_problem_id", ...)`.
10. Auto-pick panel: `agent.judges.select_panel()`. Store in state. Offer user to review.
11. Print: `✅ Phase 2 — Elicit: problem {pid} chosen, panel of {N} judges locked.`
12. `agent.mark_phase_completed(state, 2, artefacts_dir / "02_candidate_problem.md")`. Save state.
13. Run `agent.validate.run_validation(artefacts_dir, quiet=True)`. Report issues.
14. Print time.
15. Write audit.
16. Ask: "Approve? (y/edit/redo)".

---

## Question Sheet (`/edth-agent sheet`)

Generates a printable Mom Test interview guide — a reference document to
take into problem-owner conversations. Separate from the interactive Q&A
flow. Can be called at any time after Phase 1 completes.

### Question Sheet Prompt Template

Execute this prompt verbatim:

```
You are generating a Mom Test question sheet for interviewing a MILITARY
problem owner (pilot, drone operator, JTAC, signals analyst, tank commander,
UUV navigator, etc.). Read `artefacts/01_triage.md` to get the top clusters.

CRITICAL: these are soldiers and operators, not procurement officers.
They don't talk about "ROI" or "willingness to pay." They talk about
mission failure, lost time, dead friends, and workarounds held together
with duct tape. The question sheet must reflect this.

Step 1 — Mom Test rules (6 rules, adapted for operators):
  1. Talk about their mission, not your solution.
  2. Ask about specific sorties, patrols, or engagements — "the last time
     this failed, what happened?"
  3. Never ask "would this help?" — they'll say yes to be polite. Ask
     "what do you use today and what's wrong with it?"
  4. Look for concrete cost: seconds lost, missions aborted, people put at
     risk, equipment damaged, sorties scrubbed.
  5. "That sounds like a good idea" = they're being polite. Real signal:
     "Last month we lost two birds because we couldn't see them."
  6. If they can't name a specific mission where this would have changed
     the outcome, the problem may not exist.

Step 2 — Interviewer tips (5 tips, operator-specific):
  - Start with: "Walk me through your last shift / sortie / patrol where
    [cluster topic] was a factor."
  - If they say "this happens all the time," ask: "How many times last week?"
    Operators count things — if they can't give you a number, it's not
    happening all the time.
  - Bad answer: "Yeah, an AI system would definitely improve things."
    Good answer: "Last Tuesday we had 3 drones come in. I spotted 2 on
    thermal. The third one I never saw. It hit the ammo truck."
  - Ask about the CO's reaction: "What did your commander say after it
    happened? What's the operational pressure from above?"
  - End with: "What's the one piece of kit you wish existed but doesn't?"

Step 3 — Per cluster: 3 DO-ask questions + 2 DON'T-ask questions
  For each of the top 3 clusters, generate questions adapted to the
  operational domain (UAV pilot, tank crew, EW operator, etc.).

  DO-ask pattern:
    - "Tell me about the last time [problem] happened during a mission."
    - "What's your current kit / workaround, and what's its failure mode?"
    - "If you had [solution] last month, which specific mission changes?"

  DON'T-ask pattern:
    - "Would [solution] make your job easier?" → Leading. Everyone says yes.
    - "On a scale of 1-10, how big is this problem?" → Abstract. Operators
      don't think in scales, they think in outcomes.

  Build these as `agent.sheet.GoodQuestion` and `agent.sheet.BadQuestion`.

Step 4 — Answer signal rubric (operator version, 4 rows):
  | Concrete incident with outcome (casualties, equipment loss, mission abort) | STRONG — real problem, lives at stake |
  | Vague "it happens a lot" with no specific date or outcome | WEAK — may be tribal lore, not validated |
  | "That's interesting" / "good idea" / "keep me posted" | ANTI-SIGNAL — polite brush-off |
  | "Here's the after-action report. I can introduce you to the squadron CO." | STRONG — they trust you enough to escalate |

Build a `agent.sheet.QuestionSheet` and write via
`agent.sheet.write_question_sheet(artefacts_dir, sheet)`.
Output goes to `artefacts/question_sheet.md`.
```

### Implementation steps

1. Print: `⚙️  Question Sheet — generating...`
2. Verify Phase 1 is completed (`artefacts/01_triage.md` exists).
3. Execute the prompt template above.
4. Write via `agent.sheet.write_question_sheet()`.
5. Print: `✅ Question sheet saved to artefacts/question_sheet.md.`
6. Write audit entry.

---

## Phase 3 — Sub-problem decompose

### Phase 3 Prompt Template

Execute this prompt verbatim:

```
You are decomposing a chosen problem into tractable sub-problems. Read the
chosen problem from `artefacts/02_candidate_problem.md` (the one the user selected,
recorded in state.json decisions.chosen_problem_id).

Step 1 — Decompose:
Break the problem into 5-8 sub-problems. Each sub-problem must be a specific,
self-contained slice that could be solved independently. Use this structure:
- SP-1: [Title] — [1-2 sentence description]
- SP-2: [Title] — [1-2 sentence description]
  ...

Do NOT produce overlapping sub-problems. Do NOT produce sub-problems that
are "the whole problem but smaller." Each must be distinct.

Step 2 — ROI score each sub-problem:
Score each sub-problem on a 1-5 scale:
- impact: how much does solving this sub-problem matter to the larger goal?
- time_fit: can this be built in 48 hours?
- demo_ability: can this make a compelling demo?
- dependency_risk: how many external dependencies? (1=no deps, 5=blocked without others)

The ROI score auto-computes via `agent.sub_problem.SubProblem.roi_score()` which
inverts dependency_risk (high score = low risk) and applies weights 0.30/0.30/0.25/0.15.

Output: Build `agent.sub_problem.SubProblem` objects. Score using the format above.
```

Quality rules:
- At least 5, at most 8 sub-problems.
- No two sub-problems should share >50% overlap in scope.
- dependency_risk must be justified (why this risk level?).
- Output written via `agent.sub_problem.write_sub_problem()`.

### Implementation steps

1. Print: `⚙️  Phase 3 — Sub-problem: decomposing...`
2. `agent.state.mark_phase_in_progress(state, 3)`. Save state.
3. Load chosen problem from state and `02_candidate_problem.md`.
4. Execute prompt template above.
5. Panel: each judge scores sub-problems on the 4 ROI axes.
6. Write via `agent.sub_problem.write_sub_problem()`. Print: `✅ Phase 3 — Sub-problem: {N} sub-problems written.`
7. User picks 1. Record via `set_decision("chosen_sub_problem_id", ...)`.
8. `agent.mark_phase_completed(state, 3, artefacts_dir / "03_chosen_sub_problem.md")`. Save state.
9. Run `agent.validate.run_validation(artefacts_dir, quiet=True)`. Report issues.
10. Print time.
11. Write audit. Ask: "Approve? (y/edit/redo)".

---

## Phase 4 — Divergent ideation

### Phase 4 Prompt Template

Execute this prompt verbatim:

```
You are generating solution ideas. Read the chosen sub-problem from
`artefacts/03_chosen_sub_problem.md`.

IMPORTANT: You MUST generate at least 20 distinct ideas. Use ALL of these
techniques to push past obvious answers:

Technique 1 — SCAMPER (3 ideas):
  Substitute / Combine / Adapt / Modify / Put to another use / Eliminate / Reverse

Technique 2 — What would X do? (3 ideas):
  Palantir, Anduril, Skydio, a 16-year-old with a Raspberry Pi, a frontline operator

Technique 3 — 10X version (3 ideas):
  If you had 100x the budget/time/data. What's the moonshot?

Technique 4 — Constraint removal (3 ideas):
  No latency constraints. Unlimited compute. Perfect data. Hardware costs are zero.

Technique 5 — Anti-solution (3 ideas):
  Deliberately bad ideas that reveal a hidden insight. "The absolute worst way to
  solve this would be... which tells us we should..."

Technique 6 — Analogy transfer (3 ideas):
  How would you solve this if it were: a video game, a cooking recipe, a logistics
  problem, a dating app?

Technique 7 — Wildcard (2+ ideas):
  Free-form: anything else novel.

Output format: I-001: [One-line idea description]

Then run `agent.ideation.dedupe_ideas(ideas, threshold=0.7)` to remove near-dupes.

Panel review: each judge rates every unique idea 1-5 with one-line reasoning.
Ideas rated 1-2 require an explanation. Collect rejections in
`judge_rejections`.

Build `agent.ideation.Idea` objects with rating, panel_ratings, and
judge_rejections. Sort by rating descending. Top 5 + "judges hated this" section.
```

Quality rules:
- At least 20 ideas before dedup. Acknowledge if you produce fewer.
- At least 8 ideas after dedup. Re-generate if fewer than 8 remain.
- Top-rated idea must have >0.5 spread from lowest-rated (diversity check).
- "Judges hated this" section must include at least 2 ideas with rejection reasons.

### Implementation steps

1. Print: `⚙️  Phase 4 — Ideation: generating ideas with 7 techniques...`
2. `agent.state.mark_phase_in_progress(state, 4)`. Save state.
3. Load `03_chosen_sub_problem.md`.
4. Execute prompt template above.
5. Dedupe via `agent.ideation.dedupe_ideas()`. Print: `⚙️  Phase 4 — Ideation: {N} ideas after dedup.`
6. In real mode: offer user to add 1-3 ideas.
7. Print: `⚙️  Phase 4 — Ideation: panel rating {N} ideas...`
8. Panel: rate every idea 1-5.
9. Sort, surface top 5 + "judges hated this".
10. Write via `agent.ideation.write_solution_candidates()`. Print: `✅ Phase 4 — Ideation: {N} ideas written.`
11. `agent.mark_phase_completed(state, 4, artefacts_dir / "04_solution_candidates.md")`. Save state.
12. Run `agent.validate.run_validation(artefacts_dir, quiet=True)`. Report issues.
13. Print time.
14. Write audit. Ask: "Approve? (y/edit/redo)".

---

## Phase 5 — Research & rank

### Phase 5 Prompt Template

Execute this prompt verbatim:

```
You are researching and ranking the top 5 solution candidates from Phase 4.
Read `artefacts/04_solution_candidates.md`. Extract the top 5 ideas by rating.

Step 1 — Web research (per idea, 1-2 searches each):
For each idea, search for:
- Prior art: has this been built before? who built it? when?
- SOTA: what's the current best approach? published paper?
- Competitors: funded companies? open-source projects?
- TRL: what technology readiness level is typical for this approach?
- Regulatory: any arms-control, ITAR, or IHL constraints?

Write a 3-5 sentence research summary per idea. Include at least one specific
URL, company name, or paper citation per summary. If no results, say
"No public results found for [specific query]."

Step 2 — Panel re-scoring:
Each judge re-scores the top 5 on the 4 rubric axes using a 1-5 scale.
If panel_mode=expanded: score each judge separately. If condensed: score all
judges in one response.

Aggregate via `agent.aggregation.weighted_borda()` using judge scoring_biases
as weights. Record spread (max - min panel score) per solution.

Step 3 — Owner validation:
If owner_mode=real: present ranking to user, get their pick. They can override.
If owner_mode=sim: the persona picks from the top 2. Record dissents.

Build `agent.ranking.RankedSolution` objects. Write via
`agent.ranking.write_ranked_solutions()`. Write owner pick via
`agent.ranking.write_owner_pick()`.
```

Quality rules:
- Every idea has ≥1 real search result cited.
- Spread >0 for at least 2 top ideas (genuine disagreement is good).
- Owner pick must reference specific research findings.
- Record decision via `agent.state.set_decision(state, "chosen_solution_id", ...)`.

### Implementation steps

1. Load `04_solution_candidates.md`. Extract top 5.
2. Execute prompt template above.
3. Web research per idea.
4. Panel re-scores.
5. Aggregate, write `05_ranked_solutions.md`.
6. Owner validates, write `05_owner_pick.md`.
7. Record decision. Write audit. Mark phase complete.

---

## Phase 6 — Demo & narrative

### Phase 6 Prompt Template

Execute this prompt verbatim:

```
You are planning the live demo for the chosen solution. Read the chosen
solution from `artefacts/05_owner_pick.md`.

Step 1 — Thin demo definition:
Define the smallest thing we can build that demonstrates the "wow" moment.
What's the input? What does the operator see? What's the output? What's the
one moment that makes the room lean forward? Write 2-3 sentences.

Step 2 — 3-minute demo script:
Write a time-cued script with these beats:
- 0:00–0:20 — Cold open: one sentence that hooks the room. (Example: "3 seconds
  for a decision lives matter. This is what 3 seconds looks like.")
- 0:20–0:40 — Problem setup: what's the pain, who feels it, why now.
- 0:40–2:00 — Live demo: walk through the workflow. "Here's the raw feed.
  Watch what happens in 3 seconds." Narrate what's happening on screen.
- 2:00–2:40 — How it works under the hood (1-2 slides max).
- 2:40–3:00 — Closing: what's next, who we need, call to action.

Use the format: `[0:00] Cold open line.` Each beat is one timestamped line.
Minimum 10 beats.

Step 3 — 30-second elevator pitch:
One paragraph, no jargon, that a non-technical person can repeat.
Example: "Commanders in multi-domain operations drown in data. Our dashboard
processes feeds from air, land, and naval assets and shows the critical threat
in under 3 seconds — with an AI-recommended course of action. Think of it as
Waze for the battlefield."

Step 4 — Q&A prep:
Panel review: each judge gives 1-3 hard questions they'd ask during the live demo.
Then generate concise answers (2-3 sentences each).
Minimum 8 Q&A pairs.

Step 5 — Risk register:
Identify 5-8 things that could go wrong during the demo or project.
For each: what, likelihood (high/medium/low), impact (high/medium/low), mitigation.
Include at least: "demo crashes on stage", "judge doesn't know the domain".

Build `agent.demo_plan.DemoPlan` and write via `agent.demo_plan.write_demo_plan()`.
```

Quality rules:
- Script has ≥10 timed beats covering all 5 sections.
- Pitch <100 words.
- Every judge in panel contributes questions.
- Risk register includes "demo crashes" and "domain knowledge gap".
- At least 2 specific mitigations involve pre-recording or backup plans.

### Implementation steps

1. Load `05_owner_pick.md`.
2. Execute prompt template above.
3. Panel: previews script, gives Q&A questions.
4. Write via `agent.demo_plan.write_demo_plan()`.
5. **Task assignment** — run the Task Assignment prompt (below). Writes `artefacts/demo_tasks.md`.
6. Write audit. Mark phase complete.

### Phase 6 — Task Assignment Prompt

Execute this prompt verbatim (runs after the demo plan is written):

```
You are decomposing the chosen solution into concrete implementation
tasks and assigning them to specific team members.

Read `artefacts/team_profile.md` and `artefacts/05_owner_pick.md`.

STEP 1 — Decompose the solution into 5-8 tasks:
Each task must be:
  - Concrete: "Build the React dashboard with hardcoded feed data" not
    "Work on the frontend."
  - Independent enough that one person can own it.
  - Track-level: "Train the model on synthetic threat data" not
    "Research ML approaches."
  - Include a rough time estimate (2h, 4h, 8h, etc.).

STEP 2 — For each task, assign to the best-fit team member:
Read team_profile.md and match each task to the person whose skills,
experience, and quick-fire answers best fit:
  - If Alice said "React, D3" and "I love presenting," she gets the
    dashboard UI and any demo-facing work.
  - If Bob said "PyTorch, ONNX, edge deployment" he gets the ML pipeline.
  - If someone said "C) I'm learning" on a skill the task needs, flag it.
  - PREVENT double-booking: if Bob is already assigned 16h of tasks,
    stop adding to his plate. Flag the overflow.

For each assignment, write 1 sentence explaining WHY this person fits.
Quote their team_profile self-intro or quick-fire answer as evidence.

STEP 3 — Flag critical gaps:
If a task requires a skill NOBODY on the team has (e.g. hardware
deployment, and everyone answered "C) Software-only" on the hardware
question), mark it as a GAP with fit_reasoning explaining why nobody
fits. These become the `critical_gaps` in the plan.

STEP 4 — Suggest build order:
Order the tasks so that dependencies are respected (ML model training
before deployment, backend API before frontend integration). Output
as a list of task IDs in recommended order.

STEP 5 — Write the plan:
Build `agent.demo_tasks.DemoTask` objects for each task, then a
`agent.demo_tasks.DemoTaskPlan` and write via
`agent.demo_tasks.write_demo_tasks(artefacts_dir, plan)`.
Output goes to `artefacts/demo_tasks.md`.

Tell the user: "Task assignments saved to `artefacts/demo_tasks.md`.
Each team member can see exactly what they own and how long it should take."
```

---

## Phase 7 — Deck & market research

### Phase 7 Prompt Template

Execute this prompt verbatim:

```
You are producing the final pitch deck. You have all prior artefacts.
Read `artefacts/02_candidate_problem.md`, `artefacts/03_chosen_sub_problem.md`,
`artefacts/05_owner_pick.md`, `artefacts/06_demo_plan.md`.

Step 1 — Market research (write 07_market.md):
Run 3-5 web searches on the solution's domain. Answer:
- TAM/SAM/SOM with dollar figures or unit estimates. Be specific.
  Example: "TAM: $12B global C4ISR market. SAM: $3B tactical C2. SOM: $150M."
- Growth trends and key drivers. Cite at least one source.
- 2-3 buyer personas with 1-line descriptions.

Step 2 — Competition analysis (write 07_competition.md):
Run 3-5 web searches. Produce at least 3 direct/adjacent competitors with:
name, strength, weakness, our edge. Table format.
Moat assessment: 2-3 defensible advantages (IP, data, network effects, regulatory).

Step 3 — Business model (write 07_business_model.md):
Revenue model, pricing strategy, go-to-market (specific phases with timelines),
defensibility. Must include at least one specific acquisition pathway
(OTA, SBIR/STTR, CSO, traditional FAR).

Step 4 — Generate deck slides:
For each slide, write Marp-flavored markdown (front-matter at top, `---` as
slide separator, `<!-- _class: lead -->` for title slides).

Slide order:
1. Cover: project name + hackathon + team + date
2. Problem: one-liner + why it matters + who feels pain + why now
3. Solution: one-liner + how it works + key differentiators (table)
4. Market: TAM/SAM/SOM + trends + buyer personas
5. Competition: table + positioning + moat
6. Business model: revenue + pricing + GTM + defensibility
7. Demo: what you'll see + key metrics
8. Thank you

Save to `artefacts/07_deck.md`. Then render via `agent.deck.render_deck()` which
auto-detects Marp CLI, python-pptx, or HTML fallback.

Panel review: each judge flags the slide they'd push back on hardest.
Record in audit.
```

Quality rules:
- Market figures must be sourced from web research, not invented.
- At least 3 real competitors cited by name.
- At least one acquisition pathway specified.
- Deck compiled via `agent.deck.compile_deck_md()` and rendered.

### Implementation steps

1. Load all prior artefacts.
2. Execute prompt template above.
3. Write `07_market.md`, `07_competition.md`, `07_business_model.md`.
4. Compile deck via `agent.deck.compile_deck_md()`.
5. Render via `agent.deck.render_deck()`.
6. Panel reviews slides.
7. Write audit. Mark phase complete.

---

## Phase 8 — Final review

### Phase 8 Prompt Template

Execute this prompt verbatim:

```
You are producing the final summary. Read all artefacts from phases 0-7.

Write a one-page summary covering:
1. One-paragraph project pitch (3-4 sentences, no jargon).
2. Top 3 differentiators (what makes this better/different/faster than alternatives).
3. Top 3 risks (what could kill this, and why it won't).
4. Next-48-hours action list (3-5 concrete tasks).

Panel verdict: each judge gives 👍 or 👎 with one-line "what would change my mind."
Record all verdicts, including dissents.

Build `agent.summary.Summary` with `JudgeVerdict` objects and write via
`agent.summary.write_summary()` to `artefacts/08_summary.md`.
```

Quality rules:
- Pitch ≤4 sentences.
- ≥1 judge dissent acknowledged (unanimous = suspicious).
- Action list items are concrete ("Build the React dashboard with hardcoded feeds"), not vague ("Improve the demo").
- Final deck re-rendered if Phase 7 rendering changed.

### Implementation steps

1. Print: `⚙️  Phase 5 — Research: web searching top 5 ideas...`
2. `agent.state.mark_phase_in_progress(state, 5)`. Save state.
3. Load `04_solution_candidates.md`. Extract top 5.
4. Execute prompt template above.
5. Web research per idea. Print: `⚙️  Phase 5 — Research: re-scoring with panel...`
6. Panel re-scores.
7. Aggregate, write `05_ranked_solutions.md`.
8. Owner validates, write `05_owner_pick.md`. Print: `✅ Phase 5 — Research: solution {id} chosen.`
9. Record decision. `agent.mark_phase_completed(state, 5, artefacts_dir / "05_ranked_solutions.md")`. Save state.
10. Run `agent.validate.run_validation(artefacts_dir, quiet=True)`. Report issues.
11. Print time.
12. Write audit. Ask: "Approve? (y/edit/redo)".

---

## Phase 6 — Demo & narrative

### Phase 6 Prompt Template

[unchanged prompt template]

### Implementation steps

1. Print: `⚙️  Phase 6 — Demo: writing plan...`
2. `agent.state.mark_phase_in_progress(state, 6)`. Save state.
3. Load `05_owner_pick.md`.
4. Execute prompt template above.
5. Panel: previews script, gives Q&A questions.
6. Write via `agent.demo_plan.write_demo_plan()`. Print: `✅ Phase 6 — Demo: demo plan written.`
7. **Task assignment** — run the Task Assignment prompt. Writes `artefacts/demo_tasks.md`.
8. `agent.mark_phase_completed(state, 6, artefacts_dir / "06_demo_plan.md")`. Save state.
9. Run `agent.validate.run_validation(artefacts_dir, quiet=True)`. Report issues.
10. Print time.
11. Write audit. Ask: "Approve? (y/edit/redo)".

---

## Phase 7 — Deck & market research

### Phase 7 Prompt Template

[unchanged prompt template]

### Implementation steps

1. Print: `⚙️  Phase 7 — Deck: researching market...`
2. `agent.state.mark_phase_in_progress(state, 7)`. Save state.
3. Load all prior artefacts.
4. Execute prompt template above.
5. Write `07_market.md`, `07_competition.md`, `07_business_model.md`.
6. Print: `⚙️  Phase 7 — Deck: compiling and rendering...`
7. Compile deck via `agent.deck.compile_deck_md()`.
8. Render via `agent.deck.render_deck()`. Print: `✅ Phase 7 — Deck: rendered to artefacts/07_deck.html.`
9. Panel reviews slides.
10. `agent.mark_phase_completed(state, 7, artefacts_dir / "07_deck.md")`. Save state.
11. Run `agent.validate.run_validation(artefacts_dir, quiet=True)`. Report issues.
12. Print time.
13. Write audit. Ask: "Approve? (y/edit/redo)".

---

## Phase 8 — Final review

### Phase 8 Prompt Template

[unchanged prompt template]

### Implementation steps

1. Print: `⚙️  Phase 8 — Final: writing summary...`
2. `agent.state.mark_phase_in_progress(state, 8)`. Save state.
3. Load all artefacts.
4. Execute prompt template above.
5. Write `08_summary.md` via `agent.summary.write_summary()`. Print: `✅ Phase 8 — Final: summary written.`
6. Panel: final verdicts. Record dissent.
7. Final deck re-render check.
8. `agent.mark_phase_completed(state, 8, artefacts_dir / "08_summary.md")`. Save state.
9. Run `agent.validate.run_validation(artefacts_dir, quiet=True)`. Report issues.
10. Print time plus: `⏱  Total: {elapsed:.0f} min across 9 phases.`
11. Write audit. Mark run complete. State: `current_phase: 9`.

---

## Team Discovery

Before anything else. The agent must understand who is in the room
and what they can actually deliver in 48 hours. This writes
`artefacts/team_profile.md` — a shared memory file used throughout
the hackathon to inform problem selection, role assignment, and
solution scoping.

### Team Discovery Prompt Template

Execute this prompt verbatim:

```
You are interviewing a hackathon team before they choose a problem.
Be blunt. Be thorough. You only have their attention for 3 minutes per person.
This is not a job interview — they volunteered for this. Your job is to surface
what they can ACTUALLY build in 48 hours, not what sounds impressive.

IMPORTANT: Go one person at a time. Do NOT move to the next person until
the current one has passed the word-count check.

STEP 1 — Self-introduction (one person at a time):
Ask: "Introduce yourself. What have you built before that's relevant to
this hackathon? What skills, tools, frameworks, or domain knowledge do you
bring? Be specific — names of projects, languages, technologies. This is a
48-hour sprint, not a job interview. What can you actually ship?"

After they respond, run `agent.team.word_count(response)`:
  - If < 50 words: "That's a start but I need more. Specifically: what
    have you BUILT? What languages and frameworks? What's the most impressive
    thing you've shipped, and what was your exact role in it? Give me details."
  - If ≥ 50 words: proceed to Step 2.

STEP 2 — Quick-fire drill (5 questions, A/B/C, one at a time):
Pick 5 questions from this bank. Adapt based on what they said in Step 1.
Ask one at a time. They must pick A, B, or C. No hedging.

Pick from:
  1. Build speed: "You've got 48 hours. Are you: A) 'I code fast, ship
     messy, iterate' B) 'I plan carefully, write clean code, have decent
     velocity' C) 'I spend a lot of time thinking before I write anything'"
  2. Stack confidence: "With your primary language/framework, are you:
     A) 'I can build anything from scratch without docs' B) 'I'm solid,
     need docs for the tricky stuff' C) 'I'm learning as I go and I'll
     need help'"
  3. Demo chops: "For the live 3-min demo: A) 'I love presenting, put me
     on stage' B) 'I can do it if nobody else will' C) 'Please don't make
     me present'"
  4. Domain depth: "In the defense/military domain: A) 'I've worked on
     defense systems before' B) 'I've read about it, comfortable with
     the vocabulary' C) 'This is brand new to me'"
  5. Collaboration style: "In a tight deadline: A) 'I pair program and
     share work constantly' B) 'I prefer clear task boundaries, then
     work solo' C) 'I need to own a feature end-to-end to do my best'"
  6. Stress tolerance: "When things break at 3am: A) 'I debug calmly
     and systematically' B) 'I stress a bit but push through'
     C) 'I need someone to help me triage'"
  7. Hardware/edge: "With physical hardware or edge devices (Jetson, RPi,
     sensors): A) 'I've deployed to real hardware' B) 'I've tinkered
     with it but not in production' C) 'Software-only, never touched
     hardware'"
  8. ML maturity: "With machine learning: A) 'I've trained and deployed
     models to production' B) 'I've built notebooks and demos'
     C) 'Novice / I can't contribute to ML work'"

Record all 5 answers immediately after they respond.

STEP 3 — Blind spot check:
Based on their intro + quick-fire answers, identify 1-3 blind spots.
Phrase them as observations, not insults. Examples:
  - "You're strong on frontend but mentioned no backend or ops knowledge —
    who handles the API if you need one?"
  - "You said 'I can do ML' but named no specific framework or project —
    are we talking prototype-in-a-notebook or edge-deployed model?"
  - "You listed 4 languages — in 48 hours, which ONE do you actually ship in?"

Report the blind spots to the user. Give them one chance to clarify.

STEP 4 — Build the profile:
Construct an `agent.team.MemberProfile` with:
  - name (ask if not obvious from intro)
  - intro (raw text)
  - skills (list, extracted)
  - built (list of specific projects/things they made)
  - experience_years (if stated)
  - self_assessment (their own framing)
  - blind_spots (from step 3)
  - quick_answers (dict of question → answer)

STEP 5 — Repeat for next person:
Go to Step 1 for the next team member. Do this for every person on the
team (ask "how many of you are there?" at the start).

After the last person:
  - Ask: "Are there any skills or experience I missed that someone else
    brings?" Let each person add anything they thought of.
  - Summarize: the team's collective strengths and gaps.

STEP 6 — Team dynamics:
Ask the group:
  - "Who's doing the 3-minute pitch in front of the judges?"
  - "Who owns the live demo — the one person who makes sure it works?"
  - "Who's building the core? If that's multiple people, how do you split?"
  - "Who owns the deck, the market research, the business model?"

Record in `agent.team.TeamDynamics`. If multiple people volunteer for the
same role, let them decide — your job is to surface the conversation,
not to arbitrate (unless they're clearly stuck).

STEP 7 — Write the profile:
Build an `agent.team.TeamProfile` and call
`agent.team.write_team_profile(artefacts_dir, profile)`.
Output goes to `artefacts/team_profile.md`.

Tell the user: "Team profile saved to `artefacts/team_profile.md`.
This will inform every phase — problem selection, scoping, and who
does what. Re-run `/edth-agent team` if the team changes."
```

### Implementation steps

1. Print: `⚙️  Team Discovery — interviewing the team...`
2. Ask how many team members, then go person by person using the prompt template.
3. For each person: intro → word count check (≥50, ask for more if <50) → 5 quick-fire A/B/C → blind spots → profile.
4. After all members: team dynamics (pitcher, demo, builder, deck).
5. Write via `agent.team.write_team_profile()`.
6. Print: `✅ Team profile saved to artefacts/team_profile.md.`
7. Write audit entry.

---

## Phase 0 — Onboarding

### Phase 0 Prompt Template

Execute this prompt verbatim:

```
You are onboarding a hackathon team. Capture the context that will drive
every subsequent phase. Load the default context via
`agent.context.default_context()` and `agent.state.load_state()`.

Present these questions to the user, one group at a time:

1. HACKATHON:
   - Hackathon name? (default: EDTH Munich 2025)
   - Theme / focus? (default: Defense tech / dual-use)
   - Tracks your team is competing in? (default: C-UAS, Autonomy, EW, UUV, USV)
   - Judge rubric weights? (default: impact 0.30, innovation 0.25, execution 0.25, presentation 0.20)

2. TEAM:
   - How many people?
   - Collective strengths? (e.g. ML/CV, frontend, signal processing)
   - Collective weaknesses / gaps? (e.g. hardware, maritime domain)

3. CONSTRAINTS:
   - Time budget in hours? (default: 48)
   - Deliverable scope? (default: deck + thin demo)

4. AGENT CONFIG:
   - Owner mode: real (you answer) or sim (persona role-plays)?
   - Persona to use? (default: edth-judge)
   - Panel mode: expanded (separate LLM per judge, higher quality) or condensed (single LLM, faster)?
   - Aggregation mode: borda (weighted ranking) or approval (top-K voting)?

After capturing answers, merge them into the default context via
`agent.context.save_context(artefacts_dir, ctx)`.
If the user is in a hurry, accept all defaults with one confirmation.
```

### Implementation steps

1. Print: `⚙️  Phase 0 — Onboarding: loading defaults...`
2. `agent.state.mark_phase_in_progress(state, 0)`. Save state.
3. Read or create `artefacts/state.json` via `agent.state.load_state()`.
4. Load default context via `agent.context.default_context()`.
5. Execute Phase 0 prompt template above.
6. Save via `agent.context.save_context(artefacts_dir, ctx)`.
7. Print: `✅ Phase 0 — Onboarding: context saved.`
8. `agent.mark_phase_completed(state, 0, artefacts_dir / "00_context.yaml")`. Save state.
9. Run `agent.validate.run_validation(artefacts_dir, quiet=True)`. Report issues.
10. Print time: `⏱  {elapsed:.0f} min elapsed, {remaining} phases remaining.`
11. Write audit. Mark phase complete.
12. Ask: "Approve? (y/edit/redo)" (real mode) or auto-continue (sim).

---

## Dry-run mode

When user types `/edth-agent dry-run`:

1. Print: `⚙️  Dry-run: starting with sim owner + condensed panel...`
2. `agent.state.empty_state()` — fresh state.
3. Set `owner_mode: sim`, `persona: edth-judge`, `panel_mode: condensed`.
4. Phase 0: auto-accept default context. **BAIL if** `00_context.yaml` not written.
5. Phase 1: Parse CSV. **BAIL if** `01_problems.json` is empty or parsing fails. Print progress per substep. **BAIL if** `01_triage.md` has <2 clusters — warn user the CSV may be misconfigured.
6. Auto-pick problem #1. Phase 2 in sim (persona answers). **BAIL if** `02_candidate_problem.md` missing or empty.
7. Auto-pick panel. Phase 3: decompose + auto-pick sub-problem #1.
8. Phase 4: ideation, auto-top-5. **BAIL if** <5 ideas survive dedup — warn user.
9. Phase 5: research + rank, persona picks #1.
10. Phase 6: demo plan + task assignment.
11. Phase 7: deck + market + render.
12. Print: `✅ Dry-run complete. Deck: artefacts/07_deck.html.`
13. Run `agent.validate.run_validation(artefacts_dir, quiet=False)`.
14. Print: "Start over with real data? `/edth-agent reset` then `/edth-agent run`."

## Skip-to mode

When user types `/edth-agent skip-to <N>`:

1. Print: `⚙️  Skip-to: generating stub artefacts for phases 0 to {N-1}...`
2. Run `agent.state.empty_state()` for a fresh state.
3. For phases 0..N-1, generate minimal stub artefacts:
   - Phase 0: `agent.context.save_context(artefacts_dir, agent.context.default_context())`.
   - Phase 1: Parse the configured CSV, write all problems as one cluster. Use default scores (3.0 for all axes). Mark `[STUB]` in the cluster name.
   - Phase 2: Pick problem #1. Generate 3 Q&A pairs with `[STUB ANSWER]`. Write chosen.
   - Phase 3: Decompose into 3 sub-problems. Pick #1. Use mid-range scores (3.0). Mark `[STUB]`.
   - Phase 4: Generate 5 generic ideas. Pick #1 at rating 3.0. Mark `[STUB]`.
   - Phase 5: Research stubs: "Web research skipped (stub)." Pick #1 at score 3.0. Mark `[STUB]`.
   - Phase 6: Generate a minimal demo plan stub. Task assignment: `[STUB — re-run after real phases fill in].
4. Each stub phase: `agent.state.mark_phase_completed(state, p, artefacts_dir / stub_path)`.
5. Set `current_phase = N`. Save state.
6. Print: `✅ Stubs generated for phases 0–{N-1}. Ready for phase {N}. Run /edth-agent run.`
7. Print: "⚠️  Stub artefacts are marked [STUB]. Replace them by re-running `/edth-agent rerun <N>` with real data."

## Rerun command

When user types `/edth-agent rerun <N>`:

1. If the artefact for phase N already exists, snapshot it: copy to `artefacts/snapshots/<filename>.bak.<timestamp>`.
2. Print: "Previous version saved to `artefacts/snapshots/`."
3. Run the phase implementation steps as normal (mark_phase_in_progress → execute prompt → write → mark_phase_completed → validate → time).

---

## Validate command

When user types `/edth-agent validate` (or `--quiet`):

Run `agent.validate.run_validation(artefacts_dir, quiet=True/False)`. This checks:

1. `state.json` exists, is valid JSON, has all required keys, `current_phase` is within 0-9.
2. Each completed phase has its artefact file present and non-empty.
3. `01_triage.md` has ≥2 clusters with scores.
4. `02_candidate_problem.md` has ≥2 candidates.
5. `03_chosen_sub_problem.md` has ≥3 sub-problems with ROI scores.
6. `04_solution_candidates.md` has ≥5 ideas with ratings.
7. `05_ranked_solutions.md` has ≥1 solution with research content.
8. `05_owner_pick.md` exists and references a valid idea_id.
9. `06_demo_plan.md` has a script with ≥5 timed beats.
10. `07_deck.md` exists and has ≥3 slides (count `---` separators).
11. `07_market.md`, `07_competition.md`, `07_business_model.md` exist and non-empty.
12. `08_summary.md` exists and has a pitch section AND panel verdicts.
13. If panel is locked, `state.json` `panel.auto_selected` has 3-5 entries.
14. If decisions exist in state, they reference valid problem/sub/solution IDs present in the artefacts.

Report results:
- If all pass: "✅ All {N} checks passed."
- If issues found: "⚠️ {N} issue(s):" with file-specific messages.
- Quiet mode: only output if issues found.

---

## Linting & quality

- **Ruff** — fast Python linter + formatter (Rust, ~0.01s). Run `uv run ruff check agent/ tests/ --fix && uv run ruff format agent/ tests/` to auto-fix.
- **Pre-commit hooks** — run `uv run pre-commit install --install-hooks` once. After that, ruff + end-of-file-fixer + trailing-whitespace + merge-conflict check run automatically on every `git commit`.

When you create or modify Python code, the agent automatically runs ruff before continuing. If ruff finds unfixable issues, it will report them.
