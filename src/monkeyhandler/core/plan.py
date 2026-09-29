"""成案：训练计划的数据模型。

计划必须可解释：rationale 字段说明「为什么这样排」，并引用画像事实、
领域方法与人性知识库条目。
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class Load(BaseModel):
    """一次训练的负荷。intensity 为 0-1 相对强度，具体标定由领域包解释；
    上限受人性知识库硬规则（恢复预算）约束。"""

    intensity: float = Field(ge=0.0, le=1.0)
    volume: float = Field(ge=0.0)
    note: str = ""


class Session(BaseModel):
    """一次训练节次。"""

    id: str
    week: int
    day: int  # 周内第几天（从 1 起）
    title: str
    objective: str  # 本次训练要达成什么
    content: list[str] = Field(default_factory=list)  # 任务/动作步骤
    load: Load | None = None
    duration_min: int = 60
    motivation_hook: str = ""  # 本节次的动机设计（见 core/motivation.py）


class Phase(BaseModel):
    """训练分期（类似中周期/mesocycle）。"""

    name: str
    weeks: int
    focus: str


class Plan(BaseModel):
    """一份训练计划：目标 + 分期 + 节次 + 依据。"""

    goal: str
    horizon_weeks: int
    phases: list[Phase] = Field(default_factory=list)
    sessions: list[Session] = Field(default_factory=list)
    rationale: str = ""  # 计划依据：为什么这样排（可解释性硬要求）

    def sessions_by_week(self, week: int) -> list[Session]:
        return sorted((s for s in self.sessions if s.week == week), key=lambda s: s.day)
