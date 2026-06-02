# EDTH Hackathon Agent

An OpenCode skill that reads a CSV of problem statements and walks you through a 9-phase hackathon workflow — triage, elicitation, ideation, ranking, demo planning, deck generation — reviewed by a panel of 12 tough-judge personas (military operator, EW specialist, defense PM, ethics lawyer, red-team adversary, and more).

**Output:** a pitch deck (Marp/HTML) + supporting research artefacts.

## What it looks like

```
$ /edth-agent dry-run

 Phase 0 ✅ — Onboarding (EDTH default context)
 Phase 1 ✅ — 4 problems parsed, 3 clusters scored
 Phase 2 ✅ — Owner Q&A (sim), top-3 candidates, problem P-001 chosen
 Phase 3 ✅ — 6 sub-problems decomposed, SP-2 picked
 Phase 4 ✅ — 22 ideas generated, 8 unique after dedup, top-5 surfaced
 Phase 5 ✅ — Web research on top-5, panel re-ranking, owner picks I-14
 Phase 6 ✅ — Demo script (12 beats), 30s pitch, 9 Q&A, 6 risks
 Phase 7 ✅ — Market ($12B TAM), competition (3 rivals), deck rendered
──────────────────────────────────────────────
 ✅ Deck: artefacts/07_deck.html (open in browser)
 ✅ 104 automated checks passed
```

The rendered deck has 8 slides (cover → problem → solution → market → competition → business model → demo → thank you), navigable with arrow keys.

## Install

### 1. Install Python dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate      # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

### 2. Install Marp CLI (optional, for best deck rendering)

```bash
npm install -g @marp-team/marp-cli
# or: brew install marp-cli
```

If Marp is not installed, the agent falls back to python-pptx or self-contained HTML.

### 3. Place your problem CSV

Default: `input/sample-problems.csv` (8 synthetic examples). Drop your real CSV in `input/` and update the path:

```bash
mkdir -p artefacts
python -c "
from agent.context import default_context, save_context
from pathlib import Path
ctx = default_context()
ctx['agent']['input_csv'] = 'input/your-real-file.csv'
save_context(Path('artefacts'), ctx)
"
```

Real CSVs in `input/` are gitignored.

## Run

All commands are typed into the OpenCode chat:

| Command | What it does |
|---|---|
| `/edth-agent help` | Show all commands and phase reference |
| `/edth-agent dry-run` | 30-second smoke test — runs Phase 0→7 automatically |
| `/edth-agent run` | Start with Phase 0 onboarding (or resume the next pending phase) |
| `/edth-agent run 3` | Jump to Phase 3 (sub-problem decompose) |
| `/edth-agent skip-to 5` | Generate stubs for phases 0–4, jump to ranking |
| `/edth-agent validate` | Scan all artefacts and report issues |
| `/edth-agent panel viper` | Chat with Maj. Viper in character |
| `/edth-agent status` | Show current phase, decisions, panel |
| `/edth-agent render` | Re-render the deck from existing artefacts |

### Dry-run (recommended first step)

```bash
/edth-agent dry-run
```

This runs the full pipeline in ~30 seconds with a simulated owner and condensed panel. Open `artefacts/07_deck.html` in a browser to see the output.

### Real run (interactive)

```bash
/edth-agent run        # Phase 0: onboarding
/edth-agent run        # Phase 1: triage
/edth-agent run        # Phase 2: elicit & narrow (you answer questions here)
...
```

After each phase, the agent asks "Approve? (y/edit/redo)". Answer `y` to continue, `edit` to tweak the artefact, or `redo` to regenerate.

## How it works

```
   input.csv          Phase 1          Phase 2          Phase 3-5          Phase 7
   ─────────         ────────         ────────         ──────────         ────────
 ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
 │ 40+ raw  │ ──► │ 6 clusters│ ──► │ Top 3    │ ──► │ 8 ideas  │ ──► │ 07_deck  │
 │ problems │     │ scored    │     │ candidates│     │ ranked   │     │ .html    │
 └──────────┘     └──────────┘     └──────────┘     └──────────┘     └──────────┘
                        │                │                │
                   ┌────▼────┐     ┌────▼────┐     ┌────▼────┐
                   │  Quality │     │  Owner  │     │  Panel  │
                   │  Flags   │     │  Q&A    │     │ (5 judges)
                   └─────────┘     └─────────┘     └─────────┘
```

1. **Parse & flag** — Problems get quality flags (vague, requires-hardware, multi-problem).
2. **Cluster & score** — Problems grouped into 4-8 themes, scored on impact/innovation/execution/presentation.
3. **Owner Q&A** — The agent asks you (or plays a persona) 6-10 questions about pain, environment, constraints.
4. **Panel review** — 5 judges (auto-selected or hand-picked) review every phase output.
5. **Ideation** — 20+ divergent ideas generated via SCAMPER, "what would X do", anti-solutions, analogy transfer.
6. **Research** — Web search for prior art, competitors, TRL.
7. **Deck** — Marp-flavored markdown compiled and rendered.

## The 12 judges

Each judge has a distinct personality, expertise, biases, and pet peeves. The agent auto-selects 5 based on your chosen problem domain.

| Short | Judge | Role |
|---|---|---|
| `viper` | Maj. Viper Reyes (ret.) | F-16 pilot, 2200 hrs, JTAC-qualified |
| `tran` | Dr. Linh Tran | EW specialist, MITRE researcher |
| `whitfield` | Karen Whitfield | Defense prime PM, 15 yrs on radar programs |
| `mehta` | Ravi Mehta | Technical skeptic (always-on), CTO, ex-Palantir |
| `park` | Daniel Park | Acquisition official, FAR/DFARS expert |
| `kovalenko` | Oleksandr K. | Ukrainian drone operator, current conflict |
| `hassan` | Dr. Amira Hassan | IHL lawyer, autonomous weapons policy |
| `lee` | Jordan Lee | Defense VC, former Army officer |
| `volkov` | Col. Yuri Volkov (ret.) | Red-team adversary, offensive EW |
| `shah` | Priya Shah | Scaling engineer, ex-Palantir, SLO obsession |
| `sutter` | Mark Sutter | Intelligence analyst, ex-CIA |
| `chen` | Maj. Sarah Chen | Operator UX, USAF Test Pilot School |

Chat with any judge: `/edth-agent panel viper` — "What do you think of the swarm sub-problem?"

## Project structure

```
SKILL.md              ← the agent (prompt templates, commands, workflow)
agent/                ← Python glue (parse, normalize, score, render, validate)
judges/               ← 12 judge YAMLs
personas/             ← problem-owner personas
templates/            ← Marp slide skeletons
examples/sample-run/  ← pre-generated run with rendered deck
tests/                ← 104 pytest tests
```

## Troubleshooting

**"ModuleNotFoundError: No module named 'agent'"**
→ You forgot `pip install -e ".[dev]"`. Run it.

**Marp not found, deck renders as HTML**
→ Install Marp CLI for PDF output. HTML deck works fine for viewing.

**"ParseError: CSV is missing required columns"**
→ Your CSV needs columns named exactly `Name` and `Problem statement`.

**Validation warnings about missing sections**
→ Re-run the phase with `/edth-agent rerun <N>`. The prompt templates include self-validation.

**Tests failing**
→ `pip install -e ".[dev]"` — pytest-cov is an optional dep. Then run `pytest`.

**Want a different hackathon?**
→ Edit `hackathons/edth.yaml` or point to a different config in `artefacts/00_context.yaml`.

## Design doc

## Documentation

See `docs/superpowers/plans/` for the implementation plan.
