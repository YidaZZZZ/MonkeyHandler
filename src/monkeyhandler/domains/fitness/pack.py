"""健身领域包：第一个内置领域（DomainPack 参考实现）。

M0 为规则版：离线模板 + 人性知识库硬规则（恢复预算），不依赖 LLM，
即使没有 API key 也能完整跑通「画像 → 领域知识 → 计划」。
M1-M2 逐步替换为「LLM + 真实调研」驱动，本文件保留作为契约参考。
"""
from __future__ import annotations

from ...core.domain import DomainPack
from ...core.humanity import recovery_budget
from ...core.plan import Load, Phase, Plan, Session
from ...core.profiling import Question
from ...core.research import DomainProfile
from ...core.user_model import Dimension, UserModel

# 按动作模式组织（而非按肌群），对新手更稳、认知负担更低
_PATTERNS = {
    "squat": "深蹲模式（杯式深蹲/箱式深蹲）",
    "hinge": "髋铰链（罗马尼亚硬拉/臀桥）",
    "push": "水平推（俯卧撑/卧推）",
    "pull": "水平拉（划船/弹力带划船）",
    "core": "抗伸展核心（平板支撑/死虫式）",
}

_PRESCRIPTION = {
    "none": "2-3 组 × 10-12 次（RPE 6，留 4 次余力）",
    "some": "3 组 × 8-10 次（RPE 6-7）",
    "experienced": "3-4 组 × 6-8 次（RPE 7-8）",
}

# 动机钩子按自报动机取向选型（d_motivation_orientation）
_HOOKS = {
    "progress": [
        "记录今天的重量/次数——只和上周的自己比（u_progress_competence）",
        "练后 30 秒写一句：今天哪里比上周轻松？（即时反馈，u_present_bias）",
        "翻开训练日志看看第一周——那是三个星期前的你",
    ],
    "streak": [
        "出勤本身就是胜利——延续你的连续记录（每一次行动都是给身份投票）",
        "今天只要求到场，热身完就算赢",
        "连续记录是一面镜子，照见你正在成为的人",
    ],
    "social": [
        "约一个训练伙伴，或把今天的完成发出去（自愿启用，u_social_commitment）",
        "找一位同路人，互相报本周出勤",
        "把计划告诉一个会追问你进度的人",
    ],
    "competition": [
        "给自己设一个小赌注：本周完成 X 次训练",
        "和上周的自己比赛：同动作多完成一次就算赢",
        "本周定一个跳一跳够得着的小目标，写下来给自己看",
    ],
}
_DEFAULT_HOOKS = _HOOKS["progress"]


class FitnessPack(DomainPack):
    id = "fitness"
    name = "健身训练"

    def research_brief(self, goal: str) -> str:
        return (
            f"围绕目标「{goal}」调研健身训练领域：1) 有证据支持的训练原则"
            "（渐进超负荷、训练分期、动作模式优先）；2) 新手最常见的失败模式与弃练原因"
            "（依从性研究）；3) 伤病预防与恢复（睡眠/减量周）；4) 不同器械条件下的替代方案。"
            "产出需逐主张标注证据等级并附引用。"
        )

    def profile_questions(self) -> list[Question]:
        """领域专属补充问题（通用核心集之外），同样必须声明 decision_point。"""
        return [
            Question(
                id="training_experience",
                text="训练经验如何？（none/some/experienced）",
                dimension=Dimension.COGNITIVE,
                decision_point="起始强度与分化模板（领域先验水平）",
                kb_entry="d_prior_level",
            ),
            Question(
                id="available_days_per_week",
                text="每周能保证几天训练？（2-6）",
                dimension=Dimension.PREFERENCE,
                decision_point="分化模板与每周频次",
            ),
            Question(
                id="equipment",
                text="可用器械条件？（gym/home_minimal/bodyweight）",
                dimension=Dimension.PREFERENCE,
                decision_point="动作库选型（每个动作模式的可行变体）",
            ),
            Question(
                id="injuries",
                text="有无伤病或需要回避的动作？",
                dimension=Dimension.PHYSIOLOGICAL,
                decision_point="动作回避与安全替换（安全类硬约束）",
            ),
        ]

    @classmethod
    def sample_answers(cls) -> dict[str, str]:
        """演示用答案集（真实使用中由问卷/访谈采集）。"""
        return {
            "name": "示例用户",
            "training_experience": "none",
            "available_days_per_week": "3",
            "equipment": "home_minimal",
            "injuries": "无",
            "sleep_hours": "7.5",
            "stress_level": "mid",
            "chronotype": "neither",
            "motivation_style": "progress",
            "consistency_history": "两次办卡都在第 3 周左右因加班中断",
            "time_budget": "5",
        }

    # ------------------------------------------------------------------
    def build_plan(self, user: UserModel, domain: DomainProfile, horizon_weeks: int = 4) -> Plan:
        days = self._days_per_week(user)
        level = self._level(user)
        base_intensity = {"none": 0.5, "some": 0.65, "experienced": 0.75}[level]

        # 人性知识库硬规则：恢复预算约束任何一次训练的强度上限
        sleep = self._float(user, "sleep_hours", 7.5)
        stress = user.text("stress_level", "mid") or "mid"
        cap = recovery_budget(sleep, stress)
        start_intensity = min(base_intensity, cap)
        limited_by = (
            f"恢复预算硬规则 u_recovery_supercompensation（睡眠 {sleep}h / 压力 {stress}）"
            if cap < base_intensity
            else "起始水平（先验摸底）"
        )

        style = user.text("motivation_style", "progress") or "progress"
        hooks = _HOOKS.get(style, _DEFAULT_HOOKS)

        phases = [
            Phase(
                name="基础适应" if level == "none" else "重建节奏",
                weeks=horizon_weeks,
                focus="动作质量与依从性优先，负荷缓坡递进",
            )
        ]

        templates = self._templates(days, level)
        sessions: list[Session] = []
        n = 0
        for week in range(1, horizon_weeks + 1):
            deload = horizon_weeks >= 4 and week == horizon_weeks
            ramp = 1.0 + 0.05 * (week - 1)
            week_intensity = min(base_intensity * ramp, cap)
            for day, (title, patterns) in enumerate(templates, start=1):
                n += 1
                content = ["热身：5 分钟快走/动态活动 + 轻组预热"]
                content += [f"{_PATTERNS[p]} · {_PRESCRIPTION[level]}" for p in patterns]
                if deload:
                    content.append("减量周：组数减半，只做动作质量，不追负荷")
                sessions.append(
                    Session(
                        id=f"s{n}",
                        week=week,
                        day=day,
                        title=f"{title}（第 {week} 周）",
                        objective="建立动作模式与出勤节奏" if level == "none" else "恢复节奏并缓坡加量",
                        content=content,
                        load=Load(
                            intensity=round(week_intensity * (0.7 if deload else 1.0), 2),
                            volume=len(patterns) * (2.5 if level == "none" else 3.0),
                            note="相对强度 0-1；M3 起由自报 RPE 校准",
                        ),
                        duration_min=45 if level == "none" else 60,
                        motivation_hook=(
                            "减量周是计划的一部分，不是失败（u_recovery_supercompensation）"
                            if deload
                            else hooks[(week + day) % len(hooks)]
                        ),
                    )
                )

        return Plan(
            goal=user.goal,
            horizon_weeks=horizon_weeks,
            phases=phases,
            sessions=sessions,
            rationale=self._rationale(
                user, domain, days, level, start_intensity, limited_by, horizon_weeks
            ),
        )

    # ------------------------------------------------------------------
    def _rationale(
        self,
        user: UserModel,
        domain: DomainProfile,
        days: int,
        level: str,
        start_intensity: float,
        limited_by: str,
        weeks: int,
    ) -> str:
        methods = "、".join(m.name for m in domain.training_methods) or "（离线占位，无真实方法引用）"
        parts = [
            f"画像：每周 {days} 练、经验 {level}、起始强度 {start_intensity:.2f}（受限于{limited_by}）",
            f"领域方法：{methods}",
            f"结构：强度按周缓坡递进（+5%/周），第 {weeks} 周减量（u_recovery_supercompensation）",
            "动机设计：按自报动机取向选钩子（u_progress_competence / u_present_bias / u_social_commitment）",
        ]
        history = user.text("consistency_history")
        if history:
            parts.append(
                f"历史放弃模式「{history}」→ M3 起将在对应时段主动减载并加强支持（d_consistency_history）"
            )
        return "；".join(parts)

    @staticmethod
    def _days_per_week(user: UserModel) -> int:
        raw = user.text("available_days_per_week", "3")
        try:
            return max(2, min(6, int(str(raw).strip())))
        except ValueError:
            return 3

    @staticmethod
    def _level(user: UserModel) -> str:
        value = (user.text("training_experience", "none") or "none").strip().lower()
        return value if value in ("none", "some", "experienced") else "none"

    @staticmethod
    def _float(user: UserModel, key: str, default: float) -> float:
        raw = user.text(key)
        try:
            return float(str(raw).strip())
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _templates(days: int, level: str) -> list[tuple[str, list[str]]]:
        if level == "none" or days <= 3:
            pool = [
                ("全身 A", ["squat", "push", "pull", "core"]),
                ("全身 B", ["hinge", "push", "pull", "core"]),
            ]
        elif days == 4:
            pool = [
                ("上肢", ["push", "pull", "core"]),
                ("下肢", ["squat", "hinge", "core"]),
            ]
        else:
            pool = [
                ("推", ["push", "core"]),
                ("拉", ["pull", "core"]),
                ("腿", ["squat", "hinge", "core"]),
            ]
        return [pool[i % len(pool)] for i in range(days)]
