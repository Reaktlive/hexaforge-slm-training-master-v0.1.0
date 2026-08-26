"""Reference capability e2e (Fas 2.16) - the chassis runs the FULL happy path.

Factory-controlled proof (external DD #7): with DOER_REFERENCE_MODE=1 every
unimplemented CUSTOMER_SLOT returns a contract-derived REFERENCE output and the
privileged gate's _apply_ seam performs a side-effect-free reference execution,
so one event traverses ingress -> nodes -> action gate -> egress. Approval
provenance stays FULLY enforced (Fas 2.13c): gated tiers approve ONLY with
structured, action-bound, role-scoped, nonce-fresh, SIGNED approvals carried on
the event. Default mode (reference OFF) stays fail-closed.
"""
import hashlib
import hmac
import importlib
import os

import pytest
from fastapi.testclient import TestClient

from runtime.api_server import app

INGRESS_NODE_ID = "hexaforge_slm_training_master_intake_octa"
# Declared privileged gates and their CCAS tiers - baked from the karta itself.
GATE_TIERS = {"hexaforge_slm_training_master_start_training_job_approval_gate_hexa":"auto","hexaforge_slm_training_master_requeue_job_approval_gate_hexa":"manual","hexaforge_slm_training_master_retry_with_adjustment_approval_gate_hexa":"manual","hexaforge_slm_training_master_kill_job_approval_gate_hexa":"manual","hexaforge_slm_training_master_pause_campaign_approval_gate_hexa":"manual","hexaforge_slm_training_master_resume_campaign_approval_gate_hexa":"manual","hexaforge_slm_training_master_park_job_approval_gate_hexa":"manual","hexaforge_slm_training_master_keep_parked_approval_gate_hexa":"manual","hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa":"manual","hexaforge_slm_training_master_promote_and_bind_adapter_approval_gate_hexa":"human","hexaforge_slm_training_master_deny_bind_approval_gate_hexa":"human","hexaforge_slm_training_master_rollback_binding_approval_gate_hexa":"human","hexaforge_slm_training_master_delete_artifact_approval_gate_hexa":"dual_approval","hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa":"manual","hexaforge_slm_training_master_bind_adapter_to_fleet_agent_approval_gate_hexa":"human","hexaforge_slm_training_master_rollback_fleet_binding_approval_gate_hexa":"human","hexaforge_slm_training_master_grant_shared_adapter_training_approval_gate_hexa":"dual_approval","hexaforge_slm_training_master_issue_delegation_grant_approval_gate_hexa":"dual_approval","hexaforge_slm_training_master_revoke_delegation_grant_approval_gate_hexa":"manual"}
GATED = {k: v for k, v in GATE_TIERS.items() if v != "auto"}
KEY = "reference-capability-key-2.16"


@pytest.fixture
def client():
    return TestClient(app)


def _sample_event(event_id):
    event = dict({})
    event["event_id"] = event_id
    event.setdefault("source", "reference-capability-e2e")
    return event


def _reload_ccas():
    import src.shared.ccas_gate as cg
    importlib.reload(cg)
    return cg


def _signed_approvals(cg, action_ref, count):
    out = []
    for i in range(count):
        who = "ref-approver-%d" % (i + 1)
        # Fas 2.17 — unique nonce per RUN: the persistent ledger consumes
        # releasing approvals forever, so a re-run must present fresh nonces.
        nonce = "ref-nonce-%s-%d-%s" % (action_ref, i + 1, os.urandom(4).hex())
        msg = cg._canonical_approval_msg(action_ref, who, "approver", nonce)
        sig = hmac.new(KEY.encode("utf-8"), msg, hashlib.sha256).hexdigest()
        out.append({"approver_principal": who, "role": "approver", "action_ref": action_ref, "nonce": nonce, "signature": sig})
    return out


def test_reference_off_default_stays_fail_closed(client):
    os.environ.pop("DOER_REFERENCE_MODE", None)
    response = client.post("/api/events", json=_sample_event("evt-ref-000"))
    assert response.status_code == 200, response.text
    body = response.json()
    assert body.get("status") in ("ok", "degraded_blocking_stub"), response.text
    if body.get("status") == "degraded_blocking_stub":
        # A6/2.2c fail-closed default: blocking stubs hold the release.
        assert body.get("disposition") == "hold"
        assert body.get("release_allowed") is False


def test_reference_mode_completes_but_never_executes_ungated(client):
    os.environ["DOER_REFERENCE_MODE"] = "1"
    try:
        response = client.post("/api/events", json=_sample_event("evt-ref-001"))
        assert response.status_code == 200, response.text
        body = response.json()
        # The chassis completes: no blocking stub degrades the run.
        assert body.get("status") != "degraded_blocking_stub", response.text
        if not GATED:
            pytest.skip("no gated privileged actions declared in this karta")
        governed = [g for g in (body.get("governed_actions") or []) if g.get("node") in GATED]
        for g in governed:
            # Without signed approvals a gated action must NEVER execute.
            assert g.get("executed") is not True, g
            assert (g.get("ccas_decision") or {}).get("status") != "approved", g
    finally:
        os.environ.pop("DOER_REFERENCE_MODE", None)


def _gate_action_ref(body):
    """Fas 2.22 — the CONTENT ref the gate bound the approvals to, read back from
    a probe run's governed-action decision. Approvals now bind to
    canonical_action_ref(action) (a hash of the action body), NOT a request_id,
    so — exactly like a real approval backend — we discover the ref from the gate
    (it is shown the proposal + its ref) instead of guessing it."""
    for g in (body.get("governed_actions") or []):
        if g.get("node") in GATED:
            ref = (g.get("ccas_decision") or {}).get("action_ref")
            if ref:
                return ref
    return None


def test_reference_full_happy_path_through_action_gate(client):
    from src.shared.hexa_record import read_chain_for_event, verify_chain

    os.environ["DOER_REFERENCE_MODE"] = "1"
    os.environ["CCAS_APPROVAL_KEY"] = KEY
    os.environ.pop("CCAS_APPROVER_ROLES", None)
    try:
        cg = _reload_ccas()
        if not GATED:
            # No gated privileged action in this karta — the chassis happy path
            # must still complete cleanly (no blocking stub) in reference mode.
            probe = client.post("/api/events", json=_sample_event("evt-ref-002"))
            assert probe.status_code == 200, probe.text
            assert probe.json().get("status") != "degraded_blocking_stub", probe.text
            return
        # PASS 1 (probe) — run WITHOUT approvals to discover the CONTENT ref the
        # gate binds to. Fas 2.22: a valid approval must be bound to
        # canonical_action_ref(action), so we learn that ref from the gate itself
        # (mirrors a real backend showing the approver the proposal + its ref).
        probe_event = _sample_event("evt-ref-002-probe")
        probe_event["request_id"] = "ref-req-002-probe"
        probe = client.post("/api/events", json=probe_event)
        assert probe.status_code == 200, probe.text
        ref = _gate_action_ref(probe.json())
        assert ref, "probe run did not expose the gate's content action_ref: %s" % probe.json()
        # PASS 2 (release) — two distinct signed approvals BOUND TO THAT CONTENT
        # ref release the gated action (covers tier_4 dual approval; bare names
        # still count as zero — Fas 2.13c provenance never relaxed).
        event = _sample_event("evt-ref-002")
        event["request_id"] = "ref-req-002"
        event["approvals"] = _signed_approvals(cg, ref, 2)
        response = client.post("/api/events", json=event)
        assert response.status_code == 200, response.text
        body = response.json()
        assert body.get("status") != "degraded_blocking_stub", response.text
        assert body.get("disposition") != "hold", response.text
        governed = [g for g in (body.get("governed_actions") or []) if g.get("node") in GATED]
        assert governed, "declared gated action never reached the gate: %s" % body
        approved = [g for g in governed if (g.get("ccas_decision") or {}).get("status") == "approved"]
        assert approved, "no gated action approved despite signed approvals: %s" % governed
        assert any(g.get("executed") is True for g in approved), (
            "approved reference action was not executed: %s" % approved)
        # The whole run is audit-bound and the chain verifies end-to-end.
        entries = read_chain_for_event("evt-ref-002")
        assert entries, "reference run left no audit entries"
        assert verify_chain() is True, "audit chain broken after reference run"
    finally:
        os.environ.pop("DOER_REFERENCE_MODE", None)
        os.environ.pop("CCAS_APPROVAL_KEY", None)
        _reload_ccas()


def test_reference_identity_is_owned_by_the_harness_not_the_contract():
    """Fas 3.19 — a harness that works once and silently stops working is worse
    than no harness, because it keeps reporting success.

    The execution ledger is PERSISTENT and keyed on (tenant_id,
    selected_action, idempotency_key). The reference key must therefore be
    STABLE WITHIN a run - it is part of the signed approval hash - and DIFFERENT
    BETWEEN runs, or the first run executes and every later one is suppressed as
    a duplicate while the gate still reports "approved" and the action reports
    executed=False. Found on a freshly generated bundle: the reference suite
    passed on run 1 and failed on run 2 in the same untouched directory.

    The cause was a guard that only supplied the harness identity when the field
    was EMPTY. _object_for() fills a DECLARED string field with "reference",
    which is not empty, so on any agent whose XO contract declares
    idempotency_key the constant won. These fields are harness scaffolding, not
    domain data: the reference module owns them outright."""
    import importlib

    import src.shared.reference_capability as rc

    gated = sorted(GATED)
    if not gated:
        pytest.skip("no gated privileged action in this karta")
    node = gated[0]

    env = rc.reference_selection_envelope(node, "xi")
    payload = (env or {}).get("payload") or {}
    key = payload.get("idempotency_key")

    assert key == rc._REFERENCE_IDEMPOTENCY_KEY, (
        "the reference envelope carries %r instead of the key the harness owns (%r) — a "
        "contract-derived placeholder is never a valid idempotency key"
        % (key, rc._REFERENCE_IDEMPOTENCY_KEY))
    assert key != "reference", "the idempotency key is the generic string placeholder"
    assert str(key).startswith("reference-") and len(str(key)) > len("reference-")
    assert payload.get("tenant_id") == "reference-tenant", payload.get("tenant_id")

    # Stable WITHIN the run: the key is inside the signed approval hash, so a
    # second envelope in the same process must bind identically.
    again = (rc.reference_selection_envelope(node, "xi") or {}).get("payload") or {}
    assert again.get("idempotency_key") == key, "the key changed within a single run"

    # Different BETWEEN runs: reloading re-executes the module the way a new
    # process would, and the ledger must see a key it has not consumed.
    first = rc._REFERENCE_IDEMPOTENCY_KEY
    try:
        importlib.reload(rc)
        assert rc._REFERENCE_IDEMPOTENCY_KEY != first, (
            "a fresh run produced the SAME reference idempotency key — the persistent ledger "
            "will suppress it as a duplicate and the harness becomes a no-op that still "
            "reports approved")
        fresh = (rc.reference_selection_envelope(node, "xi") or {}).get("payload") or {}
        assert fresh.get("idempotency_key") == rc._REFERENCE_IDEMPOTENCY_KEY
    finally:
        importlib.reload(rc)
