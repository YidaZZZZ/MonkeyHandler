"""编排器：把 识人 → 识域 → 成案 串成一条流水线。

计划的生成同时受三方约束：
- 个体画像（这一个人，带证据）
- 领域知识（这个专业，带引用）
- 人性知识库（人的一般规律：硬规则强制执行，软知识注入生成）

M0 为纯规则版（不需要 LLM 即可跑通）；M2 起由 LLM 自适应访谈替代
问卷、由 web 调研 agent 替换离线调研、人性知识库软上下文注入计划
生成；M3 在此之上加入执行闭环与再校准。
"""
from __future__ import annotations

from .domain import DomainPack
from .humanity import HumanKnowledgeBase
from .plan import Plan
from .profiling import Questionnaire, core_questions
from .research import DomainProfile, NullResearchEngine, ResearchEngine
from .user_model import UserModel


class CoachEngine:
    def __init__(
        self,
        pack: DomainPack,
        research: ResearchEngine | None = None,
        humanity: HumanKnowledgeBase | None = None,
    ):
        self.pack = pack
        self.research = research or NullResearchEngine()
        self.humanity = humanity or HumanKnowledgeBase.kernel()

    @property
    def questionnaire(self) -> Questionnaire:
        """采集问题 = 通用核心集（人性知识库派生）+ 领域包补充。"""
        return Questionnaire(questions=core_questions(self.humanity) + self.pack.profile_questions())

    def start(
        self,
        goal: str,
        answers: dict[str, str],
        horizon_weeks: int = 4,
    ) -> tuple[UserModel, DomainProfile, Plan]:
        """从目标与用户回答出发，产出（画像, 领域知识, 计划）。"""
        user = UserModel(goal=goal, display_name=answers.get("name", ""))
        self.questionnaire.collect(answers, user)
        domain = self.research.research(self.pack.research_brief(goal), pack_id=self.pack.id)
        plan = self.pack.build_plan(user, domain, horizon_weeks=horizon_weeks)
        return user, domain, plan
