"""API-backed embedding providers (T-06-011).

Interim production providers until the on-prem embedding model is hosted locally.
All providers return (vector, provenance_meta) matching hexa_learn.EmbeddingProviderFunc.
"""
from __future__ import annotations

import json
import math
import os
import urllib.error
import urllib.request
from typing import Any, Dict, List, Tuple

from src.shared.hexa_learn import DEFAULT_EMBED_DIM, EmbeddingProviderFunc


def _normalize(vec: List[float]) -> List[float]:
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def _post_json(url: str, payload: dict, headers: Dict[str, str]) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Embedding request failed ({exc.code}): {detail}") from exc


async def openai_embedding_provider(text: str) -> Tuple[List[float], Dict[str, Any]]:
    api_key = (os.environ.get("OPENAI_API_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for openai embedding provider")
    model = (os.environ.get("EMBEDDING_MODEL") or "text-embedding-3-small").strip()
    body = _post_json(
        "https://api.openai.com/v1/embeddings",
        {"model": model, "input": text},
        {"Authorization": f"Bearer {api_key}"},
    )
    data = (body.get("data") or [{}])[0]
    vec = _normalize([float(x) for x in data.get("embedding") or []])
    usage = body.get("usage") or {}
    return vec, {
        "model_id": model,
        "input_tokens": int(usage.get("prompt_tokens", max(1, len(text) // 4))),
        "output_tokens": 0,
        "cost_usd": 0.0,
        "embedding_dim": len(vec),
        "provider": "openai",
    }


async def voyage_embedding_provider(text: str) -> Tuple[List[float], Dict[str, Any]]:
    api_key = (os.environ.get("VOYAGE_API_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("VOYAGE_API_KEY is required for voyage embedding provider")
    model = (os.environ.get("VOYAGE_EMBEDDING_MODEL") or "voyage-3-lite").strip()
    body = _post_json(
        "https://api.voyageai.com/v1/embeddings",
        {"model": model, "input": text},
        {"Authorization": f"Bearer {api_key}"},
    )
    data = (body.get("data") or [{}])[0]
    vec = _normalize([float(x) for x in data.get("embedding") or []])
    usage = body.get("usage") or {}
    return vec, {
        "model_id": model,
        "input_tokens": int(usage.get("total_tokens", max(1, len(text) // 4))),
        "output_tokens": 0,
        "cost_usd": 0.0,
        "embedding_dim": len(vec),
        "provider": "voyage",
    }


def resolve_embedding_provider() -> EmbeddingProviderFunc:
    provider = (os.environ.get("EMBEDDING_PROVIDER") or "hash").strip().lower()
    if provider == "openai":
        return openai_embedding_provider
    if provider == "voyage":
        return voyage_embedding_provider
    from src.shared.hexa_learn import hash_embedding_provider

    return hash_embedding_provider


def embedding_degraded() -> bool:
    """True when a non-hash provider is configured but credentials are missing."""
    provider = (os.environ.get("EMBEDDING_PROVIDER") or "hash").strip().lower()
    if provider == "hash":
        return True
    if provider == "openai":
        return not (os.environ.get("OPENAI_API_KEY") or "").strip()
    if provider == "voyage":
        return not (os.environ.get("VOYAGE_API_KEY") or "").strip()
    return True


def embedding_bound() -> bool:
    provider = (os.environ.get("EMBEDDING_PROVIDER") or "hash").strip().lower()
    if provider == "hash":
        return False
    return not embedding_degraded()
