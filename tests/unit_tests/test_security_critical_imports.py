"""Security-critical runtime modules must IMPORT and WORK — Fas 3.25.

External DD, blocking. src/shared/ed25519_verify.py shipped carrying the
functions but not the module-level curve constants they close over. It raised
NameError on import; ccas_gate swallowed that; every asymmetric signature
verified as False; and the RECOMMENDED production posture
(CCAS_APPROVAL_PUBKEYS bound) could approve no gated tier at all.

Nothing caught it. The bundle's own suite never imported the module, the
factory's BUILD_IMPORT_INTEGRITY gate reported PASS without importing it, and
the red-team attack passed BECAUSE of the breakage — it only ever asked whether
a forged approval is refused, and a module that cannot run refuses everything.

Two lessons, both encoded here:
  * a module nobody imports is a module nobody tests;
  * a control that only proves a refusal cannot tell secure from inoperative.
"""
import importlib

import pytest

# Every module the governance chain depends on at runtime. Import failure here
# is a release blocker, not a warning.
SECURITY_CRITICAL = [
    "src.shared.ed25519_verify",
    "src.shared.canonical_identity",
    "src.shared.ccas_gate",
    "src.shared.approval_ledger",
    "src.shared.execution_ledger",
    "src.shared.hexa_record",
    "src.shared.state_paths",
]

# RFC 8032 section 7.1 TEST 2 — a KNOWN-GOOD signature the verifier must ACCEPT.
RFC8032_PUB = bytes.fromhex("3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c")
RFC8032_MSG = bytes.fromhex("72")
RFC8032_SIG = bytes.fromhex(
    "92a009a9f0d4cab8720e820b5f642540a2b27b5416503f8fb3762223ebdb69da"
    "085ac1e43e15996e458f3613d0f11d8c387b2eaeb4302aeeb00d291612bb0c00")


@pytest.mark.parametrize("name", SECURITY_CRITICAL)
def test_security_critical_module_imports(name):
    """A NameError here means the governance path is inoperative in production."""
    importlib.import_module(name)


def test_ed25519_accepts_a_valid_signature_not_only_refuses_bad_ones():
    """The POSITIVE control. Without it, total breakage reads as strictness."""
    from src.shared.ed25519_verify import ed25519_verify

    assert ed25519_verify(RFC8032_PUB, RFC8032_SIG, RFC8032_MSG) is True, (
        "the verifier rejects the RFC 8032 test vector — it is inoperative, not strict, "
        "and every refusal it produces is meaningless")


def test_ed25519_still_refuses_tampering():
    """The negative half, kept beside the positive one so neither stands alone."""
    from src.shared.ed25519_verify import ed25519_verify

    tampered = bytearray(RFC8032_SIG)
    tampered[0] ^= 1
    assert ed25519_verify(RFC8032_PUB, bytes(tampered), RFC8032_MSG) is False
    assert ed25519_verify(RFC8032_PUB, RFC8032_SIG, b"different message") is False
    assert ed25519_verify(bytes(32), RFC8032_SIG, RFC8032_MSG) is False


def test_one_canonical_identity_shared_by_gate_and_execution_ledger():
    """Fas 3.25 — approval binding and the execution key must agree byte for byte.

    They did not: canonical_action_ref case-folded the tenant, the execution
    ledger only stripped it. Tenant-A and tenant-a produced ONE approval
    reference and TWO execution keys, so the same approved action executed
    twice under a single idempotency key."""
    from src.shared import ccas_gate, execution_ledger
    from src.shared.canonical_identity import canonical_identity

    assert ccas_gate.canonical_identity is canonical_identity
    body = {"selected_action": "act", "target_asset": "x", "idempotency_key": "K1"}
    upper = dict(body, tenant_id="Tenant-A")
    lower = dict(body, tenant_id="tenant-a")
    assert ccas_gate.canonical_action_ref(upper) == ccas_gate.canonical_action_ref(lower)
    assert execution_ledger.execution_key(upper) == execution_ledger.execution_key(lower), (
        "same approval reference, different execution key — one approved action can run twice")
