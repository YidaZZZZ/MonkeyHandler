"""MonkeyHandler 命令行入口。"""
from __future__ import annotations

import typer

from .core.engine import CoachEngine
from .domains.fitness.pack import FitnessPack
from .domains.fitness.research import FitnessOfflineResearch

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


def main() -> None:
    app()


if __name__ == "__main__":
    main()
