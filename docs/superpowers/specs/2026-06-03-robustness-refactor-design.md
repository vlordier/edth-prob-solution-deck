# Robustness Refactor — Design Spec

## Problem
The `agent/` codebase has copy-paste boilerplate (17 identical write-try-except blocks), hardcoded magic strings in 3+ files, bare `dict` instead of TypedDict everywhere, a confirmed runtime bug in `deck.py` (pptx import), and `deck.py` has zero test coverage.

## Scope
Full structural rebuild. Touch every module.

## Design

### 1. `agent/_util.py` — Shared helpers

| Function | Replaces |
|---|---|
| `write_artefact(artefacts_dir, filename, lines)` | mkdir + write_text + try/except in 17 places |
| `now_iso()` | 2 identical definitions |
| `slurp_file(artefacts_dir, name)` | 2 inline `_slurp` clones |
| `load_json_safe(path)` | validate.py `_load_json_safe` |
| `tokens(text)` | ideation.py `_tokens` |
| `jaccard(a, b)` | ideation.py + judges.py duplicates |

### 2. `agent/_constants.py` — Magic value elimination

- `ARTEFACTS` frozen dict — 14 artefact file names (single source of truth)
- `PhaseStatus` StrEnum — `PENDING`, `IN_PROGRESS`, `COMPLETED`
- `RenderMode` StrEnum — `MARP`, `PPTX`, `HTML`
- `PHASE_COUNT = 9`
- `MAX_AUDIT_RESPONSE = 5000`
- `DEFAULT_STATE_CONFIG` dict

### 3. `agent/_state_types.py` — TypedDicts for state machine

- `_PhaseState` TypedDict
- `AgentState` TypedDict
- `empty_state()` returns `AgentState`, `load_state()` returns `AgentState`

### 4. `agent/_models.py` — TypedDicts for domain objects

- `DeckContext` TypedDict — replaces bare `dict` in `deck.py`
- `Problem` moved from `parse_csv.py` TypedDict → shared

### 5. Bug fixes

- **CRITICAL**: Move `render_pptx_deck` from `deck.py` to `render.py` (fix broken import at deck.py:113)
- `sub_problem.py`: fix `roi_score()` to guard against missing ROI_WEIGHTS keys
- `ranking.py`: guard NaN in sort
- `ideation.py`: guard None rating in sort
- `parse_csv.py`: guard malformed DictReader rows
- `state.py`: guard mutators against None state
- `validate.py`: guard `_check_state` current_phase access

### 6. Tests

- Add `tests/test_deck.py` — test `compile_deck_md` with empty/partial/complete artefacts

### 7. Caller updates

- All `write_*` functions → use `write_artefact()` from `_util.py`
- All `_now_iso()` callers → use `now_iso()` from `_util.py`
- All `_slurp()` callers → use `slurp_file()` from `_util.py`
- All `_load_json_safe()` callers → use `load_json_safe()` from `_util.py`
- All hardcoded artefact names → `ARTEFACTS.xxx`
- All `"pending"`/`"in_progress"`/`"completed"` → `PhaseStatus.PENDING` etc.
- All `"marp"`/`"pptx"`/`"html"` → `RenderMode.MARP` etc.
- All bare `dict` in state machine → `AgentState` | `_PhaseState`
- `jaccard` in `judges.py` → import from `_util.py`
