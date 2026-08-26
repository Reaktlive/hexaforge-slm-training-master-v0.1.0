"""Fleet transport — the over-the-wire half of the trust plane (blocker B1).

The trust plane was proven in-process; this suite proves the WIRE and the RETURN
path in this bundle, fail-closed with positive controls:

  * no coordinator URL / no token / http without opt-out / https without a
    pinned CA                                    -> not transported (named reason)
  * unsigned release (no member key)             -> not transported (named reason)
  * coordinator rejects (accepted=false)         -> nothing installed, reasons carried
  * coordinator accepts but withholds the lease  -> nothing installed
  * lease for ANOTHER member / bad coordinator
    signature / wrong fleet / expired            -> NOT installed, previous lease untouched
  * coordinator unreachable / non-JSON           -> recorded, never raises
  * POSITIVE CONTROL: a valid coordinator answer -> lease installed atomically at
    FLEET_LEASE_PATH and ccas_decide ADMITS the scoped action; deleting the
    lease returns the gate to fail-closed.
  * the runtime no longer discards the release after release_ready (source
    guard) and serve.py refuses a half-configured TLS pair.
The fake coordinator is a loopback HTTP server that answers with whatever the
test scripts — the member-side logic under test is exactly the shipped one.
"""
from __future__ import annotations

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from src.shared import fleet_transport
from src.shared.fleet_core import (
    FLEET_SIGNAL_SCHEMA_VERSION,
    build_evidence,
    fleet_evidence_digest,
    fleet_signal_canonical,
    mint_lease,
)
from src.shared.fleet_trust import ed25519_public_key, ed25519_sign, install_lease

MEMBER_SEED = bytes(range(32))
COORD_SEED = bytes(range(32, 64))
OTHER_COORD_SEED = bytes(range(64, 96))
COORD_PUB = ed25519_public_key(COORD_SEED).hex()
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


def _local_id() -> str:
    from src.shared.fleet_trust import _identity
    return str(_identity().get("agent_id") or "")


def _coord_sign(msg: bytes) -> str:
    return ed25519_sign(COORD_SEED, msg).hex()


def _iso(ts: float) -> str:
    from datetime import datetime, timezone
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def make_release(now: float, signed: bool = True) -> dict:
    ev = build_evidence(ceve_verdict="PASS", ceve_score=100, degraded=False,
                        karta_hash=KARTA_HASH, doctrine_version=DOCTRINE, approval_provenance="ok")
    env = {
        "schema_version": FLEET_SIGNAL_SCHEMA_VERSION,
        "event_type": "k_anonymous_cohort_summary", "vertical": "reference",
        "aggregate_payload": {"cohort_size": 7}, "k_count": 7, "cycle_id": "cycle-0001",
        "window_start": _iso(now - 3600), "window_end": _iso(now),
        "member_agent_id": _local_id(), "karta_hash": KARTA_HASH, "doctrine_version": DOCTRINE,
        "sequence": 1, "nonce": "nonce-1", "emitted_at": _iso(now),
        "evidence": ev, "evidence_digest": fleet_evidence_digest(ev),
        # member-side bookkeeping that must NOT go on the wire
        "released": True, "held_reason": None,
    }
    if signed:
        env["sig"] = ed25519_sign(MEMBER_SEED, fleet_signal_canonical(env)).hex()
        env["fleet_auth"] = {"signed": True, "alg": "ed25519"}
    else:
        env["sig"] = "unsigned"
        env["fleet_auth"] = {"signed": False, "reason": "FLEET_MEMBER_KEY not provisioned"}
    return env


class _FakeCoordinator:
    """Loopback HTTP coordinator. `script` is a callable(body_dict, headers) ->
    (status, response_dict|bytes). Records every request it saw."""

    def __init__(self, script):
        self.script = script
        self.requests: list = []
        outer = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a, **k):  # silence
                pass

            def do_POST(self):
                n = int(self.headers.get("Content-Length") or 0)
                raw = self.rfile.read(n) if n else b""
                try:
                    body = json.loads(raw.decode("utf-8"))
                except ValueError:
                    body = None
                outer.requests.append({"path": self.path, "body": body,
                                       "auth": self.headers.get("Authorization"),
                                       "content_type": self.headers.get("Content-Type")})
                status, resp = outer.script(body, dict(self.headers))
                data = resp if isinstance(resp, (bytes, bytearray)) else json.dumps(resp).encode("utf-8")
                self.send_response(int(status))
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

        self.httpd = HTTPServer(("127.0.0.1", 0), H)
        self.url = "http://127.0.0.1:%d" % self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    def close(self):
        self.httpd.shutdown()
        self.httpd.server_close()


@pytest.fixture()
def member_env(tmp_path, monkeypatch):
    """A fleet-managed member wired for transport: registry with the coordinator
    PUBLIC lease key + this member's scope, a lease path, and a plaintext
    loopback opt-out (the TLS branch is exercised separately)."""
    local = _local_id()
    assert local, "the bundle identity must carry agent_id"
    reg = {"fleet_id": "test-fleet", "doctrine_version": DOCTRINE,
           "lease_pubkey_hex": COORD_PUB, "lease_epoch": 1,
           "members": {local: {"karta_hash": KARTA_HASH, "doctrine_version": DOCTRINE,
                               "pubkey_hex": ed25519_public_key(MEMBER_SEED).hex(),
                               "capability_scope": ["quarantine_host", "isolate_host"]}}}
    _fleet_posture(tmp_path, monkeypatch, reg)
    monkeypatch.setenv("FLEET_MANAGED", "1")
    monkeypatch.setenv("FLEET_LEASE_PATH", str(tmp_path / "fleet" / "lease.json"))
    monkeypatch.setenv("FLEET_COORDINATOR_TOKEN", "test-token-123")
    monkeypatch.setenv("FLEET_TRANSPORT_ALLOW_PLAINTEXT", "1")
    monkeypatch.setenv("FLEET_TRANSPORT_TIMEOUT_S", "3")
    monkeypatch.setenv("HEXA_RECORD_PATH", str(tmp_path / "hexa_record.jsonl"))
    for k in ("FLEET_COORDINATOR_URL", "FLEET_TLS_CA_FILE", "FLEET_TLS_CLIENT_CERT_FILE", "FLEET_TLS_CLIENT_KEY_FILE"):
        monkeypatch.delenv(k, raising=False)
    return {"local": local, "lease_path": tmp_path / "fleet" / "lease.json", "tmp": tmp_path}


def _lease_for(member: str, *, seed=COORD_SEED, fleet_id="test-fleet", epoch=1, now=None,
               scope=("quarantine_host",), posture="normal") -> dict:
    now = time.time() if now is None else now
    return mint_lease(fleet_id=fleet_id, member_hexa_id=member, capability_scope=list(scope),
                      now_ts=now, fleet_posture=posture, epoch=epoch,
                      sign=lambda m: ed25519_sign(seed, m).hex())


def _accept_with(lease):
    def script(body, headers):
        return 200, {"node": "fleet_coordinator", "port": "xi", "ok": True, "accepted": True,
                     "member": body.get("member_agent_id"),
                     "attestation": {"attested": True, "state": "attested", "reasons": []},
                     "drift": {"drifted": False, "flags": []},
                     "decision": {"renew": lease is not None, "action": "renew" if lease else "withhold",
                                  "reasons": [] if lease else ["lease_signing_key_not_provisioned"]},
                     "lease": lease, "signature": "fleet.intake"}
    return script


ACTION = {"selected_action": "quarantine_host", "target_asset": "host-1", "tenant_id": "t1"}


# ── configuration fail-closed ────────────────────────────────────────────

def test_no_coordinator_url_not_transported(member_env):
    rec = fleet_transport.dispatch_release(make_release(time.time()))
    assert rec["attempted"] is False and rec["transported"] is False and rec["lease_installed"] is False
    assert "coordinator_url_not_configured" in rec["reasons"]
    assert not member_env["lease_path"].exists()


def test_plaintext_refused_without_explicit_opt_out(member_env, monkeypatch):
    monkeypatch.setenv("FLEET_COORDINATOR_URL", "http://127.0.0.1:1")
    monkeypatch.delenv("FLEET_TRANSPORT_ALLOW_PLAINTEXT", raising=False)
    rec = fleet_transport.dispatch_release(make_release(time.time()))
    assert rec["attempted"] is False
    assert any(r.startswith("plaintext_refused") for r in rec["reasons"]), rec


def test_https_without_pinned_ca_refused(member_env, monkeypatch):
    monkeypatch.setenv("FLEET_COORDINATOR_URL", "https://macrohub:8443")
    rec = fleet_transport.dispatch_release(make_release(time.time()))
    assert rec["attempted"] is False and "tls_ca_not_pinned" in rec["reasons"]


def test_missing_token_refused(member_env, monkeypatch):
    monkeypatch.setenv("FLEET_COORDINATOR_URL", "http://127.0.0.1:1")
    monkeypatch.delenv("FLEET_COORDINATOR_TOKEN", raising=False)
    rec = fleet_transport.dispatch_release(make_release(time.time()))
    assert rec["attempted"] is False and "coordinator_token_not_provisioned" in rec["reasons"]


def test_unsigned_release_not_transported(member_env, monkeypatch):
    fake = _FakeCoordinator(_accept_with(_lease_for(member_env["local"])))
    try:
        monkeypatch.setenv("FLEET_COORDINATOR_URL", fake.url)
        rec = fleet_transport.dispatch_release(make_release(time.time(), signed=False))
        assert rec["attempted"] is False and "release_unsigned_member_key_not_provisioned" in rec["reasons"]
        assert fake.requests == []  # nothing left the member
    finally:
        fake.close()


# ── the wire ─────────────────────────────────────────────────────────────

def test_wire_carries_exactly_the_signed_fields_and_bearer(member_env, monkeypatch):
    fake = _FakeCoordinator(_accept_with(_lease_for(member_env["local"])))
    try:
        monkeypatch.setenv("FLEET_COORDINATOR_URL", fake.url)
        rel = make_release(time.time())
        rec = fleet_transport.dispatch_release(rel)
        assert rec["transported"] is True and rec["http_status"] == 200, rec
        assert len(fake.requests) == 1
        req = fake.requests[0]
        assert req["path"] == fleet_transport.COORDINATOR_INTAKE_PATH
        assert req["auth"] == "Bearer test-token-123"
        body = req["body"]
        # exactly the signed fields + sig — no member bookkeeping leaked
        assert set(body.keys()) == set(fleet_transport.wire_envelope(rel).keys())
        assert "released" not in body and "fleet_auth" not in body and "held_reason" not in body
        # the coordinator's XI contract needs the evidence OBJECT (digest-bound) + sig
        assert isinstance(body.get("evidence"), dict) and body.get("evidence_digest") and body.get("sig")
        for f in fleet_transport.FLEET_SIGNAL_SIG_FIELDS:
            assert f in body, f
        # the coordinator can re-derive the same canonical bytes -> the signature holds
        assert fleet_signal_canonical(body) == fleet_signal_canonical(rel)
        assert rec["signal_digest"] == fleet_transport.signal_digest(rel)
    finally:
        fake.close()


def test_positive_control_lease_installed_and_ccas_admits(member_env, monkeypatch):
    from src.shared.ccas_gate import ccas_decide
    # fail-closed BEFORE the round trip
    before = ccas_decide(ACTION, "tier_1")
    assert before["status"] == "denied" and before["route"] == "fleet_lease_gate", before
    fake = _FakeCoordinator(_accept_with(_lease_for(member_env["local"])))
    try:
        monkeypatch.setenv("FLEET_COORDINATOR_URL", fake.url)
        rec = fleet_transport.dispatch_release(make_release(time.time()))
        assert rec["accepted"] is True and rec["attested"] is True and rec["decision"] == "renew", rec
        assert rec["lease_offered"] is True and rec["lease_installed"] is True, rec
        assert member_env["lease_path"].exists()
        installed = json.loads(member_env["lease_path"].read_text())
        assert installed["member_hexa_id"] == member_env["local"]
        after = ccas_decide(ACTION, "tier_1")
        assert after.get("route") != "fleet_lease_gate", after
        # out-of-scope capability is still refused by the SAME lease
        oos = ccas_decide(dict(ACTION, selected_action="delete_all_backups"), "tier_1")
        assert oos["status"] == "denied" and oos["route"] == "fleet_lease_gate"
        # removing the lease returns the gate to fail-closed
        member_env["lease_path"].unlink()
        gone = ccas_decide(ACTION, "tier_1")
        assert gone["status"] == "denied" and gone["route"] == "fleet_lease_gate"
    finally:
        fake.close()


def test_transport_record_is_audit_logged_hash_bound(member_env, monkeypatch, tmp_path):
    """The transport outcome is a HexaRecord entry whose payload_sha256 is the
    canonical hash of the exact transport record (event + slim fields) — a run
    record can bind the wire outcome to the tamper-evident chain."""
    from src.shared.hexa_record import canonical_sha256, read_chain
    fake = _FakeCoordinator(_accept_with(_lease_for(member_env["local"])))
    try:
        monkeypatch.setenv("FLEET_COORDINATOR_URL", fake.url)
        rec = fleet_transport.dispatch_release(make_release(time.time()))
    finally:
        fake.close()
    assert rec["lease_installed"] is True
    entries = [e for e in read_chain(str(tmp_path / "hexa_record.jsonl"))
               if e.get("node_id") == "fleet_transport" and e.get("port") == "mo"]
    assert entries, "no fleet_transport entry on the audit chain"
    expected = canonical_sha256({"event": "fleet.lease_installed", **fleet_transport._slim(rec)})
    assert entries[-1]["payload_sha256"] == expected


# ── coordinator answers that must NOT install anything ───────────────────

def test_coordinator_rejection_installs_nothing_and_carries_reasons(member_env, monkeypatch):
    def reject(body, headers):
        return 200, {"ok": False, "accepted": False, "member": body.get("member_agent_id"),
                     "reasons": ["bad_signature"], "signature": "fleet.intake_rejected"}
    fake = _FakeCoordinator(reject)
    try:
        monkeypatch.setenv("FLEET_COORDINATOR_URL", fake.url)
        rec = fleet_transport.dispatch_release(make_release(time.time()))
        assert rec["transported"] is True and rec["accepted"] is False and rec["lease_installed"] is False
        assert "coordinator:bad_signature" in rec["reasons"]
        assert not member_env["lease_path"].exists()
    finally:
        fake.close()


def test_accepted_but_lease_withheld_installs_nothing(member_env, monkeypatch):
    fake = _FakeCoordinator(_accept_with(None))
    try:
        monkeypatch.setenv("FLEET_COORDINATOR_URL", fake.url)
        rec = fleet_transport.dispatch_release(make_release(time.time()))
        assert rec["accepted"] is True and rec["lease_offered"] is False and rec["lease_installed"] is False
        assert "no_lease_in_coordinator_response" in rec["reasons"]
        assert "coordinator:lease_signing_key_not_provisioned" in rec["reasons"]
        assert not member_env["lease_path"].exists()
    finally:
        fake.close()


@pytest.mark.parametrize("label,bad_lease_factory,expected", [
    ("foreign_subject", lambda local: _lease_for("some-other-member"), "member"),
    ("bad_coordinator_signature", lambda local: _lease_for(local, seed=OTHER_COORD_SEED), "sig"),
    ("wrong_fleet", lambda local: _lease_for(local, fleet_id="another-fleet"), "fleet"),
    ("wrong_epoch", lambda local: _lease_for(local, epoch=99), "epoch"),
    ("expired", lambda local: _lease_for(local, now=time.time() - 7200, posture="lockdown"), "expir"),
    ("empty_scope", lambda local: _lease_for(local, scope=()), "scope"),
])
def test_bad_lease_from_coordinator_not_installed(member_env, monkeypatch, label, bad_lease_factory, expected):
    # a GOOD lease is installed first; the bad answer must leave it untouched
    good = _lease_for(member_env["local"])
    ok, why = install_lease(good)
    assert ok, why
    before = member_env["lease_path"].read_text()
    fake = _FakeCoordinator(_accept_with(bad_lease_factory(member_env["local"])))
    try:
        monkeypatch.setenv("FLEET_COORDINATOR_URL", fake.url)
        rec = fleet_transport.dispatch_release(make_release(time.time()))
        assert rec["lease_offered"] is True and rec["lease_installed"] is False, (label, rec)
        assert any(expected in str(r) for r in rec["reasons"]), (label, rec["reasons"])
        assert member_env["lease_path"].read_text() == before  # previous lease untouched
    finally:
        fake.close()


def test_http_error_and_non_json_never_raise(member_env, monkeypatch):
    fake = _FakeCoordinator(lambda b, h: (401, {"detail": "unauthenticated"}))
    try:
        monkeypatch.setenv("FLEET_COORDINATOR_URL", fake.url)
        rec = fleet_transport.dispatch_release(make_release(time.time()))
        assert rec["attempted"] is True and rec["transported"] is False and rec["http_status"] == 401
        assert "coordinator_http_401" in rec["reasons"] and rec["lease_installed"] is False
    finally:
        fake.close()
    fake2 = _FakeCoordinator(lambda b, h: (200, b"<html>not json</html>"))
    try:
        monkeypatch.setenv("FLEET_COORDINATOR_URL", fake2.url)
        rec = fleet_transport.dispatch_release(make_release(time.time()))
        assert rec["transported"] is False and "coordinator_response_not_json" in rec["reasons"]
    finally:
        fake2.close()


def test_unreachable_coordinator_recorded_not_raised(member_env, monkeypatch):
    monkeypatch.setenv("FLEET_COORDINATOR_URL", "http://127.0.0.1:9")  # discard port: refused
    rec = fleet_transport.dispatch_release(make_release(time.time()))
    assert rec["attempted"] is True and rec["transported"] is False and rec["lease_installed"] is False
    assert any(r.startswith("transport_error:") for r in rec["reasons"]), rec


# ── the runtime and the server side ──────────────────────────────────────

def test_runtime_no_longer_discards_the_release():
    """DD finding: 'runtime keeps only metadata and discards the release'.
    The generated runtime must hand the signed release to the transport."""
    from pathlib import Path
    src = (Path(__file__).resolve().parents[2] / "runtime" / "api_server.py").read_text()
    assert "release_ready" in src
    assert "dispatch_release(_r_mo[\"release\"], event_id=event_id)" in src, "api_server must transport the release (bound to the event), not drop it"


def test_serve_tls_pair_fail_closed():
    from runtime.serve import tls_kwargs
    assert tls_kwargs({}) == {}
    with pytest.raises(SystemExit):
        tls_kwargs({"TLS_CERT_FILE": "/x/cert.pem"})
    with pytest.raises(SystemExit):
        tls_kwargs({"TLS_CLIENT_CA_FILE": "/x/ca.pem"})
    kw = tls_kwargs({"TLS_CERT_FILE": "/x/cert.pem", "TLS_KEY_FILE": "/x/key.pem", "TLS_CLIENT_CA_FILE": "/x/ca.pem"})
    import ssl
    assert kw["ssl_certfile"] == "/x/cert.pem" and kw["ssl_ca_certs"] == "/x/ca.pem"
    assert kw["ssl_cert_reqs"] == ssl.CERT_REQUIRED
