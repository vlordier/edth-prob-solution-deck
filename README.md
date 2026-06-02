# EDTH Hackathon Agent

> *"What's your problem?"*
>
> I'd go from table to table around noon on Saturday and ask. Few teams could answer. Fewer had validated it with a problem owner. Almost nobody knew how to ask good questions. Of the ones who had a problem well-defined, maybe half had ideated properly. Of those, almost none had stress-tested their ideas against anyone who'd push back before they started building.

I built this agent so teams would spend 30 minutes to an hour actually going through systematic steps instead of winging it.

It reads problem statements from a CSV and walks you through the three things most teams skip:

1. **Problem selection** — cluster, score, flag quality, check the market, panel review → top 3. No more "this one sounds cool."
2. **Problem elicitation & validation** — Mom Test-style interview questions (adapted for soldiers and operators, not procurement officers), decompose into sub-problems, ROI-score the highest slice. No more solving the wrong thing.
3. **Solution ideation** — 20+ divergent ideas across 7 techniques, deduped, rated 1-5 by a panel of 12 domain-expert judges, web-researched, ranked, and validated. No more "we brainstormed 3 ideas and picked the first one."

**Output:** a ranked solution + demo plan + full Marp pitch deck with market, competition, and business model.

---

```
/edth-agent
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

### 3. Clone and go

```bash
git clone https://github.com/vlordier/edth-prob-solution-deck.git
cd edth-prob-solution-deck
bash setup.sh   # auto-detects macOS/Linux/Windows — installs uv, syncs deps, pre-commit hooks
opencode        # or: claude
```

The agent is an Agent Skills-compatible skill — OpenCode and Claude Code both discover it automatically from `.opencode/skills/` and `.claude/skills/`. The first invocation auto-checks that `uv run python -c "import agent"` works.

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

All commands in OpenCode or Claude Code chat:

| Command | Does |
|---|---|
| `/edth-agent` | **Default** — resume or start the workflow |
| `/edth-agent dry-run` | 30s smoke test — full pipeline, zero interaction |
| `/edth-agent team` | Interview each member — skills, blind spots, roles |
| `/edth-agent sheet` | Generate a printable Mom Test question sheet |
| `/edth-agent panel viper` | Chat with a judge in character |
| `/edth-agent validate` | Check all artefacts for issues |
| `/edth-agent skip-to 5` | Jump to ranking with stub phases |

After each phase: "Approve? (y/edit/redo)".

## Output

```
artefacts/
├── 07_deck.html      ← Open in browser
├── 07_deck.pdf       ← If Marp CLI installed
├── 07_market.md      ← TAM/SAM/SOM
├── 07_competition.md ← Rivals, strengths, moat
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
uv sync --all-groups && uv run pytest   # 116 tests
uv run ruff check agent/ tests/         # Python lint (0 errors)
```

## Project

| What | Where |
|---|---|
| Agent driver | `.opencode/skills/edth-agent/SKILL.md` — prompt templates, commands, workflow |
| Python glue | `agent/` — parse, normalize, score, render, validate |
| Judges | `judges/` — 12 YAMLs |
| Templates | `templates/` — Marp slide skeletons |
| Setup | `setup.sh` — cross-platform auto-install (macOS/Linux/Windows) |
| Linting | `.pre-commit-config.yaml` — ruff + markdownlint on commit |
| Tests | `tests/` — 116 tests |

---

Fork it. Hack it. Profit.
