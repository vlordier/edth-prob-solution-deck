# EDTH Hackathon Agent — Design Spec

**Date:** 2026-06-02
**Status:** Draft, awaiting user review
**Owner:** Vincent

## 1. Purpose & scope

### What this is

A reusable agent, packaged as an OpenCode skill backed by thin Python glue, that walks a solo hacker or small team through the full lifecycle of a hackathon project — from a CSV of raw problem statements to a final problem/solution pitch deck — using a structured, judge-panel-reviewed process. The agent embodies the workflow of a "best in the world hackathon participant": ruthless triage, multi-perspective review, divergent ideation, defensible choices, and a deck that tells the story.

### What this isn't

- Not a generic AI assistant.
- Not a stand-alone web app or notebook.
- Not a backend service with persistent storage.
- Not tied to any one hackathon. EDTH is the default config; the core is hackathon-agnostic.

### In scope (v1)

- One CSV of problem statements as input.
- A 9-phase workflow producing 9 primary artefacts + 1 final deck.
- A library of 12 judge personas with auto-selection, plus 1 user-editable problem-owner persona.
- Marp-rendered deck (HTML + PDF) with Python fallback if Marp CLI is unavailable.
- Local filesystem storage of artefacts; resumable from any phase.
- Audit trail of LLM reasoning per phase.
- Tests for the Python glue modules; smoke tests for the skill commands.
- A sample run for orientation.

### Out of scope (v1, deferred to v2+)

- Multi-user / multi-tenant state.
- Cloud-hosted LLM orchestration (we use the OpenCode LLM directly).
- Real-time collaboration on artefacts.
- Web UI (Streamlit etc.). Phase 1 may add a thin viewer; not committed.
- Automatic commit / push of artefacts to remote.
- Judge-library marketplace / community-submitted judges.

## 2. Architecture overview

```
┌────────────────────────────────────────────────────────────┐
│                    OpenCode (LLM-driven)                   │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  SKILL.md  (the "agent")                             │  │
│  │  - Reads state, decides next phase                  │  │
│  │  - Drives LLM reasoning for creative steps          │  │
│  │  - Uses web_search / file tools for research        │  │
│  │  - Role-plays judges & owner personas               │  │
│  │  - Writes artefacts to disk                         │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                               │
│                            │ invokes                       │
│                            ▼                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Python glue (agent/*.py)                           │  │
│  │  - state.py       : load/save state.json            │  │
│  │  - parse_csv.py   : CSV → normalized JSON           │  │
│  │  - normalize.py   : statement quality flags         │  │
│  │  - score.py       : weighted scoring, bias apply     │  │
│  │  - rubric.py      : judging rubric definitions       │  │
│  │  - personas.py    : load & instantiate personas      │  │
│  │  - judges.py      : judge library, auto-selection    │  │
│  │  - render.py      : Marp → HTML/PDF, fallback chain  │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                               │
│                            ▼                               │
│  artefacts/  (one .md / .json per phase, state.json)       │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Why this split:** the LLM is the only thing that can do the creative work (cluster, ideate, evaluate, write copy). The Python modules handle the deterministic, testable, repeatable glue: parse, score, render. This mirrors Approach A in the brainstorm.

## 3. File / folder structure

```
edth-prob-solution-deck/
├── SKILL.md                      # OpenCode skill — workflow driver
├── README.md                     # User-facing quick start
├── pyproject.toml                # Python deps & entry points
├── .gitignore
│
├── input/
│   └── PB-SOL-EDTH - Sheet1.csv  # Provided problem statements
│
├── hackathons/
│   └── edth.yaml                 # Default hackathon config
│
├── agent/                        # Thin Python glue
│   ├── __init__.py
│   ├── state.py                  # state.json I/O
│   ├── parse_csv.py              # CSV → 01_problems.json
│   ├── normalize.py              # quality flags, de-dup
│   ├── score.py                  # weighted scoring, bias application
│   ├── rubric.py                 # judging rubric (impact/innovation/execution/presentation)
│   ├── personas.py               # problem-owner persona loader
│   ├── judges.py                 # judge library loader + auto-selection
│   └── render.py                 # marp / python-pptx / html fallback
│
├── personas/                     # Problem-owner personas
│   ├── edth-judge.yaml
│   └── README.md
│
├── judges/                       # Judge library (12 shipped)
│   ├── README.md                 # What each judge is for
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
├── templates/                    # Marp slide skeletons
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
│   └── sample-run/               # Pre-generated happy-path run for orientation
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
├── tests/                        # pytest
│   ├── conftest.py
│   ├── test_parse_csv.py
│   ├── test_normalize.py
│   ├── test_score.py
│   ├── test_state.py
│   ├── test_judges.py
│   └── test_render.py
│
└── artefacts/                    # Generated by the skill (gitignored except state.json & .md)
    ├── state.json
    ├── 00_context.yaml
    ├── 01_triage.md
    ├── 01_problems.json
    ├── 02_owner_questions.md
    ├── 02_owner_answers.md
    ├── 02_candidate_problem.md
    ├── 03_chosen_sub_problem.md
    ├── 04_solution_candidates.md
    ├── 05_ranked_solutions.md
    ├── 05_owner_pick.md
    ├── 06_demo_plan.md
    ├── 07_market.md
    ├── 07_competition.md
    ├── 07_business_model.md
    ├── 07_deck.md
    ├── 07_deck.html
    ├── 07_deck.pdf
    ├── 08_summary.md
    └── audit/
        ├── 01_triage.md
        ├── 02_candidate_problem.md
        └── ...
```

## 4. Workflow — the 9 phases

Each phase has: a single primary artefact, a definition of done, an audit-trail log, and an explicit "approve / edit / redo" gate. In `owner_mode: real` every gate pauses for the user; in `owner_mode: sim` the gate auto-approves after writing the artefact.

### Phase 0 — Onboarding

- **Definition of done:** `artefacts/00_context.yaml` exists, contains hackathon + team + agent config, and the user has confirmed it.
- **Interactive:** always (one-time per run).
- **I/O:** none in → `00_context.yaml` out.
- **Notes:** captures hackathon name, theme, tracks, judging rubric weights, team strengths/weaknesses, time budget, deliverable, owner mode, persona. Editable in-session; re-running Phase 0 overwrites the file.

### Phase 1 — Triage

- **Definition of done:** `artefacts/01_triage.md` exists; CSV is parsed and normalized; clusters are scored; panel (or default scoring) has produced top-cluster rankings; market-signal check is documented per cluster.
- **Interactive:** yes.
- **I/O:** `input/*.csv` + `00_context.yaml` → `01_problems.json` (intermediate) + `01_triage.md` (primary).
- **Sub-steps:**
  1. `python -m agent.parse_csv` produces normalized problem list with `id, name, problem, themes[], tags[], source_row, source_hash, quality_flags[]`.
  2. LLM clusters problems (4–8 clusters) and assigns theme/tag gaps.
  3. Each cluster scored on 4 axes (impact, tractability, demo-ability, fit) using the judging rubric.
  4. Quick market-signal check per cluster (1–2 web searches: "is anyone doing this? funded competitors?").
  5. Panel review: each judge gives top-3 cluster picks with one-line reasoning; aggregation (Borda default) produces group ranking.
  6. Output written.

### Phase 2 — Elicit & narrow

- **Definition of done:** `artefacts/02_candidate_problem.md` exists; top-3 candidate problems are scored and presented; a problem is picked.
- **Interactive:** yes — in `owner_mode: real` the user picks; in `owner_mode: sim` the persona picks (user can override by editing the file).
- **I/O:** `01_triage.md` → `02_owner_questions.md` (questions) + `02_owner_answers.md` (answers) + `02_candidate_problem.md` (primary).
- **Sub-steps:**
  1. LLM generates owner questions for the top 3 clusters (pain, env, constraints, success criteria, who-decides, who-pays).
  2. Panel adds 2–3 hard questions per cluster from each judge's `hard_questions_seed`.
  3. Capture answers (real or sim persona). Real: the skill asks the user interactively; sim: persona YAML is loaded and the LLM role-plays answers.
  4. Re-score top 3 with answers; write `02_candidate_problem.md` with scores, reasoning, and the panel's view.
  5. User picks 1; decision recorded in `state.json`.

### Phase 3 — Sub-problem decompose

- **Definition of done:** `artefacts/03_chosen_sub_problem.md` exists; chosen problem is decomposed into 5–8 sub-problems; each is ROI-scored; a sub-problem is picked.
- **Interactive:** yes — real: user picks; sim: persona picks.
- **I/O:** `02_candidate_problem.md` → `03_chosen_sub_problem.md`.
- **ROI scoring axes:** impact (for the chosen problem), time-fit (vs. team/time budget), demo-ability, dependency-risk. Default weights: 0.30 / 0.30 / 0.25 / 0.15. User can edit in `00_context.yaml`.

### Phase 4 — Divergent ideation

- **Definition of done:** `artefacts/04_solution_candidates.md` exists; 20+ raw ideas generated, clustered/deduped to 8–10; each rated by every panel judge; top 5 by group consensus surfaced; "judges hated this" section preserved.
- **Interactive:** yes (user may add ideas before ranking).
- **I/O:** `03_chosen_sub_problem.md` → `04_solution_candidates.md`.
- **Divergent techniques used:** SCAMPER, "worst possible idea", "what would [Palantir / Anduril / Skydio / a 16-year-old hacker] do?", constraint removal, "10× version". LLM is prompted to push for novelty, not safety.

### Phase 5 — Research & rank

- **Definition of done:** `artefacts/05_ranked_solutions.md` exists; top 5 candidates have web-research summaries; re-scoring uses research signal; panel produces final ranking; `05_owner_pick.md` captures the owner's validation.
- **Interactive:** yes — real: user validates the panel ranking and can swap top picks; sim: persona validates (with dissent recorded).
- **I/O:** `04_solution_candidates.md` → `05_ranked_solutions.md` + `05_owner_pick.md`.
- **Web research per top 5:** prior art, SOTA, funded competitors, deployment examples, public-domain prior solutions, TRL estimates, regulatory pathway.

### Phase 6 — Demo & narrative

- **Definition of done:** `artefacts/06_demo_plan.md` exists; thin-demo is defined; 3-minute demo script is time-stamped; 30-second elevator pitch is written; 8–12 judge questions with prepared answers exist; risk register has 5–8 entries.
- **Interactive:** yes (user reviews and edits in real mode; auto-approved in sim).
- **I/O:** `05_owner_pick.md` → `06_demo_plan.md`.
- **Thin-demo definition:** the smallest thing we can build in the remaining time that demonstrates the "wow" moment. Includes failure modes and the "what if the demo crashes" contingency.

### Phase 7 — Deck & market research

- **Definition of done:** `artefacts/07_deck.md` exists; `07_market.md`, `07_competition.md`, `07_business_model.md` exist; deck is rendered to `07_deck.html` (and `07_deck.pdf` if renderer supports it).
- **Interactive:** yes.
- **I/O:** `06_demo_plan.md` → `07_market.md` + `07_competition.md` + `07_business_model.md` + `07_deck.md` + `07_deck.html` + `07_deck.pdf`.
- **Sub-steps:**
  1. Market research (web): TAM / SAM / SOM, growth, segments, buyer personas, willingness-to-pay.
  2. Competition analysis (web): direct + adjacent competitors, market share estimates, positioning, moat analysis.
  3. Business model: canvas, pricing, GTM, customer-acquisition plan, defensibility.
  4. Generate Marp problem slide from `02_candidate_problem.md` + `03_chosen_sub_problem.md`.
  5. Generate Marp solution slide from `05_owner_pick.md` + market/comp/BM.
  6. Compile `07_deck.md` from cover + problem + solution + market + competition + business-model templates.
  7. Render via `agent/render.py` (see §9).

### Phase 8 — Final review

- **Definition of done:** `artefacts/08_summary.md` exists; deck is rendered; per-judge thumbs-up/down with one-line "what would change my mind" is captured; optional git commit of artefacts.
- **Interactive:** yes.
- **I/O:** all prior artefacts → `08_summary.md`.
- **Summary contains:** one-paragraph project pitch, top 3 risks, top 3 differentiators, panel dissent, next-48-hours action list.

## 5. The Judge Panel system

### 5.1 Library — 12 judges shipped in `judges/`

| File | Short | Domain tags |
|---|---|---|
| `military-operator.yaml` | "Maj. Viper Reyes (ret.)" | c-uas, autonomy, swarm, ew |
| `ew-specialist.yaml` | "Dr. Linh Tran" | ew, signal_proc, radar |
| `defense-prime-pm.yaml` | "Karen Whitfield" | all |
| `technical-skeptic.yaml` | "Ravi Mehta" | all |
| `acquisition-procurement.yaml` | "Daniel Park" | all |
| `end-user-frontline.yaml` | "Oleksandr K." | c-uas, autonomy, ew |
| `ethics-compliance.yaml` | "Dr. Amira Hassan" | autonomy, ew, c-uas |
| `defense-vc.yaml` | "Jordan Lee" | all |
| `red-team-adversary.yaml` | "Col. Yuri Volkov (ret.)" | ew, c-uas, autonomy |
| `scaling-engineer.yaml` | "Priya Shah" | all software |
| `intel-analyst.yaml` | "Mark Sutter" | ew, c2, autonomy |
| `operator-ux.yaml` | "Maj. Sarah Chen" | c2, autonomy, swarm |

### 5.2 Judge YAML schema

```yaml
name: "Maj. 'Viper' Reyes (ret.)"
short: "Military Operator"
tags: [c-uas, autonomy, swarm, ew]
background: "<one-paragraph biography>"
priorities: [<3-6 short strings>]
anti_priorities: [<3-6 short strings, explicit pet peeves>]
decision_style: "<one sentence>"
language_patterns: [<3-6 phrases they use>]
scoring_biases:
  impact: <float, default 0>
  innovation: <float>
  execution: <float>
  presentation: <float>
knowledge_gaps: [<2-4 things they don't know well>]
hard_questions_seed: [<3-6 hard questions for any project>]
```

`scoring_biases` shift the rubric weights at scoring time, so the persona actually changes scores — not just tone.

### 5.3 Auto-selection algorithm

Triggered by `/edth-agent panel generate` after Phase 2 (problem chosen). Steps:

1. Compute Jaccard similarity between the chosen problem's `themes[]` ∪ `tags[]` and each judge's `tags[]`.
2. Sort judges by similarity descending.
3. Apply hard rules:
   - `technical-skeptic` is always included (meta-judge).
   - If problem has `autonomy` theme → include `ethics-compliance`.
   - If problem has `ew` theme → include `red-team-adversary`.
   - If problem has `c2` or `decision_support` theme → include `operator-ux`.
   - If problem has `software` tag → include `scaling-engineer`.
4. Take top 5, with hard rules overriding.
5. User can `panel add / remove / replace` before locking.
6. State.json stores the locked panel for the run.

### 5.4 Per-phase panel participation

| Phase | Panel action | Output location |
|---|---|---|
| 1 Triage | Each judge ranks top-3 clusters; Borda aggregation | `01_triage.md` "Panel" section + `audit/01_triage.md` |
| 2 Elicit | Each judge contributes 2–3 owner questions | `02_owner_questions.md` tagged by judge |
| 3 Sub-problem | Each judge scores sub-problems; convergence surfaced | `03_chosen_sub_problem.md` "Panel scores" |
| 4 Ideation | Each judge rates 1–5 with one-line reasoning; rejection reasoning preserved | `04_solution_candidates.md` |
| 5 Research & rank | Each judge re-scores top 5 post-research; weighted vote; spread (max–min) recorded | `05_ranked_solutions.md` + `05_owner_pick.md` |
| 6 Demo | Each judge previews script; gives 1–3 hard questions for live demo | `06_demo_plan.md` "Judge Q&A" |
| 7 Deck | Each judge previews deck; flags the slide they'd push back on hardest | `audit/07_deck.md` per-judge |
| 8 Final | Each judge gives thumbs up/down + "what would change my mind" | `08_summary.md` |

### 5.5 Aggregation modes

- **Borda count** (default): each judge ranks top-to-bottom; sum of positions = group rank. Weights from `scoring_biases`.
- **Approval voting** (alternative for final ranking): each judge approves top-K (K=3 or 5). Less brittle to outlier picks.

Mode is set in `00_context.yaml`. Default: Borda for phases 1, 3, 4; approval for phase 5 final ranking.

### 5.6 Token-economy toggle

- `panel_mode: expanded` — one LLM call per judge per phase. Most distinct voices. Most expensive.
- `panel_mode: condensed` — one LLM call role-plays all judges in labeled sections. 5–10× cheaper. Slightly less distinct.

Default: `expanded` for phases 5, 6, 7 (high-stakes); `condensed` for phases 1, 3 (routine).

### 5.7 Panel chat command

`/edth-agent panel <short-name>` opens a free-form chat with one judge, using their persona system prompt. The user can ask that judge anything about the current state. Example:

```
> /edth-agent panel viper
[Maj. Viper Reyes in character]
What do you think of the swarm coordination sub-problem?
> The LLM responds in Viper's voice, using the current artefacts as context.
```

The chat is a session-only interaction; it does not write to artefacts unless the user explicitly asks "save this to the audit log."

## 6. The Persona system (problem owner)

### 6.1 What it is

A single YAML file representing the person the agent is *eliciting from* (as distinct from the judges who *review*). The owner is the source of truth on pain, environment, constraints, and acceptance criteria.

### 6.2 Schema

```yaml
name: "EDTH Defense Judge"
role: "Senior evaluator at a defense-tech prime"
background: "<one paragraph>"
priorities: [...]
anti_priorities: [...]
decision_style: "<one sentence>"
language_patterns: [...]
constraints:
  - "real-world impact matters more than novelty"
  - "prefers solutions fieldable in 12 months"
  - "values demo-able results"
communication_style: "direct, asks pointed questions, pushes back on hand-waving"
```

`scoring_biases` is *not* part of the owner schema — the owner doesn't score, they answer.

### 6.3 Default persona

`personas/edth-judge.yaml` ships as default. User can substitute any YAML in `personas/` via `agent.persona` in `00_context.yaml`.

### 6.4 Sim mode behavior

In `owner_mode: sim`, the LLM role-plays the owner using the persona YAML as the system prompt. The user can override any auto-answer by editing `02_owner_answers.md` directly; the skill will re-read it on next phase.

## 7. Artefact schema

Each phase produces one primary artefact. All artefacts are human-readable markdown or YAML/JSON for easy diffing.

| Phase | Primary artefact | Format |
|---|---|---|
| 0 | `00_context.yaml` | YAML config |
| 1 | `01_triage.md` | Markdown (clusters, scores, panel ranking, market signals) |
| 1 (intermediate) | `01_problems.json` | JSON (normalized problem list) |
| 2 (questions) | `02_owner_questions.md` | Markdown |
| 2 (answers) | `02_owner_answers.md` | Markdown |
| 2 (primary) | `02_candidate_problem.md` | Markdown (top-3, scores, panel view) |
| 3 | `03_chosen_sub_problem.md` | Markdown (sub-problems, ROI scores, panel scores) |
| 4 | `04_solution_candidates.md` | Markdown (20+ ideas, ratings, rejections preserved) |
| 5 | `05_ranked_solutions.md` | Markdown (top-5, research, panel ranking) |
| 5 | `05_owner_pick.md` | Markdown (owner's validated pick) |
| 6 | `06_demo_plan.md` | Markdown (demo, script, pitch, Q&A, risks) |
| 7 | `07_market.md` | Markdown |
| 7 | `07_competition.md` | Markdown |
| 7 | `07_business_model.md` | Markdown |
| 7 | `07_deck.md` | Marp-flavored markdown |
| 7 (rendered) | `07_deck.html`, `07_deck.pdf` | Output |
| 8 | `08_summary.md` | Markdown (one-pager) |

### 7.1 Audit trail

`artefacts/audit/<NN>_<phase>.md` per phase contains:
- Exact prompt(s) sent to the LLM
- Raw LLM response(s)
- Tool calls (web searches, file reads)
- Post-processed artefact with diff-from-previous (if rerun)

Audit files are gitignored — they bloat fast and are not needed for resumption.

## 8. State model

### 8.1 `artefacts/state.json` schema

```json
{
  "version": "0.1.0",
  "started_at": "2026-06-02T10:00:00Z",
  "updated_at": "2026-06-02T14:32:11Z",
  "current_phase": 5,
  "config": {
    "input_csv": "input/PB-SOL-EDTH - Sheet1.csv",
    "output_dir": "artefacts",
    "owner_mode": "real",
    "persona": "edth-judge",
    "panel_mode": "expanded",
    "aggregation_mode": "borda",
    "rubric_path": "hackathons/edth.yaml"
  },
  "phases": {
    "0":  {"status": "completed", "artefact": "artefacts/00_context.yaml", "completed_at": "..."},
    "1":  {"status": "completed", "artefact": "artefacts/01_triage.md",     "completed_at": "..."},
    "2":  {"status": "completed", "artefact": "artefacts/02_candidate_problem.md", "completed_at": "..."},
    "3":  {"status": "completed", "artefact": "artefacts/03_chosen_sub_problem.md", "completed_at": "..."},
    "4":  {"status": "completed", "artefact": "artefacts/04_solution_candidates.md", "completed_at": "..."},
    "5":  {"status": "in_progress", "artefact": "artefacts/05_ranked_solutions.md", "started_at": "..."},
    "6":  {"status": "pending"},
    "7":  {"status": "pending"},
    "8":  {"status": "pending"}
  },
  "decisions": {
    "chosen_problem_id": "P-028",
    "chosen_sub_problem_id": "P-028.SP-2",
    "chosen_solution_id": "P-028.SP-2.S-7"
  },
  "panel": {
    "auto_selected": ["viper", "tran", "whitfield", "mehta", "kovalenko"],
    "manually_overridden": false,
    "locked": true
  },
  "branches": {
    "considered_problems": [{"id": "P-031", "phase_decided": 2, "artefact": null}],
    "considered_sub_problems": [],
    "considered_solutions": []
  }
}
```

### 8.2 Branching / fork

`/edth-agent fork <phase>` moves the current decision to `branches.considered_*` and lets the user re-pick. Re-runs the chosen phase forward. Original artefacts preserved in `artefacts/branches/<timestamp>/`.

## 9. Marp integration with fallback

### 9.1 Three-tier strategy

`agent/render.py` chooses the best available renderer in this order:

1. **Marp CLI** — produces `.html` and `.pdf`. Preferred.
2. **python-pptx** — produces native `.pptx`. Good for sharing/editing.
3. **Self-contained HTML deck** — single `.html` file with embedded CSS, sections as slides, JS for keyboard navigation. Always works, no external deps.

The agent auto-detects:
- Marp: `which marp` and `marp --version` succeed.
- python-pptx: `import pptx` succeeds.
- HTML fallback: always.

If all three are missing, it returns an error and the user can re-run after installing. The agent never silently produces a broken deck.

### 9.2 Template structure

`templates/*.md` are Marp skeletons with front-matter (`---marp ... ---`), slide dividers (`---`), and placeholder sections. The LLM fills the placeholders with phase-specific content; `agent/render.py` concatenates phase outputs in deck order.

### 9.3 Deck order (Phase 7 output)

1. Cover (hackathon name, team, project name, date)
2. Problem (statement, pain, why now, who's affected)
3. Solution (one-liner, how it works, demo screenshot/description)
4. Market (TAM/SAM/SOM, growth, segments)
5. Competition (positioning map, top-3 competitors, our wedge)
6. Business model (canvas summary, pricing, GTM, defensibility)
7. Traction / next steps (what we'd do in 48h more)
8. Thank you / contact

## 10. Audit trail

### 10.1 What gets logged

`artefacts/audit/<NN>_<phase>.md` per phase contains:

- The exact prompt(s) sent to the LLM (skill-side prompt, not raw API call)
- Raw LLM response(s)
- Tool calls (web searches, file reads) with results
- Post-processed artefact (the actual file written)
- If rerun: diff vs. previous version

### 10.2 Why

- Challenge any LLM decision (cluster assignment, scoring, persona pick).
- Debug weird outputs.
- Onboard new users — they can see exactly what the agent did and why.
- Future fine-tuning: training data for "what good brainstorming looks like."

### 10.3 Cost

Audit files are gitignored. Disk usage grows fast (~1–5 MB per phase). Acceptable for local use.

## 11. Testing strategy

### 11.1 Unit tests (pytest)

- `test_parse_csv.py` — handles messy rows, multi-line cells, quotes, BOMs, UTF-8.
- `test_normalize.py` — quality flags (`vague`, `multi-problem`, `requires_hardware`, `out_of_scope_for_48h`), de-dup by `source_hash`.
- `test_score.py` — weighted scoring, persona bias application, Borda/approval aggregation.
- `test_state.py` — load/save state.json, resume, fork, branch tracking.
- `test_judges.py` — judge YAML schema validation, auto-selection algorithm, hard-rule overrides.
- `test_render.py` — Marp front-matter generation, fallback chain logic, HTML-deck generation.

### 11.2 Smoke tests (manual / CI)

- Run the skill on `examples/sample-run/input.csv` and assert all 9 artefacts are produced and the deck renders.
- Run each panel chat command with a stub judge; assert it doesn't crash.

### 11.3 What we explicitly don't test

- LLM output quality. Subjective, costly. The sample run is the closest we get to regression testing.

## 12. Gitignore strategy

`.gitignore`:

```gitignore
# Generated artefacts
artefacts/audit/
artefacts/07_deck.pdf
artefacts/07_deck.html
examples/sample-run/artefacts/audit/

# But keep resumable state and inspectable artefacts
!artefacts/state.json
!artefacts/*.md
!artefacts/*.yaml
```

The `!` exceptions are tricky in gitignore. Practical approach: ignore `artefacts/*`, then `!` exception each one we want. Or just commit `state.json` and the `.md` files explicitly. Document the approach in README.

## 13. Sample run

`examples/sample-run/` contains a complete pre-generated run on a synthetic problem (or one anonymized from the input CSV). It includes:

- `input.csv` — a small slice of the real CSV, anonymized.
- `artefacts/` — all 9 primary artefacts, fully written.
- `artefacts/07_deck.html` — rendered deck.
- `README.md` — explains what to look at, what success looks like, common pitfalls.

The sample run is the user's first reference: "is my run going to look like this?"

## 14. Open questions for implementation

1. **Persona chat command for owner?** The user can chat with a judge (`/edth-agent panel viper`); should they also be able to chat with the owner persona for free-form Q&A? Likely yes; add `/edth-agent owner` as a parallel.
2. **Live re-scoring.** If the user edits `00_context.yaml` mid-run (e.g., changes rubric weights), should the skill offer to re-score all phases automatically? Probably yes with a confirmation prompt.
3. **Multiple hackathon configs in one run.** Probably not a v1 need; defer.
4. **Persona authoring UI.** A small form to create a new judge/owner YAML without hand-writing. Probably a stretch; v1 = text editor.
5. **Local LLM support.** If the user wants to run the skill with Ollama / local model, the OpenCode side already supports it. No code change needed in the agent.
6. **Marp theme.** Default to `default`; user can override in `00_context.yaml.marp_theme`.

## 15. Out of scope (deferred to v2+)

- Multi-user state, remote storage.
- Web UI for the workflow.
- Git auto-commit of artefacts (offered as a manual command; not automatic).
- Judge library marketplace / community submission flow.
- Persistent judge "memory" across runs (currently each run is fresh).
- Internationalization (English only for v1).

---

**End of spec.** Awaiting user review.
