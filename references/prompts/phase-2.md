Generate structured owner questions for the top 3 problem clusters
from Phase 1, following The Mom Test methodology (Rob Fitzpatrick).

Read `artefacts/01_triage.md`. Get the clusters and their problem IDs.

These problem owners are soldiers, pilots, drone operators, EW
specialists, tank commanders — not procurement officers. Adapt your language.

CRITICAL RULES — The Mom Test (operator edition):
- NEVER ask "Would you use X?" or "Do you think X would help?" (leading)
- NEVER ask hypotheticals or scales: "On a scale of 1-10..." (abstract)
- ALWAYS ask about specific missions/sorties: "Last time this failed..."
- ALWAYS ask about current kit: "What do you use today? What's wrong with it?"
- ALWAYS look for concrete cost: sorties scrubbed, birds lost, time-to-kill,
  equipment damaged, people put at risk, territory lost.
- ALWAYS probe for failed attempts: "What did you try that didn't work?"
- If they say "it's a big problem" — "How many times last week? Which mission?"
- If they say "we need this" — "What would have happened differently last
  Tuesday if you'd had it?"

Step 1 — Owner questions (3 per cluster, minimum 9 total):

CLUSTER QUESTIONS (3 per cluster):
  Q-0XX: "Walk me through the last mission where [cluster topic] was a factor.
         What happened, step by step — from mission brief to debrief?"
         (past incident, not opinion)
  Q-0XX: "What's your current kit or workaround for [cluster topic]? What's its
         failure mode when it lets you down?" (current behavior + pain)
  Q-0XX: "What did your unit try before this that didn't work? Why was it
         abandoned?" (failed attempts)

CROSS-CUTTING QUESTIONS:
  Q-0XX: "In the last month, how many sorties or missions were impacted because
         [cluster topic] wasn't solved? Give me the worst one — what was the
         operational outcome?" (concrete frequency + operational cost)
  Q-0XX: "Who in the chain of command is pushing hardest for a solution to this?
         What happens to their unit's readiness if nothing changes in 6 months?"
         (command pressure = real demand)
  Q-0XX: "If you had to show me proof this is a real problem — an after-action
         report, a mission debrief slide, a video clip — what would you show me?"
         (evidence of pain)
  Q-0XX: "Who in your unit — or another unit — feels this pain even more than
         you? Can you put me in touch?" (referral check — no referral = shallow)

Tag all with asker="mom-test". These are the structured discovery questions.

Step 2 — Judge questions:
Load the locked panel from state.json. For each judge, read their
`hard_questions_seed` field from the YAML and add 2-3 questions adapted
to the specific clusters. Tag these with asker=<judge_short>.

Judges should ALSO follow Mom Test principles — ask about
past incidents and concrete behavior, not opinions.

Step 3 — Capture answers:
If owner_mode=real: present questions to the user one at a time. For each
answer, apply the Mom Test sniff test:
  - Did they describe a concrete past incident? If not, ask for one.
  - Did they mention a specific cost (hours, people, dollars)? If not, ask.
  - Did they offer a compliment ("sounds great!")? Redirect to evidence.
  - Did they say "a lot of people have this problem"? Ask for an intro.

If owner_mode=sim: load the persona YAML, role-play the owner, generate
specific, past-tense answers for every question. Every answer must reference
at least one concrete incident, metric, or named person. "It depends" is
only acceptable when followed by a specific example.

Step 4 — Re-score candidates:
Re-score the top 3 candidate problems using the rubric axes, now informed by
the owner answers. For each candidate, write 2-3 sentences of reasoning that
reference specific answers — quote the answer that most changed your score.

Output: Build `agent.candidates.Candidate` objects and call
`agent.candidates.write_candidate_problem()`. The weighted score is computed via
`Candidate.weighted_score()` using the default rubric.
