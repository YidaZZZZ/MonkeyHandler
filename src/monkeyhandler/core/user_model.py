"""识人第三层：个体画像。

设计约束：
- 画像中的每一条事实都必须携带证据（来自哪次采集/测评/行为观察），
  禁止「凭空出现」的结论——这是对抗幻觉、保证画像可信的底线；
- 画像是有版本的、持续演进的：执行闭环中的每次 check-in 都可能
  修正画像（M3 起）；
- 画像属于敏感数据：默认只存本地（见 docs/architecture.md 隐私一节）。
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class EvidenceSource(str, Enum):
    INTERVIEW = "interview"      # 访谈对话
    SELF_REPORT = "self_report"  # 自报式采集（问卷 / check-in：睡眠、精力、压力、RPE）
    BEHAVIOR = "behavior"        # 执行行为观察（缺席、提前完成、成绩曲线）——最诚实的信号
    ASSESSMENT = "assessment"    # 标准化测评 / 摸底
    INFERENCE = "inference"      # 系统推断（detail 中必须写明推理依据）


class Dimension(str, Enum):
    COGNITIVE = "cognitive"          # 认知：先验水平、学习速度、误区
    PSYCHOLOGICAL = "psychological"  # 心理：动机取向、自我效能、坚持模式、畏难点
    PHYSIOLOGICAL = "physiological"  # 生理：作息、精力、压力、伤病、恢复（M0-M1 自报式）
    PREFERENCE = "preference"        # 偏好与约束：时间预算、场地器械、喜好


class Evidence(BaseModel):
    source: EvidenceSource
    detail: str
    confidence: float = Field(ge=0.0, le=1.0)
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProfileAttribute(BaseModel):
    """一条画像事实：值 + 证据链 +（可选）所依据的人性知识库差异维度。"""

    key: str
    dimension: Dimension
    value: str
    evidence: list[Evidence] = Field(default_factory=list)
    based_on: str | None = None  # 关联 HumanKnowledgeBase 差异维度条目的 id

    @property
    def confidence(self) -> float:
        if not self.evidence:
            return 0.0
        return max(e.confidence for e in self.evidence)


class UserModel(BaseModel):
    """个体画像。所有写入必须经过 assert_fact（强制携带证据）。"""

    display_name: str = ""
    goal: str = ""
    version: int = 1
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    attributes: dict[str, ProfileAttribute] = Field(default_factory=dict)

    def assert_fact(
        self,
        key: str,
        dimension: Dimension,
        value: str,
        evidence: Evidence | list[Evidence],
        based_on: str | None = None,
    ) -> None:
        """写入/更新一条画像事实。key 相同时 value 覆盖、证据追加。"""
        if not evidence:
            raise ValueError(f"画像事实 {key!r} 必须携带证据（Evidence）")
        evs = evidence if isinstance(evidence, list) else [evidence]
        attr = self.attributes.get(key)
        if attr is None:
            attr = ProfileAttribute(
                key=key, dimension=dimension, value=value, evidence=list(evs), based_on=based_on
            )
        else:
            attr.value = value
            attr.evidence.extend(evs)
            if based_on is not None:
                attr.based_on = based_on
        self.attributes[key] = attr
        self.updated_at = datetime.now(timezone.utc)

    def facts(self, dimension: Dimension | None = None) -> list[ProfileAttribute]:
        attrs = list(self.attributes.values())
        if dimension is not None:
            attrs = [a for a in attrs if a.dimension == dimension]
        return sorted(attrs, key=lambda a: a.key)

    def text(self, key: str, default: str | None = None) -> str | None:
        attr = self.attributes.get(key)
        return attr.value if attr is not None else default

    def summary(self) -> str:
        """供 LLM 使用的画像摘要（最小化披露：只发事实，不带身份信息）。"""
        lines = [f"- 目标: {self.goal or '未设定'}"]
        for a in self.facts():
            lines.append(f"- [{a.dimension.value}] {a.key} = {a.value} (置信度 {a.confidence:.2f})")
        return "\n".join(lines)
