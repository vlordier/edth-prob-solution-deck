# EDTH Hackathon Agent

A reusable agent that walks through the full lifecycle of a hackathon project — from a CSV of problem statements to a problem/solution pitch deck — using a 9-phase workflow reviewed by a panel of 12 tough-judge personas.

> Built as an OpenCode skill backed by thin Python glue.
> [Design spec](docs/superpowers/specs/2026-06-02-edth-agent-design.md) | [Implementation plan](docs/superpowers/plans/2026-06-02-edth-agent.md)

## Quick Start

### 1. Install
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

### 2. Place your problem CSV
Default expects `input/sample-problems.csv` (8 synthetic examples). Replace with your real CSV and update the path via `hackathons/edth.yaml` or `artefacts/00_context.yaml`. Real CSVs in `input/` are gitignored.

### 3. Run the agent
From OpenCode chat:
```
/edth-agent status      # show current phase
/edth-agent run         # next pending phase
/edth-agent panel       # show current judge panel
/edth-agent panel viper # chat with Maj. Viper
/edth-agent render      # re-render deck
/edth-agent help        # all commands
```

### 4. View the deck
After Phase 7: open `artefacts/07_deck.html`

## Project Structure
```
SKILL.md              # OpenCode skill
agent/                # Python glue
judges/               # 12 tough judges
personas/             # Problem-owner personas
templates/            # Marp slide templates
examples/sample-run/  # Pre-generated sample
tests/                # pytest
```

## Rendering (3-tier fallback)
1. Marp CLI (preferred): `npm i -g @marp-team/marp-cli`
2. python-pptx (auto-installed)
3. Self-contained HTML (always works)

## Development
```
pip install -e ".[dev]"
pytest
```
