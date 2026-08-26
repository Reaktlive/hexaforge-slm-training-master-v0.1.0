"""hexaforge_slm_training_master_rollback_binding_approval_gate_hexa — Forseti privileged-action handler, CCAS-tier-gated (tier=human).

Auto-generated platform infra — NOT a CUSTOMER_SLOT stub. This node executes a
DECLARED privileged action (CORE_DOCTRINE_REMINDER §3). Every side-effect port
(xo/yo) routes the action through ccas_decide(action, "human") and
only emits when approved at the declared tier. Customer business logic lives in
the _apply_<port>() CUSTOMER_SLOT INSIDE the gate; the ccas_decide() call MUST
NOT be removed — H_PRIVILEGED_ACTION_DECLARED rejects any bundle where a
privileged node's side-effect port bypasses the declared CCAS tier.
"""
from typing import Any
from src.shared.ccas_gate import ccas_decide, canonical_action_ref
from src.shared.execution_ledger import ExecutionLedgerUnavailable, classify_apply_result, complete, reserve
from src.shared.reference_capability import reference_enabled, reference_apply


async def handle_xo(payload: Any) -> dict:
    """hexaforge_slm_training_master_rollback_binding_approval_gate_hexa.xo — DECLARED privileged action, CCAS-gated (tier=human).

    CORE_DOCTRINE_REMINDER §3: this node executes a declared privileged action.
    The side effect MUST NOT emit until ccas_decide() approves it at the
    DECLARED tier. A pending/escalated decision holds the action for approval;
    the side effect is never auto-emitted past its tier.
    """
    if not isinstance(payload, dict):
        payload = {"action": payload}
    # Tier is the DECLARED CCAS tier for this action (karta.privileged_actions),
    # not a generic default — H_PRIVILEGED_ACTION_DECLARED checks this call.
    decision = ccas_decide(action=payload, tier="human")
    if decision["status"] != "approved":
        # Held for human approval — DO NOT execute the side effect.
        return {
            "node": "hexaforge_slm_training_master_rollback_binding_approval_gate_hexa",
            "port": "xo",
            "ok": False,
            "status": decision["status"],
            "ccas_decision": decision,
            "action": payload,
        }
    # Fas 2.22 (external DD, Peter #1/#2) — executor-boundary integrity: the
    # action we are about to execute MUST be byte-identical to the action the
    # gate approved. Re-derive the content hash and refuse on ANY drift, so an
    # approval issued for one action body can never drive a different side effect
    # (confused deputy at the executor seam). Fail-closed — never execute on drift.
    approved_ref = decision.get("action_ref")
    if not approved_ref or canonical_action_ref(payload) != approved_ref:
        return {
            "node": "hexaforge_slm_training_master_rollback_binding_approval_gate_hexa",
            "port": "xo",
            "ok": False,
            "status": "integrity_error",
            "ccas_decision": decision,
            "action": payload,
        }
    # Fas 3.3 (external DD, major) — REAL IDEMPOTENCY. The contract says the
    # idempotency_key prevents double execution; until 3.3 nothing enforced it —
    # the approval ledger only makes an APPROVAL single-use, so a FRESH approval
    # carrying the same key executed the side effect again. Claim the right to
    # execute ONCE, atomically, BEFORE the side effect. A duplicate returns the
    # earlier outcome instead of repeating it; an unavailable ledger refuses to
    # execute at all (no side effect without a reservation).
    try:
        _claim, _prior = reserve(payload)
    except ExecutionLedgerUnavailable as _e:
        return {
            "node": "hexaforge_slm_training_master_rollback_binding_approval_gate_hexa",
            "port": "xo",
            "ok": False,
            "executed": False,
            "status": "execution_ledger_unavailable",
            "ccas_decision": decision,
            "action": payload,
            "detail": str(_e),
        }
    if _claim == "duplicate":
        return {
            "node": "hexaforge_slm_training_master_rollback_binding_approval_gate_hexa",
            "port": "xo",
            "ok": True,
            "executed": False,
            "status": "duplicate_suppressed",
            "ccas_decision": decision,
            "action": payload,
            "prior_execution": _prior,
        }
    # Approved at the declared tier, content re-verified and execution reserved —
    # execute the (customer) side effect.
    try:
        result = await _apply_xo(payload)
    except Exception as _exc:  # noqa: BLE001 — the outcome is recorded either way
        complete(payload, "failed", str(_exc))
        raise
    # Fas 3.25 (external DD, MAJOR) — RECORD WHAT ACTUALLY HAPPENED.
    #
    # This used to write "succeeded" the moment _apply_ returned, including when
    # it returned {"applied": False, "status": "not_implemented"} — which is what
    # EVERY unwired seam in a skeleton returns. Two harms, both real: the ledger
    # became false evidence that a side effect occurred, and the reservation then
    # suppressed the LEGITIMATE retry once the customer wired the integration —
    # the replay answered "succeeded" for something that never ran.
    #
    # The outcome is now read from the seam's own result, and the result payload
    # travels with it so a replay can answer with what actually happened rather
    # than with a word.
    # Fas 3.37 (external DD, counter-proof) — ONE decision for the ledger and
    # the response. This gate used to classify the seam result twice: the
    # ledger outcome came from bool(result.get("applied")) while "executed"
    # below used an identity test. A seam returning the STRING "false" was therefore
    # written to the durable ledger as "succeeded" and reported as
    # executed=false in the same response — and the reservation then suppressed
    # the legitimate retry with a success that never happened.
    #
    # Both values now come from the same call. They cannot disagree.
    _executed, _outcome = classify_apply_result(result)
    complete(payload, _outcome, result if isinstance(result, dict) else None)
    # A2: "ok" only means the GATE could process the call. "executed" follows the
    # REAL side effect: an unwired _apply_ seam returns applied=False and must
    # never be reported as an executed action.
    return {
        "node": "hexaforge_slm_training_master_rollback_binding_approval_gate_hexa",
        "port": "xo",
        "ok": True,
        "status": "approved",
        "executed": _executed,
        "ccas_decision": decision,
        "result": result,
    }



async def _apply_xo(payload: dict) -> dict:
    # CUSTOMER_SLOT: implement the real privileged side effect for hexaforge_slm_training_master_rollback_binding_approval_gate_hexa.xo
    # INSIDE the gate (e.g. call the enforcement API for this action). The ccas_decide() gate in
    # handle_xo is platform infra and MUST stay; fill only this seam.
    # Fas 2.16 — REFERENCE MODE (explicit opt-in, default OFF): side-effect-free
    # reference execution of the APPROVED action. Only reachable after
    # ccas_decide approved at the declared tier — the gate is never bypassed.
    if reference_enabled():
        return reference_apply("hexaforge_slm_training_master_rollback_binding_approval_gate_hexa", "xo", payload)
    return {"applied": False, "status": "not_implemented", "action": payload}  # FAIL-CLOSED: unwired seam never claims execution


async def handle_yo(payload: Any) -> dict:
    """hexaforge_slm_training_master_rollback_binding_approval_gate_hexa.yo — DECLARED privileged action, CCAS-gated (tier=human).

    CORE_DOCTRINE_REMINDER §3: this node executes a declared privileged action.
    The side effect MUST NOT emit until ccas_decide() approves it at the
    DECLARED tier. A pending/escalated decision holds the action for approval;
    the side effect is never auto-emitted past its tier.
    """
    if not isinstance(payload, dict):
        payload = {"action": payload}
    # Tier is the DECLARED CCAS tier for this action (karta.privileged_actions),
    # not a generic default — H_PRIVILEGED_ACTION_DECLARED checks this call.
    decision = ccas_decide(action=payload, tier="human")
    if decision["status"] != "approved":
        # Held for human approval — DO NOT execute the side effect.
        return {
            "node": "hexaforge_slm_training_master_rollback_binding_approval_gate_hexa",
            "port": "yo",
            "ok": False,
            "status": decision["status"],
            "ccas_decision": decision,
            "action": payload,
        }
    # Fas 2.22 (external DD, Peter #1/#2) — executor-boundary integrity: the
    # action we are about to execute MUST be byte-identical to the action the
    # gate approved. Re-derive the content hash and refuse on ANY drift, so an
    # approval issued for one action body can never drive a different side effect
    # (confused deputy at the executor seam). Fail-closed — never execute on drift.
    approved_ref = decision.get("action_ref")
    if not approved_ref or canonical_action_ref(payload) != approved_ref:
        return {
            "node": "hexaforge_slm_training_master_rollback_binding_approval_gate_hexa",
            "port": "yo",
            "ok": False,
            "status": "integrity_error",
            "ccas_decision": decision,
            "action": payload,
        }
    # Fas 3.3 (external DD, major) — REAL IDEMPOTENCY. The contract says the
    # idempotency_key prevents double execution; until 3.3 nothing enforced it —
    # the approval ledger only makes an APPROVAL single-use, so a FRESH approval
    # carrying the same key executed the side effect again. Claim the right to
    # execute ONCE, atomically, BEFORE the side effect. A duplicate returns the
    # earlier outcome instead of repeating it; an unavailable ledger refuses to
    # execute at all (no side effect without a reservation).
    try:
        _claim, _prior = reserve(payload)
    except ExecutionLedgerUnavailable as _e:
        return {
            "node": "hexaforge_slm_training_master_rollback_binding_approval_gate_hexa",
            "port": "yo",
            "ok": False,
            "executed": False,
            "status": "execution_ledger_unavailable",
            "ccas_decision": decision,
            "action": payload,
            "detail": str(_e),
        }
    if _claim == "duplicate":
        return {
            "node": "hexaforge_slm_training_master_rollback_binding_approval_gate_hexa",
            "port": "yo",
            "ok": True,
            "executed": False,
            "status": "duplicate_suppressed",
            "ccas_decision": decision,
            "action": payload,
            "prior_execution": _prior,
        }
    # Approved at the declared tier, content re-verified and execution reserved —
    # execute the (customer) side effect.
    try:
        result = await _apply_yo(payload)
    except Exception as _exc:  # noqa: BLE001 — the outcome is recorded either way
        complete(payload, "failed", str(_exc))
        raise
    # Fas 3.25 (external DD, MAJOR) — RECORD WHAT ACTUALLY HAPPENED.
    #
    # This used to write "succeeded" the moment _apply_ returned, including when
    # it returned {"applied": False, "status": "not_implemented"} — which is what
    # EVERY unwired seam in a skeleton returns. Two harms, both real: the ledger
    # became false evidence that a side effect occurred, and the reservation then
    # suppressed the LEGITIMATE retry once the customer wired the integration —
    # the replay answered "succeeded" for something that never ran.
    #
    # The outcome is now read from the seam's own result, and the result payload
    # travels with it so a replay can answer with what actually happened rather
    # than with a word.
    # Fas 3.37 (external DD, counter-proof) — ONE decision for the ledger and
    # the response. This gate used to classify the seam result twice: the
    # ledger outcome came from bool(result.get("applied")) while "executed"
    # below used an identity test. A seam returning the STRING "false" was therefore
    # written to the durable ledger as "succeeded" and reported as
    # executed=false in the same response — and the reservation then suppressed
    # the legitimate retry with a success that never happened.
    #
    # Both values now come from the same call. They cannot disagree.
    _executed, _outcome = classify_apply_result(result)
    complete(payload, _outcome, result if isinstance(result, dict) else None)
    # A2: "ok" only means the GATE could process the call. "executed" follows the
    # REAL side effect: an unwired _apply_ seam returns applied=False and must
    # never be reported as an executed action.
    return {
        "node": "hexaforge_slm_training_master_rollback_binding_approval_gate_hexa",
        "port": "yo",
        "ok": True,
        "status": "approved",
        "executed": _executed,
        "ccas_decision": decision,
        "result": result,
    }



async def _apply_yo(payload: dict) -> dict:
    # CUSTOMER_SLOT: implement the real privileged side effect for hexaforge_slm_training_master_rollback_binding_approval_gate_hexa.yo
    # INSIDE the gate (e.g. call the enforcement API for this action). The ccas_decide() gate in
    # handle_yo is platform infra and MUST stay; fill only this seam.
    # Fas 2.16 — REFERENCE MODE (explicit opt-in, default OFF): side-effect-free
    # reference execution of the APPROVED action. Only reachable after
    # ccas_decide approved at the declared tier — the gate is never bypassed.
    if reference_enabled():
        return reference_apply("hexaforge_slm_training_master_rollback_binding_approval_gate_hexa", "yo", payload)
    return {"applied": False, "status": "not_implemented", "action": payload}  # FAIL-CLOSED: unwired seam never claims execution


async def handle_xi(payload: Any) -> dict:
    """hexaforge_slm_training_master_rollback_binding_approval_gate_hexa.xi — DECLARED privileged action gate: CCAS route-on-tier (tier=human).

    CORE_DOCTRINE_REMINDER §3: the action is gated AFTER the decision and BEFORE
    egress; downstream emission is gated on the declared-tier approval. Primary-
    path realisation of the gate (same route-on-tier contract as the platform
    decision node), so the gate.XO -> egress.XI edge carries a GATED envelope:
      approved                     -> emit  (pass the action downstream, hold=False)
      pending / escalated / dual   -> hold  (park for approval, hold=True, payload=None)
    The real-world side effect stays on the YO sink (handle_yo), CCAS-gated.
    """
    if not isinstance(payload, dict):
        payload = {"payload": payload}
    body = payload.get("payload") if isinstance(payload.get("payload"), dict) else payload
    action = body if isinstance(body, dict) else {"action": body}
    decision = ccas_decide(action=action, tier="human")
    emit = decision["status"] == "approved"
    return {
        "node": "hexaforge_slm_training_master_rollback_binding_approval_gate_hexa",
        "port": "xi",
        "ok": True,
        "ts": payload.get("ts"),
        "status": decision["status"],
        "ccas_decision": decision,
        "route": decision["route"],
        "hold": not emit,
        "payload": body if emit else None,
        "gate_signature": decision["status"],
        "signature": decision["status"],
    }


async def handle_yi(payload: Any) -> dict:
    """hexaforge_slm_training_master_rollback_binding_approval_gate_hexa.yi — non-emitting port; CCAS gating applies on the side-effect (xo/yo) ports."""
    return {"node": "hexaforge_slm_training_master_rollback_binding_approval_gate_hexa", "port": "yi", "ok": True}


async def handle_zi(payload: Any) -> dict:
    """hexaforge_slm_training_master_rollback_binding_approval_gate_hexa.zi — non-emitting port; CCAS gating applies on the side-effect (xo/yo) ports."""
    return {"node": "hexaforge_slm_training_master_rollback_binding_approval_gate_hexa", "port": "zi", "ok": True}


async def handle_zo(payload: Any) -> dict:
    """hexaforge_slm_training_master_rollback_binding_approval_gate_hexa.zo — non-emitting port; CCAS gating applies on the side-effect (xo/yo) ports."""
    return {"node": "hexaforge_slm_training_master_rollback_binding_approval_gate_hexa", "port": "zo", "ok": True}
