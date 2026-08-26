"""Degraded-mode signal (regelverk: truth over green).

doctrine-tags: N8-audit, regelverk-truth-over-green

DOCTRINE — TRUTH OVER GREEN: the agent must never sit silently "green" while
it is running without a real cognitive substrate. Two seams can leave the
pipeline contract-valid but doing PLACEHOLDER work:

  1. LLM — when no client is configured, the 8 cognitive nodes fail-closed to
     the deterministic ``_build_xo`` stub (contract-valid, empty analysis).
  2. EMBEDDINGS — when no semantic provider is bound, ``incident_correlator``
     runs on the offline hash stub, so correlation is STRUCTURAL, not
     semantic.

In both cases the API looks healthy and CEVE stays green, hiding that the
agent is producing placeholder analysis. ``degraded_status()`` surfaces this:
the operator API exposes it (GET /api/autonomy) and every incident records
whether it was produced in degraded mode.

Detection is read-only and side-effect-free: it never makes a network call,
never resolves a credential, and never raises. It reuses each seam's OWN state
(``llm_binding`` client resolution; the correlator's ``set_embedding_provider``
default) rather than re-deriving "is a real backend configured?" itself.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List


def _llm_client_present() -> bool:
    """True iff the LLM/SLM substrates required by MODEL_ROUTING are available.

    Reuses llm_binding's own resolution state:
      - no routing map -> legacy single global client (injected or credential)
      - slm-routed nodes -> SLM client must be bound (T-06-010)
      - llm-routed nodes -> Anthropic credential or injected global client
    """
    from src.shared import llm_binding

    if getattr(llm_binding, "_INJECTED_CLIENT", None) is not None:
        return True

    routing = llm_binding._route_map()
    if not routing:
        for suffix in ("TOKEN_ENDPOINT", "API_KEY", "API_KEY_DEV"):
            val = os.environ.get(f"ANTHROPIC_{suffix}")
            if val and val.strip():
                return True
        return False

    slm_nodes = {k for k, v in routing.items() if v == "slm"}
    llm_nodes = {k for k, v in routing.items() if v == "llm"}

    slm_ok = not slm_nodes or getattr(llm_binding, "_SLM_CLIENT", None) is not None
    llm_ok = True
    if llm_nodes:
        llm_ok = False
        for suffix in ("TOKEN_ENDPOINT", "API_KEY", "API_KEY_DEV"):
            val = os.environ.get(f"ANTHROPIC_{suffix}")
            if val and val.strip():
                llm_ok = True
                break
    return slm_ok and llm_ok


def _embedding_provider_real() -> bool:
    """True when a real (non-hash) embedding provider is bound.

    Generic/doctrine-pure: uses the shelf's embedding_providers.embedding_bound()
    probe so the check is domain-independent (no per-agent node import).
    """
    try:
        from src.shared.embedding_providers import embedding_bound
        return bool(embedding_bound())
    except Exception:
        return False


def degraded_status() -> Dict[str, Any]:
    """Return the agent's degraded-mode signal.

    Shape::

        {
            "degraded": bool,          # any check failed
            "reasons": [str, ...],     # human-readable, one per failed check
            "checks": {"llm": bool, "embeddings": bool},  # True = healthy
        }

    A check value of ``True`` means that component is doing the real job;
    ``False`` means it has fallen back to a deterministic stub.
    """
    llm_ok = _llm_client_present()
    embeddings_ok = _embedding_provider_real()

    reasons: List[str] = []
    if not llm_ok:
        from src.shared import llm_binding

        routing = llm_binding._route_map()
        slm_nodes = {k for k, v in routing.items() if v == "slm"} if routing else set()
        if slm_nodes and getattr(llm_binding, "_SLM_CLIENT", None) is None:
            reasons.append(
                "llm: MODEL_ROUTING maps nodes to slm but SLM_ENDPOINT is not "
                "bound — SLM-routed nodes fail-closed to deterministic stubs"
            )
        else:
            reasons.append(
                "llm: no client configured — cognitive nodes fail-closed to "
                "deterministic stubs"
            )
    if not embeddings_ok:
        reasons.append(
            "embeddings: hash-stub (no semantic provider) — correlation is "
            "structural, not semantic"
        )

    return {
        "degraded": bool(reasons),
        "reasons": reasons,
        "checks": {"llm": llm_ok, "embeddings": embeddings_ok},
    }
