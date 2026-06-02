# Competitive Landscape Pass (runs after Phase 2)

You are mapping the competitive landscape for the chosen problem.
Read `artefacts/02_candidate_problem.md` — specifically the candidate
the user selected (recorded in state.json decisions.chosen_problem_id).

This pass runs BEFORE sub-problem decomposition. The goal is to
understand who else is solving this problem, how, and at what cost —
so the team doesn't waste 48 hours rebuilding something that exists.

Use Exa MCP for all web searches. If unavailable, use built-in tools.

---

## SEARCH — 4 queries per problem

Generate 4 search queries:

1. "[problem] deployed system fielded 2024 2025 2026"
2. "[problem] startup company defense funding contract product"
3. "[problem] open source project github"
4. "[problem] cost per unit price"

Run searches. For each result, capture: name, URL if available, 1-line
description, type (company / government program / open source / research),
estimated TRL if discernible, estimated unit cost if available.

---

## CLASSIFY — group competitors

Organize findings into:

### Funded startups / scale-ups
Companies with VC, program of record, or customer contracts.
List: name, funding (if known), product name, one-line differentiation.

### Government / defense programs
Named programs by country (US, UK, EU, Ukraine, etc.).
List: program name, country, status (fielded / in development / cancelled).

### Open source projects
GitHub repos, community projects, academic toolkits.
List: repo, stars (approx), last commit date, license.

### Prior art / adjacent solutions
Things that are close but not exactly this problem.
List: what it is, why it's NOT your solution, what it DOES solve.

---

## ASSESS — your competitive position

Answer in 2-3 sentences each:

1. "How crowded is this space?" (lots of companies? all government?
   one dominant player? empty?)
2. "What's the obvious thing that everyone does — and what's still
   unsolved?" (the gap where innovation lives)
3. "If the market is crowded, what's the wedge?" (why should anyone
   care about a 48h hackathon project?)
4. "What's the reference price?" (if something similar is sold,
   how much does it cost? If nothing exists, what's the closest?)

---

## OUTPUT — append to `02_candidate_problem.md`

Append a new section `## Competitive Landscape` to the BOTTOM of
`artefacts/02_candidate_problem.md`. Do NOT overwrite — append.

Format:

## Competitive Landscape

### Competitors
[Table: name | type | TRL | cost | one-line]

### Open Source
[Table: repo | stars | license | one-line]

### Positioning
- **Crowded?** [answer]
- **Gap:** [answer]
- **Wedge:** [answer]
- **Reference price:** [answer]
