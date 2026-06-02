You are planning the live demo for the chosen solution. Read the chosen
solution from `artefacts/05_owner_pick.md`.

Step 1 — Thin demo definition:
Define the smallest thing we can build that demonstrates the "wow" moment.
What's the input? What does the operator see? What's the output? What's the
one moment that makes the room lean forward? Write 2-3 sentences.

Step 2 — 3-minute demo script:
Write a time-cued script with these beats:
- 0:00–0:20 — Cold open: one sentence that hooks the room. (Example: "3 seconds
  for a decision lives matter. This is what 3 seconds looks like.")
- 0:20–0:40 — Problem setup: what's the pain, who feels it, why now.
- 0:40–2:00 — Live demo: walk through the workflow. "Here's the raw feed.
  Watch what happens in 3 seconds." Narrate what's happening on screen.
- 2:00–2:40 — How it works under the hood (1-2 slides max).
- 2:40–3:00 — Closing: what's next, who we need, call to action.

Use the format: `[0:00] Cold open line.` Each beat is one timestamped line.
Minimum 10 beats.

Step 3 — 30-second elevator pitch:
One paragraph, no jargon, that a non-technical person can repeat.
Example: "Commanders in multi-domain operations drown in data. Our dashboard
processes feeds from air, land, and naval assets and shows the critical threat
in under 3 seconds — with an AI-recommended course of action. Think of it as
Waze for the battlefield."

Step 4 — Q&A prep:
Panel review: each judge gives 1-3 hard questions they'd ask during the live demo.
Then generate concise answers (2-3 sentences each).
Minimum 8 Q&A pairs.

Step 5 — Risk register:
Identify 5-8 things that could go wrong during the demo or project.
For each: what, likelihood (high/medium/low), impact (high/medium/low), mitigation.
Include at least: "demo crashes on stage", "judge doesn't know the domain".

IMPORTANT — Pre-mortem (must include this as the last entry):
"It's Sunday at 3pm. The judges just announced the winners. You didn't win.
Why not? Be brutally honest." Write this as a risk entry titled "Pre-mortem:
why we lost." This is the most important entry in the register.

IMPORTANT — Adversary countermeasure (must include this as an entry):
Load the `red-team-adversary` judge's YAML. Ask: "If I were the adversary, how
would I defeat this solution in 6 months?" Write this as a risk entry titled
"Adversary countermeasure: how the enemy defeats this."

Build `agent.demo_plan.DemoPlan` and write via `agent.demo_plan.write_demo_plan()`.
