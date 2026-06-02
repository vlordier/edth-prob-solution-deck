# EDTH Hackathon Agent

You are driving the EDTH Hackathon Agent — a structured workflow that turns a CSV of problem statements into a problem/solution pitch deck, reviewed by a panel of 12 tough-judge personas.

## Quick start

1. Make sure the input CSV is at `input/sample-problems.csv` (or drop your real CSV in `input/` and update `agent.config.input_csv`).
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
4. Update `state.json` via the `agent.state` Python helpers.
5. In `owner_mode: real`, pause for user review. In `owner_mode: sim`, auto-approve.

When in doubt, refer to the spec: `docs/superpowers/specs/2026-06-02-edth-agent-design.md`.

## Panel system (12 tough judges)

The agent maintains a panel of judge personas that review every artefact. Default library lives in `judges/*.yaml`.

### Panel lifecycle

1. After Phase 2 (problem chosen), call `/edth-agent panel generate` to auto-pick 5 judges.
2. User can `panel add / remove / replace` before locking.
3. The locked panel is recorded in `state.json` under `panel.auto_selected`.
4. Each phase uses the locked panel for per-phase review (see spec §5.4).
5. In `panel_mode: expanded` (default for high-stakes phases), each judge gets a separate LLM call.

### Panel chat command

`/edth-agent panel <short>` opens a free-form chat with one judge. The judge responds in character using their YAML as the system prompt.

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

## Per-phase implementation guide

### Phase 0 — Onboarding

1. Ask the user for hackathon name, theme, tracks, team size/strengths/weaknesses, time budget.
2. Call `agent.context.default_context()` for the default EDTH context template.
3. Merge user answers into the context dict, write via `agent.context.save_context(artefacts_dir, ctx)`.
4. If the user wants a custom hackathon config, point them to `hackathons/` and explain the YAML format.
5. Update state: `state["phases"]["0"]["status"] = "completed"` and set `current_phase = 1`.
6. In `owner_mode: real`, confirm before proceeding; in `sim`, auto-approve.
7. Write audit entry via `agent.audit.write_audit_entry()`.

### Phase 1 — Triage

1. Call `agent.parse_csv.parse_problems(Path(state["config"]["input_csv"]))` to get the raw problem list.
2. Run `agent.normalize.assign_quality_flags()` on each problem; store the flags.
3. Dedupe via `agent.normalize.dedupe_problems()` by `source_hash`.
4. Write `01_problems.json` as the intermediate artefact.
5. LLM prompt: cluster the problems into 4–8 groups by theme. Assign themes/tags to each cluster. For each cluster, pick the most representative problems.
6. LLM prompt: score each cluster on the 4 rubric axes (impact, innovation, execution, presentation) using the 1–5 scale. Compute weighted scores via `agent.rubric.score_to_weighted()`.
7. LLM prompt: run a market-signal check per cluster. Use web search: "who is solving this? funded competitors? SOTA?" Document 1–2 sentences per cluster.
8. Panel review: each judge ranks top-3 clusters with one-line reasoning. Aggregate via `agent.aggregation.borda_count()`.
9. Build a `TriageReport` dataclass from `agent.triage` and write via `agent.triage.write_triage_report()`.
10. Update state: mark phase 1 completed with artefact path `artefacts/01_triage.md`.
11. Write audit entry.

### Phase 2 — Elicit & narrow

1. Load `01_triage.md` and extract the top 3 clusters.
2. LLM: generate 6–8 owner questions per cluster covering pain, environment, constraints, success criteria, who-decides, who-pays.
3. Panel: each judge contributes 2–3 hard questions from their `hard_questions_seed`.
4. Build `OwnerQuestion` dataclasses from `agent.elicitation` and write via `agent.elicitation.write_owner_questions()`.
5. In `owner_mode: real`, present questions to the user and capture answers. In `owner_mode: sim`, load the owner persona YAML via `agent.personas` and LLM-role-play answers.
6. Write answers via `agent.elicitation.write_owner_answers()`.
7. LLM: re-score the top-3 candidate problems incorporating the answers.
8. Build `Candidate` dataclasses from `agent.candidates` with `panel_picks` from Phase 1's Borda results. Write via `agent.candidates.write_candidate_problem()`.
9. Present top-3 to the user with panel view. User picks 1. Record via `agent.state.set_decision(state, "chosen_problem_id", pid)`.
10. Auto-pick judges: load all judges via `agent.judges`, compute Jaccard similarity with the chosen problem's themes, apply hard rules (technical-skeptic always included, etc.), pick top 5.
11. Store picked panel in `state["panel"]["auto_selected"]`.
12. Update state, write audit entry.

### Phase 3 — Sub-problem decompose

1. Load `02_candidate_problem.md` and extract the chosen problem.
2. LLM: decompose into 5–8 sub-problems. Each sub-problem must be a specific, tractable slice of the larger problem.
3. LLM: ROI-score each sub-problem on 4 axes: impact, time-fit, demo-ability, dependency-risk (1–5 scale).
4. Build `SubProblem` dataclasses from `agent.sub_problem`; the `.roi_score()` method auto-computes weighted ROI using `agent.sub_problem.ROI_WEIGHTS`.
5. Panel: each judge scores the sub-problems independently. Surface convergence (which sub-problems have tight agreement vs. wide spread).
6. Write via `agent.sub_problem.write_sub_problem()`.
7. User picks 1 sub-problem. Record via `agent.state.set_decision(state, "chosen_sub_problem_id", sp_id)`.
8. Update state, write audit entry.

### Phase 4 — Divergent ideation

1. Load `03_chosen_sub_problem.md` and extract the chosen sub-problem.
2. LLM: use divergent techniques (SCAMPER, "worst possible idea", "what would [competitor] do?", constraint removal, "10x version") to generate 20+ raw ideas.
3. Clean: strip duplicates, normalize phrasing. Dedupe via `agent.ideation.dedupe_ideas()` using Jaccard similarity (default threshold 0.7).
4. In `owner_mode: real`, offer the user a chance to add 1–3 ideas before ranking.
5. Panel: each judge rates every idea 1–5 with one-line reasoning. Judges who reject an idea must give their reasoning.
6. Build `Idea` dataclasses from `agent.ideation` with `rating`, `panel_ratings`, and `judge_rejections`.
7. Sort by average rating descending. Surface top 5 + "judges hated this" section.
8. Write via `agent.ideation.write_solution_candidates()`.
9. Update state, write audit entry.

### Phase 5 — Research & rank

1. Load `04_solution_candidates.md` and extract the top 5 ideas.
2. For each of the top 5: web search for prior art, SOTA, funded competitors, deployment examples, TRL estimates, regulatory pathway. 1–2 search queries per idea, 3–5 sentence research summary per idea.
3. Panel: each judge re-scores the top 5 post-research using a 1–5 scale on the 4 rubric axes.
4. Compute aggregate scores via `agent.aggregation.weighted_borda()` (weighted by judge expertise/confidence).
5. Record spread (max score - min score) for each solution.
6. Build `RankedSolution` dataclasses from `agent.ranking`. Write ranked solutions via `agent.ranking.write_ranked_solutions()`.
7. Present ranking to the owner. In `owner_mode: real`, user validates and may swap top picks. In `owner_mode: sim`, persona validates with any dissents recorded.
8. Write owner pick via `agent.ranking.write_owner_pick()` with validation notes and dissents.
9. Record via `agent.state.set_decision(state, "chosen_solution_id", solution_id)`.
10. Update state, write audit entry.

### Phase 6 — Demo & narrative

1. Load `05_owner_pick.md` and extract the chosen solution.
2. Define the thin-demo: smallest buildable thing that demonstrates the "wow" moment.
3. Write a timed 3-minute demo script with beats (0:00–0:30 setup, 0:30–2:00 demo, 2:00–3:00 pitch).
4. Write a 30-second elevator pitch.
5. Panel: each judge gives 1–3 hard questions they'd ask during a live demo.
6. LLM: prepare 8–12 answers to judged questions.
7. Build a risk register with 5–8 entries (risk, likelihood, impact, mitigation).
8. Write `06_demo_plan.md` with all sections.
9. Update state, write audit entry.

### Phase 7 — Deck & market

1. Load all prior artefacts: `02_candidate_problem.md`, `03_chosen_sub_problem.md`, `05_owner_pick.md`, `06_demo_plan.md`.
2. Market research (web): TAM/SAM/SOM, growth, segments, buyer personas, willingness-to-pay. Write `07_market.md`.
3. Competition analysis (web): direct + adjacent competitors, market share estimates, positioning, moat. Write `07_competition.md`.
4. Business model: canvas, pricing, GTM, customer-acquisition plan, defensibility. Write `07_business_model.md`.
5. Generate Marp problem slide from Phase 2+3 content.
6. Generate Marp solution slide from Phase 5+6 content + market/comp/BM.
7. Generate market, competition, business-model, demo, pitch slides from templates.
8. Compile `07_deck.md` in deck order (cover → problem → solution → market → competition → BM → traction → thanks).
9. Render via `agent.render`: try Marp CLI first, then python-pptx, then self-contained HTML. Write `07_deck.html` and optionally `07_deck.pdf`.
10. Panel: each judge flags the slide they'd push back on hardest. Record in audit.
11. Update state, write audit entry.

### Phase 8 — Final review

1. Load all artefacts.
2. Write a one-page summary: one-paragraph pitch, top 3 risks, top 3 differentiators, next-48-hours action list.
3. Panel: each judge gives thumbs up/down verdict with one-line "what would change my mind."
4. Record panel dissent if any.
5. Write `08_summary.md`.
6. Render final deck if not already done.
7. Optional: git commit artefacts via user prompt.
8. Update state to completed, write final audit entry.


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
