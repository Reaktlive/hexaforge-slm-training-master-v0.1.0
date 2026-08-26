"""OpenAI-compatible SLM client adapter (T-06-010).

Presents an Anthropic-shaped messages.create() surface so existing cognitive
nodes can call the distilled SOC SLM without code changes. Requires #59
(llm_binding.set_slm_client) at runtime bootstrap.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Callable, Dict, List, Optional


def _safe_json(raw: str) -> Dict[str, Any]:
    """Parse SLM-emitted JSON; on malformed output return {} so the caller
    fails the XO contract loud (LlmContractError) instead of raising here."""
    try:
        v = json.loads(raw)
        return v if isinstance(v, dict) else {}
    except (ValueError, TypeError):
        return {}


class SlmMessages:
    def __init__(self, endpoint: str, api_key: Optional[str], model: str) -> None:
        self._endpoint = endpoint.rstrip("/")
        self._api_key = api_key
        self._model = model

    def create(self, **kwargs: Any) -> Any:
        tools = kwargs.get("tools") or []
        tool_choice = kwargs.get("tool_choice") or {}
        messages = kwargs.get("messages") or []
        system = kwargs.get("system") or ""

        user_content = ""
        for msg in messages:
            if msg.get("role") == "user":
                user_content = str(msg.get("content", ""))

        tool_name = tool_choice.get("name") if isinstance(tool_choice, dict) else None
        if not tool_name and tools:
            tool_name = tools[0].get("name")

        payload: Dict[str, Any] = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user_content},
            ],
            "temperature": kwargs.get("temperature", 0),
            "max_tokens": kwargs.get("max_tokens", 1024),
        }
        if tools:
            payload["tools"] = tools
            if tool_name:
                payload["tool_choice"] = {"type": "function", "function": {"name": tool_name}}

        req = urllib.request.Request(
            f"{self._endpoint}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                **({"Authorization": f"Bearer {self._api_key}"} if self._api_key else {}),
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"SLM request failed ({exc.code}): {detail}") from exc

        return _SlmResponse.from_openai(body, tool_name)


class _Usage:
    def __init__(self, input_tokens: int = 0, output_tokens: int = 0) -> None:
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens


class _ToolUseBlock:
    def __init__(self, name: str, tool_input: Dict[str, Any]) -> None:
        self.type = "tool_use"
        self.name = name
        self.input = tool_input


class _SlmResponse:
    def __init__(
        self,
        content: List[_ToolUseBlock],
        usage: _Usage,
        stop_reason: str = "tool_use",
        response_id: str = "slm-response",
    ) -> None:
        self.content = content
        self.usage = usage
        self.stop_reason = stop_reason
        self.id = response_id

    @classmethod
    def from_openai(cls, body: Dict[str, Any], expected_tool: Optional[str]) -> "_SlmResponse":
        choice = (body.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        usage_raw = body.get("usage") or {}
        usage = _Usage(
            input_tokens=int(usage_raw.get("prompt_tokens", 0)),
            output_tokens=int(usage_raw.get("completion_tokens", 0)),
        )

        tool_input: Dict[str, Any] = {}
        tool_name = expected_tool or "tool"

        if message.get("tool_calls"):
            call = message["tool_calls"][0]
            fn = call.get("function") or {}
            tool_name = fn.get("name") or tool_name
            args = fn.get("arguments") or "{}"
            tool_input = _safe_json(args) if isinstance(args, str) else dict(args)
        elif message.get("function_call"):
            fn = message["function_call"]
            tool_name = fn.get("name") or tool_name
            args = fn.get("arguments") or "{}"
            tool_input = _safe_json(args) if isinstance(args, str) else dict(args)
        else:
            content = message.get("content")
            if isinstance(content, str) and content.strip().startswith("{"):
                tool_input = _safe_json(content)

        return cls(
            content=[_ToolUseBlock(tool_name, tool_input)],
            usage=usage,
            stop_reason=choice.get("finish_reason") or "tool_use",
            response_id=str(body.get("id") or "slm-response"),
        )


class SlmClient:
    """Anthropic-compatible facade over an OpenAI-compatible SLM endpoint."""

    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        self._endpoint = (endpoint or os.environ.get("SLM_ENDPOINT") or "").strip()
        self._api_key = api_key if api_key is not None else (os.environ.get("SLM_API_KEY") or "").strip() or None
        self._model = (model or os.environ.get("SLM_MODEL") or "hexabox-slm-v1").strip()
        if not self._endpoint:
            raise ValueError("SLM_ENDPOINT is required to create SlmClient")
        self.messages = SlmMessages(self._endpoint, self._api_key, self._model)

    @property
    def model_id(self) -> str:
        return self._model


def create_slm_client_from_env() -> Optional[SlmClient]:
    endpoint = (os.environ.get("SLM_ENDPOINT") or "").strip()
    if not endpoint:
        return None
    return SlmClient(endpoint=endpoint)
