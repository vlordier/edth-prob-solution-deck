You are decomposing the chosen solution into concrete implementation
tasks and assigning them to specific team members.

Read `artefacts/team_profile.md` and `artefacts/05_owner_pick.md`.

Also read `artefacts/team_profile.md` `## Team Equipment` section.
Equipment availability is a HARD constraint on what tasks are possible.

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

STEP 2.5 — Equipment availability check (per task):
For each task, check if it requires specific hardware from the equipment
inventory. Flag constraints:
  - If the task needs hardware in `### Available` → note "✅ {hardware} available."
  - If the task needs hardware in `### Accessible` → note "⚠️ Must source {hardware} first. Assign this person to pick it up."
  - If the task needs hardware in `### Critical Gaps` → mark as GAP with
    fit_reasoning: "Hardware blocker: team needs {hardware} but none available.
    Either scope this task out or find an alternative approach that doesn't
    require {hardware}."
  - If the task is pure software → note "Laptops sufficient."

STEP 3 — Flag critical gaps:
Two types of gaps:
  a) SKILL gaps: task requires a skill nobody has. Flag as GAP.
  b) EQUIPMENT gaps: task requires hardware in the Critical Gaps list.
     Flag as GAP with higher severity — equipment gaps are harder to
     overcome than skill gaps in a 48h sprint.

STEP 4 — Suggest build order:
Order the tasks so that dependencies are respected (ML model training
before deployment, backend API before frontend integration). Also:
  - If a task depends on `### Accessible` hardware, schedule it AFTER
    the hardware is sourced (add a "Source {hardware}" task at position 1).
  - If multiple tasks compete for the same hardware (e.g. one Jetson,
    two people need it), serialize them — don't parallelize.

Output as a list of task IDs in recommended order.

STEP 5 — Write the plan:
Build `agent.demo_tasks.DemoTask` objects for each task, then a
`agent.demo_tasks.DemoTaskPlan` and write via
`agent.demo_tasks.write_demo_tasks(artefacts_dir, plan)`.
Output goes to `artefacts/demo_tasks.md`.

Tell the user: "Task assignments saved to `artefacts/demo_tasks.md`.
Each team member can see exactly what they own, what equipment they
need, and how long it should take."
