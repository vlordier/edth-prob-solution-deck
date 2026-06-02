# Personas

Personas define the problem-owner perspective for hackathon evaluations. Each `.yaml` file represents one persona.

## Default Persona

- **edth-judge** — EDTH Defense Judge: senior evaluator with 20 years in defense procurement.

## Adding a Persona

1. Create `personas/<short-name>.yaml` using `edth-judge.yaml` as a template.
2. Run tests to verify: `uv run pytest tests/test_personas.py -v`
