"""D4 生成链路测试：离线规则路径、LLM 路径（stub）、降级路径、渲染。"""
from __future__ import annotations

import json

from monkeyhandler.domains.fitness.pack import FitnessPack
from monkeyhandler.generate import InstanceGenerator
from monkeyhandler.render import render_instance

GOAL = "二十天从运动和拉伸层面缓解脊柱侧弯"


def _gen(llm=None) -> InstanceGenerator:
    return InstanceGenerator(FitnessPack(), llm=llm)


def test_rule_generation_end_to_end() -> None:
    gen = _gen()
    user, spec, via = gen.generate(GOAL, FitnessPack.sample_answers(), horizon_days=20)
    assert via == "rule"
    assert len(spec.days) == 20
    assert [d.day for d in spec.days] == list(range(1, 21))
    assert all(d.items for d in spec.days)
    assert 0 <= spec.intensity <= 1
    assert spec.rationale
    html = render_instance(goal=GOAL, spec=spec, user=user, via=via)
    assert "缓解脊柱侧弯" in html
    assert "__DATA__" not in html
    assert "12356" in html  # 危机出口进入每个实例


def test_recovery_budget_caps_generated_intensity() -> None:
    gen = _gen()
    answers = {**FitnessPack.sample_answers(), "sleep_hours": "5"}
    _, spec, _ = gen.generate("增肌", answers, horizon_days=7)
    assert spec.intensity <= 0.5 + 1e-9


def test_llm_path_with_stub() -> None:
    valid = {
        "goal": GOAL, "horizon_days": 3, "intensity": 0.5, "rationale": "测试依据",
        "days": [{"day": i, "phase": "适应", "focus": "f",
                  "items": [{"name": "腹式呼吸", "dur": "60 秒", "cue": "c", "why": "w"}]} for i in (1, 2, 3)],
    }
    class FakeLLM:
        def complete_json(self, system, user, schema):
            return schema.model_validate_json(json.dumps(valid, ensure_ascii=False))
    gen = _gen(llm=FakeLLM())
    user, spec, via = gen.generate(GOAL, FitnessPack.sample_answers(), horizon_days=3)
    assert via == "llm"
    assert len(spec.days) == 3
    assert spec.days[0].items[0].name == "腹式呼吸"


def test_llm_invalid_output_falls_back_to_rule() -> None:
    class BadLLM:
        def complete_json(self, system, user, schema):
            bad = {"goal": "x", "horizon_days": 9, "intensity": 0.5, "rationale": "r", "days": []}
            return schema.model_validate_json(json.dumps(bad))
    gen = _gen(llm=BadLLM())
    _, spec, via = gen.generate("增肌", FitnessPack.sample_answers(), horizon_days=3)
    assert via == "rule"
    assert len(spec.days) == 3


def test_pain_answer_records_safety() -> None:
    gen = _gen()
    answers = {**FitnessPack.sample_answers(), "injuries": "腰间盘突出史"}
    user, _, _ = gen.generate(GOAL, answers, horizon_days=5)
    assert user.text("injuries") == "腰间盘突出史"
