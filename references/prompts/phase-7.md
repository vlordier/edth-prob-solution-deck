Produce the final pitch deck. Read all prior artefacts.

**Knock-off question:** "What's the minimum the judge needs to understand why this
matters, how it works, and why it's different?" Cut everything that doesn't
answer that. 5-7 slides is fine. 9 slides with filler is worse than 5 with signal.

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
defensibility. Must include at least one specific EUROPEAN acquisition pathway
(EDIP — European Defence Industry Programme, EDF — European Defence Fund,
SAFE loans, OCCAR, national MoD direct procurement). For dual-use solutions,
also cover civilian market entry. Do NOT reference US procurement (FAR, SBIR/STTR,
OTA) unless the solution is explicitly dual-use for the US market.

Step 4 — Generate deck slides:
For each slide, write Marp-flavored markdown (front-matter at top, `---` as
slide separator, `<!-- _class: lead -->` for title slides).

Slide order (signal-first):
1. Cover: name + team + date
2. Problem: battlefield pain. One-sentence pitch from Phase 5.5. Why it matters.
3. Solution: what it does. Kill chain position. One-liner differentiator.
4. Competition: what exists today. Why ours is different. TRL comparison table.
5. Deployment path: how this reaches the field. Acquisition pathway + timeline.
6. Business model (if dual-use). Market only if commercially relevant. Skip otherwise.
7. Demo: what you'll see + key metric.
8. Thank you.

Save to `artefacts/07_deck.md`. Render via `agent.deck.render_deck()`.
Panel: each judge flags the slide they'd push back on hardest. Record in audit.
