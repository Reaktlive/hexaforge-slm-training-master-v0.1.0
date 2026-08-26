"""ARTIFACT_CCAS_APPROVAL_PROVENANCE — no bare-name approvals.

Fas 2.13c (external DD, Peter). Dual approval could be obtained with just names
({"approvals": ["alice", "bob"]}). Now an approval only counts when it is a
structured record bound to THIS action (action_ref), carries an approver role
(CCAS_APPROVER_ROLES), uses a fresh nonce (anti-replay), and is signature-
verified (verify_approval_signature, fail-closed on CCAS_APPROVAL_KEY — a
CUSTOMER_SLOT). Fas 2.17: an approval that has RELEASED an action is CONSUMED
in the persistent ledger (src/shared/approval_ledger.py) before "approved" is
returned and can never release again ON THAT HOST — the consume cycle is atomic
under an exclusive flock, which is advisory and per-host, so cross-replica
single-use needs a shared compare-and-set store (stated in the ledger module
itself); explicit expires_at is signature-bound.
CCAS is a tier-enforcement interface + fail-closed approval seam, not a
finished approvals system. Static checks (the emitted runtime test proves the
behaviour dynamically).
"""
import pathlib
GATE_ID = "ARTIFACT_CCAS_APPROVAL_PROVENANCE"; GATE_NAME = "CCAS Approval Provenance (structured, action-bound, signed, fail-closed — no bare-name approvals)"; GATE_KIND = "hard"
GATE_CATEGORY = "artifact"

def applies(karta):
    return True

def _read(root, rel):
    p = root / rel
    return p.read_text(errors="ignore") if p.is_file() else ""

def evaluate(karta, root: pathlib.Path):
    violations = []
    g = _read(root, "src/shared/ccas_gate.py")
    if not g:
        return {"status": "N_A", "violations": [], "details": "No CCAS gate (src/shared/ccas_gate.py) in this bundle."}
    if "def verify_approval_signature" not in g:
        violations.append({"file": "src/shared/ccas_gate.py", "fix_hint": "no verify_approval_signature — approvals not provenance-checked."})
    if "if not CCAS_APPROVAL_KEY" not in g:
        violations.append({"file": "src/shared/ccas_gate.py", "fix_hint": "signature verification not fail-closed on CCAS_APPROVAL_KEY."})
    if "if not isinstance(item, dict)" not in g:
        violations.append({"file": "src/shared/ccas_gate.py", "fix_hint": "bare-name approvals not rejected — an approval must be a structured record."})
    if "action_ref" not in g:
        violations.append({"file": "src/shared/ccas_gate.py", "fix_hint": "approvals not bound to THIS action (action_ref)."})
    if "CCAS_APPROVER_ROLES" not in g:
        violations.append({"file": "src/shared/ccas_gate.py", "fix_hint": "no approver-role check (CCAS_APPROVER_ROLES)."})
    if "used_nonces" not in g:
        violations.append({"file": "src/shared/ccas_gate.py", "fix_hint": "no anti-replay (nonce de-dup)."})
    if "approval_ledger" not in g or "is_consumed(" not in g:
        violations.append({"file": "src/shared/ccas_gate.py", "fix_hint": "no PERSISTENT anti-replay (consumed-approval ledger check missing) — the same approvals could release again in a later call."})
    if "_consume_for_release" not in g:
        violations.append({"file": "src/shared/ccas_gate.py", "fix_hint": "approvals not consumed before release."})
    if "_not_expired" not in g:
        violations.append({"file": "src/shared/ccas_gate.py", "fix_hint": "explicit expires_at not honored."})
    led = _read(root, "src/shared/approval_ledger.py")
    if not led:
        violations.append({"file": "src/shared/approval_ledger.py", "fix_hint": "persistent approval-consumption ledger module missing."})
    else:
        for needle in ("def is_consumed", "def consume", "LedgerUnavailable", "CCAS_LEDGER_PATH"):
            if needle not in led:
                violations.append({"file": "src/shared/approval_ledger.py", "fix_hint": "ledger module lacks '%s'." % needle})
    t = _read(root, "tests/unit_tests/test_ccas_approval_provenance.py")
    if ("def test_bare_name_approvals_never_satisfy_dual_approval" not in t
            or "def test_unsigned_approvals_are_fail_closed" not in t
            or "def test_signed_action_bound_approvals_from_two_principals_approve" not in t
            or "def test_approvals_are_consumed_on_release_and_replay_is_rejected" not in t
            or "def test_expired_approval_never_counts_and_expiry_is_signature_bound" not in t
            or "def test_clock_rollback_cannot_revive_an_expired_approval" not in t):
        violations.append({"file": "tests/unit_tests/test_ccas_approval_provenance.py", "fix_hint": "runtime proofs for CCAS approval provenance (incl. persistent replay, signature-bound expiry and clock-rollback resistance) are not emitted."})
    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": "A bare name counts for nothing; an approval must be a structured record bound to THIS action, carry an approver role, use a fresh nonce, be unexpired (expires_at signature-bound), be NOT-YET-CONSUMED in the persistent ledger (2.17: consumed before release, fail-closed on unavailable ledger), and be signature-verified (fail-closed on CCAS_APPROVAL_KEY, a CUSTOMER_SLOT). Tier-enforcement interface + fail-closed approval seam (external DD, L7/L8)."}
