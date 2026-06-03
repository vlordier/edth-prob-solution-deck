# Hostile Q&A Simulation

You are convening the full 12-judge panel for an adversarial interrogation of the team's solution. This is NOT a review — this is a gauntlet. The team has their chosen solution, demo plan, and deck. Now they need to survive hostile questioning before facing real judges.

Read `artefacts/05_owner_pick.md`, `artefacts/06_demo_plan.md`, and `artefacts/07_deck.md`.

DISPATCH RULES:

For EACH of the 12 judges, dispatch a subagent with the prompt below. Run all 12 in parallel. Collect every question. Then present to the team.

SUBAGENT PROMPT (one per judge):

You are {judge_name} ({judge_short}), {judge_background}.
Your expertise: {judge_tags}. Your anti-priorities: {judge_anti_priorities}.

You are interrogating a hackathon team that will pitch to real judges in a few hours. Your job is to find the weakest part of their story and attack it. Be adversarial. Be specific. Do NOT be polite — polite questions don't prepare teams for real judges.

Read the solution, demo plan, and deck below.

RELEVANCE GATE:
If your expertise is not directly relevant to this solution, return empty.
"No relevant questions — my domain ({tags}) doesn't overlap with this solution."

If relevant, generate EXACTLY 3 questions. Format:

Q1: [One sentence setting the trap — quote their specific claim]
[One sentence attack — why it's wrong, optimistic, or unproven]
*Pressure angle: [what you're testing — TRL inflation? cost naivety? execution gap?]

Q2: [Same format]

Q3: [Same format]

Example questions (adapt to the solution):
- "On slide 4 you claim 'TRL 7 — field-tested.' Your research section lists no field trials, no partner unit, no test range. Walk me through a single deployment. Where was it tested, by whom, and what broke?"
- "Your cost-per-effect is $2,500. Your closest competitor charges $15,000. How? If your BOM adds up to $2,100, this is a hardware company selling at 15% margin. If it's $4,200, you lose money per unit. Show the BOM."
- "You say 'AI-powered detection.' What's your false-positive rate at 10km? At 15km? If you don't know, what's your training data size? Sensor type? Weather envelope? 'AI' is not an architecture."
- "Your demo plan has 12 minutes of pre-recorded video in a 3-minute pitch. Who's watching video instead of talking to you? The judges. Cut the video or triple the pitch time."
- "You're building an EW solution but nobody on the team has an SDR background. Three says 'learning fast.' What happens when your radio doesn't sync on demo day? Do you have a backup?"
- "Your business model is 'government contracts.' Typical timeline from first contact to first payment: 18 months. You have 3 months of runway. What's your bridge?"

SOLUTION + DECK:
{deck_text}

COLLECTING RESULTS:

After all 12 subagents return:
1. Compile ALL questions (relevant judges only).
2. Group by attack angle: TRL inflation, cost naivety, execution gap, demo fragility, team gap, market naivety.
3. Identify the 3 most dangerous questions — the ones that would kill the pitch if unaddressed.
4. For each of the top 3, write a 2-3 sentence recommended response the team can prepare.

PRESENT TO USER:

```
🧨 Hostile Q&A Simulation — {N} judges engaged

## Most Dangerous Questions

1. "{question}"
   Recommended: {response}

2. "{question}"  
   Recommended: {response}

3. "{question}"
   Recommended: {response}

## All Questions by Attack Angle

### TRL Inflation ({N} questions)
- ...

### Cost Naivety ({N} questions)
- ...

### Execution Gap ({N} questions)
- ...

### Demo Fragility ({N} questions)
- ...

### Team Gap ({N} questions)
- ...

### Market Naivety ({N} questions)
- ...

## Summary
- {M} of 12 judges found this relevant
- {T} total questions asked
- 3 most dangerous questions identified with prepared responses
```

Write the full output to `artefacts/hostile_qa.md`.

Tell the user: "Hostile Q&A saved to artefacts/hostile_qa.md. Prepare responses to the top 3 questions before demo day. The real judges will ask at least one of these."