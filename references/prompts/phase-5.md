# Phase 5 — Research & Rank (Three-Salvo Iterative)

## CONTEXT — Read This First

This research supports the **European Defense Tech Hub (EDTH)** community of
hackathons. EDTH's mission: "Deterring aggression through technological
superiority — supporting Ukraine in winning the war and ensuring Europe and its
allies remain strong and sovereign."

### What matters for this domain:

1. **Operational relevance > academic novelty.** A TRL 8 fielded system that
   works beats a TRL 3 paper with flashy results. Judges are defense
   practitioners, not academics.

2. **Ukraine has proven what works and what doesn't.** The war has accelerated
   drone warfare, EW/counter-EW, AI-assisted targeting, GPS-denied navigation,
   and decentralized C2 (Delta, Kropyva). Fiber-optic drones emerged to
   counter EW in <6 months. Computer-vision drones bypass jamming entirely.
   If a solution claims novelty, check whether Ukraine already fields it.

3. **EU defense priorities (2026):** The EU Readiness Roadmap 2030 defines
   four flagships — European Drone Defence, Eastern Flank Watch, European
   Air Shield, European Space Shield. Ukraine's top 3: air/missile defense,
   Ukrainian-made UAVs, extended-range munitions (~80% of security
   assistance). If a solution maps to one of these, it's strategically aligned.

   **EU procurement is NOT US procurement.** EDTH partners use EU pathways:
   EDIP (European Defence Industry Programme), EDF (European Defence Fund),
   SAFE loans, OCCAR, and direct national MoD contracts. Do NOT reference
   US pathways (FAR, SBIR/STTR, OTA) unless the solution is explicitly
   dual-use for the US market.

4. **Cost-exchange ratio is existential.** Shooting down a $35K Shahed with
   a $3.7M missile loses the war by attrition. Ukraine fields FPV interceptors
   at ~$2,500/unit. If your research finds cost data, always compute the ratio.

5. **EU production gap.** Europe produces <100K small drones/year vs Ukraine's
   7M+. European supply chains depend on Chinese semiconductors, American ITAR
   components, and single-source suppliers. Sovereignty matters.

6. **Field reality > lab reality.** Can a conscript operate it with 4 hours
   of training? Does it need Starlink? A generator? Two soldiers to carry it?
   If search results describe a lab prototype, flag the deployment gap.

7. **The team's blind spots.** Read `artefacts/team_profile.md` before
   researching. If the team has no ML experience, flag solutions that depend
   on ML. If all rated "C) Software-only" on hardware, flag hardware solutions.
   This constrains what's buildable in 48 hours.

### What the agent already knows (from prior phases):

- The chosen problem + sub-problem (from `artefacts/02_candidate_problem.md`
  and `artefacts/03_chosen_sub_problem.md`)
- The kill chain position + European defense context (appended to
  `artefacts/03_chosen_sub_problem.md`)
- The team's strengths, gaps, and blind spots (from
  `artefacts/team_profile.md`)
- The top 5 solution candidates from Phase 4's divergent ideation
  (`artefacts/04_solution_candidates.md`)

### What this phase adds:

Real-world evidence. Each solution gets validated or invalidated by what
actually exists — not by what the LLM trained on.

---

Run a structured, iterative research phase on the top 5 solution
candidates from Phase 4. Read `artefacts/04_solution_candidates.md` to get the
top 5 ideas by rating.

This is NOT a one-shot search. Run THREE salvos, with critique and
synthesis between each. Use Exa MCP (`web_search_exa` / `web_search_advanced_exa`)
for all web searches. If Exa is unavailable, use the LLM's built-in web search.

---

## SALVO 1 — Surface Research (broad, discovery-oriented)

For EACH of the top 5 ideas, generate 3-4 SEARCH QUERIES (not keywords — full
questions a defense analyst would type into a search engine):

Query types per idea:
  1. PRIOR ART + OPERATIONAL: "[idea] deployed military system 2024 2025 2026" AND
     "[idea] Ukraine field use battlefield"
  2. SOTA: "state of the art [idea domain] 2025 2026 research paper defense"
  3. COMPETITORS: "companies building [idea] defense startup funding contract"
  4. TRL / FIELDING: "[idea] technology readiness level fielded operational unit cost"
  5. COUNTERMEASURE: "[idea] countermeasure jamming spoofing defeat" — the adversary
     is adapting. Search for how this would be defeated.

Run all searches. For each idea, write a SALVO 1 BRIEF (4-5 sentences) covering:
  - What exists today (at least one named company, product, or program)
  - What published research or SOTA exists (at least one paper or approach)
  - Who is funded and deploying (investors, programs of record)
  - TRL estimate with justification ("this is TRL 6 because...")
  - Gaps — what you DIDN'T find that you expected to

---

## CRITIQUE — pause and evaluate Salvo 1

After all 5 ideas have Salvo 1 briefs, answer these questions for EACH idea:

  1. "What's the most surprising thing I found?"
  2. "What did I expect to find that I didn't?"
  3. "Which source is most questionable — and why?" (bias? dated? single-vendor?
     funded by a company with a stake in the answer?)
  4. "What angle is completely missing from my search?"
  5. "If I were the problem owner — a unit commander with 48 hours to decide —
     what would I want to know that isn't covered?"
  6. "Is there any evidence this has been tried in Ukraine and failed?"
  7. "What's the cost-exchange ratio if this exists? If not in my data, flag it."
  8. "Does this depend on a non-European supply chain? Chips? ITAR components?"

This critique is the SPEC for Salvo 2. Every unanswered question generates a
new query.

---

## SALVO 2 — Deep Research (gap-filling, adversarial)

Based on the CRITIQUE, generate 2-3 follow-up queries per idea targeting:

  - The gaps identified in the critique
  - The "missing angle" from question 4
  - Specific verification of questionable sources from question 3
  - Counter-evidence: search for "why [idea] WON'T work" or "[idea] failed
    deployment" — adversarial search

Run these searches. For each idea, append a SALVO 2 ADDENDUM (2-3 sentences):
  - What the new search confirmed or contradicted
  - Any new competitor, paper, or program discovered in this salvo
  - Updated TRL if Salvo 2 changed the assessment

---

## SYNTHESIS — cross-reference and identify contradictions

After both salvos, for each of the top 5 ideas, produce:

  1. **CONVERGENT FINDINGS** (both salvos agree): 1-2 bullet points
  2. **DIVERGENT FINDINGS** (salvos contradict): if any, what's the
     contradiction and which source is more credible?
  3. **MISSING DATA** (neither salvo found): what's still unknown?
  4. **DEPLOYMENT REALISM**: based on everything found — can this solution
     be operated by a conscript with 4 hours of training? Does it need
     Starlink, a generator, or a vehicle trailer? Is it European-made or
     dependent on non-European supply? Answer what you can, flag what you can't.
  5. **RISK-ADJUSTED TRL**: combine both salvos into a single TRL with
     confidence level ("TRL 6 ± 1, high confidence based on 4 confirming
     sources")

---

## HUMAN INTERACTION — present findings to the user

After synthesis, present to the user:

```
📊 Research Summary — Top 5 Candidates

Idea {N}: {one-line description}
  Salvo 1 findings: {2-3 key points}
  Salvo 2 findings: {2-3 key points}
  TRL: {risk-adjusted TRL}
  Sources: {count} search results across 2 salvos
  Key gap remaining: {what we still don't know}

{Repeat for all 5}

❓ Questions for you:
  1. Are any of these findings wrong based on what you know?
  2. What should I have searched for that I didn't?
  3. Is there a specific company, product, or paper you know
     about that didn't appear in my searches?
  4. Which of these 5 ideas do you want me to prioritize
     for deeper research?
```

Capture the user's answers. If they mention specific companies, papers, or
angles you missed, run ONE additional search per mention (Salvo 3, targeted).
If they identify a wrong finding, correct it in place.

---

## FINAL COMPILATION — build ranked solutions

After the user interaction, build `agent.ranking.RankedSolution` objects with
the combined research from all salvos. Each solution must include:

  - The full research summary (merging Salvo 1 + 2 + user corrections)
  - At least one specific URL, company, or citation (from search)
  - The risk-adjusted TRL with confidence
  - Any user-provided information or corrections noted as such

### Panel re-scoring:
Each judge re-scores the top 5 on the 4 rubric axes using a 1-5 scale.
If panel_mode=expanded: score each judge separately (subagent per judge).
If condensed: score all judges in one response.

Aggregate via `agent.aggregation.weighted_borda()` using judge scoring_biases
as weights. Record spread (max - min panel score) per solution.

### Owner validation:
If owner_mode=real: present ranking to user, get their pick. They can override.
If owner_mode=sim: the persona picks from the top 2. Record dissents.

Write via `agent.ranking.write_ranked_solutions()`. Write owner pick via
`agent.ranking.write_owner_pick()`.
