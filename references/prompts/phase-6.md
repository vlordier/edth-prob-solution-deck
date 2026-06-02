You are planning a 3-minute live demo. Read `artefacts/05_owner_pick.md`.

**Knock-off question:** "What's the ONE thing the room leans forward for?"

No brand exercise. No polished script reading. The demo is about signal.
Everything else is noise.

Step 1 — What the operator sees (2-3 lines, max):
  Input? Output? The moment that makes them lean forward? What's the
  "before" and "after" on the screen? No jargon.

Step 2 — 3-minute script (minimum 10 beats, timestamped):
  0:00 — Cold open. One sentence. Kill the hook.
  0:20 — Problem. Who feels this? What's the cost?
  0:40 — Demo. Walk through the workflow. "Here's the raw feed. Watch."
  2:00 — How it works. 30 seconds. 1 slide max. The operator doesn't
         care about your architecture — they care about what it does.
  2:30 — Kill chain position. Where does this fit in F2T2EA?
  2:45 — Close. What's next. What you need.
  Format: `[M:SS] Text.`

Step 3 — Elevator pitch (one paragraph, ≤80 words). Colonel can repeat it.

Step 4 — Q&A prep (minimum 8 pairs). Each judge gives 1-3 hard questions.
  Answer each in 2-3 sentences. No hedging.

Step 5 — Risk register (5-8 entries). Format: risk | likelihood | impact | mitigation.
  Must include:
  - "Demo crashes on stage"
  - "Judge doesn't know the domain"
  - "Pre-mortem: It's Sunday 3pm. You lost. Why?"
  - "Adversary countermeasure: how Volkov defeats this in 6 months"

Build `agent.demo_plan.DemoPlan`. Write via `agent.demo_plan.write_demo_plan()`.
