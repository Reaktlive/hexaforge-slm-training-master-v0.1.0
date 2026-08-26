"""HexaSource — AI-BOM / provenance for LLM calls."""
import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any

# Overridable so read-only-rootfs deployments (k8s) can point the chain at a
# writable mount; see deploy/k8s/configmap.yaml (HEXA_SOURCE_PATH).
PROVENANCE_LOG = os.environ.get("HEXA_SOURCE_PATH", "./hexa_source.jsonl")


def register_llm_call(model_id: str, prompt: str, cost_usd: float, response_meta: dict[str, Any]) -> dict:
    rec = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "model_id": model_id,
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "cost_usd": cost_usd,
        "response_meta": response_meta,
    }
    with open(PROVENANCE_LOG, "a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec
