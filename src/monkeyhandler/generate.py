"""D4 生成链路：问卷 → 画像 → LLM → InstanceSpec → 单页 HTML 实例。

纪律（2026-09-30 创始人裁决）：**只有 LLM 路径**——未配置 LLM 或输出两次不合法时
明确报错，不静默降级到规则模板（与 NullLLM 的「明确报错而非降级假象」一致）。
硬规则由代码强制：恢复预算上限约束 intensity（LLM 输出超限即钳制并记入安全注记）。
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from .core.humanity import HumanKnowledgeBase, recovery_budget
from .core.llm import LLMProvider, LLMUnavailable
from .core.profiling import Questionnaire, core_questions
from .core.user_model import UserModel
from .domains.fitness.pack import FitnessPack


# ---------------------------------------------------------------------------
# 生成物的数据模型（实例渲染器的输入契约）
# ---------------------------------------------------------------------------
class ExerciseItem(BaseModel):
    name: str
    dur: str = ""
    cue: str = ""
    why: str = ""


class DayPlan(BaseModel):
    day: int
    phase: str
    focus: str
    items: list[ExerciseItem] = Field(default_factory=list)


class InstanceSpec(BaseModel):
    goal: str
    horizon_days: int
    intensity: float = Field(ge=0.0, le=1.0)
    rationale: str = ""
    days: list[DayPlan] = Field(default_factory=list)
    safety: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# 生成器
# ---------------------------------------------------------------------------
class InstanceGenerator:
    """把「目标 + 问卷答案」经 LLM 变成可运行的单页训练实例。

    LLM 只负责内容填充（练习、节奏、rationale）；结构校验、天数连续性、
    恢复预算钳制与安全文本由代码强制。输出两次不合法 → 明确报错。
    """

    MAX_ATTEMPTS = 2

    def __init__(self, domain_pack: FitnessPack, llm: LLMProvider | None = None,
                 kb: HumanKnowledgeBase | None = None):
        self.pack = domain_pack
        self.llm = llm
        self.kb = kb or HumanKnowledgeBase.kernel()

    def questionnaire(self) -> Questionnaire:
        return Questionnaire(questions=core_questions(self.kb) + self.pack.profile_questions())

    def build_profile(self, goal: str, answers: dict[str, str]) -> UserModel:
        user = UserModel(goal=goal, display_name=answers.get("name", ""))
        self.questionnaire().collect(answers, user)
        return user

    def generate(self, goal: str, answers: dict[str, str], horizon_days: int = 20) -> tuple[UserModel, InstanceSpec, str]:
        if self.llm is None:
            raise LLMUnavailable(
                "未配置 LLM：请用 --ai-config 传入配置 JSON，或设置 MONKEYHANDLER_LLM_BASE_URL / "
                "MONKEYHANDLER_LLM_API_KEY / MONKEYHANDLER_LLM_MODEL（主平台「设置」页生成的配置可直接导出使用）。"
            )
        user = self.build_profile(goal, answers)
        sleep = float(user.text("sleep_hours", "7.5") or 7.5)
        stress = user.text("stress_level", "mid") or "mid"
        cap = recovery_budget(sleep, stress)
        spec = self._llm_spec(user, goal, horizon_days, cap)
        return user, spec, "llm"

    GEN_SYSTEM = (
        "你是 MonkeyHandler 的训练计划生成器。原则：逆向设计（先能力证据后活动）、"
        "难度缓坡、动作模式优先、依从性优先、强度缓坡递进并含减量日；"
        "练习内容为通用运动常识并如实标注，不构成医疗处方，不承诺治愈，"
        "出现疼痛类内容时以停止与就医建议回应。只输出合法 JSON，无 markdown 围栏。"
    )

    def _llm_spec(self, user: UserModel, goal: str, horizon: int, cap: float) -> InstanceSpec:
        base_prompt = (
            f"训练目标：{goal}\n\n用户画像：\n{user.summary()}\n\n硬约束：\n"
            f"- horizon_days 必须等于 {horizon}；days 数组从 day=1 连续编号到 {horizon}\n"
            f"- intensity（起始强度 0-1）不得超过 {cap:.2f}（恢复预算硬规则）\n"
            f"- 每天一个训练日，含 3-6 个练习项（items），每项含 name/dur/cue/why\n"
            f"- 三阶段推进（适应→稳定→巩固），末段安排减量日；rationale 说明依据\n"
            f"- 安全：通用运动常识；不承诺治愈；不使用医疗断言\n\n"
            "输出 JSON 结构："
            '{"goal": str, "horizon_days": int, "intensity": float, "rationale": str, '
            '"days": [{"day": int, "phase": str, "focus": str, '
            '"items": [{"name": str, "dur": str, "cue": str, "why": str}]}]}'
        )
        last_err: str | None = None
        for attempt in range(self.MAX_ATTEMPTS):
            prompt = base_prompt if last_err is None else (
                base_prompt + f"\n\n注意：你上一次的输出未通过校验（{last_err}），请修正后重新输出完整 JSON。"
            )
            try:
                spec = self.llm.complete_json(self.GEN_SYSTEM, prompt, InstanceSpec)  # type: ignore[union-attr]
                self._validate(spec, horizon, cap)
                return spec
            except Exception as e:
                last_err = str(e)
        raise LLMUnavailable(f"LLM 输出连续 {self.MAX_ATTEMPTS} 次未通过校验：{last_err}")

    @staticmethod
    def _validate(spec: InstanceSpec, horizon: int, cap: float) -> None:
        if spec.horizon_days != horizon:
            raise ValueError(f"horizon_days 应为 {horizon}，实际 {spec.horizon_days}")
        if [x.day for x in spec.days] != list(range(1, horizon + 1)):
            raise ValueError("days 编号必须从 1 连续到 horizon_days")
        if any(not x.items for x in spec.days):
            raise ValueError("存在空训练日")
        if spec.intensity > cap + 1e-9:
            spec.intensity = round(cap, 2)
            spec.safety.append("模型给出的强度超出了恢复保护上限，已自动调低")
