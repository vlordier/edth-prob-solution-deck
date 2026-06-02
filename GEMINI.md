---
name: edth-agent
description: >
  Turn a CSV of defense-tech problem statements into a winning pitch deck —
  problem selection, Mom Test elicitation, 12-judge validation, solution ideation,
  ranking, and deck generation. 9-phase workflow. Discovered from `.opencode/skills/edth-agent/SKILL.md`.
disable-model-invocation: true
---

# EDTH Hackathon Agent

This project contains an Agent Skills-compatible skill at `.opencode/skills/edth-agent/SKILL.md`
(also at `.claude/skills/edth-agent/SKILL.md` and `.agents/skills/edth-agent/SKILL.md`).

OpenCode, Claude Code, and Gemini CLI all auto-discover it when you open this repo.

## Quick start

```bash
git clone https://github.com/vlordier/edth-prob-solution-deck.git
cd edth-prob-solution-deck
bash setup.sh   # cross-platform: macOS / Linux / Windows-WSL
opencode        # or: claude, gemini
```

Then type `/edth-agent`.

## Project overview

- **Skill driver**: `.opencode/skills/edth-agent/SKILL.md` — workflow spine, behavior rules, commands
- **Prompt templates**: `references/prompts/phase-*.md` — loaded on demand per phase
- **Judge profiles**: `references/judges.md` — 12 judge personas + CRUD commands
- **Python glue**: `agent/` — parse, normalize, score, render, validate, doctor
- **Judge YAMLs**: `judges/` — 12 shipped + custom (backed up to `judges/backups/`)
- **MCP config**: `.mcp.json` + `opencode.json` — Exa + Context7 auto-loaded
- **Tests**: `tests/` — 203 tests, 0 ruff errors
