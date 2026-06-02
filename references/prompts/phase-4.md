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
