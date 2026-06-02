# EDTH Hackathon Agent

Read a CSV of problem statements. Get a winning pitch deck — with 12 domain-expert judges reviewing every step.

```
/edth-agent dry-run
/edth-agent run
open artefacts/07_deck.html
```

## Install from scratch

### 1. Install OpenCode

```bash
curl -fsSL https://opencode.ai/install | bash
```

[Other install methods →](https://opencode.ai/docs/#install)

### 2. Choose a free model

Sign up at [opencode.ai/auth](https://opencode.ai/auth), add a payment method (required but unused for free models), and copy your API key.

Free models available: **DeepSeek V4 Flash**, **MiMo-V2.5**, **Nemotron 3 Super**, **Big Pickle**.

In OpenCode, run `/connect`, select **opencode**, paste your key. Then `/models` to pick one.

[Zen docs →](https://opencode.ai/docs/zen)

   3. clone and go

```bash
git clone https://github.com/vlordier/edth-prob-solution-deck.git
cd edth-prob-solution-deck
opencode
```

In the OpenCode chat:

```
/edth-agent dry-run
```

The agent sets up Python + deps automatically the first time you run it. 30 seconds later, open `artefacts/07_deck.html` in your browser.

## Your own CSV

Drop a CSV with columns `Name` and `Problem statement` in `input/`. Real CSVs are gitignored.

```bash
python -c "
from agent.context import default_context, save_context; from pathlib import Path
ctx = default_context(); ctx['agent']['input_csv'] = 'input/your-file.csv'
save_context(Path('artefacts'), ctx)
"
```

## Run

All commands in OpenCode chat:

| Command | Does |
|---|---|
| `/edth-agent dry-run` | 30s smoke test — full pipeline, zero interaction |
| `/edth-agent run` | Start or resume the workflow |
| `/edth-agent validate` | Check all artefacts for issues |
| `/edth-agent sheet` | Generate a printable Mom Test question sheet |
| `/edth-agent panel viper` | Chat with a judge in character |
| `/edth-agent skip-to 5` | Jump to ranking with stub phases |

After each phase the agent asks "Approve? (y/edit/redo)".

## Output

```
artefacts/
├── 07_deck.html      ← Open in browser (arrow keys to navigate)
├── 07_deck.pdf       ← If Marp CLI installed
├── 07_market.md      ← TAM/SAM/SOM, trends, personas
├── 07_competition.md ← 3+ rivals, strengths, weaknesses, moat
└── 07_business_model.md
```

## How it works

| Stage | What happens |
|---|---|
| **Select** | Cluster 40+ problems, score, flag quality, check market → top 3 |
| **Elicit** | Owner Q&A + 5 judges ask hard questions → pick #1 |
| **Validate** | Decompose into sub-problems, ROI-score, panel reviews → pick slice |
| **Ideate** | 7 divergent techniques, 20+ ideas, panel rates 1-5 → top 5 |
| **Rank** | Web research, panel re-rank, owner validates → winner |
| **Ship** | Demo plan, market/competition/BM, 8-slide deck rendered |

## Judges

12 personas: F-16 pilot, EW specialist, defense PM, procurement, Ukrainian drone op, ethics lawyer, VC, red-team adversary, scaling eng, intel analyst, UX designer — and Ravi Mehta, the always-on technical skeptic. The agent auto-selects 5 for your domain.

`/edth-agent panel viper` — *"What kills this at 3am?"*

## Tune it

- Edit `hackathons/edth.yaml` to change hackathon, rubric weights, or team profile.
- Drop real CSVs in `input/` (gitignored). Update path in `artefacts/00_context.yaml`.
- Add your own judge: copy any file in `judges/`, fill in the YAML schema.

```bash
uv sync && uv run pytest   # 104 tests
```

## Project

## Project

| What | Where |
|---|---|
| Agent driver | `SKILL.md` — prompt templates, commands, workflow |
| Python glue | `agent/` — parse, normalize, score, render, validate |
| Judges | `judges/` — 12 YAMLs |
| Templates | `templates/` — Marp slide skeletons |
| Sample run | `examples/sample-run/` — pre-generated artefacts + deck |
| Tests | `tests/` — 104 tests |
