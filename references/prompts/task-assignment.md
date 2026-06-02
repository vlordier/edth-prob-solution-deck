You are decomposing the chosen solution into concrete implementation
tasks and assigning them to specific team members.

Read `artefacts/team_profile.md` and `artefacts/05_owner_pick.md`.

STEP 1 — Decompose the solution into 5-8 tasks:
Each task must be:
  - Concrete: "Build the React dashboard with hardcoded feed data" not
    "Work on the frontend."
  - Independent enough that one person can own it.
  - Track-level: "Train the model on synthetic threat data" not
    "Research ML approaches."
  - Include a rough time estimate (2h, 4h, 8h, etc.).

STEP 2 — For each task, assign to the best-fit team member:
Read team_profile.md and match each task to the person whose skills,
experience, and quick-fire answers best fit:
  - If Alice said "React, D3" and "I love presenting," she gets the
    dashboard UI and any demo-facing work.
  - If Bob said "PyTorch, ONNX, edge deployment" he gets the ML pipeline.
  - If someone said "C) I'm learning" on a skill the task needs, flag it.
  - PREVENT double-booking: if Bob is already assigned 16h of tasks,
    stop adding to his plate. Flag the overflow.

For each assignment, write 1 sentence explaining WHY this person fits.
Quote their team_profile self-intro or quick-fire answer as evidence.

STEP 3 — Flag critical gaps:
If a task requires a skill NOBODY on the team has (e.g. hardware
deployment, and everyone answered "C) Software-only" on the hardware
question), mark it as a GAP with fit_reasoning explaining why nobody
fits. These become the `critical_gaps` in the plan.

STEP 4 — Suggest build order:
Order the tasks so that dependencies are respected (ML model training
before deployment, backend API before frontend integration). Output
as a list of task IDs in recommended order.

STEP 5 — Write the plan:
Build `agent.demo_tasks.DemoTask` objects for each task, then a
`agent.demo_tasks.DemoTaskPlan` and write via
`agent.demo_tasks.write_demo_tasks(artefacts_dir, plan)`.
Output goes to `artefacts/demo_tasks.md`.

Tell the user: "Task assignments saved to `artefacts/demo_tasks.md`.
Each team member can see exactly what they own and how long it should take."
