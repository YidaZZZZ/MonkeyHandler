"""D4 生成链路测试：仅 LLM 路径——调研、校验、钳制、依据引用、重试与明确报错。

D17（2026-10-03）：按目标动态调研三本著作；每个练习项 src 必须引用所列著作；
保护文案按 is_physical 分流（健身文案不进非身体域）。
"""
from __future__ import annotations

import json

import pytest

from monkeyhandler.core.llm import LLMUnavailable
from monkeyhandler.domains.fitness.pack import FitnessPack
from monkeyhandler.generate import InstanceGenerator
from monkeyhandler.render import render_instance

GOAL = "二十天从运动和拉伸层面缓解脊柱侧弯"


def _research(is_physical: bool = True) -> dict:
    works = [
        {"title": "刻意练习", "author": "Ericsson", "year": "2016",
         "why": "目标-反馈-小步的拆解奠基", "methods": ["目标→能力证据→活动", "走出舒适区的小步"]},
        {"title": "周期：运动训练理论与方法" if is_physical else "认知天性",
         "author": "Bompa" if is_physical else "Brown", "year": "2018" if is_physical else "2014",
         "why": "负荷缓坡与恢复的实证" if is_physical else "间隔与检索的实证",
         "methods": ["适应→稳定→巩固", "减量日安排"] if is_physical else ["间隔练习", "检索练习"]},
        {"title": "为什么我们睡觉", "author": "Walker", "year": "2017",
         "why": "恢复预算的实证来源", "methods": ["睡眠不足先降强度"]},
    ]
    return {"is_physical": is_physical, "works": works,
            "failure_modes": ["首次就上强度", "跳过基础"],
            "safety_notes": ["调研级安全注意：不适即停"] if is_physical else ["持续挫败超过三天应降级任务"]}


def _valid(horizon: int, intensity: float = 0.5, src: str = "《刻意练习》目标-反馈-小步") -> dict:
    return {
        "goal": GOAL, "horizon_days": horizon, "intensity": intensity,
        "rationale": "测试依据：《刻意练习》目标-反馈-小步",
        "days": [{"day": i, "phase": "适应", "focus": "f",
                  "items": [{"name": "腹式呼吸", "dur": "60 秒", "cue": "c", "why": "w", "src": src}]} for i in range(1, horizon + 1)],
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
    with pytest.raises(LLMUnavailable, match="还没有连接 AI 服务"):
        gen.generate(GOAL, FitnessPack.sample_answers(), horizon_days=20)


def test_llm_generation_end_to_end() -> None:
    llm = ScriptedLLM([json.dumps(_research(), ensure_ascii=False),
                       json.dumps(_valid(5), ensure_ascii=False)])
    user, spec, via = _gen(llm).generate(GOAL, FitnessPack.sample_answers(), horizon_days=5)
    assert via == "llm"
    assert [d.day for d in spec.days] == [1, 2, 3, 4, 5]
    assert all(d.items for d in spec.days)
    assert len(spec.works) == 3  # D17：调研产出附着到 spec
    assert spec.is_physical is True
    assert all(it.src for d in spec.days for it in d.items)  # 逐项依据
    html = render_instance(goal=GOAL, spec=spec, user=user, via=via)
    assert "缓解脊柱侧弯" in html
    assert "方法论依据" in html and "刻意练习" in html  # 著作卡片渲染
    assert "__DATA__" not in html
    assert "12356" in html


def test_research_reaches_plan_prompt() -> None:
    """D17：三本著作与失败模式必须进入计划阶段的提示词。"""
    llm = ScriptedLLM([json.dumps(_research(is_physical=False), ensure_ascii=False),
                       json.dumps(_valid(3), ensure_ascii=False)])
    _gen(llm).generate("二十天掌握使用大模型构建项目", FitnessPack.sample_answers(), horizon_days=3)
    assert "《刻意练习》" in llm.calls[1]
    assert "失败模式" in llm.calls[1]


def test_non_physical_goal_gets_universal_safety() -> None:
    """D17：健身保护文案不进认知域；调研级安全注意并入。"""
    llm = ScriptedLLM([json.dumps(_research(is_physical=False), ensure_ascii=False),
                       json.dumps(_valid(3), ensure_ascii=False)])
    _, spec, _ = _gen(llm).generate("二十天掌握使用大模型构建项目", FitnessPack.sample_answers(), horizon_days=3)
    assert spec.is_physical is False
    assert any("不构成专业建议" in s for s in spec.safety)
    assert not any("疼痛" in s for s in spec.safety)
    assert any("降级任务" in s for s in spec.safety)
    html = render_instance(goal="掌握大模型", spec=spec, user=None, via="llm", storage_key="t1")
    assert "施罗斯" not in html  # 健身页脚不进认知域
    assert "未经人工审核" in html


def test_src_missing_retries_then_passes() -> None:
    bad = json.dumps(_valid(3, src=""), ensure_ascii=False)
    llm = ScriptedLLM([json.dumps(_research(), ensure_ascii=False), bad,
                       json.dumps(_valid(3), ensure_ascii=False)])
    _, spec, _ = _gen(llm).generate("增肌", FitnessPack.sample_answers(), horizon_days=3)
    assert all(it.src for d in spec.days for it in d.items)
    assert "缺少依据" in llm.calls[2]  # 重试提示带上校验错误


def test_src_not_citing_works_rejected() -> None:
    llm = ScriptedLLM([json.dumps(_research(), ensure_ascii=False),
                       json.dumps(_valid(3, src="拍脑袋来的"), ensure_ascii=False),
                       json.dumps(_valid(3, src="拍脑袋来的"), ensure_ascii=False)])
    with pytest.raises(LLMUnavailable, match="连续两次给出的计划都无法使用"):
        _gen(llm).generate("增肌", FitnessPack.sample_answers(), horizon_days=3)


def test_research_persistent_failure_raises() -> None:
    bad_research = json.dumps({"is_physical": False, "works": [], "failure_modes": [], "safety_notes": []})
    llm = ScriptedLLM([bad_research, bad_research])
    with pytest.raises(LLMUnavailable, match="连续两次都无法完成领域调研"):
        _gen(llm).generate("增肌", FitnessPack.sample_answers(), horizon_days=3)


def test_llm_intensity_clamped_to_recovery_budget() -> None:
    llm = ScriptedLLM([json.dumps(_research(), ensure_ascii=False),
                       json.dumps(_valid(5, intensity=0.9), ensure_ascii=False)])
    answers = {**FitnessPack.sample_answers(), "sleep_hours": "5"}  # 恢复预算 → 0.5
    _, spec, _ = _gen(llm).generate("增肌", answers, horizon_days=5)
    assert spec.intensity == 0.5
    assert any("自动调低" in s for s in spec.safety)


def test_llm_invalid_then_valid_retries_with_feedback() -> None:
    bad = json.dumps({"goal": "x", "horizon_days": 9, "intensity": 0.5, "rationale": "r", "days": []})
    llm = ScriptedLLM([json.dumps(_research(), ensure_ascii=False), bad,
                       json.dumps(_valid(3), ensure_ascii=False)])
    _, spec, via = _gen(llm).generate("增肌", FitnessPack.sample_answers(), horizon_days=3)
    assert via == "llm"
    assert len(spec.days) == 3
    assert "未通过校验" in llm.calls[2]  # 重试时带上了上一次的错误反馈


def test_llm_persistently_invalid_raises() -> None:
    bad = json.dumps({"goal": "x", "horizon_days": 9, "intensity": 0.5, "rationale": "r", "days": []})
    llm = ScriptedLLM([json.dumps(_research(), ensure_ascii=False), bad, bad])
    with pytest.raises(LLMUnavailable, match="连续两次给出的计划都无法使用"):
        _gen(llm).generate("增肌", FitnessPack.sample_answers(), horizon_days=3)


def test_history_reaches_prompt() -> None:
    """N3 回程最小闭环：既往执行数据必须进入 LLM 的提示词。"""
    captured = {}
    class Cap:
        def complete_json(self, system, user, schema):
            captured["user"] = user
            if not captured.get("researched"):
                captured["researched"] = True
                return schema.model_validate_json(json.dumps(_research(), ensure_ascii=False))
            return schema.model_validate_json(json.dumps(_valid(3), ensure_ascii=False))
    gen = _gen(llm=Cap())
    gen.generate("改善睡眠", FitnessPack.sample_answers(), horizon_days=3,
                 history="既往训练平台执行记录（本机回程）：共完成 6 次训练；平均 RPE 4.2；疼痛最高 5/10。")
    assert "共完成 6 次训练" in captured["user"]
    assert "必须至少引用其中一项具体观察" in captured["user"]
