"""识人第二层：采集引擎（个体的关键属性如何被有效、可信地收集）。

方法论约束（已确认）：
- 通用核心属性集由人性知识库的差异维度条目派生（core_questions），
  领域包只补充领域专属问题（DomainPack.profile_questions）；
- 最小提问原则：每个问题必须声明 decision_point——它将改变的计划
  决策。答案不会改变任何决策的问题，不该存在；
- 每个答案以 Evidence(SELF_REPORT) 写入画像；未回答的问题跳过，
  不臆造、不默认；
- 升级路线：M0-M1 结构化问卷 → M2 LLM 自适应访谈（追问/澄清/按需
  探查）→ M3 起以行为数据交叉验证自报偏差（三角验证）。
"""
from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from .humanity import HumanKnowledgeBase
from .user_model import Dimension, Evidence, EvidenceSource, UserModel


class Question(BaseModel):
    """一道采集问题。decision_point 是最小提问原则的执行点。"""

    id: str
    text: str
    dimension: Dimension
    decision_point: str  # 答案将改变的计划决策
    kb_entry: str | None = None  # 关联的人性知识库差异维度条目


class Questionnaire(BaseModel):
    """结构化问卷（M0-M1 采集形态）。"""

    questions: list[Question] = Field(default_factory=list)

    @model_validator(mode="after")
    def _enforce_minimal_questions(self) -> "Questionnaire":
        for q in self.questions:
            if not q.decision_point.strip():
                raise ValueError(f"问题 {q.id} 缺少 decision_point（最小提问原则）")
        return self

    def collect(self, answers: dict[str, str], user: UserModel) -> UserModel:
        """把答案写入画像（带证据）。未回答的问题跳过。"""
        for q in self.questions:
            answer = answers.get(q.id)
            if not answer:
                continue
            user.assert_fact(
                key=q.id,
                dimension=q.dimension,
                value=str(answer),
                evidence=Evidence(
                    source=EvidenceSource.SELF_REPORT,
                    detail=f"采集：{q.text}",
                    confidence=0.7,
                ),
                based_on=q.kb_entry,
            )
        return user


def core_questions(kb: HumanKnowledgeBase) -> list[Question]:
    """通用核心问题集：跨领域复用，由人性知识库的差异维度派生。

    派生关系是显式的：每个问题的 kb_entry 必须真实存在于知识库，
    保证「问的每个问题都有人性知识依据」。
    """
    questions = [
        Question(
            id="sleep_hours",
            text="你平均每晚睡多久？（小时）",
            dimension=Dimension.PHYSIOLOGICAL,
            decision_point="恢复预算 → 强度上限（u_recovery_supercompensation）",
            kb_entry="d_sleep",
        ),
        Question(
            id="stress_level",
            text="近期生活压力水平？（low/mid/high）",
            dimension=Dimension.PHYSIOLOGICAL,
            decision_point="恢复预算 → 强度上限；高压期自动降量",
            kb_entry="d_stress_load",
        ),
        Question(
            id="chronotype",
            text="你是早起型还是夜猫型？（morning/evening/neither）",
            dimension=Dimension.PHYSIOLOGICAL,
            decision_point="训练时段建议（u_circadian）",
            kb_entry="d_chronotype",
        ),
        Question(
            id="motivation_style",
            text="什么最让你把一件事坚持下去？（progress/streak/social/competition）",
            dimension=Dimension.PSYCHOLOGICAL,
            decision_point="动机钩子选型（进度对比/出勤链/社交问责/竞赛）",
            kb_entry="d_motivation_orientation",
        ),
        Question(
            id="consistency_history",
            text="过去尝试训练或学习时，一般坚持到第几周、因为什么停下？",
            dimension=Dimension.PSYCHOLOGICAL,
            decision_point="在历史放弃点前主动减载与加强支持",
            kb_entry="d_consistency_history",
        ),
        Question(
            id="time_budget",
            text="每周实际可投入多少小时？",
            dimension=Dimension.PREFERENCE,
            decision_point="单次时长与每周频次上限",
        ),
    ]
    for q in questions:
        if q.kb_entry is not None and not kb.has(q.kb_entry):
            raise ValueError(f"问题 {q.id} 关联的知识条目 {q.kb_entry} 不在人性知识库中")
    return questions
