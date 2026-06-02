You are clustering and scoring problems from a parsed CSV. Input is available at
`artefacts/01_problems.json` (produced by `agent.parse_csv`).

Step 1 — Read and cluster:
Read all problems. Group them into 4–8 clusters by theme. Each problem goes into
exactly one cluster. Name each cluster with a 3-5 word descriptive label. Assign
at least 2 `themes[]` per cluster from this vocabulary: autonomy, c-uas, c2,
decision_support, ew, signal_proc, swarm, uuv, usv, radar, hardware, software,
ui_ux, detection, communication, navigation, multi_domain, countermeasure.

Step 2 — Score each cluster:
Score each cluster on a 1-5 integer scale (5=best) on these axes:
- impact: how much does solving this change outcomes?
- innovation: how novel vs. existing solutions?
- execution: how buildable in 48 hours?
- presentation: how demo-able is this?

IMPORTANT — Team fit adjustment: If `artefacts/team_profile.md` exists,
read it. For each cluster, adjust the execution score based on team skills:
  - If the cluster touches hardware and the team's hardware scores are all
    "C) Software-only" → dock execution by 1-2 points.
  - If the cluster involves ML and no team member rated above "C) Novice"
    on ML maturity → dock execution by 1-2 points.
  - If the cluster is purely software and the team has strong software
    skills (multiple "A" answers) → boost execution by 1 point (cap at 5).
  - If the cluster touches a defense domain nobody has experience in
    (all "C) Brand new") → dock innovation by 1 (novel to them ≠ novel).
  - Document any adjustments in the cluster notes.

IMPORTANT — Equipment constraints: If `artefacts/team_profile.md` has a
`## Team Equipment` section, read it. Equipment is a hard GO/NO-GO gate:
  - If the cluster requires SDR/spectrum hardware and the team's equipment
    gaps list "No SDR hardware" → dock execution by 3 points AND add a
    warning flag: "⚠️ EQUIPMENT BLOCKER: No SDR hardware. This problem
    cannot be meaningfully solved without spectrum access."
  - If the cluster requires GPU/accelerator (ML training, video processing)
    and the gap list flags no GPU access → dock execution by 2 and flag:
    "⚠️ EQUIPMENT RISK: No GPU beyond laptops. Large model training or
    video processing at scale may be infeasible."
  - If the cluster requires physical robotics/hardware and the gap list
    flags no hardware → dock execution by 3 and flag as EQUIPMENT BLOCKER.
  - If the equipment section lists specific hardware that DIRECTLY enables
    a cluster (e.g., "Raspberry Pi 5 × 2" for an edge-computing problem)
    → boost execution by 1 and note: "✅ Equipment match: {hardware}."
  - Equipment blockers are FIXED constraints — they cannot be overcome
    with team skill. Flag them more aggressively than skill gaps.

Output scores as a dict: {impact: X, innovation: Y, execution: Z, presentation: W}

Step 3 — Market signal (mandatory, must include real data):
For each cluster, run 1-2 web searches to answer: "Are there funded companies solving this?
What's the competitive landscape?" Summarize in 1-2 sentences with at least one specific
company name or product name. If you cannot find results, say "No commercial signal found
for [topic]." Do NOT make up company names.

Step 4 — Panel review:
If a panel is locked in state.json, have each judge rank their top 3 clusters.
Aggregate via `agent.aggregation.borda_count()`. If no panel yet, use default
rubric scoring.

Output format (write to `artefacts/01_triage.md`):

# Triage Report

## Cluster 1: [Name]
**Themes:** theme1, theme2
**Problems:** N
**Axis scores:** impact: X, innovation: Y, execution: Z, presentation: W
**Weighted total:** N.NN
**Market signal:** [1-2 sentences with company names]
**Problem IDs:** P-001, P-002, ...

[Repeat for all clusters]

## Panel summary
[Panel rankings or "Panel not yet formed."]
