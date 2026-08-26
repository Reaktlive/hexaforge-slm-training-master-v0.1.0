"""CCAS approval provenance — no bare-name approvals, fail-closed seam.

Fas 2.13c (external DD): dual approval could be obtained with {"approvals":
["alice", "bob"]}. These tests import the real CCAS gate and prove a bare name
counts for nothing, unsigned approvals are fail-closed, and only structured,
action-bound, role-scoped, signed approvals from two distinct principals approve.
"""
import hashlib
import hmac
import importlib
import os
import tempfile

KEY = "test-approval-key-2.13c"


def _load(key):
    if key is None:
        os.environ.pop("CCAS_APPROVAL_KEY", None)
    else:
        os.environ["CCAS_APPROVAL_KEY"] = key
    os.environ.pop("CCAS_APPROVER_ROLES", None)
    # Fas 2.17 — fresh persistent ledger per test (the path is read per call by
    # approval_ledger, so no reload of that module is needed).
    os.environ["CCAS_LEDGER_PATH"] = os.path.join(
        tempfile.mkdtemp(prefix="ccas-ledger-"), "ledger.jsonl")
    import src.shared.ccas_gate as m
    importlib.reload(m)
    return m


def _sign(m, action_ref, approver, role, nonce, expires_at=None):
    msg = m._canonical_approval_msg(action_ref, approver, role, nonce, expires_at)
    return hmac.new(KEY.encode("utf-8"), msg, hashlib.sha256).hexdigest()


def _approval(m, action_ref, approver, role="approver", nonce=None, expires_at=None):
    nonce = nonce or ("n-" + approver)
    a = {"approver_principal": approver, "role": role, "action_ref": action_ref,
         "nonce": nonce, "signature": _sign(m, action_ref, approver, role, nonce, expires_at)}
    if expires_at is not None:
        a["expires_at"] = expires_at
    return a


# Fas 2.22 — approvals bind to the action CONTENT hash (canonical_action_ref),
# not a request_id. Each test builds a minimal ActionProposal body and binds the
# approvals to ITS content ref, using the gate's OWN canonicalisation so the test
# can never drift from the shipped hash.
def _content(m, **overrides):
    # Fas 3.2 — a GATED ActionProposal is tenant-scoped by nature: the tenant is
    # part of the signed hash, and the gate fails closed without it. The test
    # bodies model correct usage rather than being weakened to fit the old gap.
    body = {"selected_action": "transmit_report", "target_asset": "asset-1",
            "tenant_id": "tenant-under-test"}
    body.update(overrides)
    return body


def _ref(m, body):
    return m.canonical_action_ref(body)


def _bound(m, body, approvals):
    action = dict(body)
    action["request_id"] = "req-" + str(len(approvals))
    action["approvals"] = approvals
    return action


def test_bare_name_approvals_never_satisfy_dual_approval():
    m = _load(KEY)
    body = _content(m)
    d = m.ccas_decide(_bound(m, body, ["alice", "bob"]), "dual_approval")
    assert d["status"] == "pending_dual_approval", d
    assert d["approvals"] == 0


def test_unsigned_approvals_are_fail_closed():
    m = _load(None)
    body = _content(m)
    ref = _ref(m, body)  # canonical_action_ref needs no key
    action = _bound(m, body, [
        {"approver_principal": "dr_a", "role": "approver", "action_ref": ref, "nonce": "x1", "signature": "deadbeef"},
        {"approver_principal": "dr_b", "role": "approver", "action_ref": ref, "nonce": "x2", "signature": "deadbeef"},
    ])
    d = m.ccas_decide(action, "dual_approval")
    assert d["status"] == "pending_dual_approval", d
    assert d["approvals"] == 0


def test_signed_action_bound_approvals_from_two_principals_approve():
    m = _load(KEY)
    body = _content(m)
    ref = _ref(m, body)
    action = _bound(m, body, [_approval(m, ref, "dr_a"), _approval(m, ref, "dr_b")])
    d = m.ccas_decide(action, "dual_approval")
    assert d["status"] == "approved", d
    assert d["approvals"] == 2


def test_same_approver_twice_is_one():
    m = _load(KEY)
    body = _content(m)
    ref = _ref(m, body)
    action = _bound(m, body, [
        _approval(m, ref, "dr_a", nonce="a1"),
        _approval(m, ref, "dr_a", nonce="a2"),
    ])
    d = m.ccas_decide(action, "dual_approval")
    assert d["status"] == "pending_dual_approval", d
    assert d["approvals"] == 1


def test_wrong_action_ref_and_non_approver_role_are_rejected():
    m = _load(KEY)
    body = _content(m)
    ref = _ref(m, body)
    # Fas 2.22 — "wrong action" now means signed for DIFFERENT action CONTENT
    # (the confused-deputy attack): a swapped body has a different ref.
    other_ref = _ref(m, _content(m, selected_action="a_different_action"))
    wrong_action = _approval(m, other_ref, "dr_a")           # signed for different content
    wrong_role = _approval(m, ref, "dr_c", role="observer")   # not an approver role
    good = _approval(m, ref, "dr_b")
    d = m.ccas_decide(_bound(m, body, [wrong_action, wrong_role, good]), "dual_approval")
    assert d["status"] == "pending_dual_approval", d
    assert d["approvals"] == 1  # only dr_b is content-bound + role-valid + signed


def test_approvals_are_consumed_on_release_and_replay_is_rejected():
    """Fas 2.17 — persistent anti-replay ACROSS calls: the exact approvals that
    released an action once are consumed in the ledger and can never release a
    second action, not even in a later, separate call."""
    import json as _json
    import os as _os

    m = _load(KEY)
    body = _content(m)
    ref = _ref(m, body)
    action = _bound(m, body, [_approval(m, ref, "dr_a"), _approval(m, ref, "dr_b")])
    first = m.ccas_decide(action, "dual_approval")
    assert first["status"] == "approved", first
    ledger_path = _os.environ["CCAS_LEDGER_PATH"]
    entries = [_json.loads(l) for l in open(ledger_path) if l.strip()]
    assert len(entries) == 2, "both releasing approvals must be consumed in the ledger"
    # SAME approvals again (same nonces, same signatures) — a later call.
    second = m.ccas_decide(action, "dual_approval")
    assert second["status"] == "pending_dual_approval", second
    assert second["approvals"] == 0, "consumed approvals must count for nothing on replay"


def test_unreadable_ledger_is_fail_closed():
    """Fas 2.17 — a corrupt/unreadable ledger means freshness cannot be proven:
    every approval is invalid until the ledger is restored."""
    import os as _os

    m = _load(KEY)
    body = _content(m)
    ref = _ref(m, body)
    with open(_os.environ["CCAS_LEDGER_PATH"], "w") as f:
        f.write("not-json-at-all")
    d = m.ccas_decide(_bound(m, body, [_approval(m, ref, "dr_a"), _approval(m, ref, "dr_b")]), "dual_approval")
    assert d["status"] == "pending_dual_approval", d
    assert d["approvals"] == 0


def test_expired_approval_never_counts_and_expiry_is_signature_bound():
    """Fas 2.17 — an EXPLICIT expires_at in the past (or malformed) invalidates
    the approval fail-closed; the expiry is PART of the signed bytes, so
    STRIPPING it from a signed approval breaks the signature (no un-expiring)."""
    import time as _time

    m = _load(KEY)
    body = _content(m)
    ref = _ref(m, body)
    expired = _approval(m, ref, "dr_a", expires_at=_time.time() - 60)
    malformed = _approval(m, ref, "dr_b", expires_at="not-a-timestamp")
    d = m.ccas_decide(_bound(m, body, [expired, malformed]), "dual_approval")
    assert d["approvals"] == 0, d
    # Strip-attack: take a signed-with-expiry approval and delete the expiry —
    # the signature covered it, so the stripped record must not verify.
    stripped = _approval(m, ref, "dr_e", expires_at=_time.time() - 60)
    del stripped["expires_at"]
    d_strip = m.ccas_decide(_bound(m, body, [stripped]), "manual")
    assert d_strip["status"] == "pending", d_strip  # signature no longer verifies
    fresh = _approval(m, ref, "dr_c", expires_at=_time.time() + 3600)
    other = _approval(m, ref, "dr_d")
    d2 = m.ccas_decide(_bound(m, body, [fresh, other]), "dual_approval")
    assert d2["status"] == "approved", d2


def test_clock_rollback_cannot_revive_an_expired_approval(reissue_fleet_lease):
    """Fas 3.13 (adversarial) — expires_at is judged against time.time(), and
    nothing in a container makes that clock trustworthy. Move it back a day and
    every expired approval is fresh again; demonstrated on the real signed
    bundle. Time cannot be VERIFIED without a trusted source, so the guard does
    not pretend to: it makes rollback DETECTABLE from what is already on disk.
    The approval ledger is append-only, so its highest timestamp is a floor the
    clock must never fall below, and a release is withheld when it does."""
    import time as _time

    m = _load(KEY)
    body = _content(m)
    ref = _ref(m, body)

    # On a brand-new deployment nothing has been recorded, so there is no floor
    # and rollback is genuinely UNDETECTABLE. The decision says so rather than
    # implying a guarantee the file cannot give - the posture is disclosed, not
    # assumed away. The trust is sampled BEFORE the decision on purpose: it must
    # describe the clock as it was when expiry was judged.
    assert m.clock_trust() == "no_high_water"
    first = m.ccas_decide(
        _bound(m, body, [_approval(m, ref, "dr_a"), _approval(m, ref, "dr_b")]),
        "dual_approval")
    assert first["status"] == "approved", first
    assert first["clock_trust"] == "no_high_water", first

    # That release consumed the approvals into the append-only ledger, and THAT
    # is what creates the floor the clock can no longer fall below.
    assert m.clock_trust() == "monotonic_ok"

    # THE ATTACK: the process clock now reads a day earlier, so an approval that
    # expired an hour ago looks fresh. Sign it AT the rolled-back time, which is
    # what an attacker who controls the clock would actually be able to produce.
    real_time = _time.time
    body2 = _content(m, request_id="rollback-probe")
    ref2 = _ref(m, body2)
    try:
        m.time.time = lambda: real_time() - 86400
        # Re-mint the fleet capability lease AT the rolled-back clock, so the
        # coordinator lease is genuinely fresh under the attacker's clock. This
        # is the strong case: the lease gate is SATISFIED, and the decision must
        # still be withheld by the DEEPER defence — the approval ledger's
        # monotonic floor — proving that layer catches rollback on its own, not
        # that the lease freshness merely masked it. (No-op on a non-fleet bundle.)
        reissue_fleet_lease(real_time() - 86400)
        revived = _approval(m, ref2, "dr_c", expires_at=real_time() - 3600)
        assert m._not_expired(revived) is True, (
            "fixture is wrong: the rolled-back clock must make the expiry look fresh")
        d = m.ccas_decide(
            _bound(m, body2, [revived, _approval(m, ref2, "dr_d")]), "dual_approval")
    finally:
        m.time.time = real_time
        reissue_fleet_lease(real_time())

    assert d["clock_trust"] == "rollback_detected", d
    assert d["status"] != "approved", (
        "an approval revived by moving the clock backwards must not release")
    assert d["route"] == "approval_queue", d
