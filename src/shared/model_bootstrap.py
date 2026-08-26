"""Bootstrap the distilled SLM client from environment (T-06-010).

Depends on T-04-026 (llm_binding.set_slm_client). Binds ONLY the SLM client.
The LLM intentionally keeps llm_binding's ZT-1 credential-broker path
(_build_real_client via resolve_credential) — we never inject a raw, unbrokered
Anthropic client here. Fail-closed: with SLM_ENDPOINT unset, nothing is bound
and the agent stays on the deterministic stub / degraded mode.
"""
from __future__ import annotations

import os
from typing import Dict


def bootstrap_model_clients() -> Dict[str, bool]:
    status = {"slm_bound": False}
    try:
        from src.shared import llm_binding
    except ImportError:
        return status

    if (os.environ.get("SLM_ENDPOINT") or "").strip():
        try:
            from src.shared.slm_client import SlmClient
            llm_binding.set_slm_client(SlmClient())
            status["slm_bound"] = True
        except Exception:
            # Fail-closed: a bad SLM endpoint must not crash boot; stay on stub.
            status["slm_bound"] = False
    return status
