"""健身领域的离线调研占位实现。

比 NullResearchEngine 更丰富：返回模板化的健身领域知识，让 M0 的
demo 在没有 web 调研的情况下也能展示「领域知识 → 计划依据」的链路。
所有方法/引用均标注为占位，M2 由逐主张验证、带真实引用的调研 agent 替换。
"""
from __future__ import annotations

from ...core.research import Citation, DomainProfile, ResearchEngine, SkillNode, TrainingMethod


class FitnessOfflineResearch:
    """离线健身领域知识（M0 占位，引用待 M2 替换为真实出处）。"""

    def research(self, brief: str, pack_id: str) -> DomainProfile:
        placeholder = Citation(title="（M0 占位）待 M2 调研 agent 替换为真实引用")
        return DomainProfile(
            domain_id=pack_id,
            topic=brief,
            skill_graph=[
                SkillNode(id="patterns", name="五大动作模式", description="蹲/铰链/推/拉/稳定"),
                SkillNode(id="compound", name="复合动作技术", prerequisites=["patterns"]),
                SkillNode(id="progression", name="渐进超负荷", prerequisites=["compound"]),
                SkillNode(id="periodization", name="训练分期", prerequisites=["progression"]),
            ],
            training_methods=[
                TrainingMethod(
                    name="渐进超负荷",
                    description="以可控幅度逐步增加负荷或容量，是适应的根本驱动",
                    evidence_level="strong",
                    citations=[placeholder],
                ),
                TrainingMethod(
                    name="依从性优先",
                    description="计划的第一约束是「用户真的会执行」；弃练是新手最大失败源",
                    evidence_level="strong",
                    citations=[placeholder],
                ),
                TrainingMethod(
                    name="训练分期与减量",
                    description="强度/容量周期化安排，定期减量防止过度训练",
                    evidence_level="moderate",
                    citations=[placeholder],
                ),
                TrainingMethod(
                    name="动作模式优先",
                    description="先建立蹲/铰链/推/拉/稳定的基本模式，再谈专项化",
                    evidence_level="moderate",
                    citations=[placeholder],
                ),
            ],
            failure_modes=[
                "目标定得过于激进，2-3 周后弃练",
                "只练喜欢的部位，动作模式失衡导致伤病",
                "忽视睡眠与恢复，进入「越练越累」的负循环",
                "没有渐进，长期同一负荷进入平台期",
            ],
            safety_notes=[
                "疼痛≠酸痛：出现尖锐疼痛立即停止并评估",
                "有伤病史的用户应先获得专业评估再上强度",
            ],
            open_questions=["器械可用性的细节？", "伤病史的具体动作限制？"],
        )
