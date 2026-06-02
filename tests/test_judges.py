from __future__ import annotations
from pathlib import Path
import pytest
from agent.judges import list_judges, load_judge, load_judge_library

def _write(d:Path,s:str,n:str,tags:list[str]) -> None:
    d.mkdir(exist_ok=True)
    (d/f"{s}.yaml").write_text(f'name: "{n}"\nshort: "{s}"\ntags: {tags}\nbackground: "bg"\npriorities: ["p"]\nanti_priorities: ["ap"]\ndecision_style: "ds"\nlanguage_patterns: ["lp"]\nscoring_biases:\n  impact: 0.0\n  innovation: 0.0\n  execution: 0.0\n  presentation: 0.0\nknowledge_gaps: ["kg"]\nhard_questions_seed: ["hq"]\n',encoding="utf-8")

def test_load_judge_returns_dict(tmp_path:Path)->None:
    _write(tmp_path,"viper","Maj.Viper",["c-uas"])
    j=load_judge(tmp_path,"viper")
    assert j["short"]=="viper"; assert j["tags"]==["c-uas"]

def test_load_invalid_raises(tmp_path:Path)->None:
    tmp_path.mkdir(exist_ok=True);(tmp_path/"bad.yaml").write_text("name:bad\n",encoding="utf-8")
    with pytest.raises(Exception):load_judge(tmp_path,"bad")

def test_list_judges(tmp_path:Path)->None:
    _write(tmp_path,"a","A",[]);_write(tmp_path,"b","B",[])
    assert sorted(list_judges(tmp_path))==["a","b"]

def test_load_library_all(tmp_path:Path)->None:
    _write(tmp_path,"a","A",[]);_write(tmp_path,"b","B",[])
    assert {j["short"] for j in load_judge_library(tmp_path)}=={"a","b"}

def test_load_library_skips_bad(tmp_path:Path)->None:
    _write(tmp_path,"a","A",[]);(tmp_path/"bad.yaml").write_text("name:bad\n",encoding="utf-8")
    assert [j["short"] for j in load_judge_library(tmp_path)]==["a"]
