import os as _os
import sys as _sys

# Ensure the repo root is importable regardless of how pytest is invoked.
# `pytest tests/` does NOT add CWD to sys.path the way `python -m pytest` does,
# so without this `from runtime...` / `from src...` fail during collection.
# (Harvest of the Eihwaz #85 fix into the generator — every bundle's tests run
# green out-of-the-box, satisfying Purity Gate P3.)
_REPO_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _REPO_ROOT not in _sys.path:
    _sys.path.insert(0, _REPO_ROOT)

# Fas 2.5 (A3) — transport auth is FAIL-CLOSED by default (unset => ON).
# This suite tests the PIPELINE, not the transport, so the dev opt-out is
# made EXPLICITLY AND VISIBLY here — never implicitly. The dedicated
# Zero-Trust tests re-enable auth themselves (and restore this value).
_os.environ["ZT_REQUIRE_AUTH"] = "0"

import pytest


@pytest.fixture
def sample_event():
    return {"event_id": "evt-1", "ts": "2026-05-08T12:00:00Z", "source": "test-suite", "payload": {}}


# ── Fleet posture provisioning (DD P0 FTC-3, 2026-08-14) ─────────────────────
# A delivered fleet specialist is a SIGNED fleet member (identity.owner.fleet_id
# present), so fleet_trust.fleet_managed() is True by construction and EVERY
# privileged action fail-closes without a valid, in-scope, coordinator-signed
# capability lease. That enforced posture is the SHIPPED default, not an opt-in
# flag. So the bundle's own governance tests must run AS a properly-provisioned
# fleet member — this fixture stands up exactly the runtime deployment wiring a
# fleet operator supplies: a member registry (publishing the coordinator's PUBLIC
# lease key + this member's DECLARED capability scope) and a coordinator-signed
# lease scoped to this agent's declared privileged actions. It never sets
# FLEET_MANAGED (enforcement is decided by the signed identity, not an env flag)
# and never weakens the gate: an undeclared action, a wrong subject, an expired
# or absent lease all still deny — see tests/unit_tests/test_fleet_trust.py,
# whose dedicated lease tests monkeypatch their own posture and are unaffected.
# A genuine standalone (non-fleet) bundle carries no fleet_id and is skipped.
# Populated by the session fixture below with this fleet member's demo lease
# posture (coordinator seed, declared scope, paths) so a test that manipulates
# the process clock can re-mint a lease valid under its own clock via the
# `reissue_fleet_lease` fixture — proving the deeper defence layer, not masking it.
_FLEET_POSTURE: dict = {}


def _mint_member_lease(now_ts: float) -> None:
    """(Re)write this member's capability lease at an explicit clock, signed with
    the demo coordinator key the registry publishes. No-op for a non-fleet bundle."""
    if not _FLEET_POSTURE:
        return
    import json
    from src.shared import fleet_trust as ft
    from src.shared.fleet_core import mint_lease
    seed = _FLEET_POSTURE["coord_seed"]
    lease = mint_lease(fleet_id=_FLEET_POSTURE["fleet_id"],
                       member_hexa_id=_FLEET_POSTURE["agent_id"],
                       capability_scope=_FLEET_POSTURE["scope"], now_ts=float(now_ts),
                       fleet_posture="normal", epoch=1,
                       sign=lambda msg: ft.ed25519_sign(seed, msg).hex())
    _FLEET_POSTURE["lease_path"].write_text(json.dumps(lease))


@pytest.fixture(scope="session", autouse=True)
def _fleet_member_lease_posture(tmp_path_factory):
    import json
    import time
    import hashlib
    from pathlib import Path
    try:
        from src.shared import fleet_trust as ft
    except Exception:
        yield
        return
    ident = ft._identity()
    owner = ident.get("owner") if isinstance(ident.get("owner"), dict) else {}
    fleet_id = owner.get("fleet_id") or ident.get("fleet_id")
    agent_id = str(ident.get("agent_id") or "")
    if not fleet_id or not agent_id:
        # Genuine standalone (non-fleet) bundle — not lease-gated, nothing to do.
        yield
        return
    scope = []
    karta_hash = ""
    try:
        raw = (Path(_REPO_ROOT) / "karta.compiled.json").read_bytes()
        karta_hash = hashlib.sha256(raw).hexdigest()
        meta = json.loads(raw).get("metadata") or {}
        scope = sorted({
            str(a.get("name") or a.get("action") or a.get("canonical_action") or "")
            for a in (meta.get("privileged_actions") or [])
            if isinstance(a, dict) and (a.get("name") or a.get("action") or a.get("canonical_action"))
        })
    except Exception:
        scope = []
    # The generic CCAS approval-provenance unit harness drives a fixed SYNTHETIC
    # action ("transmit_report") through the gate to exercise the approval
    # mechanism itself, independent of any one agent's karta. Include it so those
    # mechanism tests run in a valid fleet posture. The scope check remains
    # meaningful and is proven independently: tests/unit_tests/test_fleet_trust.py
    # mints tightly-scoped leases and asserts out-of-scope / empty-scope / wrong-
    # subject / expired all DENY. No blanket scope is ever granted.
    _HARNESS_SYNTHETIC_ACTIONS = ("transmit_report",)
    scope = sorted(set(scope) | set(_HARNESS_SYNTHETIC_ACTIONS))
    doctrine = str(ident.get("doctrine_version") or ident.get("rules_version") or "")
    d = tmp_path_factory.mktemp("fleet_posture")
    coord_seed = hashlib.sha256(b"CONFTEST-DEMO-FLEET-LEASE-KEY-DO-NOT-SHIP").digest()
    coord_pub = ft.ed25519_public_key(coord_seed).hex()
    member_pub = ft.ed25519_public_key(
        hashlib.sha256(("CONFTEST-DEMO-MEMBER-" + agent_id).encode()).digest()).hex()
    registry = {
        "fleet_id": fleet_id, "doctrine_version": doctrine,
        "lease_pubkey_hex": coord_pub, "lease_epoch": 1,
        "members": {agent_id: {"karta_hash": karta_hash, "doctrine_version": doctrine,
                               "pubkey_hex": member_pub, "capability_scope": scope}},
    }
    reg_path = d / "fleet_member_registry.json"
    reg_path.write_text(json.dumps(registry))
    lease_path = d / "capability_lease.json"
    _FLEET_POSTURE.update({"coord_seed": coord_seed, "fleet_id": fleet_id,
                           "agent_id": agent_id, "scope": scope, "lease_path": lease_path})
    _mint_member_lease(time.time())
    _os.environ["FLEET_MEMBER_REGISTRY"] = str(reg_path)
    _os.environ["FLEET_LEASE_PATH"] = str(lease_path)
    # WS-1: a fleet-managed runtime loads a registry ONLY when it is anchored to
    # a SIGNED manifest under an EXTERNAL pin, and accepts signals only with
    # DURABLE replay/sequence state. The test posture provisions exactly that —
    # a demo signer (never shipped) signs a manifest whose registry_sha256 is the
    # canonical hash of the registry above; the pin is that signer's public key.
    canonical_reg = json.dumps(registry, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    signer_seed = hashlib.sha256(b"CONFTEST-DEMO-FLEET-MANIFEST-SIGNER-DO-NOT-SHIP").digest()
    body = {"manifest_version": "conftest", "registry_sha256": hashlib.sha256(canonical_reg).hexdigest(),
            "signer_pubkey_hex": ft.ed25519_public_key(signer_seed).hex()}
    canonical_body = json.dumps(body, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    manifest = dict(body, signature={"alg": "ed25519", "sig": ft.ed25519_sign(signer_seed, canonical_body).hex()})
    man_path = d / "fleet_manifest.json"
    man_path.write_text(json.dumps(manifest))
    _os.environ["FLEET_MANIFEST_PATH"] = str(man_path)
    _os.environ["FLEET_MANIFEST_PUBKEY"] = ft.ed25519_public_key(signer_seed).hex()
    _os.environ.setdefault("FLEET_REPLAY_PATH", str(d / "fleet_replay.json"))
    _os.environ.setdefault("FLEET_SEQ_PATH", str(d / "fleet_seq"))
    yield


@pytest.fixture
def reissue_fleet_lease():
    """Re-mint THIS member's capability lease at an explicit clock. A test that
    rolls the process clock (e.g. the clock-rollback attack) uses this so the
    coordinator lease is fresh under its manipulated clock — letting the test
    reach and prove the DEEPER defence (the approval ledger's monotonic floor)
    instead of merely re-confirming the lease gate. No-op for a non-fleet bundle."""
    return _mint_member_lease
