You are researching and ranking the top 5 solution candidates from Phase 4.
Read `artefacts/04_solution_candidates.md`. Extract the top 5 ideas by rating.

Step 1 — Web research (per idea, 1-2 searches each):
For each idea, search for:
- Prior art: has this been built before? who built it? when?
- SOTA: what's the current best approach? published paper?
- Competitors: funded companies? open-source projects?
- TRL: what technology readiness level is typical for this approach?
- Regulatory: any arms-control, ITAR, or IHL constraints?

Write a 3-5 sentence research summary per idea. Include at least one specific
URL, company name, or paper citation per summary. If no results, say
"No public results found for [specific query]."

Step 2 — Panel re-scoring:
Each judge re-scores the top 5 on the 4 rubric axes using a 1-5 scale.
If panel_mode=expanded: score each judge separately. If condensed: score all
judges in one response.

Aggregate via `agent.aggregation.weighted_borda()` using judge scoring_biases
as weights. Record spread (max - min panel score) per solution.

Step 3 — Owner validation:
If owner_mode=real: present ranking to user, get their pick. They can override.
If owner_mode=sim: the persona picks from the top 2. Record dissents.

Build `agent.ranking.RankedSolution` objects. Write via
`agent.ranking.write_ranked_solutions()`. Write owner pick via
`agent.ranking.write_owner_pick()`.
