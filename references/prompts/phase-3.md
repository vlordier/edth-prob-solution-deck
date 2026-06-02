You are decomposing a chosen problem into tractable sub-problems. Read the
chosen problem from `artefacts/02_candidate_problem.md` (the one the user selected,
recorded in state.json decisions.chosen_problem_id).

Step 1 — Decompose:
Break the problem into 5-8 sub-problems. Each sub-problem must be a specific,
self-contained slice that could be solved independently. Use this structure:
- SP-1: [Title] — [1-2 sentence description]
- SP-2: [Title] — [1-2 sentence description]
  ...

Do NOT produce overlapping sub-problems. Do NOT produce sub-problems that
are "the whole problem but smaller." Each must be distinct.

Step 2 — ROI score each sub-problem:
Score each sub-problem on a 1-5 scale:
- impact: how much does solving this sub-problem matter to the larger goal?
- time_fit: can this be built in 48 hours?
- demo_ability: can this make a compelling demo?
- dependency_risk: how many external dependencies? (1=no deps, 5=blocked without others)

The ROI score auto-computes via `agent.sub_problem.SubProblem.roi_score()` which
inverts dependency_risk (high score = low risk) and applies weights 0.30/0.30/0.25/0.15.

Output: Build `agent.sub_problem.SubProblem` objects. Score using the format above.
