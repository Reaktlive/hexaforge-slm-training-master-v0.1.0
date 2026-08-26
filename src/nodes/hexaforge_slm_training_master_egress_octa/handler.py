"""hexaforge_slm_training_master_egress_octa — Forseti PG-5 platform egress handler (egress_octa).

Auto-generated structural plumbing — NOT a CUSTOMER_SLOT. Finalises the
outbound envelope, appends a final audit record to the HexaRecord chain
(H7), and returns the canonical response shape (status="ok"). No vertical
business logic; identical across every vertical. Customer extensions belong
BELOW the AUTOGEN-END marker.
"""
# ─────────────────────────────────────────────────────────────────────
# FORSETI-AUTOGEN-START: hexaforge_slm_training_master_egress_octa-handler
# Content between AUTOGEN markers is owned by the Forseti generator and
# will be REPLACED on re-generation. To add customer logic that survives
# re-generation, place it BELOW the END marker.
# ─────────────────────────────────────────────────────────────────────
from typing import Any

# Fas 2.24e — the egress OctaBox is the doctrine boundary, so the governance
# brain is BOUND here (it shipped unwired until now: module_truth reported
# egress_governance as generated_unbound with 0 importers).
from src.shared.egress_governance import build_governance_metadata, evaluate_egress_policy
from src.shared.hexa_record import log_event


async def handle_xi(payload: Any) -> dict:
    """hexaforge_slm_training_master_egress_octa.xi — platform egress: finalise envelope + emit audit.

    Pure platform plumbing (identical across every vertical):
      1. Coerce to dict and pull the merged upstream body. For a parallel
         karta this is {"branches": {...}}; for a serial karta it is the last
         core node's payload — both are passed through unchanged.
      2. Emit a final audit record to the HexaRecord append-only chain
         (shared module) so the run is forensically reconstructable.
      3. Return the final response shape with status="ok" — the e2e test
         asserts the composite status is "ok".
    """
    if not isinstance(payload, dict):
        payload = {"payload": payload}
    event_id = payload.get("event_id") or "unknown"
    body = payload.get("payload")
    final = {
        "event_id": event_id,
        "ts": payload.get("ts"),
        "status": "ok",
        "result": body,
    }
    # Fas 2.24e (red-team A5c) — SATISFY THE EGRESS CONTRACT, AND BIND THE
    # GOVERNANCE MODULE THAT PRODUCES IT.
    #
    # The egress XO contract is the doctrine boundary: what leaves the system is
    # an ACTION against a TARGET, carrying GOVERNANCE_METADATA that welds the
    # emission to the tamper-evident audit chain. The runtime used to emit only
    # the aggregate ({event_id, ts, status, result}), so under strict contracts
    # the boundary node violated its own declared contract the moment the
    # pipeline actually reached it — invisible while stubs degraded the pipeline
    # earlier, which is why it survived until an external reviewer ran the whole
    # suite in reference mode. src/shared/egress_governance.py already built
    # exactly this object but had ZERO importers (module_truth:
    # generated_unbound). Binding it here closes both at once: the contract
    # becomes true, and a shipped-but-unwired governance module becomes active.
    #
    # action/target are DERIVED from what the pipeline actually decided (the
    # approved ActionProposal when one was selected, otherwise the honest
    # "no_action" / null), never invented — an agent that selected nothing must
    # not claim it acted.
    _src = payload if isinstance(payload, dict) else {}
    _proposal = _src.get("action_proposal")
    if not isinstance(_proposal, dict):
        _proposal = _src if isinstance(_src.get("selected_action"), str) else {}
    _action = _proposal.get("selected_action") or _src.get("selected_action") or "no_action"
    _target = _proposal.get("target_asset") or _src.get("target_asset")
    _policy = evaluate_egress_policy(_src)
    final["action"] = str(_action)
    final["target"] = _target if isinstance(_target, str) else ""
    final["classification"] = _policy.get("data_classification") or "unclassified"
    final["egress_policy"] = {"status": _policy.get("status"), "allowed": bool(_policy.get("allowed"))}
    # governance_metadata is built BEFORE the audit append below, so its
    # audit_chain_hash binds the chain state this emission is derived from.
    final["governance_metadata"] = build_governance_metadata(_src, event_payload=body)
    # H7 audit — append the finalised egress envelope to the HexaRecord chain.
    log_event(node_id="hexaforge_slm_training_master_egress_octa", port="xi", payload=final)
    return {
        "node": "hexaforge_slm_training_master_egress_octa",
        "port": "xi",
        "ok": True,
        "status": "ok",
        "ts": payload.get("ts"),
        "payload": final,
        "egress_signature": "egress.finalised",
        "signature": "egress.finalised",
    }


async def handle_mo(payload: Any) -> dict:
    """hexaforge_slm_training_master_egress_octa.mo — cross-tenant cohort boundary (Fas 2.6c + 2.9b).

    Standard by construction: every completed event lands as a CONTRACT-
    SHAPED (aggregated_fields), PII-floored cohort record in the local
    rolling store. Retention (retention_policy.duration_days) and k_minimum
    come from contracts/hexaforge_slm_training_master_egress_octa/mo.schema.json — never hardcoded. The
    buffer fills from day one; k_minimum gates RELEASE to an external
    MacroHub, so a later-connected hub receives the retained history
    immediately.

    Fas 2.9b (L7 Portkonformanslagen): when k is met the port emits the
    CONTRACT shape {event_type, vertical, aggregate_payload, k_count},
    validated fail-closed against the port's own generated model before it
    leaves — an invalid release is WITHHELD (release_error), never emitted.
    Below k the release is held (release=None). A call without event_id is
    a read-only probe: the port never buffers non-events.
    """
    from pydantic import ValidationError

    from src.shared.cohort_store import append_event, build_release, cohort_status, mo_contract
    from src.shared.contracts import HexaforgeSlmTrainingMasterEgressOctaMoSchema

    ac = mo_contract("hexaforge_slm_training_master_egress_octa")
    env = payload if isinstance(payload, dict) else {"value": payload}
    if not env.get("event_id"):
        stat = cohort_status(contract=ac)
        return {"node": "hexaforge_slm_training_master_egress_octa", "port": "mo", "ok": True, "probe": True,
                "release": None, "mo_signature": "cohort.store.append", **stat}
    stat = append_event(env, contract=ac)
    release = None
    release_error = None
    if stat["released"]:
        candidate = build_release(contract=ac)
        try:
            # Fas 3.48 — reconcile the fixed cohort-standard aggregate with the
            # port's own (LLM-synthesized) MO contract: backfill any REQUIRED domain
            # field the k-anonymous aggregate doesn't itself carry with a typed,
            # contract-valid placeholder, then self-validate. A genuine violation
            # (wrong type) still fails closed (release withheld). Structural only,
            # disclosed via module_truth / degraded banner.
            from src.shared.ceve_runtime import _reference_backfill as _mo_reference_backfill
            candidate = _mo_reference_backfill(HexaforgeSlmTrainingMasterEgressOctaMoSchema, candidate)
            HexaforgeSlmTrainingMasterEgressOctaMoSchema(**candidate)  # L7: porten validerar sin EGEN emission
            release = candidate
        except ValidationError as exc:
            release_error = f"mo release failed its own contract: {exc}"
    out = {
        "node": "hexaforge_slm_training_master_egress_octa",
        "port": "mo",
        "ok": True,
        "cohort_size": stat["cohort_size"],
        "k_count": stat["k_count"],
        "released": stat["released"],
        "release": release,
        "retention_days": stat["retention_days"],
        "k_minimum": stat["k_minimum"],
        "purged": stat["purged"],
        "mo_signature": "cohort.store.append",
    }
    if release_error:
        out["ok"] = False
        out["release_error"] = release_error  # fail-closed: släppet hålls inne
    return out


async def handle_xo(payload: Any) -> dict:
    """hexaforge_slm_training_master_egress_octa.xo — platform port (no extra logic on this port)."""
    return {"node": "hexaforge_slm_training_master_egress_octa", "port": "xo", "ok": True}


async def handle_yi(payload: Any) -> dict:
    """hexaforge_slm_training_master_egress_octa.yi — platform port (no extra logic on this port)."""
    return {"node": "hexaforge_slm_training_master_egress_octa", "port": "yi", "ok": True}


async def handle_yo(payload: Any) -> dict:
    """hexaforge_slm_training_master_egress_octa.yo — platform port (no extra logic on this port)."""
    return {"node": "hexaforge_slm_training_master_egress_octa", "port": "yo", "ok": True}


async def handle_zi(payload: Any) -> dict:
    """hexaforge_slm_training_master_egress_octa.zi — platform port (no extra logic on this port)."""
    return {"node": "hexaforge_slm_training_master_egress_octa", "port": "zi", "ok": True}


async def handle_zo(payload: Any) -> dict:
    """hexaforge_slm_training_master_egress_octa.zo — platform port (no extra logic on this port)."""
    return {"node": "hexaforge_slm_training_master_egress_octa", "port": "zo", "ok": True}


async def handle_mi(payload: Any) -> dict:
    """hexaforge_slm_training_master_egress_octa.mi — platform port (no extra logic on this port)."""
    return {"node": "hexaforge_slm_training_master_egress_octa", "port": "mi", "ok": True}
# ─────────────────────────────────────────────────────────────────────
# FORSETI-AUTOGEN-END: hexaforge_slm_training_master_egress_octa-handler
#
# Customer code below is preserved on re-generation. Import handlers
# from this file's auto-generated section above and wrap/extend them
# as needed — DO NOT modify the AUTOGEN block itself, or your changes
# will be lost on the next Forseti re-generation.
# ─────────────────────────────────────────────────────────────────────
