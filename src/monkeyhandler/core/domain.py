"""领域包（DomainPack）：把「一个专业领域」接入 MonkeyHandler 的协议。

领域包是框架可插拔性的核心，负责三件事：
1. 告诉调研引擎该为这个领域调研什么（research_brief）——领域 know-how
   的最小注入点；
2. 补充领域专属的画像问题（profile_questions，通用核心集之外）；
3. 结合用户画像与领域知识生成计划（build_plan）——必须遵守人性知识库
   的硬规则，并在 rationale 中解释依据。

新增一个领域 = 实现一个 DomainPack，核心引擎无需改动。
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from .plan import Plan
from .profiling import Question
from .research import DomainProfile
from .user_model import UserModel


class DomainPack(ABC):
    id: str
    name: str

    @abstractmethod
    def research_brief(self, goal: str) -> str:
        """调研简报：告诉 ResearchEngine 为这个领域 + 这个目标调研什么。"""

    @abstractmethod
    def profile_questions(self) -> list[Question]:
        """领域专属补充问题。同样必须声明 decision_point（最小提问原则）。"""

    @abstractmethod
    def build_plan(self, user: UserModel, domain: DomainProfile, horizon_weeks: int = 4) -> Plan:
        """结合用户画像与领域知识，产出可解释的训练计划。"""
