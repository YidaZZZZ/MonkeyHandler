"""识人第一层：人类通识知识库。

定位：最终目标是指导「如何设计有效的、辅助用户学习训练的方案」这一实践，
而不是百科式的知识堆砌。

内容策略（已确认：混合）：
- 著作库（humanity/）：搜集最具影响力且公认言之有物的人类著作
  （心理学/认知学/成功学/社会学/脑科学，以及古典哲学与人性经典），
  每本走流水线：总结 → 逐主张交叉验证（争议不入库）→ 提取面向训练
  设计的提示词与方法论 → **用户审核** → 综合（synthesis/）。
  用户审核是入库的硬门槛。
- 本模块是著作库的**运行时索引层**：只承载已审核内容的机器可读形态
  （M0 为手工维护的精选内核；M1 起由 humanity/ 库加载生成）。

知识分级使用（已确认）：
- 安全/恢复类共性知识（is_hard_rule=True）编译为可执行硬规则，
  计划生成必须遵守（如 recovery_budget）；
- 动机/偏好类共性知识作为计划生成时的软上下文（summary() 注入 LLM）。
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class EntryKind(str, Enum):
    UNIVERSAL = "universal"    # 共性：对全人类成立的机制/约束
    DIFFERENCE = "difference"  # 个体差异维度：人在该维度上彼此不同，需测量


class KnowledgeEntry(BaseModel):
    """一条人性知识。内核纪律：必须附出处；差异维度必须给出测量方法。"""

    id: str
    kind: EntryKind
    category: str  # biological / psychological / social / behavioral / needs / philosophical
    title: str
    summary: str
    design_implication: str  # 对训练方案设计意味着什么
    sources: list[str] = Field(default_factory=list)
    source_work: str | None = None  # 对应 humanity/works/<id>（可追溯）
    is_hard_rule: bool = False
    measure: str | None = None  # DIFFERENCE 条目必填

    def model_post_init(self, __context) -> None:
        if self.kind == EntryKind.DIFFERENCE and not self.measure:
            raise ValueError(f"差异维度条目 {self.id} 必须给出测量方法 measure")
        if not self.sources:
            raise ValueError(f"知识条目 {self.id} 必须附出处（著作库纪律：不可追溯的知识不入库）")


# ---------------------------------------------------------------------------
# 精选内核 v0：人工精选的最小可信集合，条目均可追溯到著作库或文献。
# M1 起改为从 humanity/ 已审核条目自动生成，本列表退化为种子。
# ---------------------------------------------------------------------------
_KERNEL: list[KnowledgeEntry] = [
    # ---------------- 共性 ----------------
    KnowledgeEntry(
        id="u_needs_structure",
        kind=EntryKind.UNIVERSAL,
        category="needs",
        title="需求结构与内在动机",
        summary="自主、胜任、关系三种基本心理需求被满足时，动机更持久；"
        "外部奖惩驱动的行为在奖励消失后容易中断。",
        design_implication="计划要给用户选择感（自主）、可感知的进步（胜任）、连接感（关系），"
        "减少纯打卡式的外部约束。",
        sources=["Deci & Ryan, Self-Determination Theory (2000)", "Pink, Drive (2009)"],
        source_work="drive",
    ),
    KnowledgeEntry(
        id="u_habit_loop",
        kind=EntryKind.UNIVERSAL,
        category="behavioral",
        title="习惯回路与锚定",
        summary="行为经由「提示→执行→奖励」循环固化为习惯；锚定到既有稳定行为上，"
        "比要求意志力开辟新时段存活率高得多。",
        design_implication="每个训练节次都绑定到用户既有习惯锚点（习惯叠加），并做环境默认设计。",
        sources=["Clear, Atomic Habits (2018)", "Lally et al., Eur J Soc Psychol (2010)"],
        source_work="atomic-habits",
    ),
    KnowledgeEntry(
        id="u_present_bias",
        kind=EntryKind.UNIVERSAL,
        category="behavioral",
        title="现时偏差",
        summary="人对近期回报的权重远高于远期回报（双曲折现）；"
        "只有远期收益的目标难以支撑当下行为。",
        design_implication="每周甚至每次训练都要有即时可感知的回报与进度证据。",
        sources=["Ainslie, Breakdown of Will (2001)", "O'Donoghue & Rabin (1999)"],
    ),
    KnowledgeEntry(
        id="u_progress_competence",
        kind=EntryKind.UNIVERSAL,
        category="psychological",
        title="胜任感来自可见进步",
        summary="可感知的能力增长是最强的动机来源之一；进步被记录、被看见时坚持率显著提升。",
        design_implication="训练日志与进度可视化是一等公民，不是附属品。",
        sources=["Bandura, Self-efficacy (1997)", "Amabile & Kramer, The Progress Principle (2011)", "Harkin et al., Psych Bull (2016)"],
        source_work="flow",
    ),
    KnowledgeEntry(
        id="u_social_commitment",
        kind=EntryKind.UNIVERSAL,
        category="social",
        title="承诺与社会性支持",
        summary="公开承诺与同伴共同参与能提高执行率；社会比较既可以是动力也可以是压力源。",
        design_implication="问责机制（同伴/公开打卡）须经用户同意后启用，尊重个体社交偏好差异。",
        sources=["Cialdini, Influence (1984)", "《社会心理学》Myers（社会助长与承诺章节）"],
        source_work="influence",
    ),
    KnowledgeEntry(
        id="u_recovery_supercompensation",
        kind=EntryKind.UNIVERSAL,
        category="biological",
        title="压力-恢复-超量补偿",
        summary="能力增长发生在恢复期而非刺激期；恢复不足（睡眠、压力）时继续加量"
        "会导致表现下降与伤病。",
        design_implication="硬规则：训练强度上限受恢复预算约束（见 recovery_budget）。",
        sources=["Bompa & Haff, Periodization", "Walker, Why We Sleep (2017)"],
        source_work="why-we-sleep",
        is_hard_rule=True,
    ),
    KnowledgeEntry(
        id="u_circadian",
        kind=EntryKind.UNIVERSAL,
        category="biological",
        title="昼夜节律与精力曲线",
        summary="力量与认知表现在一天内系统波动，且存在个体时型差异。",
        design_implication="把高质量训练安排在用户精力高点；时型作为差异维度采集。",
        sources=["Scheer et al. (2009)", "Walker, Why We Sleep (2017)"],
    ),
    KnowledgeEntry(
        id="u_flow_challenge",
        kind=EntryKind.UNIVERSAL,
        category="psychological",
        title="心流通道",
        summary="挑战略高于当前能力时专注与愉悦最强；过易无聊、过难挫败。",
        design_implication="难度校准以流通道为目标（目标成功率约 85%），而非越难越好。",
        sources=["Csikszentmihalyi, Flow (1990)", "Nakamura & Csikszentmihalyi (2014)"],
        source_work="flow",
    ),
    # ---------------- 个体差异维度 ----------------
    KnowledgeEntry(
        id="d_sleep",
        kind=EntryKind.DIFFERENCE,
        category="biological",
        title="睡眠（时长与质量）",
        summary="睡眠是恢复预算的首要输入，个体需求差异大。",
        design_implication="强度上限与训练量随睡眠调整。",
        measure="自报平均睡眠时长 + 主观恢复感（check-in 持续校准）",
        sources=["Walker, Why We Sleep (2017)"],
    ),
    KnowledgeEntry(
        id="d_stress_load",
        kind=EntryKind.DIFFERENCE,
        category="biological",
        title="生活压力与恢复预算",
        summary="工作/生活压力与训练压力占用同一套恢复资源。",
        design_implication="高压期自动降量。",
        measure="自报压力水平（low/mid/high），可换用 PSS 简版量表",
        sources=["Cohen et al. (1983) Perceived Stress Scale"],
    ),
    KnowledgeEntry(
        id="d_chronotype",
        kind=EntryKind.DIFFERENCE,
        category="biological",
        title="时型",
        summary="早/晚型差异影响一天中的表现高点。",
        design_implication="训练时段建议个性化。",
        measure="自报作息偏好与实际起床/入睡时间（可换用 MEQ 简版）",
        sources=["Horne & Östberg (1976)"],
    ),
    KnowledgeEntry(
        id="d_motivation_orientation",
        kind=EntryKind.DIFFERENCE,
        category="psychological",
        title="动机取向",
        summary="内在动机（进步/掌握）与外在动机（外观/他人评价）主导时，"
        "可用的动机设计不同。",
        design_implication="动机钩子按取向选型：进度对比/出勤链/社交问责/竞赛。",
        measure="问卷 + 访谈（「什么事你曾长期坚持过，为什么」）",
        sources=["Deci & Ryan (2000)"],
    ),
    KnowledgeEntry(
        id="d_consistency_history",
        kind=EntryKind.DIFFERENCE,
        category="behavioral",
        title="既往坚持/放弃模式",
        summary="过去的放弃点（第几周、什么原因）是未来中断风险的最直接预测源。",
        design_implication="在历史放弃点前主动减载并加强支持。",
        measure="行为史访谈（过去的尝试与中断经历）",
        sources=["Prochaska & DiClemente, 跨理论模型 (1983)"],
    ),
    KnowledgeEntry(
        id="d_self_efficacy",
        kind=EntryKind.DIFFERENCE,
        category="psychological",
        title="自我效能",
        summary="对「我能做到」的信念预测启动与坚持。",
        design_implication="新手期用低门槛快速成功喂饱效能感。",
        measure="问卷（一般自我效能量表简版）",
        sources=["Bandura (1997)"],
    ),
    KnowledgeEntry(
        id="d_prior_level",
        kind=EntryKind.DIFFERENCE,
        category="cognitive",
        title="领域先验水平",
        summary="当前能力决定起点与递进速度。",
        design_implication="摸底决定起始负荷；具体测评由领域包提供。",
        measure="领域包摸底测评（如健身的动作/体适能摸底）",
        sources=["Ericsson & Pool, Peak (2016)"],
        source_work="peak",
    ),
]


class HumanKnowledgeBase:
    """人性知识库：运行时只读索引。硬规则供代码强制执行，软知识注入 LLM。"""

    def __init__(self, entries: list[KnowledgeEntry]):
        self._entries: dict[str, KnowledgeEntry] = {e.id: e for e in entries}

    @classmethod
    def kernel(cls) -> "HumanKnowledgeBase":
        """精选内核 v0（M1 起由 humanity/ 已审核条目加载生成）。"""
        return cls(_KERNEL)

    def get(self, entry_id: str) -> KnowledgeEntry:
        return self._entries[entry_id]

    def has(self, entry_id: str) -> bool:
        return entry_id in self._entries

    def universals(self) -> list[KnowledgeEntry]:
        return [e for e in self._entries.values() if e.kind == EntryKind.UNIVERSAL]

    def differences(self) -> list[KnowledgeEntry]:
        return [e for e in self._entries.values() if e.kind == EntryKind.DIFFERENCE]

    def hard_rules(self) -> list[KnowledgeEntry]:
        return [e for e in self._entries.values() if e.is_hard_rule]

    def summary(self) -> str:
        """软上下文：给 LLM 的人性知识摘要（M1+ 注入计划生成）。"""
        lines = []
        for e in self._entries.values():
            tag = "硬规则" if e.is_hard_rule else "软知识"
            lines.append(f"- [{e.kind.value}/{e.category}/{tag}] {e.title}：{e.design_implication}")
        return "\n".join(lines)


def recovery_budget(sleep_hours: float, stress_level: str) -> float:
    """恢复预算硬规则（由 u_recovery_supercompensation 编译）：返回强度系数 0-1。

    计划生成中，任何一次训练的强度不得超过该系数。
    M3 将加入更多输入：连续训练天数、RPE 轨迹、自报恢复感。
    """
    budget = 1.0
    if sleep_hours < 6.0:
        budget = min(budget, 0.5)
    elif sleep_hours < 7.0:
        budget = min(budget, 0.7)
    if stress_level == "high":
        budget = min(budget, 0.6)
    elif stress_level == "mid":
        budget = min(budget, 0.85)
    return budget
