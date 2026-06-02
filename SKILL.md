# EDTH Hackathon Agent

You are driving the EDTH Hackathon Agent — a structured workflow that turns a CSV of problem statements into a problem/solution pitch deck, reviewed by a panel of 12 tough-judge personas.

## Quick start

1. Make sure the input CSV is at `input/PB-SOL-EDTH - Sheet1.csv` (or set `agent.config.input_csv` in `00_context.yaml`).
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
