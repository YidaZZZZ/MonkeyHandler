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

    def generate(self, goal: str, answers: dict[str, str], horizon_days: int = 20,
                 history: str = "") -> tuple[UserModel, InstanceSpec, str]:
        if self.llm is None:
            raise LLMUnavailable(
                "现在还生成不了：这台设备还没有连接 AI 服务。"
                "打开主平台 → 设置，填好接口地址和密钥（约一分钟）就好。"
            )
        user = self.build_profile(goal, answers)
        sleep = float(user.text("sleep_hours", "7.5") or 7.5)
        stress = user.text("stress_level", "mid") or "mid"
        cap = recovery_budget(sleep, stress)
        spec = self._llm_spec(user, goal, horizon_days, cap, history=history)
        return user, spec, "llm"

    GEN_SYSTEM = (
        "你是 MonkeyHandler 的训练计划生成器。原则：逆向设计（先能力证据后活动）、"
        "难度缓坡、动作模式优先、依从性优先、强度缓坡递进并含减量日；"
        "练习内容为通用运动常识并如实标注，不构成医疗处方，不承诺治愈，"
        "出现疼痛类内容时以停止与就医建议回应。只输出合法 JSON，无 markdown 围栏。"
    )

    def _llm_spec(self, user: UserModel, goal: str, horizon: int, cap: float,
                  history: str = "") -> InstanceSpec:
        level = (user.text("training_experience", "none") or "none").strip().lower()
        base = {"none": 0.5, "some": 0.65, "experienced": 0.75}.get(level, 0.5)
        base_prompt = (
            f"训练目标：{goal}\n\n用户画像：\n{user.summary()}\n\n硬约束：\n"
            f"- horizon_days 必须等于 {horizon}；days 数组从 day=1 连续编号到 {horizon}\n"
            f"- intensity（起始强度 0-1）参考 {base:.2f}（按无经验水平），硬上限 {cap:.2f}（恢复预算）\n"
            f"- 每天一个训练日，含 3-6 个练习项（items），每项含 name/dur/cue/why\n"
            f"- 输出长度纪律（防截断）：why 每项 ≤14 字且相邻天可重复；cue ≤18 字；focus ≤16 字；rationale ≤80 字\n"
            f"- 语言纪律：所有字段用中文；phase 用中文命名（例：适应期/稳定期/巩固期）；dur 用中文格式（例：「30 秒 ×2/侧」「8 次 ×2」）\n"
            f"- 三阶段推进（适应→稳定→巩固），末段安排减量日；rationale 说明依据\n"
            f"- 若提供了既往执行数据：rationale 必须至少引用其中一项具体观察，并说明本期据此做了什么调整\n\n"
            f"既往执行数据（本机回程，来自 TA 过去的训练平台）：\n{history or '（首期，无既往记录）'}\n\n"
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
        raise LLMUnavailable(
            f"AI 连续两次给出的计划都无法使用（{last_err}）。请重试一次；"
            f"如果反复出现，到设置里换一个模型，或者稍后再试。"
        )

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
        for line in ("疼痛 ≥4：停止加量并就医评估", "通用运动常识，不构成医疗处方",
                     "专向训练需专业评估（如施罗斯疗法）"):
            if line not in spec.safety:
                spec.safety.append(line)
