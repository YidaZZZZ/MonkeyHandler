"""MonkeyHandler 冒烟测试：守护框架的设计原则，而不只是功能。"""
from __future__ import annotations

import pytest

from monkeyhandler.core.engine import CoachEngine
from monkeyhandler.core.humanity import HumanKnowledgeBase, recovery_budget
from monkeyhandler.core.plan import Plan
from monkeyhandler.core.profiling import Questionnaire
from monkeyhandler.core.user_model import Dimension, UserModel
from monkeyhandler.domains.fitness.pack import FitnessPack
from monkeyhandler.domains.fitness.research import FitnessOfflineResearch


def test_kernel_discipline() -> None:
    """人性知识库内核纪律：差异维度必须有测量方法，所有条目必须有出处。"""
    kb = HumanKnowledgeBase.kernel()
    assert len(kb.universals()) >= 5
    assert len(kb.differences()) >= 5
    assert len(kb.hard_rules()) >= 1
    for e in kb.differences():
        assert e.measure, f"差异维度 {e.id} 缺少测量方法"
    for e in kb.universals() + kb.differences():
        assert e.sources, f"条目 {e.id} 缺少出处"


def test_minimal_question_principle() -> None:
    """最小提问原则：每个采集问题都必须声明它将改变的计划决策。"""
    engine = CoachEngine(FitnessPack(), research=FitnessOfflineResearch())
    questions = engine.questionnaire.questions
    # 通用核心集 6 题 + 健身领域补充 4 题
    assert len(questions) == 10
    assert all(q.decision_point.strip() for q in questions)


def test_profile_requires_evidence() -> None:
    """画像纪律：不带证据的事实写入必须被拒绝。"""
    user = UserModel()
    with pytest.raises(ValueError):
        user.assert_fact("sleep_hours", Dimension.PHYSIOLOGICAL, "7h", evidence=None)


def test_fitness_end_to_end() -> None:
    """画像 → 领域知识 → 计划 全链路跑通，且计划可解释。"""
    pack = FitnessPack()
    engine = CoachEngine(pack, research=FitnessOfflineResearch())
    user, domain, plan = engine.start("增肌减脂", pack.sample_answers(), horizon_weeks=4)

    assert isinstance(plan, Plan)
    assert plan.goal == "增肌减脂"
    assert len(plan.phases) >= 1
    assert len(plan.sessions) == 4 * 3  # 每周 3 练 × 4 周
    assert plan.rationale
    assert domain.training_methods, "计划依据应引用领域方法"
    assert all(s.content for s in plan.sessions)
    assert all(s.load is not None for s in plan.sessions)


def test_recovery_budget_hard_rule_enforced() -> None:
    """硬规则：恢复预算必须约束每一次训练的强度上限。"""
    assert recovery_budget(5.0, "mid") == 0.5
    assert recovery_budget(6.5, "high") == 0.6
    assert recovery_budget(8.0, "low") == 1.0

    pack = FitnessPack()
    engine = CoachEngine(pack, research=FitnessOfflineResearch())
    answers = {**pack.sample_answers(), "sleep_hours": "5", "training_experience": "some"}
    _, _, plan = engine.start("增肌", answers, horizon_weeks=4)
    cap = recovery_budget(5.0, "mid")
    assert all(s.load.intensity <= cap + 1e-9 for s in plan.sessions)


def test_plan_respects_available_days() -> None:
    """计划必须尊重用户画像中的频次约束。"""
    pack = FitnessPack()
    engine = CoachEngine(pack, research=FitnessOfflineResearch())
    answers = {**pack.sample_answers(), "available_days_per_week": "4"}
    _, _, plan = engine.start("增肌", answers, horizon_weeks=2)
    assert len(plan.sessions) == 2 * 4
    assert all(s.day <= 4 for s in plan.sessions)


def test_questionnaire_skips_unanswered() -> None:
    """未回答的问题跳过，不臆造画像事实。"""
    engine = CoachEngine(FitnessPack(), research=FitnessOfflineResearch())
    user = UserModel(goal="测试")
    engine.questionnaire.collect({"sleep_hours": "7"}, user)
    assert "sleep_hours" in user.attributes
    assert "stress_level" not in user.attributes
    assert isinstance(engine.questionnaire, Questionnaire)
