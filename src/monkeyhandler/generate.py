"""D4 生成链路：问卷 → 画像 → InstanceSpec（LLM 或 规则）→ 单页 HTML 实例。

两条例行纪律（philosophy §〇 / being-seen §五）：
- 离线路径是独立支持的一等公民，不是降级假象：无 LLM 配置时走规则模板生成；
- LLM 只负责内容填充，结构、硬规则（恢复预算上限）与安全文本由代码强制。
"""
from __future__ import annotations

import datetime as _dt

from pydantic import BaseModel, Field

from .core.humanity import HumanKnowledgeBase, recovery_budget
from .core.llm import LLMProvider
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
# 离线规则路径的练习库（通用运动常识；与 demo 同源，zh）
# ---------------------------------------------------------------------------
LIB: dict[str, dict[str, str]] = {
    "ab":      {"n": "腹式呼吸", "dur": "90 秒 ×2", "cue": "手放腹部，鼻吸 4 秒、口呼 6 秒。", "why": "呼吸模式是姿势与核心激活的底层（通用常识）。"},
    "lat":     {"n": "侧向呼吸", "dur": "60 秒 ×2/侧", "cue": "手放肋侧，吸气把肋骨推向手掌。", "why": "唤醒侧胸廓，两侧对比觉察（通用常识）。"},
    "catcow":  {"n": "猫牛式", "dur": "8 次 ×2", "cue": "呼气弓背、吸气塌腰，放慢。", "why": "温和恢复脊柱分段活动度（通用常识）。"},
    "twist":   {"n": "仰卧脊柱旋转", "dur": "6 次 ×2/侧", "cue": "屈膝倒向一侧，双肩贴地。", "why": "仰卧位胸椎旋转活动度（通用常识）。"},
    "childs":  {"n": "婴儿式放松", "dur": "60 秒", "cue": "臀坐脚跟，呼吸放到背部。", "why": "背部整体拉伸放松（通用常识）。"},
    "sidest":  {"n": "站姿侧向拉伸", "dur": "30 秒 ×2/侧", "cue": "手臂过头向对侧弯，骨盆稳定。", "why": "躯干两侧张力的对称练习（通用常识）。"},
    "wall":    {"n": "靠墙站立检查", "dur": "2 分钟", "cue": "后脑/上背/臀三点贴墙，收下颌。", "why": "建立每天可对照的姿势基线（通用常识）。"},
    "scap":    {"n": "肩胛后缩", "dur": "10 次 ×2", "cue": "挺胸夹背 2 秒，不耸肩。", "why": "激活上背姿势肌（通用常识）。"},
    "deadbug": {"n": "死虫式", "dur": "6 次 ×2/侧", "cue": "腰贴地，对侧手脚缓慢伸展。", "why": "抗伸展核心稳定（通用常识）。"},
    "birddog": {"n": "鸟狗式", "dur": "6 次 ×2/侧", "cue": "腰保持中立，手脚同起同落。", "why": "抗旋转稳定与髋背协调（通用常识）。"},
    "plank":   {"n": "跪姿平板", "dur": "20-30 秒 ×2", "cue": "肩腕垂直，收腹，塌腰即停。", "why": "前链核心耐力，低负荷起步（通用常识）。"},
    "sidebr":  {"n": "跪姿侧桥", "dur": "15 秒 ×2/侧", "cue": "肘膝支撑，髋部抬起成一线。", "why": "侧腹链耐力；方向性强化需专业评估（通用常识）。"},
    "ham":     {"n": "腘绳肌拉伸", "dur": "45 秒/侧", "cue": "微屈膝前屈，酸胀可忍、不痛。", "why": "释放骨盆后链张力（通用常识）。"},
    "hip":     {"n": "屈髋肌拉伸", "dur": "45 秒/侧", "cue": "弓步收腹收臀再前移。", "why": "改善久坐屈髋张力（通用常识）。"},
    "thor":    {"n": "四足胸椎旋转", "dur": "8 次 ×2/侧", "cue": "手扶头，肘找对侧手腕。", "why": "胸椎旋转活动度（通用常识）。"},
    "angel":   {"n": "靠墙天使", "dur": "8 次 ×2", "cue": "背贴墙，手臂沿墙滑动。", "why": "肩胛上回旋模式（通用常识）。"},
    "ytw":     {"n": "俯卧 Y-T-W", "dur": "6 次 ×2", "cue": "沉肩，肩胛带动手臂。", "why": "下斜方与肩袖姿势肌群（通用常识）。"},
    "balance": {"n": "单腿站立", "dur": "30 秒 ×2/侧", "cue": "髋水平，视线固定。", "why": "姿势反射与本体感觉（通用常识）。"},
    "walk":    {"n": "步行摆臂觉察", "dur": "2 分钟", "cue": "正常走，注意两侧摆臂对称。", "why": "把姿势觉察迁移到步态（通用常识）。"}
}
POOLS: dict[int, list[str]] = {
    1: ["ab", "catcow", "wall", "twist", "sidest", "childs", "lat", "scap"],
    2: ["ab", "lat", "deadbug", "birddog", "plank", "sidebr", "ham", "hip", "thor", "angel"],
    3: ["ab", "angel", "birddog", "ytw", "balance", "walk", "sidest", "ham", "thor"],
}
PHASE_NAMES = {1: "适应与觉察", 2: "建立稳定", 3: "巩固与迁移"}
FOCUS = {
    1: {"zh": "呼吸模式 · 脊柱活动度 · 姿势觉察", "en": "breathing · mobility · awareness"},
    2: {"zh": "核心与背部耐力 · 对称性力量", "en": "core & back endurance · symmetric strength"},
    3: {"zh": "日常姿势迁移 · 自主练习", "en": "daily transfer · autonomy"},
}


def _phase_of(day: int, horizon: int) -> int:
    if day <= max(1, round(horizon * 0.30)):
        return 1
    if day <= max(2, round(horizon * 0.70)):
        return 2
    return 3


def _rule_days(user: UserModel, horizon: int, tier_max: int, recovery: bool) -> list[DayPlan]:
    days: list[DayPlan] = []
    for d in range(1, horizon + 1):
        ph = _phase_of(d, horizon)
        pool = POOLS[ph]
        count = 3 if recovery else (4 if tier_max == 1 else (5 if tier_max == 2 else 6))
        picked: list[str] = []
        k = 0
        while len(picked) < count and k < len(pool) * 2:
            ex_id = pool[(d * 2 + k) % len(pool)]
            if ex_id not in picked:
                picked.append(ex_id)
            k += 1
        items = [ExerciseItem(name=LIB[e]["n"], dur=LIB[e]["dur"], cue=LIB[e]["cue"], why=LIB[e]["why"])
                 for e in picked]
        days.append(DayPlan(day=d, phase=PHASE_NAMES[ph], focus=FOCUS[ph]["zh"], items=items))
    return days


def _taper(day: int, horizon: int) -> bool:
    return horizon >= 6 and day > horizon - max(2, round(horizon * 0.1))


# ---------------------------------------------------------------------------
# 生成器
# ---------------------------------------------------------------------------
class InstanceGenerator:
    """把「目标 + 问卷答案」变成一个可运行的单页训练实例。

    LLM 路径：内容（练习、节奏、rationale）由模型按约束生成，经 pydantic 校验；
    规则路径：无 LLM 或 LLM 输出不合法时的离线回退——结构与安全规则仍由代码保证。
    """

    def __init__(self, domain_pack: FitnessPack, llm: LLMProvider | None = None, kb: HumanKnowledgeBase | None = None):
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
        user = self.build_profile(goal, answers)
        sleep = float(user.text("sleep_hours", "7.5") or 7.5)
        stress = user.text("stress_level", "mid") or "mid"
        cap = recovery_budget(sleep, stress)
        level = (user.text("training_experience", "none") or "none").strip().lower()
        tier_max = {"none": 2, "some": 3, "experienced": 3}[level]
        recovery = cap < 0.85
        via = "rule"
        spec: InstanceSpec | None = None
        if self.llm is not None:
            try:
                spec = self._llm_spec(user, goal, horizon_days, cap, tier_max)
                via = "llm"
            except Exception:
                spec = None
        if spec is None:
            spec = self._rule_spec(user, goal, horizon_days, cap, tier_max, recovery, level)
        return user, spec, via    # ---- LLM 路径 -------------------------------------------------------
    GEN_SYSTEM = (
        "你是 MonkeyHandler 的训练计划生成器。原则：逆向设计（先能力证据后活动）、"
        "难度缓坡、动作模式优先、依从性优先、强度缓坡递进并含减量日；"
        "练习内容为通用运动常识并如实标注，不构成医疗处方，不承诺治愈，"
        "出现疼痛类内容时以停止与就医建议回应。只输出合法 JSON，无 markdown 围栏。"
    )

    def _llm_spec(self, user: UserModel, goal: str, horizon: int, cap: float, tier_max: int) -> InstanceSpec:
        prompt = (
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
        spec = self.llm.complete_json(self.GEN_SYSTEM, prompt, InstanceSpec)  # type: ignore[union-attr]
        if len(spec.days) != horizon or [x.day for x in spec.days] != list(range(1, horizon + 1)):
            raise ValueError("LLM 输出的天数与要求不一致")
        if any(not x.items for x in spec.days):
            raise ValueError("LLM 输出存在空训练日")
        return spec

    # ---- 规则路径 -------------------------------------------------------
    def _rule_spec(self, user: UserModel, goal: str, horizon: int, cap: float,
                   tier_max: int, recovery: bool, level: str) -> InstanceSpec:
        base = {"none": 0.5, "some": 0.65, "experienced": 0.75}.get(level, 0.5)
        intensity = round(min(base, cap), 2)
        limited = "恢复预算" if cap < base else "起始水平"
        days = _rule_days(user, horizon, tier_max, recovery)
        taper_from = horizon - max(2, round(horizon * 0.1)) + 1
        for day in days:
            if _taper(day.day, horizon):
                day.focus = "减量日：只做动作质量 · " + day.focus
        rationale = (
            f"画像：经验 {level}、起始强度 {intensity:.2f}（受限于{limited}）；"
            f"结构：三阶段推进（适应→稳定→巩固），强度缓坡，第 {taper_from} 天起减量"
            f"（恢复预算硬规则同源）；动机设计按自报取向。"
            f"离线规则版：练习内容为通用运动常识模板，LLM 可用时将按同一约束生成个性化内容。"
        )
        return InstanceSpec(
            goal=goal, horizon_days=horizon, intensity=intensity, rationale=rationale,
            days=days,
            safety=["疼痛 ≥4：停止加量并就医评估", "出现尖锐疼痛立即停止", "专向训练需专业评估（如施罗斯疗法）"],
        )


def lang_taper() -> str:
    return "减量日：只做动作质量"
