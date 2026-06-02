# Judges Library

A curated set of defense-tech evaluator personas for hackathon solution grading.

## Quick Reference

| Short                | Name                            | Focus Area                          |
|----------------------|---------------------------------|-------------------------------------|
| `mehta`              | Dr. Mehta                       | Technical skepticism, deep physics  |
| `viper`              | Maj. Viper                      | Military operations, C-UAS          |
| `tran`               | Lt. Col. Tran                   | Electronic warfare, SIGINT          |
| `whitfield`          | Whitfield                       | Defense prime program management    |
| `park`               | Park                            | Acquisition, procurement, FAR       |
| `kovalenko`          | SFC Kovalenko                   | Frontline end-user, field realism   |
| `hassan`             | Hassan                          | Ethics, compliance, LOAC            |
| `lee`                | Lee                             | Defense VC, dual-use investment     |
| `volkov`             | Volkov                          | Red team, adversary mindset         |
| `shah`               | Shah                            | Scaling engineer, DevOps            |
| `sutter`             | Sutter                          | Intel analysis, multi-INT fusion    |
| `chen`               | Chen                            | Operator UX, human factors          |

## Adding a Judge

1. Copy an existing `.yaml` file as a template.
2. Fill in all required fields: `name`, `short`, `tags`, `background`, `priorities`, `anti_priorities`, `decision_style`, `language_patterns`, `scoring_biases` (with axes `impact`, `innovation`, `execution`, `presentation`), `knowledge_gaps`, `hard_questions_seed`.
3. Use a lowercase-hyphenated `short` name matching `[a-z0-9_-]+`.
4. Run validation: `.venv/bin/python -c "from pathlib import Path; from agent.judges import load_judge_library; lib=load_judge_library(Path('judges')); print(f'Loaded {len(lib)} judges')"`
