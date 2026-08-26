"""WS-1 generator hardening — the reviewer's 10.0-list items #2 and #4, as
emitted, fail-closed tests with positive controls.

  B2  durable replay / sequence state
      * fleet-managed producer without FLEET_SEQ_PATH   -> signal UNSIGNED (named)
      * sequence never returns to 1 across a "restart"  -> continues from disk
      * sequence write failure / corrupt state          -> UNSIGNED (named), never 0
      * fleet-managed consumer without durable replay   -> every signal REFUSED
      * replay persistence failure                      -> signal REFUSED, state not advanced
      * corrupt replay state                            -> hard error at construction
      * the reviewer's repro: accept, restart, replay   -> REFUSED (durable high-water)
  PIN  mandatory runtime manifest pin (three-case matrix)
      * right pin loads · wrong pin refused · NO pin refused (fleet-managed)
  COHORT  time-windowed buffer + real tenants + silence on the clock
      * a member that reported once ages out of k
      * one member cannot contribute unboundedly
      * silence detected without a fresh snapshot
      * k counts DISTINCT tenants — agent id is never a tenant
  K-POLICY  the signed manifest is the runtime authority for the k floor
      * signed fleet_floor 999 raises the runtime floor; a floor below the code
        constant cannot lower it; a 5->999 edit WITHOUT re-sign is refused at load
"""
from __future__ import annotations

import json
import os
import time

import pytest

from src.shared import fleet_trust
from src.shared.fleet_core import (
    FLEET_K_FLOOR,
    FLEET_SIGNAL_SCHEMA_VERSION,
    CohortBuffer,
    build_evidence,
    fleet_evidence_digest,
    fleet_signal_canonical,
    kanon_aggregate,
    sweep_silence,
)
from src.shared.fleet_trust import FleetStateError, ReplayState, ed25519_public_key, ed25519_sign, verify_envelope

SEED = bytes(range(32))
PUB = ed25519_public_key(SEED).hex()
MEMBER = "member-agent-0001"
KARTA_HASH = "a" * 64
DOCTRINE = "ruleset-14i-1.0.0"
_MANIFEST_SEED = bytes([7]) * 32


def _iso(ts: float) -> str:
    from datetime import datetime, timezone
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def _canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def _write_posture(tmp_path, monkeypatch, reg: dict, *, seed: bytes = _MANIFEST_SEED, pin: "str | None" = "right",
                   resign: bool = True, name: str = "registry") -> None:
    """Registry + signed manifest anchoring it. pin: 'right' | 'wrong' | None."""
    import hashlib as _h
    body = {"manifest_version": "test", "registry_sha256": _h.sha256(_canon(reg)).hexdigest(),
            "signer_pubkey_hex": ed25519_public_key(seed).hex()}
    manifest = dict(body, signature={"alg": "ed25519", "sig": ed25519_sign(seed, _canon(body)).hex()})
    regp = tmp_path / (name + ".json")
    regp.write_text(json.dumps(reg, indent=2))
    manp = tmp_path / (name + ".manifest.json")
    manp.write_text(json.dumps(manifest))
    monkeypatch.setenv("FLEET_MEMBER_REGISTRY", str(regp))
    monkeypatch.setenv("FLEET_MANIFEST_PATH", str(manp))
    if pin == "right":
        monkeypatch.setenv("FLEET_MANIFEST_PUBKEY", ed25519_public_key(seed).hex())
    elif pin == "wrong":
        monkeypatch.setenv("FLEET_MANIFEST_PUBKEY", "11" * 32)
    else:
        monkeypatch.delenv("FLEET_MANIFEST_PUBKEY", raising=False)


def _reg(**extra) -> dict:
    reg = {"fleet_id": "reference-fleet", "doctrine_version": DOCTRINE,
           "members": {MEMBER: {"karta_hash": KARTA_HASH, "doctrine_version": DOCTRINE, "pubkey_hex": PUB}}}
    reg.update(extra)
    return reg


def _envelope(now: float, sequence: int = 1) -> dict:
    ev = build_evidence(ceve_verdict="PASS", ceve_score=100, degraded=False,
                        karta_hash=KARTA_HASH, doctrine_version=DOCTRINE, approval_provenance="ok")
    env = {"schema_version": FLEET_SIGNAL_SCHEMA_VERSION, "event_type": "k_anonymous_cohort_summary",
           "vertical": "reference", "aggregate_payload": {"cohort_size": 7}, "k_count": 7,
           "cycle_id": "cycle-0001", "window_start": _iso(now - 3600), "window_end": _iso(now),
           "member_agent_id": MEMBER, "karta_hash": KARTA_HASH, "doctrine_version": DOCTRINE,
           "sequence": sequence, "nonce": "nonce-%d" % sequence, "emitted_at": _iso(now),
           "evidence": ev, "evidence_digest": fleet_evidence_digest(ev)}
    env["sig"] = ed25519_sign(SEED, fleet_signal_canonical(env)).hex()
    return env


@pytest.fixture()
def fleet(tmp_path, monkeypatch):
    """A fleet-managed runtime with a properly anchored registry and DURABLE
    replay state (the positive posture every negative below deviates from)."""
    monkeypatch.setenv("FLEET_MANAGED", "1")
    _write_posture(tmp_path, monkeypatch, _reg())
    monkeypatch.setenv("FLEET_REPLAY_PATH", str(tmp_path / "fleet" / "replay.json"))
    monkeypatch.setenv("FLEET_SEQ_PATH", str(tmp_path / "fleet" / "seq"))
    monkeypatch.setenv("FLEET_MEMBER_KEY", "ed25519:" + SEED.hex())
    fleet_trust._SEQ_STATE["sequence"] = 0
    return tmp_path


# ── B2: producer sequence ────────────────────────────────────────────────

def test_b2_fleet_member_without_durable_sequence_does_not_sign(fleet, monkeypatch):
    monkeypatch.delenv("FLEET_SEQ_PATH", raising=False)
    env = fleet_trust.stamp_and_sign({"schema_version": FLEET_SIGNAL_SCHEMA_VERSION})
    assert env["sig"] == "unsigned" and env["fleet_auth"]["signed"] is False
    assert env["fleet_auth"]["reason"].startswith("sequence_state_not_durable")
    assert env["sequence"] is None  # never a fresh in-memory "1"


def test_b2_sequence_never_returns_to_one_across_restart(fleet):
    a = fleet_trust.stamp_and_sign({"schema_version": FLEET_SIGNAL_SCHEMA_VERSION})
    b = fleet_trust.stamp_and_sign({"schema_version": FLEET_SIGNAL_SCHEMA_VERSION})
    assert a["fleet_auth"]["signed"] and b["fleet_auth"]["signed"]
    assert (a["sequence"], b["sequence"]) == (1, 2)
    fleet_trust._SEQ_STATE["sequence"] = 0          # "restart": process memory gone
    c = fleet_trust.stamp_and_sign({"schema_version": FLEET_SIGNAL_SCHEMA_VERSION})
    assert c["sequence"] == 3, c                     # continues from disk


def test_b2_sequence_write_failure_refuses_the_signal(fleet, monkeypatch, tmp_path):
    blocker = tmp_path / "not-a-dir"
    blocker.write_text("x")
    monkeypatch.setenv("FLEET_SEQ_PATH", str(blocker / "seq"))  # parent is a FILE -> mkdir fails
    env = fleet_trust.stamp_and_sign({"schema_version": FLEET_SIGNAL_SCHEMA_VERSION})
    assert env["sig"] == "unsigned" and env["fleet_auth"]["reason"].startswith("sequence_state_write_failed")


def test_b2_corrupt_sequence_state_refuses_never_zero(fleet, tmp_path):
    p = tmp_path / "fleet" / "seq"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("not-a-number")
    env = fleet_trust.stamp_and_sign({"schema_version": FLEET_SIGNAL_SCHEMA_VERSION})
    assert env["sig"] == "unsigned" and env["fleet_auth"]["reason"].startswith("sequence_state_corrupt")


# ── B2: consumer replay state ───────────────────────────────────────────

def test_b2_consumer_without_durable_replay_refuses_every_signal(fleet, monkeypatch):
    now = time.time()
    monkeypatch.delenv("FLEET_REPLAY_PATH", raising=False)
    result = verify_envelope(_envelope(now), now_ts=now, state=ReplayState())
    assert result["valid"] is False and result["reasons"] == ["replay_state_not_durable"], result
    # positive control: the SAME envelope with durable state is accepted
    monkeypatch.setenv("FLEET_REPLAY_PATH", str(fleet / "fleet" / "replay.json"))
    ok = verify_envelope(_envelope(now), now_ts=now, state=ReplayState())
    assert ok["valid"] is True, ok


def test_b2_reviewer_repro_accept_restart_replay_refused(fleet):
    now = time.time()
    env = _envelope(now, sequence=5)
    assert verify_envelope(env, now_ts=now, state=ReplayState())["valid"] is True
    after_restart = verify_envelope(env, now_ts=now, state=ReplayState())  # new object = restart
    assert after_restart["valid"] is False
    assert any(str(r).startswith("sequence_replay") or r == "nonce_replay" for r in after_restart["reasons"]), after_restart


def test_b2_replay_persist_failure_refuses_and_does_not_advance(fleet, monkeypatch, tmp_path):
    now = time.time()
    blocker = tmp_path / "blocker"
    blocker.write_text("x")
    monkeypatch.setenv("FLEET_REPLAY_PATH", str(blocker / "replay.json"))  # unwritable location
    st = ReplayState()
    result = verify_envelope(_envelope(now, sequence=9), now_ts=now, state=st)
    assert result["valid"] is False and any(str(r).startswith("replay_persist_failed") for r in result["reasons"]), result
    assert st.last_sequence == {}  # memory untouched
    # positive control: same signal on a working store is accepted
    monkeypatch.setenv("FLEET_REPLAY_PATH", str(fleet / "fleet" / "replay.json"))
    assert verify_envelope(_envelope(now, sequence=9), now_ts=now, state=ReplayState())["valid"] is True


def test_b2_corrupt_replay_state_is_a_hard_error(fleet, tmp_path):
    p = fleet / "fleet" / "replay.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("{not json")
    with pytest.raises(FleetStateError):
        ReplayState()
    p.write_text(json.dumps({"last_sequence": [], "nonces": {}}))  # wrong shape
    with pytest.raises(FleetStateError):
        ReplayState()


# ── mandatory pin: the three-case matrix ─────────────────────────────────

def test_pin_matrix_right_loads_wrong_refused_none_refused(fleet, monkeypatch, tmp_path):
    _write_posture(tmp_path, monkeypatch, _reg(), pin="right", name="m1")
    assert isinstance(fleet_trust.load_registry(), dict)
    _write_posture(tmp_path, monkeypatch, _reg(), pin="wrong", name="m2")
    assert fleet_trust.load_registry() is None
    _write_posture(tmp_path, monkeypatch, _reg(), pin=None, name="m3")
    assert fleet_trust.load_registry() is None, "no pin = no registry (not opt-in) for a fleet-managed runtime"
    # and without a manifest at all (registry alone) — refused too
    _write_posture(tmp_path, monkeypatch, _reg(), pin="right", name="m4")
    monkeypatch.delenv("FLEET_MANIFEST_PATH", raising=False)
    assert fleet_trust.load_registry() is None


# ── cohort semantics ─────────────────────────────────────────────────────

def test_cohort_member_reported_once_ages_out_of_k():
    buf = CohortBuffer(ttl_s=60.0)
    t0 = 1_000.0
    for i in range(6):
        buf.upsert("m%d" % i, {"tenant_id": "tenant-%d" % i}, t0)
    assert kanon_aggregate(buf.rows(t0), 5)["k_satisfied"] is True
    buf.sweep(t0 + 61.0)                                   # the window passes, nobody re-reports
    assert len(buf) == 0
    assert kanon_aggregate(buf.rows(t0 + 61.0), 5)["k_satisfied"] is False


def test_cohort_one_member_cannot_contribute_unboundedly():
    buf = CohortBuffer(ttl_s=60.0)
    for i in range(100):
        buf.upsert("chatty", {"tenant_id": "tenant-a", "ceve_score": 100}, 1_000.0 + i)
    assert len(buf) == 1
    agg = kanon_aggregate(buf.rows(1_100.0), 5)
    assert agg["k_satisfied"] is False and agg["k_count"] == 1


def test_cohort_silence_detected_without_a_fresh_snapshot():
    baselines = {"quiet": {"last_attested_at": 1_000.0}, "fresh": {"last_attested_at": 1_050.0}}
    assert sweep_silence(baselines, now_ts=1_040.0, ttl_s=60.0) == []          # both inside the window
    assert sweep_silence(baselines, now_ts=1_070.0, ttl_s=60.0) == ["quiet"]   # evaluated from the clock
    buf = CohortBuffer(ttl_s=60.0)
    buf.upsert("quiet", {"tenant_id": "t1"}, 1_000.0)
    assert buf.silent_members(1_070.0) == ["quiet"]


def test_cohort_k_counts_distinct_tenants_never_agent_ids():
    rows = [{"tenant_id": "operator-A", "member_agent_id": "agent-1"},
            {"tenant_id": "operator-A", "member_agent_id": "agent-2"},
            {"tenant_id": None, "member_agent_id": "agent-3", "hexa_id": "agent-3"}]
    agg = kanon_aggregate(rows, 5)
    assert agg["k_count"] == 1, agg  # two agents of one operator = ONE tenant; unbound tenant not counted


def test_member_tenant_comes_from_the_signed_registry(fleet, monkeypatch, tmp_path):
    reg = _reg()
    reg["members"][MEMBER]["tenant_id"] = "operator-A"
    _write_posture(tmp_path, monkeypatch, reg, name="t1")
    assert fleet_trust.member_tenant(MEMBER) == "operator-A"
    assert fleet_trust.member_tenant("unknown") is None
    _write_posture(tmp_path, monkeypatch, _reg(), name="t2")   # no tenant bound
    assert fleet_trust.member_tenant(MEMBER) is None


# ── signed k-policy as runtime authority ─────────────────────────────────

def test_k_policy_signed_floor_is_runtime_authority(fleet, monkeypatch, tmp_path):
    _write_posture(tmp_path, monkeypatch, _reg(k_policy={"fleet_floor": 999, "member_floor": 7}), name="k1")
    assert fleet_trust.fleet_k_floor("fleet") == 999
    assert fleet_trust.fleet_k_floor("member") == 7
    from src.shared.cohort_store import _effective_k
    assert _effective_k({"k_minimum": 5}) == 7                       # member store follows the signed floor
    # a policy BELOW the code constant cannot lower the floor
    _write_posture(tmp_path, monkeypatch, _reg(k_policy={"fleet_floor": 1, "member_floor": 1}), name="k2")
    assert fleet_trust.fleet_k_floor("fleet") == FLEET_K_FLOOR
    assert _effective_k({"k_minimum": 1}) == FLEET_K_FLOOR


def test_k_policy_edit_without_resign_is_refused_at_load(fleet, monkeypatch, tmp_path):
    _write_posture(tmp_path, monkeypatch, _reg(k_policy={"fleet_floor": 5}), name="k3")
    assert fleet_trust.fleet_k_floor("fleet") == 5
    regp = tmp_path / "k3.json"
    edited = json.loads(regp.read_text())
    edited["k_policy"]["fleet_floor"] = 999                          # the reviewer's 5 -> 999 edit, no re-sign
    regp.write_text(json.dumps(edited, indent=2))
    assert fleet_trust.load_registry() is None                       # refused at load, never silently ignored
    assert fleet_trust.fleet_k_floor("fleet") == FLEET_K_FLOOR       # falls back to the code floor, not to 999 unsigned
    # positive control: the same change RE-SIGNED reaches the runtime
    _write_posture(tmp_path, monkeypatch, _reg(k_policy={"fleet_floor": 999}), name="k4")
    assert fleet_trust.fleet_k_floor("fleet") == 999
