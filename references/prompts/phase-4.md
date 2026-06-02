You are generating solution ideas. Read the chosen sub-problem from
`artefacts/03_chosen_sub_problem.md`.

Also read `artefacts/02_candidate_problem.md` `## Competitive Landscape`
section — you know who else is in this space. Use that knowledge to
generate ideas that exploit the gaps, not ideas that compete head-on
with fielded systems.

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

TECHNIQUE 8 — Gap exploit (2+ ideas):
  From the Competitive Landscape, what's the gap identified?
  ("What's still unsolved?") Generate ideas that EXCLUSIVELY target
  that gap. These are your highest-value ideas — the ones that don't
  compete with fielded systems.

Output format: I-001: [One-line idea description]

Then run `agent.ideation.dedupe_ideas(ideas, threshold=0.7)` to remove near-dupes.

---

## Innovation Competitive Scan (runs after dedup, before panel rating)

For each UNIQUE idea after dedup (the ~8-10 that survive), run 1-2
quick web searches (Exa MCP or built-in):

  "[idea one-liner] existing solution deployed company 2024 2025"

Goal: answer for each idea:
  1. "Does something like this already exist?" (yes / partially / no)
  2. "If yes — who built it? When? What's different about our version?"
  3. "If partially — what's the gap between what exists and our idea?"
  4. "If no — why not? (Too hard? Nobody thought of it? No market?)"

Output: For each idea, add a 1-2 line `competitive_signal` to its
`Idea` object (use the `judge_rejections` field as a carrier, or
add a note to the idea's description).

THE PANEL MUST SEE THIS before they rate. Each judge reads the idea
AND its competitive signal. They use this to inform their 1-5 rating.

Panel review: each judge rates every unique idea 1-5 with one-line reasoning.
Ideas rated 1-2 require an explanation. Collect rejections in
`judge_rejections`.

Build `agent.ideation.Idea` objects with rating, panel_ratings, and
judge_rejections. Sort by rating descending. Top 5 + "judges hated this" section.
