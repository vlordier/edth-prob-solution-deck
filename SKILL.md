# EDTH Hackathon Agent

You are driving the EDTH Hackathon Agent — a structured workflow that turns a CSV of problem statements into a problem/solution pitch deck, reviewed by a panel of 12 tough-judge personas.

## Setup (run once)

Before executing any phase, verify the Python environment is ready. If `uv` is not found, install it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then install deps and run `edth-agent` commands:

```bash
uv sync
uv run pytest
```

All subsequent `python` and `python -m agent.X` calls should be prefixed with `uv run`:

```bash
uv run python -c "from agent.state import empty_state; ..."
uv run python -m agent.parse_csv
uv run pytest
```

If the user wants PDF output, check for marp and offer to install it:

```bash
npm install -g @marp-team/marp-cli || brew install marp-cli
```

If neither is available, the HTML fallback works fine — mention this and continue.

## Behavior rules
- Every phase has a concrete prompt template below. Execute the prompt verbatim. Do not improvise.
- After each phase output, run `/edth-agent validate --quiet` to self-check. Fix issues before continuing.
- In `owner_mode: real`, ask the user "Approve? (y/edit/redo)" after writing each artefact. In `owner_mode: sim`, auto-continue.
- Every phase writes an audit entry via `agent.audit.write_audit_entry()`.

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

1. `python -m agent.parse_csv` or call `agent.parse_csv.parse_problems()`. Save to `artefacts/01_problems.json`.
2. `agent.normalize.assign_quality_flags()` on each problem. `agent.normalize.dedupe_problems()`.
3. Execute the prompt template above verbatim. Do not improvise.
4. If panel is locked, run panel review: Borda aggregation.
5. Build `agent.triage.TriageReport`, write via `agent.triage.write_triage_report()`.
6. Write audit entry. Mark phase complete.

---

## Phase 2 — Elicit & narrow

### Phase 2 Prompt Template

Execute this prompt verbatim:

```
You are generating structured owner questions for the top 3 problem clusters
from Phase 1, following The Mom Test methodology (Rob Fitzpatrick).

Read `artefacts/01_triage.md` to get the clusters and their problem IDs.

CRITICAL RULES — The Mom Test:
- NEVER ask "Would you use X?" or "Do you think X is a problem?" (leading)
- NEVER ask hypotheticals: "How much would you pay?" (speculation)
- ALWAYS ask about specific past incidents: "Tell me about the last time..."
- ALWAYS ask about current behavior: "How do you solve this today?"
- ALWAYS look for concrete cost: "How many hours/people/dollars does this burn?"
- ALWAYS probe for failed attempts: "What did you try that didn't work?"
- If they say "it's a big problem" — ask "how many times did it happen last week?"
- If they say "we'd buy that" — ask "who signs the PO and what's their email?"

Step 1 — Owner questions (3 per cluster, minimum 9 total):

CLUSTER QUESTIONS (3 per cluster):
  Q-0XX: "Walk me through the last time you dealt with [cluster topic]. What
         happened, step by step?" (past incident, not opinion)
  Q-0XX: "How do you solve [cluster topic] today? What tools, people, or
         workarounds are you using right now?" (current behavior)
  Q-0XX: "What did you try before your current approach, and why did you
         abandon it?" (failed attempts)

CROSS-CUTTING QUESTIONS (asked once, tagged with cluster that triggers it):
  Q-0XX: "In the past month, how many times did a mission or operation get
         delayed or compromised because [cluster topic] wasn't solved? What was
         the worst incident?" (concrete frequency + cost)
  Q-0XX: "Who specifically is the person accountable for fixing this? What's
         their title and what happens to them if it's not fixed in 6 months?"
         (purchasing intent + consequences)
  Q-0XX: "If you had to show me proof that this is a real problem right now
         — a screenshot, an email thread, an after-action report — what would
         you show me?" (evidence of pain)
  Q-0XX: "Is there anyone else I should talk to who feels this pain more
         acutely than you?" (referral check — if no one comes to mind,
         the problem may be shallow)

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

1. Load `01_triage.md`. Read top 3 clusters.
2. Execute prompt template above.
3. Build `OwnerQuestion` objects. Write via `agent.elicitation.write_owner_questions()`.
4. Capture answers. Write via `agent.elicitation.write_owner_answers()`.
5. Re-score candidates. Write via `agent.candidates.write_candidate_problem()`.
6. User picks 1. Record via `agent.state.set_decision(state, "chosen_problem_id", ...)`.
7. Auto-pick panel: `agent.judges.select_panel()`. Store in state. Offer user to review.
8. Write audit. Mark phase complete.

---

## Question Sheet (`/edth-agent sheet`)

Generates a printable Mom Test interview guide — a reference document to
take into problem-owner conversations. Separate from the interactive Q&A
flow. Can be called at any time after Phase 1 completes.

### Question Sheet Prompt Template

Execute this prompt verbatim:

```
You are generating a printable Mom Test question sheet for interviewing
a problem owner. Read `artefacts/01_triage.md` to get the top 3 clusters.

Step 1 — Mom Test rules (5-6 rules, verbatim):
  1. Talk about their life, not your idea.
  2. Ask about specific past incidents — "the last time this happened..."
  3. Never ask "would you use X?" or "how much would you pay?"
  4. Look for concrete cost: hours, people, dollars burned.
  5. Compliments are traps — "sounds great" means "I'm being polite."
  6. If they can't introduce you to someone who feels it more, the problem
     may not exist.

Step 2 — Interviewer tips (4-5 tips):
  - Start every question with "Tell me about the last time..."
  - If they say "a lot of people have this problem", ask for an introduction
    right there. Pull out your phone.
  - Bad answer: "We'd definitely use that." Good answer: "Last week we lost
    3 hours because we didn't have this. Here's the email thread."
  - Record the call. Note specific names, dates, and numbers.
  - End with: "Is there anything I should have asked?"

Step 3 — Per cluster: 3 DO-ask questions + 2 DON'T-ask questions
  For each of the top 3 clusters, generate:
  - 3 good questions (past-tense, incident-based, cost-probing)
  - 2 bad questions (leading, hypothetical, opinion-seeking) with WHY they're bad
  Build these as `agent.sheet.GoodQuestion` and `agent.sheet.BadQuestion`.

Step 4 — Answer scoring rubric (4 rows):
  | Concrete past incident with cost | Strong signal — validated problem |
  | Vague complaint, no specifics | Weak signal — not validated |
  | "Sounds great" / "very interesting" | Anti-signal — being polite |
  | "Let me introduce you to X" | Strong signal — they care enough to connect |

Build a `agent.sheet.QuestionSheet` and write via
`agent.sheet.write_question_sheet(artefacts_dir, sheet)`.
Output goes to `artefacts/question_sheet.md`.
```

### Implementation steps

1. Verify Phase 1 is completed (`artefacts/01_triage.md` exists).
2. Execute the prompt template above.
3. Write via `agent.sheet.write_question_sheet()`.
4. Tell the user: "Question sheet saved to `artefacts/question_sheet.md`.
   Print it or share it before your next owner interview."
5. Write audit entry.

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

1. Load chosen problem from state and `02_candidate_problem.md`.
2. Execute prompt template above.
3. Panel: each judge scores sub-problems on the 4 ROI axes.
4. Write via `agent.sub_problem.write_sub_problem()`.
5. User picks 1. Record via `set_decision("chosen_sub_problem_id", ...)`.
6. Write audit. Mark phase complete.

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

1. Load `03_chosen_sub_problem.md`.
2. Execute prompt template above.
3. Dedupe via `agent.ideation.dedupe_ideas()`.
4. In real mode: offer user to add 1-3 ideas.
5. Panel: rate every idea 1-5.
6. Sort, surface top 5 + "judges hated this".
7. Write via `agent.ideation.write_solution_candidates()`.
8. Write audit. Mark phase complete.

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
5. Write audit. Mark phase complete.

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

1. Load all artefacts.
2. Execute prompt template above.
3. Write `08_summary.md` via `agent.summary.write_summary()`.
4. Panel: final verdicts. Record dissent.
5. Final deck re-render check.
6. Write audit. Mark run complete. State: `current_phase: 9`, `status: completed`.

---

## Phase 0 — Onboarding

### Implementation steps

1. Read or create `artefacts/state.json` via `agent.state`.
2. Load default context via `agent.context.default_context()`.
3. Present the default to the user. Ask them to confirm or edit.
   If this is a dry-run: auto-accept the default.
4. Save via `agent.context.save_context(artefacts_dir, ctx)`.
5. Write audit. Mark phase 0 complete.

---

## Dry-run mode

When user types `/edth-agent dry-run`:

1. Set `owner_mode: sim`, `persona: edth-judge`, `panel_mode: condensed`.
2. Create a fresh state via `agent.state.empty_state()`.
3. Run Phase 0 with auto-accept on default context.
4. Run Phase 1 (parse + cluster + score the sample CSV).
5. Auto-pick problem #1 as "chosen." Run Phase 2 in sim (persona answers).
6. Auto-pick panel. Run Phase 3 (decompose + auto-pick sub-problem #1).
7. Run Phase 4 (ideation, auto-top-5), Phase 5 (research + rank, persona picks #1).
8. Run Phase 6 (demo plan), Phase 7 (deck + market + render).
9. Print: "Dry-run complete. Deck rendered to `artefacts/07_deck.html`. Review with `/edth-agent validate`."
10. Offer: "Start over with real data? `/edth-agent reset` then `/edth-agent run`."

## Skip-to mode

When user types `/edth-agent skip-to <N>`:

1. Run `agent.state.empty_state()` for a fresh state.
2. For phases 0..N-1, generate minimal stub artefacts:
   - Phase 0: `agent.context.save_context(artefacts_dir, agent.context.default_context())`.
   - Phase 1: Parse the configured CSV, write all problems as one cluster, default scores.
   - Phase 2: Pick problem #1, generate 3 generic Q&A pairs, write as chosen.
   - Phase 3: Decompose into 3 sub-problems, pick #1. Use mid-range scores.
   - Phase 4: Generate 5 generic ideas, pick #1 at rating 3.0.
   - Phase 5: Research stubs: "Web research skipped (stub)." Pick #1 at score 3.0.
   - Phase 6: Generate a minimal demo plan stub.
3. Mark all stub phases as completed in state.
4. Set `current_phase = N`.
5. Print: "Stubs generated for phases 0–{N-1}. Ready to start phase {N}. Run `/edth-agent run`."
6. User can now run or edit stubs before proceeding.

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
