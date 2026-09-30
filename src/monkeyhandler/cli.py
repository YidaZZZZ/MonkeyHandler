"""MonkeyHandler 命令行入口。"""
from __future__ import annotations

import datetime as _dt

import typer

from .core.engine import CoachEngine
from .domains.fitness.pack import FitnessPack
from .domains.fitness.research import FitnessOfflineResearch
from .generate import InstanceGenerator
from .render import render_instance

app = typer.Typer(help="MonkeyHandler：个体化学习/训练计划框架", no_args_is_help=True)


@app.callback()
def callback() -> None:
    """MonkeyHandler：个体化学习/训练计划框架。"""


@app.command()
def demo(
    goal: str = typer.Option("增肌减脂，改善体态", help="训练目标"),
    weeks: int = typer.Option(4, min=2, max=12, help="计划周期（周）"),
) -> None:
    """离线演示：示例画像 → 健身领域包 → 生成并打印训练计划（无需 LLM）。"""
    pack = FitnessPack()
    engine = CoachEngine(pack, research=FitnessOfflineResearch())
    user, domain, plan = engine.start(goal, pack.sample_answers(), horizon_weeks=weeks)

    kb = engine.humanity
    typer.echo("== MonkeyHandler 离线演示（M0 规则版，无 LLM）==")
    typer.echo(
        f"\n[人性知识库] 内核 {len(kb.universals()) + len(kb.differences())} 条："
        f"共性 {len(kb.universals())}（含硬规则 {len(kb.hard_rules())}）"
        f" / 个体差异维度 {len(kb.differences())}"
    )
    typer.echo(f"\n[画像] {len(user.attributes)} 条事实，全部携带证据（自报式）")
    typer.echo(user.summary())
    typer.echo(
        f"\n[领域] {pack.name} DomainProfile（离线占位；M2 接入逐主张验证的真实调研）"
        f"：{len(domain.training_methods)} 种方法 / {len(domain.failure_modes)} 条失败模式"
    )
    typer.echo(
        f"\n[计划] 目标：{plan.goal} · {plan.horizon_weeks} 周 · 共 {len(plan.sessions)} 次训练"
    )
    for week in range(1, plan.horizon_weeks + 1):
        typer.echo(f"\n-- 第 {week} 周 --")
        for s in plan.sessions_by_week(week):
            load = f"强度 {s.load.intensity:.2f}" if s.load else ""
            typer.echo(f"  D{s.day} {s.title}（{s.duration_min}min {load}）")
            for line in s.content:
                typer.echo(f"    - {line}")
            if s.motivation_hook:
                typer.echo(f"    ✦ {s.motivation_hook}")
    typer.echo(f"\n[计划依据] {plan.rationale}")


@app.command()
def generate(
    goal: str = typer.Option(..., "--goal", help="训练目标（一句话，例如：二十天从运动和拉伸层面缓解脊柱侧弯）"),
    days: int = typer.Option(20, "--days", min=3, max=60, help="周期天数"),
    time: int = typer.Option(20, "--time", min=5, max=120, help="每天可投入分钟数"),
    sleep: float = typer.Option(7.5, "--sleep", min=0, max=14, help="平均每晚睡眠小时数"),
    stress: str = typer.Option("mid", "--stress", help="近期压力：low/mid/high"),
    level: str = typer.Option("none", "--level", help="运动基础：none/some/experienced"),
    pain: str = typer.Option("no", "--pain", help="背部疼痛：no/some/often"),
    style: str = typer.Option("progress", "--style", help="激励取向：progress/streak/social/competition"),
    ai_config: str = typer.Option(None, "--ai-config", help="AI 配置 JSON 文件（base/key/model）；缺省读环境变量 MONKEYHANDLER_LLM_*，均无则离线规则生成"),
    out: str = typer.Option(None, "--out", help="输出 HTML 路径（默认 instances/ 下按时间命名）"),
) -> None:
    """D4 生成链路：问卷答案 → 画像 → （LLM 或 规则）→ 生成单页训练平台实例。"""
    import json as _json
    import os as _os
    import pathlib as _pl

    from .core.llm import OpenAICompatClient
    from .render import render_instance

    cfg = None
    if ai_config:
        cfg = _json.loads(_pl.Path(ai_config).read_text(encoding="utf-8"))
    else:
        b = _os.environ.get("MONKEYHANDLER_LLM_BASE_URL")
        k = _os.environ.get("MONKEYHANDLER_LLM_API_KEY")
        m = _os.environ.get("MONKEYHANDLER_LLM_MODEL")
        if b and k and m:
            cfg = {"base": b, "key": k, "model": m}
    llm = OpenAICompatClient(cfg["base"], cfg["key"], cfg["model"]) if cfg else None

    answers = {
        "training_experience": level,
        "available_days_per_week": "7",
        "equipment": "home_minimal",
        "injuries": "无" if pain == "no" else pain,
        "sleep_hours": str(sleep),
        "stress_level": stress,
        "chronotype": "neither",
        "motivation_style": style,
        "time_budget": str(time * 7),
    }
    gen = InstanceGenerator(FitnessPack(), llm=llm)
    user, spec, via = gen.generate(goal, answers, horizon_days=days)
    html = render_instance(goal=goal, spec=spec, user=user, via=via)
    if out:
        path = _pl.Path(out)
    else:
        stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M")
        path = _pl.Path("instances") / f"instance-{stamp}.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    typer.echo(f"已生成实例：{path}")
    typer.echo(f"生成路径：{via} · 天数：{len(spec.days)} · 起始强度：{spec.intensity:.2f}")
    typer.echo("双击该文件即可在浏览器中使用；数据仅保存在本机浏览器。")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
