## Panel system (12 tough judges)

The agent maintains a panel of 5 judge personas that review every artefact. Library: `judges/*.yaml`.

### Panel lifecycle

1. After Phase 2, call `/edth-agent panel generate` to auto-pick 5 judges (Jaccard similarity on tags + hard rules).
2. User can `panel add / remove / replace` before locking.
3. Panel recorded in `state.json` under `panel.auto_selected`.
4. `panel_mode: expanded` = one subagent per judge (higher quality, recommended). `panel_mode: condensed` = all judges in one LLM call (faster). Default: expanded for Phases 1, 5, 6, 7 (high-stakes); condensed for Phases 3, 4.
5. **Relevance gate:** Every judge subagent first checks: "Is my expertise relevant to this topic?" If no (Jaccard < 0.2 on tags vs cluster themes), they return "No relevant questions — my expertise does not directly apply." Judges who stay quiet do NOT ask generic questions.

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

## Judge Management

Custom judges persist as YAML files in `judges/` and are auto-discovered
by `load_judge_library()`. All mutations are backed up to `judges/backups/`.

### Add a Judge (`/edth-agent judge add`)

Execute this prompt verbatim:

```
You are helping a user create a new custom judge persona. The judge
will be saved as `judges/<short>.yaml` and auto-discovered in all
future sessions.

Ask questions one at a time until ALL required fields in the judge
schema (`agent.judge_schema.REQUIRED_FIELDS`) are filled:

1. SHORT: "Short identifier? Lowercase, hyphens OK. Becomes
   judges/<short>.yaml. Example: drone-operator."

2. FULL NAME: "Full display name? Example: Maj. Elena Vasquez"

3. TAGS: "Domain expertise? Pick from standard tags + custom.
   Standard: autonomy, c-uas, c2, decision_support, ew, signal_proc,
   swarm, uuv, usv, radar, hardware, software, ui_ux, detection,
   communication, navigation, multi_domain, countermeasure.
   Include 'all' if cross-domain. Example: ['c-uas','swarm','autonomy']"

4. BACKGROUND: "One paragraph: who are they? Units served in?
   Conflicts? Systems built or operated? What makes them qualified?"

5. PRIORITIES (3-6): "What do they prioritize? Example:
   ['operational relevance', 'survivability', 'simplicity']"

6. ANTI-PRIORITIES (3-6): "What do they hate? Pet peeves, buzzwords.
   Example: ['vendor lock-in', 'AI for AI's sake']"

7. DECISION STYLE: "One sentence. Example: 'decisive; 30-second
   answer or admit you don't know'"

8. LANGUAGE PATTERNS (3-6): "Phrases they actually say. Capture their
   voice. Example: ['on the flight line', 'what kills this']"

9. SCORING BIASES: "How much do they over/under-weight each rubric
   axis? Dict with all 4 axes. Example:
   {impact: 0.10, innovation: -0.05, execution: 0.10, presentation: 0.00}.
   Biases add to defaults (0.30/0.25/0.25/0.20)."

10. KNOWLEDGE GAPS (2-4): "What do they NOT know? Example: ['consumer
    tech', 'business modeling']"

11. HARD QUESTIONS (3-6): "Questions they always ask. Get adapted per
    phase. Example: ['What's the kill chain?', 'What's the 3am
    maintenance story?']"

Validate via `agent.judge_schema.validate_judge(data)`.
Call `agent.judges.add_judge(judges_dir, data)`.
Print: "✅ Judge {short} added. Available for auto-selection."
```

### Edit a Judge (`/edth-agent judge edit <short>`)

Load `judges/{short}.yaml`. Present current profile. Ask what to change.
Do NOT let them change the `short` field. Call
`agent.judges.update_judge(judges_dir, short, data)`.
Backup auto-created at `judges/backups/{short}.yaml.bak.<timestamp>`.

### Remove a Judge (`/edth-agent judge remove <short>`)

Call `agent.judges.remove_judge(judges_dir, short)`. File moved to
`judges/backups/{short}.yaml.removed.<timestamp>` — safe-delete.

### Reset a Judge (`/edth-agent judge reset <short>`)

Restore the original shipped version: `git checkout HEAD -- judges/{short}.yaml`.
If the file was never in git (custom judge), error.

### List Judges (`/edth-agent judge list`)

Call `agent.judges.list_judges_full(judges_dir)`. Print table:
short, name, tags, custom flag, background excerpt.
