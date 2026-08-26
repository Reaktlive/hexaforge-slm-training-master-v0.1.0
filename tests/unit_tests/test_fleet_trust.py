"""Fleet trust plane — adversarial tests with positive controls (DD P0).

Covers exactly the attacks the external review demonstrated:
  * fabricated attestation fields        -> rejected (signal_not_verified)
  * schema_version "evil/v999"           -> rejected (bad_schema_version)
  * unknown member                       -> rejected (unknown_member)
  * karta-hash / doctrine mismatch       -> rejected (binding mismatch)
  * invalid date strings                 -> rejected (unparseable)
  * sequence replay / nonce replay       -> rejected (replay), and STILL rejected
                                            after a coordinator restart (FTC-5)
  * bad or missing signature             -> rejected (bad_signature)
  * tampered evidence after signing      -> rejected (evidence_digest_mismatch, FTC-1)
  * lease for another member / empty or
    out-of-scope capability / expired    -> privileged action DENIED (FTC-2/3)
  * member cannot mint its own lease     -> forged lease DENIED (asymmetric, FTC-2)
Each rejection is paired with the SAME envelope/lease correctly formed -> accepted.
"""
import json
import time

import pytest

from src.shared import fleet_trust
from src.shared.fleet_core import (
    FLEET_SIGNAL_SCHEMA_VERSION,
    attest_conformance,
    build_evidence,
    fleet_evidence_digest,
    fleet_signal_canonical,
    lease_canonical,
    mint_lease,
    verify_fleet_signal,
    verify_lease,
)
from src.shared.fleet_trust import (
    ReplayState,
    ed25519_public_key,
    ed25519_sign,
    verify_envelope,
)

SEED = bytes(range(32))
PUB = ed25519_public_key(SEED).hex()
MEMBER = "member-agent-0001"
KARTA_HASH = "a" * 64
DOCTRINE = "ruleset-14i-1.0.0"


# ── WS-1 posture helper: a fleet-managed runtime only loads a registry that is
#    anchored to a SIGNED manifest under an EXTERNAL pin, and only accepts
#    signals with DURABLE replay/sequence state. Tests build exactly that.
_MANIFEST_SEED = bytes([7]) * 32


def _fleet_posture(tmp_path, monkeypatch, reg: dict, *, seed: bytes = _MANIFEST_SEED, name: str = "registry") -> dict:
    """Write reg + a signed manifest anchoring it, pin the signer, and give the
    runtime durable replay/sequence paths. Returns the manifest."""
    import hashlib as _h
    from src.shared.fleet_trust import ed25519_public_key as _pub, ed25519_sign as _sign
    canonical_reg = json.dumps(reg, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    body = {"manifest_version": "test", "registry_sha256": _h.sha256(canonical_reg).hexdigest(),
            "signer_pubkey_hex": _pub(seed).hex()}
    canonical_body = json.dumps(body, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    manifest = dict(body, signature={"alg": "ed25519", "sig": _sign(seed, canonical_body).hex()})
    regp = tmp_path / (name + ".json")
    regp.write_text(json.dumps(reg, indent=2))          # non-canonical on purpose
    manp = tmp_path / (name + ".manifest.json")
    manp.write_text(json.dumps(manifest))
    monkeypatch.setenv("FLEET_MEMBER_REGISTRY", str(regp))
    monkeypatch.setenv("FLEET_MANIFEST_PATH", str(manp))
    monkeypatch.setenv("FLEET_MANIFEST_PUBKEY", _pub(seed).hex())
    monkeypatch.setenv("FLEET_REPLAY_PATH", str(tmp_path / "fleet" / "replay.json"))
    monkeypatch.setenv("FLEET_SEQ_PATH", str(tmp_path / "fleet" / "seq"))
    return manifest


def _iso(ts: float) -> str:
    from datetime import datetime, timezone
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def make_evidence(verdict: str = "PASS", score: int = 100, **ov) -> dict:
    # FTC-1: the authority-bearing evidence object bound into the signature.
    return build_evidence(ceve_verdict=verdict, ceve_score=score,
                          degraded=ov.get("degraded", False), karta_hash=KARTA_HASH,
                          doctrine_version=DOCTRINE,
                          approval_provenance=ov.get("approval_provenance", "ok"))


def make_envelope(now: float, sequence: int = 1, evidence: dict = None, **overrides) -> dict:
    ev = evidence if isinstance(evidence, dict) else make_evidence()
    env = {
        "schema_version": FLEET_SIGNAL_SCHEMA_VERSION,
        "event_type": "k_anonymous_cohort_summary",
        "vertical": "reference",
        "aggregate_payload": {"cohort_size": 7},
        "k_count": 7,
        "cycle_id": "cycle-0001",
        "window_start": _iso(now - 3600),
        "window_end": _iso(now),
        "member_agent_id": MEMBER,
        "karta_hash": KARTA_HASH,
        "doctrine_version": DOCTRINE,
        "sequence": sequence,
        "nonce": "nonce-" + str(sequence),
        "emitted_at": _iso(now),
        # FTC-1: evidence object + its signed digest.
        "evidence": ev,
        "evidence_digest": fleet_evidence_digest(ev),
    }
    env.update(overrides)
    env["sig"] = ed25519_sign(SEED, fleet_signal_canonical(env)).hex()
    return env


@pytest.fixture()
def registry(tmp_path, monkeypatch):
    reg = {
        "fleet_id": "reference-fleet",
        "doctrine_version": DOCTRINE,
        "members": {MEMBER: {"karta_hash": KARTA_HASH, "doctrine_version": DOCTRINE, "pubkey_hex": PUB}},
    }
    _fleet_posture(tmp_path, monkeypatch, reg)
    return reg


def test_positive_control_valid_envelope_is_accepted(registry):
    now = time.time()
    result = verify_envelope(make_envelope(now), now_ts=now, state=ReplayState())
    assert result["valid"] is True, result


def test_evil_schema_version_rejected(registry):
    now = time.time()
    env = make_envelope(now, schema_version="evil/v999")
    result = verify_envelope(env, now_ts=now, state=ReplayState())
    assert result["valid"] is False
    assert any(r.startswith("bad_schema_version") for r in result["reasons"])


def test_unknown_member_rejected(registry):
    now = time.time()
    env = make_envelope(now, member_agent_id="not-a-member")
    result = verify_envelope(env, now_ts=now, state=ReplayState())
    assert result["valid"] is False
    assert any(r.startswith("unknown_member") for r in result["reasons"])


def test_karta_hash_mismatch_rejected(registry):
    now = time.time()
    env = make_envelope(now, karta_hash="b" * 64)
    result = verify_envelope(env, now_ts=now, state=ReplayState())
    assert result["valid"] is False
    assert "karta_hash_mismatch" in result["reasons"]


def test_invalid_dates_rejected(registry):
    now = time.time()
    env = make_envelope(now, emitted_at="not-a-date", window_start="also-not-a-date")
    result = verify_envelope(env, now_ts=now, state=ReplayState())
    assert result["valid"] is False
    assert "unparseable_emitted_at" in result["reasons"]
    assert "unparseable_window" in result["reasons"]


def test_sequence_replay_rejected(registry):
    now = time.time()
    st = ReplayState()
    assert verify_envelope(make_envelope(now, sequence=5), now_ts=now, state=st)["valid"] is True
    replayed = verify_envelope(make_envelope(now, sequence=5, nonce="fresh-nonce"), now_ts=now, state=st)
    assert replayed["valid"] is False
    assert any(r.startswith("sequence_replay") for r in replayed["reasons"])


def test_nonce_replay_rejected(registry):
    now = time.time()
    st = ReplayState()
    first = make_envelope(now, sequence=1, nonce="same-nonce")
    assert verify_envelope(first, now_ts=now, state=st)["valid"] is True
    second = make_envelope(now, sequence=2, nonce="same-nonce")
    result = verify_envelope(second, now_ts=now, state=st)
    assert result["valid"] is False
    assert "nonce_replay" in result["reasons"]


def test_bad_signature_rejected(registry):
    now = time.time()
    env = make_envelope(now)
    env["sig"] = "00" * 64
    result = verify_envelope(env, now_ts=now, state=ReplayState())
    assert result["valid"] is False
    assert "bad_signature" in result["reasons"]


def test_tampered_field_after_signing_rejected(registry):
    now = time.time()
    env = make_envelope(now)
    env["k_count"] = 999  # tamper AFTER signing
    result = verify_envelope(env, now_ts=now, state=ReplayState())
    assert result["valid"] is False
    assert "bad_signature" in result["reasons"]


def test_no_registry_rejects_everything(monkeypatch, tmp_path):
    monkeypatch.delenv("FLEET_MEMBER_REGISTRY", raising=False)
    monkeypatch.setenv("FLEET_REPLAY_PATH", str(tmp_path / "replay.json"))  # durable, so the registry is what fails
    now = time.time()
    result = verify_envelope(make_envelope(now), now_ts=now, state=ReplayState())
    assert result["valid"] is False
    assert "no_member_registry" in result["reasons"]


# ── the exact spoof the external review ran, now refused ────────────────

def test_fabricated_attestation_fields_are_refused_without_verification():
    spoof = {"hexa_id": "fabricated", "ceve_verdict": "PASS", "ceve_score": 100,
             "karta_hash": "f" * 64}
    record = attest_conformance(spoof, DOCTRINE)  # no verification record at all
    assert record["attested"] is False
    assert record["state"] == "rejected"
    assert any(r.startswith("signal_not_verified") for r in record["reasons"])


def test_attestation_accepts_only_a_verified_envelope(registry):
    now = time.time()
    env = make_envelope(now)
    sv = verify_envelope(env, now_ts=now, state=ReplayState())
    assert sv["valid"] is True
    # FTC-1: the snapshot the coordinator attests is the VERIFIED envelope (it
    # carries the signed evidence object); attest reads CEVE from that evidence,
    # never from unsigned top-level fields.
    snapshot = dict(env, hexa_id=MEMBER)
    record = attest_conformance(snapshot, DOCTRINE, sv)
    assert record["attested"] is True, record
    # positive control: the same snapshot with an INVALID verification is refused
    bad = attest_conformance(snapshot, DOCTRINE, {"valid": False, "reasons": ["bad_signature"]})
    assert bad["attested"] is False


# ── producer side ────────────────────────────────────────────────────────

def test_stamp_and_sign_without_key_is_explicitly_unsigned(monkeypatch, tmp_path):
    monkeypatch.delenv("FLEET_MEMBER_KEY", raising=False)
    monkeypatch.setenv("FLEET_SEQ_PATH", str(tmp_path / "seq"))  # durable, so the KEY is what is missing
    env = fleet_trust.stamp_and_sign({"schema_version": FLEET_SIGNAL_SCHEMA_VERSION})
    assert env["sig"] == "unsigned"
    assert env["fleet_auth"]["signed"] is False


def test_stamp_and_sign_with_key_verifies_round_trip(monkeypatch, registry, tmp_path):
    monkeypatch.setenv("FLEET_MEMBER_KEY", "ed25519:" + SEED.hex())
    monkeypatch.setenv("FLEET_MEMBER_ID", MEMBER)
    now = time.time()
    # evidence/evidence_digest are left out too: stamp_and_sign builds the
    # member's OWN evidence from its identity (karta_hash must equal the
    # envelope's — the strict evidence check, DD review v3, enforces that).
    base = {k: v for k, v in make_envelope(now).items()
            if k not in ("member_agent_id", "karta_hash", "doctrine_version",
                          "sequence", "nonce", "emitted_at", "sig",
                          "evidence", "evidence_digest")}
    env = fleet_trust.stamp_and_sign(base)
    assert env["fleet_auth"]["signed"] is True
    # identity comes from disk identity.json when present; bind the registry to
    # whatever was stamped so the signature itself is what is under test.
    reg = {"doctrine_version": env["doctrine_version"],
           "members": {env["member_agent_id"]: {"karta_hash": env["karta_hash"],
                                                 "doctrine_version": env["doctrine_version"],
                                                 "pubkey_hex": PUB}}}
    _fleet_posture(tmp_path, monkeypatch, reg, name="reg2")
    result = verify_envelope(env, now_ts=now, state=ReplayState())
    assert result["valid"] is True, result


# ── FTC-1: evidence tamper (Peter's P0#1 counterexample, verbatim) ───────
# Sign FAIL/0/degraded, then swap the evidence object to PASS/100 without
# re-signing. Before FTC-1 this attested green; now the digest/signature catch it.

def test_evidence_tamper_after_signing_is_rejected(registry):
    now = time.time()
    bad = make_evidence(verdict="FAIL", score=0, degraded=True)
    env = make_envelope(now, evidence=bad)          # legitimately signs FAIL/0
    env["evidence"] = make_evidence(verdict="PASS", score=100)  # attacker flips it
    result = verify_envelope(env, now_ts=now, state=ReplayState())
    assert result["valid"] is False
    assert "evidence_digest_mismatch" in result["reasons"], result

    # attacker re-digests to match, but cannot re-sign (no member key)
    env["evidence_digest"] = fleet_evidence_digest(env["evidence"])
    result2 = verify_envelope(env, now_ts=now, state=ReplayState())
    assert result2["valid"] is False and "bad_signature" in result2["reasons"], result2


# ── DD review v3 (P1): evidence CONTENT is validated, not just signed ─────
# Peter's repro: a legitimately member-signed signal whose evidence carried
# schema_version 'evil-evidence/v999' and karta_hash 'NOT-THE-REGISTRY-KARTA'
# was attested and leased. Now: strict schema + karta/doctrine binding.

def test_evidence_with_foreign_schema_version_is_rejected_even_when_signed(registry):
    now = time.time()
    ev = make_evidence(); ev["schema_version"] = "evil-evidence/v999"
    env = make_envelope(now, evidence=ev)            # signed by the member key
    result = verify_envelope(env, now_ts=now, state=ReplayState())
    assert result["valid"] is False
    assert any(r.startswith("bad_evidence_schema_version") for r in result["reasons"]), result


def test_evidence_karta_hash_not_registry_is_rejected_even_when_signed(registry):
    now = time.time()
    ev = make_evidence(); ev["karta_hash"] = "NOT-THE-REGISTRY-KARTA"
    env = make_envelope(now, evidence=ev)
    result = verify_envelope(env, now_ts=now, state=ReplayState())
    assert result["valid"] is False
    assert "evidence_karta_hash_not_registry" in result["reasons"], result
    assert "evidence_karta_hash_not_envelope" in result["reasons"], result


def test_evidence_types_and_unknown_fields_are_rejected(registry):
    now = time.time()
    ev = make_evidence(); ev["ceve_score"] = 250; ev["ceve_verdict"] = "MAYBE"; ev["degraded"] = "no"; ev["bonus"] = 1
    env = make_envelope(now, evidence=ev)
    result = verify_envelope(env, now_ts=now, state=ReplayState())
    assert result["valid"] is False
    rs = " ".join(result["reasons"])
    assert "bad_evidence_ceve_score" in rs and "bad_evidence_ceve_verdict" in rs and "bad_evidence_degraded_type" in rs and "unknown_evidence_field:bonus" in rs, result


def test_well_formed_evidence_still_verifies(registry):
    now = time.time()
    result = verify_envelope(make_envelope(now), now_ts=now, state=ReplayState())
    assert result["valid"] is True, result


def test_missing_evidence_object_rejected(registry):
    now = time.time()
    env = make_envelope(now)
    env.pop("evidence", None)
    result = verify_envelope(env, now_ts=now, state=ReplayState())
    assert result["valid"] is False
    assert any(r.startswith("missing") for r in result["reasons"]), result


# ── FTC-2 + FTC-3: asymmetric, subject/scope-bound leases at the ccas choke ──
# The coordinator holds the PRIVATE lease key; the member holds only the public
# key (from the signed registry). A member cannot mint its own lease. A lease is
# valid only for THIS member (subject) and only for the action's capability (scope).

_COORD_SEED = bytes([9]) * 32
_COORD_PUB = ed25519_public_key(_COORD_SEED).hex()


def _coord_sign(msg):
    return ed25519_sign(_COORD_SEED, msg).hex()


def _local_id() -> str:
    return str(fleet_trust._identity().get("agent_id") or "")


@pytest.fixture()
def lease_env(tmp_path, monkeypatch):
    """Fleet-managed member with a registry that publishes the coordinator's
    public lease key + this member's declared capability scope."""
    local = _local_id()
    reg = {"fleet_id": "test-fleet", "doctrine_version": DOCTRINE,
           "lease_pubkey_hex": _COORD_PUB, "lease_epoch": 1,
           "members": {local: {"karta_hash": KARTA_HASH, "doctrine_version": DOCTRINE,
                               "pubkey_hex": PUB, "capability_scope": ["quarantine_host", "isolate_host"]}}}
    _fleet_posture(tmp_path, monkeypatch, reg)
    monkeypatch.setenv("FLEET_MANAGED", "1")
    monkeypatch.setenv("FLEET_LEASE_PATH", str(tmp_path / "lease.json"))
    return {"local": local, "lease_path": tmp_path / "lease.json"}


ACTION = {"selected_action": "quarantine_host", "target_asset": "host-1", "tenant_id": "t1"}


def test_fleet_managed_member_denied_without_lease(lease_env):
    from src.shared.ccas_gate import ccas_decide
    d = ccas_decide(ACTION, "tier_3")
    assert d["status"] == "denied" and d["route"] == "fleet_lease_gate", d


def test_valid_scoped_lease_allows(lease_env):
    now = time.time()
    lease = mint_lease(fleet_id="test-fleet", member_hexa_id=lease_env["local"],
                       capability_scope=["quarantine_host"], now_ts=now,
                       fleet_posture="normal", epoch=1, sign=_coord_sign)
    lease_env["lease_path"].write_text(json.dumps(lease))
    from src.shared.ccas_gate import ccas_decide
    d = ccas_decide(ACTION, "tier_3")
    assert d.get("route") != "fleet_lease_gate", d


def test_expired_lease_denied(lease_env):
    now = time.time()
    lease = mint_lease(fleet_id="test-fleet", member_hexa_id=lease_env["local"],
                       capability_scope=["quarantine_host"], now_ts=now - 7200,
                       fleet_posture="lockdown", epoch=1, sign=_coord_sign)
    lease_env["lease_path"].write_text(json.dumps(lease))
    from src.shared.ccas_gate import ccas_decide
    d = ccas_decide(ACTION, "tier_3")
    assert d["status"] == "denied" and d["route"] == "fleet_lease_gate"
    assert "expired" in d["reason"], d


def test_other_member_lease_denied(lease_env):
    # Peter's counterexample: a valid lease for ANOTHER member accepted locally.
    now = time.time()
    lease = mint_lease(fleet_id="test-fleet", member_hexa_id="OTHER-MEMBER",
                       capability_scope=["quarantine_host"], now_ts=now,
                       fleet_posture="normal", epoch=1, sign=_coord_sign)
    lease_env["lease_path"].write_text(json.dumps(lease))
    from src.shared.ccas_gate import ccas_decide
    d = ccas_decide(ACTION, "tier_3")
    assert d["status"] == "denied" and d["route"] == "fleet_lease_gate", d


def test_empty_scope_lease_denied(lease_env):
    # Peter's counterexample: an empty capability scope accepted for a real action.
    now = time.time()
    lease = mint_lease(fleet_id="test-fleet", member_hexa_id=lease_env["local"],
                       capability_scope=[], now_ts=now, fleet_posture="normal",
                       epoch=1, sign=_coord_sign)
    lease_env["lease_path"].write_text(json.dumps(lease))
    from src.shared.ccas_gate import ccas_decide
    d = ccas_decide(ACTION, "tier_3")
    assert d["status"] == "denied" and d["route"] == "fleet_lease_gate", d


def test_out_of_scope_action_denied(lease_env):
    now = time.time()
    lease = mint_lease(fleet_id="test-fleet", member_hexa_id=lease_env["local"],
                       capability_scope=["quarantine_host"], now_ts=now,
                       fleet_posture="normal", epoch=1, sign=_coord_sign)
    lease_env["lease_path"].write_text(json.dumps(lease))
    from src.shared.ccas_gate import ccas_decide
    d = ccas_decide(dict(ACTION, selected_action="delete_all_backups"), "tier_3")
    assert d["status"] == "denied" and d["route"] == "fleet_lease_gate", d


def test_member_cannot_mint_its_own_lease(lease_env):
    # The member holds only the coordinator's PUBLIC key. A lease forged by
    # editing a coordinator-signed token (no re-sign) fails verification.
    now = time.time()
    good = mint_lease(fleet_id="test-fleet", member_hexa_id=lease_env["local"],
                      capability_scope=["quarantine_host"], now_ts=now,
                      fleet_posture="normal", epoch=1, sign=_coord_sign)
    forged = dict(good, capability_scope=["quarantine_host", "delete_all_backups"])
    lease_env["lease_path"].write_text(json.dumps(forged))
    from src.shared.ccas_gate import ccas_decide
    d = ccas_decide(dict(ACTION, selected_action="delete_all_backups"), "tier_3")
    assert d["status"] == "denied" and d["route"] == "fleet_lease_gate", d


# ── FTC-5: replay protection survives a coordinator restart ──────────────

def test_replay_rejected_after_restart(registry, tmp_path, monkeypatch):
    monkeypatch.setenv("FLEET_REPLAY_PATH", str(tmp_path / "replay.json"))
    now = time.time()
    env = make_envelope(now, sequence=5)
    first = verify_envelope(env, now_ts=now, state=ReplayState())
    assert first["valid"] is True, first
    # a brand-new ReplayState loads the persisted high-water from disk (restart)
    after = verify_envelope(env, now_ts=now, state=ReplayState())
    assert after["valid"] is False
    assert any(r.startswith("sequence_replay") or r == "nonce_replay" for r in after["reasons"]), after


# ── DD P0 invariant (Peter, 2026-08-14): a fleet MEMBER must ENFORCE ──────
# The validator invariant, encoded as a fail-closed assertion the bundle SHIPS
# with: if THIS agent's SIGNED identity declares fleet membership (an
# owner.fleet_id, an explicit fleet_managed, or a top-level fleet_id), then
# fleet_managed() MUST be True — so every privileged action is lease-gated. A
# fleet-assigned identity that did NOT enforce would fail here; enforcement can
# never be silently dropped from a signed fleet identity. A genuine standalone
# identity carries none of those fields, is not lease-gated, and is skipped.
def test_fleet_membership_implies_enforcement():
    ident = fleet_trust._identity()
    owner = ident.get("owner") if isinstance(ident.get("owner"), dict) else {}
    is_member = bool(owner.get("fleet_id") or ident.get("fleet_id") or ident.get("fleet_managed"))
    if not is_member:
        pytest.skip("standalone (non-fleet) identity — lease enforcement N/A")
    assert fleet_trust.fleet_managed() is True, (
        "a fleet-assigned identity (owner.fleet_id) MUST be fleet_managed so every "
        "privileged action is lease-gated — enforcement cannot be dropped")
