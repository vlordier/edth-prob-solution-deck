You are onboarding a hackathon team. Capture the context that will drive
every subsequent phase. Load the default context via
`agent.context.default_context()` and `agent.state.load_state()`.

Present these questions to the user, one group at a time:

1. HACKATHON:
   - Hackathon name? (default: EDTH Munich 2025)
   - Theme / focus? (default: Defense tech / dual-use)
   - Tracks your team is competing in? (default: C-UAS, Autonomy, EW, UUV, USV)
   - Judge rubric weights? (default: impact 0.30, innovation 0.25, execution 0.25, presentation 0.20)

2. TEAM:
   - How many people?
   - Collective strengths? (e.g. ML/CV, frontend, signal processing)
   - Collective weaknesses / gaps? (e.g. hardware, maritime domain)

3. CONSTRAINTS:
   - Time budget in hours? (default: 48)
   - Deliverable scope? (default: deck + thin demo)

4. AGENT CONFIG:
   - Owner mode: real (you answer) or sim (persona role-plays)?
   - Persona to use? (default: edth-judge)
   - Panel mode: expanded (separate LLM per judge, higher quality) or condensed (single LLM, faster)?
   - Aggregation mode: borda (weighted ranking) or approval (top-K voting)?

After capturing answers, merge them into the default context via
`agent.context.save_context(artefacts_dir, ctx)`.
If the user is in a hurry, accept all defaults with one confirmation.
