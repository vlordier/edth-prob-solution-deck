You are generating solution ideas. Read `artefacts/03_chosen_sub_problem.md`
and the `## Competitive Landscape` section from `artefacts/02_candidate_problem.md`.

**Knock-off question:** "What exists? What's the gap? What can we build in 12 hours
that's better, cheaper, or different enough to matter?"

Start by killing the first 5 obvious ideas. Write them. Then cross them out.
The first ideas are always the ones everyone else thinks of. What's next?

Generate at least 20 distinct ideas. Use these 8 techniques. No fluff — one line
per idea.

Technique 1 — SCAMPER (3): Substitute / Combine / Adapt / Modify / Eliminate / Reverse
Technique 2 — What would X do? (3): Palantir, Anduril, a 16-year-old with an RPi, a Ukrainian drone op
Technique 3 — 10X (3): Unlimited budget/data/time. Moonshot.
Technique 4 — Constraint removal (3): No latency. Unlimited compute. Perfect data.
Technique 5 — Anti-solution (3): The worst possible idea. Reveals what to avoid.
Technique 6 — Analogy (3): Video game. Cooking recipe. Dating app. Logistics problem.
Technique 7 — Wildcard (2+): Free-form.
Technique 8 — Gap exploit (2+): Target ONLY the gap identified in Competitive Landscape.

Output: I-001: [one line]. No essays. Dedupe via `agent.ideation.dedupe_ideas(ideas, 0.7)`.

## Innovation Competitive Scan (after dedup, before panel)

For each unique idea (~8-10), run 1-2 Exa web searches. For each, answer with
military directness:
  1. "Exists?" (yes/partially/no)
  2. "Who?" (name, year if yes)
  3. "Difference?" (one line — what's our edge or why bother)
  4. "Why not?" (if no — too hard / nobody thought of it / no market)

Panel rates 1-5 informed by the competitive signal. Ideas rated 1-2 must have
an explanation. No "interesting" — tell me WHY.

Collect in `judge_rejections`. Sort descending. Top 5 + "judges hated this."
