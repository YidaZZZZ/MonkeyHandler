"""LLM 层：可插拔、结构化输出。

M0 只定义端口与占位实现；D4 交付 OpenAI 兼容实现（标准库 urllib，零新增依赖），
通过环境变量配置：
    MONKEYHANDLER_LLM_BASE_URL  # 可指向 GLM 等兼容端点
    MONKEYHANDLER_LLM_API_KEY
    MONKEYHANDLER_LLM_MODEL

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
            "未配置 LLM：请设置 MONKEYHANDLER_LLM_BASE_URL / MONKEYHANDLER_LLM_API_KEY / "
            "MONKEYHANDLER_LLM_MODEL（OpenAI 兼容实现于 D4 交付），或使用离线规则路径。"
        )


import json as _json
import urllib.request as _request


def _strip_fences(text: str) -> str:
    """剥掉 ```json 围栏并截取首个 { 到末个 }，容错常见模型输出格式。"""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("模型输出中未找到 JSON 对象")
    return cleaned[start:end + 1]


class OpenAICompatClient:
    """OpenAI 兼容 chat/completions 客户端（标准库实现，零新增依赖）。

    满足 LLMProvider 协议：complete_json 返回经 pydantic 校验的实例；
    JSON 不合法时抛出 ValueError，由调用方决定降级或重试。
    """

    def __init__(self, base_url: str, api_key: str, model: str, timeout: int = 90, temperature: float = 0.7):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.temperature = temperature

    def complete_json(self, system: str, user: str, schema: type[T]) -> T:
        payload = _json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": self.temperature,
        }).encode("utf-8")
        req = _request.Request(
            self.base_url + "/chat/completions",
            data=payload,
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + self.api_key},
            method="POST",
        )
        with _request.urlopen(req, timeout=self.timeout) as resp:
            data = _json.loads(resp.read().decode("utf-8"))
        content = data["choices"][0]["message"]["content"]
        return schema.model_validate_json(_strip_fences(content))
