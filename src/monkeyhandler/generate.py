"""D4 生成链路：问卷 → 画像 → 领域调研 → LLM → InstanceSpec → 单页 HTML 实例。

纪律（2026-09-30 创始人裁决）：**只有 LLM 路径**——未配置 LLM 或输出两次不合法时
明确报错，不静默降级到规则模板（与 NullLLM 的「明确报错而非降级假象」一致）。
硬规则由代码强制：恢复预算上限约束 intensity（LLM 输出超限即钳制并记入安全注记）。

D17（2026-10-03 创始人裁决）：**按目标动态调研**——每种训练目标出现时，先调研该
领域最相关的三本著作，依托其方法论拆解目标；计划的每个练习项必须标注依据（src
引用所列著作），不可追溯的细节不进计划。理论只在适用范围内迁移：身体域与
非身体域的保护文案由调研判定（is_physical）分流，健身文案不进认知域。
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
    src: str = ""  # D17：依据——《著作》要点；每个细节必须可溯源
    how: list[str] = Field(default_factory=list)  # D18：操作步骤（3-6 步，可独立成页）
    mistake: str = ""  # D18：新手常见错误与自检


class DayPlan(BaseModel):
    day: int
    phase: str
    focus: str
    items: list[ExerciseItem] = Field(default_factory=list)


class WorkRef(BaseModel):
    """D17：支撑本计划的方法论著作（由调研阶段产出）。"""

    title: str
    author: str = ""
    year: str = ""
    why: str = ""  # 为什么与该目标相关
    methods: list[str] = Field(default_factory=list)  # 提炼出的计划设计原则


class InstanceSpec(BaseModel):
    goal: str
    horizon_days: int
    intensity: float = Field(ge=0.0, le=1.0)
    rationale: str = ""
    days: list[DayPlan] = Field(default_factory=list)
    safety: list[str] = Field(default_factory=list)
    works: list[WorkRef] = Field(default_factory=list)
    is_physical: bool = True


class GoalResearch(BaseModel):
    """D17 调研阶段的结构化产出。"""

    is_physical: bool = False
    works: list[WorkRef] = Field(default_factory=list)
    failure_modes: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# 生成器
# ---------------------------------------------------------------------------
class InstanceGenerator:
    """把「目标 + 问卷答案」经调研与 LLM 变成可运行的单页训练实例。

    LLM 负责内容（调研、练习、节奏、rationale、src）；结构校验、天数连续性、
    恢复预算钳制、依据引用完整性与安全文案由代码强制。输出两次不合法 → 明确报错。
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
                 history: str = "", progress=None) -> tuple[UserModel, InstanceSpec, str]:
        """progress: 可选回调 progress(pct:int, text:str)——调研/编排阶段推送给界面。"""
        if self.llm is None:
            raise LLMUnavailable(
                "现在还生成不了：这台设备还没有连接 AI 服务。"
                "打开主平台 → 设置，填好接口地址和密钥（约一分钟）就好。"
            )
        user = self.build_profile(goal, answers)
        sleep = float(user.text("sleep_hours", "7.5") or 7.5)
        stress = user.text("stress_level", "mid") or "mid"
        cap = recovery_budget(sleep, stress)
        if progress:
            progress(10, "调研领域著作中……")
        research = self._research(goal, user)
        if progress:
            progress(45, f"调研完成：《{research.works[0].title}》《{research.works[1].title}》"
                         f"《{research.works[2].title}》——编排计划中……")
        spec = self._llm_spec(user, goal, horizon_days, cap, research=research,
                              history=history, progress=progress)
        if progress:
            progress(88, "校验依据与渲染实例中……")
        return user, spec, "llm"

    # ---- D17 调研阶段 -----------------------------------------------------
    RESEARCH_SYSTEM = (
        "你是 MonkeyHandler 的领域调研员。针对训练目标，调研该领域最相关的三本著作："
        "必须真实存在、作者与内容你确信无误，优先该领域公认的奠基或权威著作；"
        "不确定的书宁可换成更稳的。从每本提炼可直接指导「把目标拆解为训练计划」的"
        "方法论要点——要计划设计原则，不要内容知识点。同时判断目标是否属于身体训练域"
        "（决定保护规则文案），并给出该领域新手最常见的失败模式与必要的安全注意事项。"
        "只输出合法 JSON，无 markdown 围栏。"
    )

    def _research(self, goal: str, user: UserModel) -> GoalResearch:
        prompt = (
            f"训练目标：{goal}\n\n用户画像摘要：\n{user.summary()}\n\n硬要求：\n"
            f"- works 恰好 3 本；why ≤40 字说明与该目标的相关性；"
            f"methods 2-4 条、每条 ≤20 字，必须是可操作的计划设计原则\n"
            f"- failure_modes 2-4 条（该领域新手最常见的失败模式，每条 ≤24 字）\n"
            f"- safety_notes 0-4 条（该领域必要的安全注意，每条 ≤30 字）\n"
            f"- is_physical：该目标是否以身体训练为主\n\n"
            '输出 JSON：{"is_physical": bool, "works": [{"title": str, "author": str, '
            '"year": str, "why": str, "methods": [str]}], "failure_modes": [str], '
            '"safety_notes": [str]}'
        )
        last_err: str | None = None
        for attempt in range(self.MAX_ATTEMPTS):
            try:
                research = self.llm.complete_json(self.RESEARCH_SYSTEM, prompt, GoalResearch)  # type: ignore[union-attr]
                self._validate_research(research)
                return research
            except Exception as e:
                last_err = str(e)
        raise LLMUnavailable(
            f"AI 连续两次都无法完成领域调研（{last_err}）。请重试一次；"
            f"如果反复出现，到设置里换一个模型，或者稍后再试。"
        )

    @staticmethod
    def _validate_research(research: GoalResearch) -> None:
        for w in research.works:
            w.title = w.title.strip().strip("《》").strip()
        if len(research.works) != 3:
            raise ValueError(f"依据著作必须恰好 3 本，实际 {len(research.works)}")
        if any(not w.title.strip() for w in research.works):
            raise ValueError("著作缺少书名")
        if any(not w.methods for w in research.works):
            raise ValueError(f"《{research.works[[i for i, w in enumerate(research.works) if not w.methods][0]].title}》缺少方法论要点")

    # ---- 计划阶段 ---------------------------------------------------------
    GEN_SYSTEM = (
        "你是 MonkeyHandler 的训练计划生成器。原则：逆向设计（先能力证据后活动）、"
        "难度缓坡、依从性优先、强度缓坡递进并含减量日；"
        "每个练习项都必须标注依据（src 引用给定的三本著作之一），"
        "不可追溯的细节不进计划。练习内容为通用常识并如实标注，不构成专业建议，"
        "不承诺效果；出现疼痛类内容时以停止与就医建议回应。只输出合法 JSON，无 markdown 围栏。"
    )

    def _llm_spec(self, user: UserModel, goal: str, horizon: int, cap: float,
                  research: GoalResearch, history: str = "",
                  progress=None) -> InstanceSpec:
        """整期计划编排。超过 CHUNK_DAYS 天时分段生成（防输出截断——D17 实测 28 天超限）。"""
        works_block = "\n".join(
            f"- 《{w.title}》{w.author}{'（' + w.year + '）' if w.year else ''}：{'；'.join(w.methods)}"
            for w in research.works
        )
        level = (user.text("training_experience", "none") or "none").strip().lower()
        base = {"none": 0.5, "some": 0.65, "experienced": 0.75}.get(level, 0.5)
        common = (
            f"训练目标：{goal}\n\n用户画像：\n{user.summary()}\n\n"
            f"三本依据著作与方法论要点（拆解逻辑与每项 src 必须引用它们）：\n{works_block}\n\n"
            f"该领域新手常见失败模式（设计时主动规避）：{'；'.join(research.failure_modes) or '（无）'}\n\n"
            f"硬约束：\n"
            f"- intensity（整期起始强度 0-1）参考 {base:.2f}（按无经验水平），硬上限 {cap:.2f}（恢复预算）\n"
            f"- 每天一个训练日，含 3-6 个练习项（items），每项含 name/dur/cue/why/src/how/mistake\n"
            f"- src ≤24 字，必须包含某本著作的书名并给出要点（例：《刻意练习》目标-反馈-小步）\n"
            f"- how：操作步骤数组，3-6 步、每步 ≤30 字——写清身体位置/动作次序/呼吸/节奏，"
            f"让没做过的人能照着做；认知域则写清打开什么、输入什么、产出到哪里；步骤须与 src 所引方法一致\n"
            f"- mistake：新手最常见错误与自检方法，≤30 字\n"
            f"- 输出长度纪律（防截断）：why 每项 ≤14 字且相邻天可重复；cue ≤18 字；focus ≤16 字；rationale ≤80 字\n"
            f"- 语言纪律：所有字段用中文；phase 用中文命名（例：适应期/稳定期/巩固期）；dur 用中文格式（例：「30 分钟」）\n"
            f"- 若提供了既往执行数据：rationale 必须至少引用其中一项具体观察，并说明本期据此做了什么调整\n\n"
            f"既往执行数据（本机回程，来自 TA 过去的训练平台）：\n{history or '（首期，无既往记录）'}\n\n"
        )
        schema_json = (
            '{"goal": str, "horizon_days": int, "intensity": float, "rationale": str, '
            '"days": [{"day": int, "phase": str, "focus": str, '
            '"items": [{"name": str, "dur": str, "cue": str, "why": str, "src": str, '
            '"how": [str], "mistake": str}]}]}'
        )

        def _attempt(prompt: str) -> InstanceSpec:
            spec = self.llm.complete_json(self.GEN_SYSTEM, prompt, InstanceSpec)  # type: ignore[union-attr]
            spec.works = research.works
            spec.is_physical = research.is_physical
            return spec

        def _run_with_retry(build: callable, validate) -> InstanceSpec:
            last_err: str | None = None
            for _ in range(self.MAX_ATTEMPTS):
                prompt = build() if last_err is None else build() + (
                    f"\n\n注意：你上一次的输出未通过校验（{self._short(last_err)}），请修正后重新输出完整 JSON。")
                try:
                    spec = _attempt(prompt)
                    validate(spec)
                    return spec
                except Exception as e:
                    last_err = str(e)
            raise LLMUnavailable(
                f"AI 连续两次给出的计划都无法使用（{self._short(last_err)}）。请重试一次；"
                f"如果反复出现，到设置里换一个模型，或者稍后再试。")

        def _validate_chunk_days(spec: InstanceSpec, a: int, b: int) -> None:
            if [x.day for x in spec.days] != list(range(a, b + 1)):
                raise ValueError(f"days 必须从 {a} 连续到 {b}")
            if any(not x.items for x in spec.days):
                raise ValueError("存在空训练日")

        if horizon <= self.CHUNK_DAYS:
            def build() -> str:
                return (common +
                        f"整期共 {horizon} 天，三阶段推进（适应→稳定→巩固），末段安排减量日；"
                        f"days 从 day=1 连续到 {horizon}。\n\n输出 JSON 结构：\n" + schema_json)
            spec = _run_with_retry(build, lambda s: self._validate(s, horizon, cap, research))
            return spec

        # 长周期：分段生成（每段带前文衔接，避免输出超限截断）
        ranges = [(a, min(a + self.CHUNK_DAYS - 1, horizon))
                  for a in range(1, horizon + 1, self.CHUNK_DAYS)]
        taper_from = horizon - max(2, round(horizon * 0.1)) + 1
        merged_days: list[DayPlan] = []
        intensity: float | None = None
        rationale = ""
        for i, (a, b) in enumerate(ranges):
            if progress:
                progress(45 + int(40 * i / len(ranges)),
                         f"编排计划中（第 {i + 1}/{len(ranges)} 段：第 {a}–{b} 天）……")
            tail = ""
            if merged_days:
                last = merged_days[-1]
                tail = (f"已生成的最后一天（衔接用）：第 {last.day} 天 · {last.phase} · {last.focus}；"
                        f"练习：{'、'.join(it.name for it in last.items)}。\n\n")
            chunk = _run_with_retry(
                lambda: (common +
                         f"整期共 {horizon} 天；三阶段推进（适应→稳定→巩固），第 {taper_from} 天起为减量段——"
                         f"阶段命名与强度推进要与整期规划一致。\n"
                         f"你负责第 {a} 到第 {b} 天：days 只含 day={a}..{b}，共 {b - a + 1} 天。\n"
                         f"rationale ≤80 字（{'本段是整期开头，说明整期「目标→能力证据→活动」拆解链条' if a == 1 else '可沿用前段，一句话即可'}）。\n"
                         + tail + "输出 JSON 结构：\n" + schema_json),
                lambda s: _validate_chunk_days(s, a, b))
            merged_days.extend(chunk.days)
            if intensity is None:
                intensity, rationale = chunk.intensity, chunk.rationale
        spec = InstanceSpec(goal=goal, horizon_days=horizon, intensity=intensity or base,
                            rationale=rationale, days=merged_days)
        spec.works = research.works
        spec.is_physical = research.is_physical
        self._validate(spec, horizon, cap, research)
        return spec

    CHUNK_DAYS = 7  # how/mistake 加入后单项输出变大，段调小防截断

    @staticmethod
    def _short(text: str, n: int = 140) -> str:
        return text if len(text) <= n else text[:n] + "……"

    @staticmethod
    def _normalize(text: str) -> str:
        return text.replace("《", "").replace("》", "").replace(" ", "").strip().lower()

    @staticmethod
    def _validate(spec: InstanceSpec, horizon: int, cap: float, research: GoalResearch) -> None:
        if spec.horizon_days != horizon:
            raise ValueError(f"horizon_days 应为 {horizon}，实际 {spec.horizon_days}")
        if [x.day for x in spec.days] != list(range(1, horizon + 1)):
            raise ValueError("days 编号必须从 1 连续到 horizon_days")
        if any(not x.items for x in spec.days):
            raise ValueError("存在空训练日")
        if spec.intensity > cap + 1e-9:
            spec.intensity = round(cap, 2)
            spec.safety.append("模型给出的强度超出了恢复保护上限，已自动调低")
        # D17：逐项依据校验——src 必须存在且引用所列著作
        titles = [InstanceGenerator._normalize(w.title) for w in spec.works]
        for x in spec.days:
            for it in x.items:
                if not it.src.strip():
                    raise ValueError(f"第 {x.day} 天「{it.name}」缺少依据（src）")
                if not any(t and t in InstanceGenerator._normalize(it.src) for t in titles):
                    raise ValueError(f"第 {x.day} 天「{it.name}」的依据未引用三本著作之一")
                # D18：操作步骤校验——没有 how 的步骤开不了详解页
                steps = [s.strip() for s in it.how if s.strip()]
                if not 2 <= len(steps) <= 6:
                    raise ValueError(f"第 {x.day} 天「{it.name}」的 how 需要 2-6 步操作分解")
                if any(len(s) > 50 for s in steps):
                    raise ValueError(f"第 {x.day} 天「{it.name}」的 how 有步骤超过 50 字")
        # 保护文案分流（D17：理论只在适用范围内迁移——健身文案不进非身体域）
        if spec.is_physical:
            for line in ("疼痛 ≥4：停止加量并就医评估", "通用运动常识，不构成医疗处方",
                         "专向训练需专业评估（如施罗斯疗法）"):
                if line not in spec.safety:
                    spec.safety.append(line)
        else:
            universal = "本计划为训练设计，不构成专业建议；持续受挫或不适时降低强度或暂停"
            spec.safety = [s for s in spec.safety if s not in (
                "疼痛 ≥4：停止加量并就医评估", "通用运动常识，不构成医疗处方",
                "专向训练需专业评估（如施罗斯疗法）")]
            if universal not in spec.safety:
                spec.safety.insert(0, universal)
            for s in research.safety_notes[:4]:
                if s not in spec.safety:
                    spec.safety.append(s)
