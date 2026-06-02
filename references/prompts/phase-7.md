You are producing the final pitch deck. You have all prior artefacts.
Read `artefacts/02_candidate_problem.md`, `artefacts/03_chosen_sub_problem.md`,
`artefacts/05_owner_pick.md`, `artefacts/06_demo_plan.md`.

Step 1 — Market research (write 07_market.md):
Run 3-5 web searches on the solution's domain. Answer:
- TAM/SAM/SOM with dollar figures or unit estimates. Be specific.
  Example: "TAM: $12B global C4ISR market. SAM: $3B tactical C2. SOM: $150M."
- Growth trends and key drivers. Cite at least one source.
- 2-3 buyer personas with 1-line descriptions.

Step 2 — Competition analysis (write 07_competition.md):
Run 3-5 web searches. Produce at least 3 direct/adjacent competitors with:
name, strength, weakness, our edge. Table format.
Moat assessment: 2-3 defensible advantages (IP, data, network effects, regulatory).

Step 3 — Business model (write 07_business_model.md):
Revenue model, pricing strategy, go-to-market (specific phases with timelines),
defensibility. Must include at least one specific acquisition pathway
(OTA, SBIR/STTR, CSO, traditional FAR).

Step 4 — Generate deck slides:
For each slide, write Marp-flavored markdown (front-matter at top, `---` as
slide separator, `<!-- _class: lead -->` for title slides).

Slide order (MilTech priority):
1. Cover: project name + hackathon + team + date
2. Problem: battlefield pain + why it matters + one-sentence pitch from Phase 5.5
3. Solution: one-liner + how it works + kill chain position
4. Competition / deployed capability: what exists today? why is yours different? TRL comparison (table)
5. Deployment path: how does this reach the battlefield? acquisition pathway + timeline
6. Business model: revenue, pricing, GTM (if dual-use)
7. Market: TAM/SAM/SOM + trends (only if commercially relevant — otherwise skip)
8. Demo: what you'll see + key metrics
9. Thank you

Save to `artefacts/07_deck.md`. Then render via `agent.deck.render_deck()` which
auto-detects Marp CLI, python-pptx, or HTML fallback.

Panel review: each judge flags the slide they'd push back on hardest.
Record in audit.
