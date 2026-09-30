"""D4 生成链路测试：仅 LLM 路径——校验、钳制、重试与明确报错。"""
from __future__ import annotations

import json

import pytest

from monkeyhandler.core.llm import LLMUnavailable
from monkeyhandler.domains.fitness.pack import FitnessPack
from monkeyhandler.generate import InstanceGenerator
from monkeyhandler.render import render_instance

GOAL = "二十天从运动和拉伸层面缓解脊柱侧弯"


def _valid(horizon: int, intensity: float = 0.5) -> dict:
    return {
        "goal": GOAL, "horizon_days": horizon, "intensity": intensity, "rationale": "测试依据",
        "days": [{"day": i, "phase": "适应", "focus": "f",
                  "items": [{"name": "腹式呼吸", "dur": "60 秒", "cue": "c", "why": "w"}]} for i in range(1, horizon + 1)],
    }


class ScriptedLLM:
    """按脚本依次返回输出的假 LLM；记录每次收到的 user prompt。"""

    def __init__(self, outputs: list[str]):
        self.outputs = list(outputs)
        self.calls: list[str] = []

    def complete_json(self, system, user, schema):
        self.calls.append(user)
        out = self.outputs.pop(0)
        return schema.model_validate_json(out)


def _gen(llm) -> InstanceGenerator:
    return InstanceGenerator(FitnessPack(), llm=llm)


def test_no_llm_raises_clearly() -> None:
    gen = _gen(None)
    with pytest.raises(LLMUnavailable, match="未配置 LLM"):
        gen.generate(GOAL, FitnessPack.sample_answers(), horizon_days=20)


def test_llm_generation_end_to_end() -> None:
    llm = ScriptedLLM([json.dumps(_valid(5), ensure_ascii=False)])
    user, spec, via = _gen(llm).generate(GOAL, FitnessPack.sample_answers(), horizon_days=5)
    assert via == "llm"
    assert [d.day for d in spec.days] == [1, 2, 3, 4, 5]
    assert all(d.items for d in spec.days)
    html = render_instance(goal=GOAL, spec=spec, user=user, via=via)
    assert "缓解脊柱侧弯" in html
    assert "__DATA__" not in html
    assert "12356" in html


def test_llm_intensity_clamped_to_recovery_budget() -> None:
    llm = ScriptedLLM([json.dumps(_valid(5, intensity=0.9), ensure_ascii=False)])
    answers = {**FitnessPack.sample_answers(), "sleep_hours": "5"}  # 恢复预算 → 0.5
    _, spec, _ = _gen(llm).generate("增肌", answers, horizon_days=5)
    assert spec.intensity == 0.5
    assert any("自动调低" in s for s in spec.safety)


def test_llm_invalid_then_valid_retries_with_feedback() -> None:
    bad = json.dumps({"goal": "x", "horizon_days": 9, "intensity": 0.5, "rationale": "r", "days": []})
    llm = ScriptedLLM([bad, json.dumps(_valid(3), ensure_ascii=False)])
    _, spec, via = _gen(llm).generate("增肌", FitnessPack.sample_answers(), horizon_days=3)
    assert via == "llm"
    assert len(spec.days) == 3
    assert "未通过校验" in llm.calls[1]  # 重试时带上了上一次的错误反馈


def test_llm_persistently_invalid_raises() -> None:
    bad = json.dumps({"goal": "x", "horizon_days": 9, "intensity": 0.5, "rationale": "r", "days": []})
    llm = ScriptedLLM([bad, bad])
    with pytest.raises(LLMUnavailable, match="连续 2 次未通过校验"):
        _gen(llm).generate("增肌", FitnessPack.sample_answers(), horizon_days=3)


def test_pain_answer_records_safety() -> None:
    llm = ScriptedLLM([json.dumps(_valid(5), ensure_ascii=False)])
    answers = {**FitnessPack.sample_answers(), "injuries": "腰间盘突出史"}
    user, _, _ = _gen(llm).generate(GOAL, answers, horizon_days=5)
    assert user.text("injuries") == "腰间盘突出史"
