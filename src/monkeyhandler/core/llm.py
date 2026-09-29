"""LLM 层：可插拔、结构化输出。

M0 只定义端口与占位实现；M2 交付 OpenAI 兼容实现，通过环境变量配置：
    OPENCOACH_LLM_BASE_URL  # 可指向 GLM 等兼容端点
    OPENCOACH_LLM_API_KEY
    OPENCOACH_LLM_MODEL

约定：LLM 只被给予最小必要信息（画像摘要而非全量数据，见 user_model.summary），
结构化输出经 pydantic schema 校验，不合法则重试。
"""
from __future__ import annotations

from typing import Protocol, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMUnavailable(RuntimeError):
    pass


class LLMProvider(Protocol):
    def complete_json(self, system: str, user: str, schema: type[T]) -> T:
        """结构化补全：返回符合 schema 的 pydantic 实例。

        实现方负责校验与重试（如 JSON 不合法时重问）。
        """
        ...


class NullLLM:
    """未配置 API 时的占位实现：明确报错，而不是静默降级。"""

    def complete_json(self, system: str, user: str, schema: type[T]) -> T:
        raise LLMUnavailable(
            "未配置 LLM：请设置 OPENCOACH_LLM_BASE_URL / OPENCOACH_LLM_API_KEY / "
            "OPENCOACH_LLM_MODEL（OpenAI 兼容实现于 M2 交付）。"
        )
