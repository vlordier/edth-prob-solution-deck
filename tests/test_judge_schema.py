from __future__ import annotations
import pytest
from agent.judge_schema import JudgeValidationError, validate_judge

def _valid() -> dict:
    return {"name":"Viper","short":"viper","tags":["c-uas"],"background":"pilot","priorities":["op"],"anti_priorities":["buzz"],"decision_style":"d","language_patterns":["lp"],"scoring_biases":{"impact":0.1,"innovation":-0.05,"execution":0.1,"presentation":0.0},"knowledge_gaps":["kg"],"hard_questions_seed":["hq"]}

def test_valid_passes() -> None:
    assert validate_judge(_valid())["short"] == "viper"

def test_missing_field_raises() -> None:
    b=_valid(); del b["tags"]
    with pytest.raises(JudgeValidationError, match="tags"):
        validate_judge(b)

def test_bad_biases_raises() -> None:
    b=_valid(); b["scoring_biases"]={"impact":0.1}
    with pytest.raises(JudgeValidationError, match="scoring_biases"):
        validate_judge(b)

def test_bad_short_raises() -> None:
    b=_valid(); b["short"]="Viper-1"
    with pytest.raises(JudgeValidationError, match="short"):
        validate_judge(b)

def test_non_float_bias_raises() -> None:
    b=_valid(); b["scoring_biases"]["impact"]="high"
    with pytest.raises(JudgeValidationError, match="float"):
        validate_judge(b)

def test_non_list_prio_raises() -> None:
    b=_valid(); b["priorities"]="op"
    with pytest.raises(JudgeValidationError, match="priorities"):
        validate_judge(b)
