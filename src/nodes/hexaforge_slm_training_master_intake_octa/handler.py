"""hexaforge_slm_training_master_intake_octa — Forseti PG-5 platform ingress handler (intake_octa).

Auto-generated structural plumbing — NOT a CUSTOMER_SLOT. Normalises and
validates the inbound ENVELOPE (event_id / ts / source) against the platform
envelope floor (_IngressEnvelope) and routes the clean envelope to the first
core node. contracts/hexaforge_slm_training_master_intake_octa/xi.schema.json is the deliberately LENIENT
PAYLOAD sub-schema, enforced separately by ceve_runtime.enforce_payload().
No vertical business logic lives here; it is identical across every vertical.
Customer extensions belong BELOW the AUTOGEN-END marker.
"""
# ─────────────────────────────────────────────────────────────────────
# FORSETI-AUTOGEN-START: hexaforge_slm_training_master_intake_octa-handler
# Content between AUTOGEN markers is owned by the Forseti generator and
# will be REPLACED on re-generation. To add customer logic that survives
# re-generation, place it BELOW the END marker.
# ─────────────────────────────────────────────────────────────────────
import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, ValidationError


class _IngressEnvelope(BaseModel):
    """Platform envelope floor — every event entering the pipeline must carry
    a stable id, an ISO-8601 timestamp, and a source. Mirrors the canonical
    XI contract; kept local so the ingress node is self-contained."""
    event_id: str = Field(..., min_length=1)
    ts: str = Field(..., min_length=1)
    source: str = Field(..., min_length=1)


def _normalise_envelope(payload: dict) -> dict:
    """Assign event_id/ts ONLY when the key is ABSENT; never invent 'source'.

    Fail-closed attribution (Fas 2.1): the platform may fill in what it
    legitimately owns (an id and a receipt timestamp) when the caller OMITTED
    them. A present-but-blank value is a caller error and is passed through
    TRIMMED so _IngressEnvelope rejects it (min_length=1). 'source' has no
    default at all — a missing or blank source is rejected, never silently
    recorded as "unknown": attribution can never be fabricated. The route now
    preserves the caller's envelope all the way here (merge semantics), so a
    legitimate source reaches this floor intact.
    Deterministic, side-effect-free, vertical-agnostic.
    """
    event_id = str(payload["event_id"]).strip() if payload.get("event_id") is not None else f"evt-{uuid.uuid4().hex[:12]}"
    ts = str(payload["ts"]).strip() if payload.get("ts") is not None else datetime.now(timezone.utc).isoformat()
    source = str(payload["source"]).strip().lower() if payload.get("source") is not None else ""
    return {"event_id": event_id, "ts": ts, "source": source}


async def handle_xi(payload: Any) -> dict:
    """hexaforge_slm_training_master_intake_octa.xi — platform ingress: validate + normalise the envelope.

    Pure platform plumbing (identical across every vertical):
      1. Coerce to dict (defensive — accepts raw event or pipeline envelope).
      2. Normalise: event_id/ts are platform-assigned ONLY when the key is
         ABSENT; a present-but-blank value is trimmed and NEVER healed.
         'source' is caller-mandatory and has no default — an unattributable
         event does not enter a governed pipeline.
      3. Validate the envelope against _IngressEnvelope (event_id/ts/source,
         min_length=1); a violation FAIL-blocks with ok=False so the pipeline
         records the bad event instead of propagating a malformed envelope.
      4. Route: emit the normalised envelope on the XO body so the first core
         node receives a clean {event_id, ts, source, payload} shape.
    """
    if not isinstance(payload, dict):
        payload = {"payload": payload}
    # Accept both a raw event and a pipeline envelope ({event_id, ts, payload}).
    body = payload.get("payload") if isinstance(payload.get("payload"), dict) else payload
    normalised = _normalise_envelope(payload)
    try:
        # Platform contract floor — XI must carry a valid event_id/ts/source.
        _IngressEnvelope(**normalised)
    except ValidationError as exc:
        return {
            "node": "hexaforge_slm_training_master_intake_octa",
            "port": "xi",
            "ok": False,
            "blocked": True,
            "reason": "ingress_envelope_invalid",
            "detail": exc.errors(),
        }
    return {
        "node": "hexaforge_slm_training_master_intake_octa",
        "port": "xi",
        "ok": True,
        "event_id": normalised["event_id"],
        "ts": normalised["ts"],
        "source": normalised["source"],
        "payload": body if isinstance(body, dict) else {"value": body},
        "ingress_signature": "ingress.normalised",
        "signature": "ingress.normalised",
    }


async def handle_xo(payload: Any) -> dict:
    """hexaforge_slm_training_master_intake_octa.xo — platform port (no extra logic on this port)."""
    return {"node": "hexaforge_slm_training_master_intake_octa", "port": "xo", "ok": True}


async def handle_yi(payload: Any) -> dict:
    """hexaforge_slm_training_master_intake_octa.yi — platform port (no extra logic on this port)."""
    return {"node": "hexaforge_slm_training_master_intake_octa", "port": "yi", "ok": True}


async def handle_yo(payload: Any) -> dict:
    """hexaforge_slm_training_master_intake_octa.yo — platform port (no extra logic on this port)."""
    return {"node": "hexaforge_slm_training_master_intake_octa", "port": "yo", "ok": True}


async def handle_zi(payload: Any) -> dict:
    """hexaforge_slm_training_master_intake_octa.zi — platform port (no extra logic on this port)."""
    return {"node": "hexaforge_slm_training_master_intake_octa", "port": "zi", "ok": True}


async def handle_zo(payload: Any) -> dict:
    """hexaforge_slm_training_master_intake_octa.zo — platform port (no extra logic on this port)."""
    return {"node": "hexaforge_slm_training_master_intake_octa", "port": "zo", "ok": True}


async def handle_mi(payload: Any) -> dict:
    """hexaforge_slm_training_master_intake_octa.mi — platform port (no extra logic on this port)."""
    return {"node": "hexaforge_slm_training_master_intake_octa", "port": "mi", "ok": True}


async def handle_mo(payload: Any) -> dict:
    """hexaforge_slm_training_master_intake_octa.mo — platform port (no extra logic on this port)."""
    return {"node": "hexaforge_slm_training_master_intake_octa", "port": "mo", "ok": True}
# ─────────────────────────────────────────────────────────────────────
# FORSETI-AUTOGEN-END: hexaforge_slm_training_master_intake_octa-handler
#
# Customer code below is preserved on re-generation. Import handlers
# from this file's auto-generated section above and wrap/extend them
# as needed — DO NOT modify the AUTOGEN block itself, or your changes
# will be lost on the next Forseti re-generation.
# ─────────────────────────────────────────────────────────────────────
