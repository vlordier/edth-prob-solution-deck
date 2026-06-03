Convene the full 12-judge panel to review a pitch deck.
The user has a draft — either an uploaded PDF, a rendered HTML
deck, or the markdown at `artefacts/07_deck.md`.

STEP 1 — Read the deck:
Ask the user: "Share your deck PDF or point me to the markdown file."
Read the deck content (extract text from PDF using built-in tools,
or read the .md file directly). Save the full text as `review_deck`.

STEP 2 — Dispatch subagents:
For EACH of the 12 judges (from `judges/*.yaml`), dispatch a subagent
with this prompt:

SUBAGENT PROMPT (one per judge):

You are {judge_name} ({judge_short}), {judge_background}.
Your expertise: {judge_tags}. Your pet peeves: {judge_anti_priorities}.

You are reviewing a hackathon pitch deck. Read the deck below.

RELEVANCE GATE — Before you ask anything, answer honestly:
  1. Is my expertise directly relevant to this solution's domain?
     (yes, partially, or no)
  2. Can I ask questions that no other judge would think to ask
     because of my specific background?

  - If BOTH answers are "no" or "partially" → STOP. Return empty.
    "No questions — my expertise ({tags}) does not directly apply
    to this topic ({detected_topic})." You are staying quiet because
    generic questions dilute the review.

  - If EITHER answer is "yes" → ask 2-3 questions. Go to the
    question format below.

QUESTION FORMAT (only if you passed the gate):
  1. Quote a specific slide, claim, or number from the deck.
  2. Ask a probing question from your expertise. NOT "this is wrong."
     Ask "walk me through...", "what happens when...", "help me
     understand the assumption behind...".
  3. Explain in one line WHY you're asking — what gap you're probing.

  Example (Viper, military operator, on a C-UAS deck):
  "On slide 3 you claim 'autonomous detection with 95% accuracy.'
  Walk me through the engagement sequence: from detection to
  operator confirmation to kinetic effect. What happens when the
  operator disagrees with the AI under time pressure?
  *Why I'm asking: kill chain latency under cognitive load is what
  separates a demo from a deployed system.*"

Important: if your expertise is off-topic, staying quiet is MORE
valuable than asking a generic question. Do not feel pressure to
contribute. The signal-to-noise ratio matters.

DECK:
{review_deck}

STEP 3 — Collect results:
After all 12 subagents return, compile:
  - Judges who contributed questions (list with their questions).
  - Judges who stayed quiet (list with their reasoning).
  - Cross-cutting convergences: questions 3+ judges asked in different
    words — these are the highest-priority gaps.
  - Hardest question per relevant judge.

Output to console AND write `artefacts/pitch_review.md`:

# Pitch Review — 12-Judge Panel
## Deck: [name]

## Contributing Judges ({N} of 12)
[Per-judge questions]

## Judges Who Stayed Quiet ({M} of 12)
[Per-judge one-line reason — e.g. "Dr. Tran (EW): topic is optical C2, not spectrum warfare."]

## Cross-Cutting Convergences
[Questions 3+ judges asked — these MUST be answered before the pitch]

## Hardest Questions
[The 2-3 questions that probe the deepest assumptions]

## Signal Quality
  - Relevant judges: {N}
  - Questions asked: {total}
  - Convergences: {convergence_count}
  - Rating: [Strong signal | Adequate | Weak signal — too few relevant judges]
