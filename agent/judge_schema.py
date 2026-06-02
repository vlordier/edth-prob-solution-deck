"""Judge YAML schema and validation."""
from __future__ import annotations
import re
from typing import Any, TypedDict

REQUIRED_FIELDS = ("name","short","tags","background","priorities","anti_priorities","decision_style","language_patterns","scoring_biases","knowledge_gaps","hard_questions_seed")
_SHORT_PATTERN = re.compile(r"^[a-z0-9_-]+$")
REQUIRED_AXES = {"impact","innovation","execution","presentation"}

class Judge(TypedDict, total=False):
    name: str; short: str; tags: list[str]; background: str
    priorities: list[str]; anti_priorities: list[str]; decision_style: str
    language_patterns: list[str]; scoring_biases: dict[str,float]
    knowledge_gaps: list[str]; hard_questions_seed: list[str]

class JudgeValidationError(ValueError):
    pass

def validate_judge(data: dict[str, Any]) -> Judge:
    for field in REQUIRED_FIELDS:
        if field not in data:
            raise JudgeValidationError(f"Missing required field: {field!r}")
    short = data["short"]
    if not isinstance(short, str) or not _SHORT_PATTERN.match(short):
        raise JudgeValidationError(f"short must match [a-z0-9_]+, got {short!r}")
    for lf in ("tags","priorities","anti_priorities","language_patterns","knowledge_gaps","hard_questions_seed"):
        if not isinstance(data[lf], list):
            raise JudgeValidationError(f"{lf} must be a list")
    biases = data["scoring_biases"]
    if not isinstance(biases, dict) or set(biases.keys()) != REQUIRED_AXES:
        raise JudgeValidationError(f"scoring_biases must have {REQUIRED_AXES}")
    for k,v in biases.items():
        if not isinstance(v,(int,float)) or isinstance(v,bool):
            raise JudgeValidationError(f"scoring_biases.{k} must be float")
    return data
