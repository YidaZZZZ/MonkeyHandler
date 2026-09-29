"""识域：领域知识调研。

设计约束：
- 调研产出的训练方法必须逐主张标注证据等级并附引用（Citation）——
  「充分调研」意味着可追溯，而不是模型拍脑袋；
- 与人性知识库同一纪律：不可追溯的知识不进计划；
- ResearchEngine 是可替换的端口：M2 交付 web 调研 agent（对每个主张
  交叉验证多个独立来源）；M0 只有离线占位实现。
"""
from __future__ import annotations

from typing import Literal, Protocol

from pydantic import BaseModel, Field


class Citation(BaseModel):
    title: str
    url: str | None = None
    note: str = ""


class TrainingMethod(BaseModel):
    """一种领域内有效的训练方法。"""

    name: str
    description: str
    evidence_level: Literal["strong", "moderate", "anecdotal"]
    citations: list[Citation] = Field(default_factory=list)


class SkillNode(BaseModel):
    """技能树节点。id 供 prerequisites 引用。"""

    id: str
    name: str
    description: str = ""
    prerequisites: list[str] = Field(default_factory=list)


class DomainProfile(BaseModel):
    """一次领域调研的结构化产出。"""

    domain_id: str
    topic: str = ""
    skill_graph: list[SkillNode] = Field(default_factory=list)
    training_methods: list[TrainingMethod] = Field(default_factory=list)
    failure_modes: list[str] = Field(default_factory=list)  # 该领域新手最常见的失败模式
    safety_notes: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)  # 调研解决不了、需访谈用户的问题


class ResearchEngine(Protocol):
    def research(self, brief: str, pack_id: str) -> DomainProfile:
        """按领域包给出的调研简报（brief）产出 DomainProfile。"""
        ...


class NullResearchEngine:
    """离线占位实现：返回退化的 DomainProfile。

    只用于 M0 结构测试；M2 由带 web 检索、逐主张验证、输出带真实引用的
    调研 agent 替换。各领域包可自带更丰富的离线实现（见
    monkeyhandler.domains.fitness.research）。
    """

    def research(self, brief: str, pack_id: str) -> DomainProfile:
        return DomainProfile(
            domain_id=pack_id,
            topic=brief,
            failure_modes=["（离线占位）未执行真实调研"],
            open_questions=["M2 接入真实调研引擎后，此占位将被替换"],
        )
