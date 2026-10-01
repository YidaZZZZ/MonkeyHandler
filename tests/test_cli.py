"""CLI 分发冒烟测试（N10）：Typer 遮蔽 bug 曾让 generate 子命令在测试全绿时失效。"""
from __future__ import annotations

from typer.testing import CliRunner

from monkeyhandler.cli import app as cli_app

runner = CliRunner()


def test_cli_lists_subcommands() -> None:
    """分发器可达：--help 必须列出全部子命令。"""
    result = runner.invoke(cli_app, ["--help"])
    assert result.exit_code == 0
    for cmd in ("generate", "app", "demo"):
        assert cmd in result.output, f"子命令 {cmd} 未出现在 help 中"


def test_generate_dispatch_reaches_handler() -> None:
    """分发可达且进入处理器：无 AI 配置时应返回明确的人话报错（exit 1）。"""
    result = runner.invoke(
        cli_app,
        ["generate", "--goal", "测试目标"],
        env={"MONKEYHANDLER_LLM_BASE_URL": "", "MONKEYHANDLER_LLM_API_KEY": "", "MONKEYHANDLER_LLM_MODEL": ""},
    )
    assert result.exit_code == 1
    assert "未配置 AI 服务" in result.output
