"""hexaforge_slm_training_master_decision_ledger_hexa — Forseti PG-5 platform decision handler (CCAS-tier router).

Auto-generated structural plumbing — NOT a CUSTOMER_SLOT. Classifies the
inbound action's CCAS tier and routes on the decision (approved -> emit,
pending/escalated -> hold). The Yo port wrapper already calls ccas_decide;
this XI handler is the matching route-on-tier step. No vertical business
logic; the route table is doctrine, identical across verticals. Customer
extensions belong BELOW the AUTOGEN-END marker.
"""
# ─────────────────────────────────────────────────────────────────────
# FORSETI-AUTOGEN-START: hexaforge_slm_training_master_decision_ledger_hexa-handler
# Content between AUTOGEN markers is owned by the Forseti generator and
# will be REPLACED on re-generation. To add customer logic that survives
# re-generation, place it BELOW the END marker.
# ─────────────────────────────────────────────────────────────────────
from typing import Any

from src.shared.ccas_gate import ccas_decide, classify_action


async def handle_xi(payload: Any) -> dict:
    """hexaforge_slm_training_master_decision_ledger_hexa.xi — platform CCAS-tier router.

    Pure platform plumbing: classify the inbound action's CCAS tier and route
    on the decision:
      * approved (tier_1)  -> emit  : pass the payload downstream (hold=False).
      * pending  (tier_2)  -> hold  : park for analyst approval (hold=True).
      * escalated(tier_3)  -> hold  : escalate to multi-party (hold=True).
    The vertical decides WHAT the action is; the platform decides whether it
    may proceed. Tier classification + routing is identical across verticals.
    """
    if not isinstance(payload, dict):
        payload = {"payload": payload}
    body = payload.get("payload") if isinstance(payload.get("payload"), dict) else payload
    action = body if isinstance(body, dict) else {"action": body}
    tier = classify_action(action)
    decision = ccas_decide(action, tier)
    emit = decision["status"] == "approved"
    return {
        "node": "hexaforge_slm_training_master_decision_ledger_hexa",
        "port": "xi",
        "ok": True,
        "ts": payload.get("ts"),
        "ccas_decision": decision,
        "route": decision["route"],
        "hold": not emit,
        "payload": body if emit else None,
        "gate_signature": decision["status"],
        "signature": decision["status"],
    }


async def handle_xo(payload: Any) -> dict:
    """hexaforge_slm_training_master_decision_ledger_hexa.xo — platform port (no extra logic on this port)."""
    return {"node": "hexaforge_slm_training_master_decision_ledger_hexa", "port": "xo", "ok": True}


async def handle_yi(payload: Any) -> dict:
    """hexaforge_slm_training_master_decision_ledger_hexa.yi — platform port (no extra logic on this port)."""
    return {"node": "hexaforge_slm_training_master_decision_ledger_hexa", "port": "yi", "ok": True}


async def handle_yo(payload: Any) -> dict:
    """hexaforge_slm_training_master_decision_ledger_hexa.yo — platform port (no extra logic on this port)."""
    return {"node": "hexaforge_slm_training_master_decision_ledger_hexa", "port": "yo", "ok": True}


async def handle_zi(payload: Any) -> dict:
    """hexaforge_slm_training_master_decision_ledger_hexa.zi — platform port (no extra logic on this port)."""
    return {"node": "hexaforge_slm_training_master_decision_ledger_hexa", "port": "zi", "ok": True}


async def handle_zo(payload: Any) -> dict:
    """hexaforge_slm_training_master_decision_ledger_hexa.zo — platform port (no extra logic on this port)."""
    return {"node": "hexaforge_slm_training_master_decision_ledger_hexa", "port": "zo", "ok": True}
# ─────────────────────────────────────────────────────────────────────
# FORSETI-AUTOGEN-END: hexaforge_slm_training_master_decision_ledger_hexa-handler
#
# Customer code below is preserved on re-generation. Import handlers
# from this file's auto-generated section above and wrap/extend them
# as needed — DO NOT modify the AUTOGEN block itself, or your changes
# will be lost on the next Forseti re-generation.
# ─────────────────────────────────────────────────────────────────────
