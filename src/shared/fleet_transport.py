"""fleet_transport — the OVER-THE-WIRE half of the fleet trust plane (blocker B1).

Until this module existed, a fleet-managed member built and SIGNED its
FleetSignal release (cohort_store.build_release -> fleet_trust.stamp_and_sign)
and the runtime then kept only `release_ready: True` — the signed release object
was discarded, the coordinator never saw it, and no lease could ever come back
into the member's CCAS gate. The trust plane was proven in-process only.

This module closes that loop, in the running container, over a real network:

  MEMBER (this runtime)                          COORDINATOR (MacroHub)
  egress.handle_mo -> signed release ──POST──▶  /fleet_coordinator/port-xi
                                                  verify_envelope -> attest ->
                                                  drift -> renew -> mint_lease
  install_lease(token) ◀────── {accepted, attestation, lease} ──────┘
    (verified with the coordinator's PUBLIC key from the signed registry,
     subject == THIS member, then written atomically to FLEET_LEASE_PATH)
  ccas_decide -> require_fleet_lease(capability)  ... admits ONLY with it.

Posture — FAIL-CLOSED at every step, and NEVER raising into the event path
(the cohort is intelligence, not the incident pipeline):
  * no FLEET_COORDINATOR_URL              -> not transported (reason)
  * http:// without the explicit dev opt-out -> refused (TLS is the default)
  * https:// without FLEET_TLS_CA_FILE     -> refused (no system-CA guessing;
                                             the coordinator's CA is PINNED)
  * unsigned release (no member key)       -> not transported (a coordinator
                                             would reject it anyway; we do not
                                             emit noise)
  * coordinator rejects / no lease         -> recorded with the coordinator's
                                             machine-readable reasons; nothing
                                             installed
  * lease not for THIS member / bad sig /
    expired / wrong fleet or epoch         -> NOT installed (reason)
  * network error / timeout / non-JSON     -> recorded, nothing installed
Whatever the outcome, the previously installed lease is left untouched unless a
NEW valid one replaces it — a transient network failure never revokes; expiry
does (require_fleet_lease checks expiry on every action).

Configuration (all env, no defaults that grant anything):
  FLEET_COORDINATOR_URL        base URL of the coordinator runtime, e.g.
                               https://macrohub:8443
  FLEET_COORDINATOR_TOKEN      bearer credential the coordinator's Zero-Trust
                               boundary maps to an identity with the events
                               scope (ZT_IDENTITIES on the coordinator side)
  FLEET_TLS_CA_FILE            PEM CA bundle that signed the coordinator's
                               server certificate (pinned trust anchor)
  FLEET_TLS_CLIENT_CERT_FILE   PEM client certificate for mutual TLS
  FLEET_TLS_CLIENT_KEY_FILE    PEM private key for the client certificate
  FLEET_TRANSPORT_TIMEOUT_S    socket timeout, default 5
  FLEET_TRANSPORT_ALLOW_PLAINTEXT=1  explicit, visible dev opt-out for http://
                               (an unsigned/unencrypted hop is never a
                               production posture)
Only the standard library is used (urllib + ssl): no new dependency enters the
bundle's supply chain for the transport.
"""
from __future__ import annotations

import hashlib
import json
import os
import ssl
import time
import urllib.error
import urllib.request
from typing import Any, Optional, Tuple
from urllib.parse import urlsplit

from src.shared.fleet_core import FLEET_SIGNAL_SIG_FIELDS, fleet_signal_canonical

TRANSPORT_SCHEMA_VERSION = "fleet_transport/v1"
COORDINATOR_INTAKE_PATH = "/fleet_coordinator/port-xi"

_TRUTHY = {"1", "true", "yes", "on"}


def _env(name: str) -> str:
    return str(os.environ.get(name, "") or "").strip()


def transport_configured() -> Tuple[bool, list]:
    """Is the wire configured well enough to even attempt a dispatch? Returns
    (ok, reasons). Every missing piece is NAMED — nothing is guessed."""
    reasons: list = []
    url = _env("FLEET_COORDINATOR_URL")
    if not url:
        return (False, ["coordinator_url_not_configured"])
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        return (False, ["coordinator_url_malformed"])
    if parts.scheme == "http" and _env("FLEET_TRANSPORT_ALLOW_PLAINTEXT").lower() not in _TRUTHY:
        reasons.append("plaintext_refused_set_FLEET_TRANSPORT_ALLOW_PLAINTEXT_for_dev")
    if parts.scheme == "https":
        ca = _env("FLEET_TLS_CA_FILE")
        if not ca:
            reasons.append("tls_ca_not_pinned")
        elif not os.path.isfile(ca):
            reasons.append("tls_ca_file_unreadable")
        cert, key = _env("FLEET_TLS_CLIENT_CERT_FILE"), _env("FLEET_TLS_CLIENT_KEY_FILE")
        if bool(cert) != bool(key):
            reasons.append("tls_client_cert_and_key_must_be_set_together")
        for label, p in (("tls_client_cert_file_unreadable", cert), ("tls_client_key_file_unreadable", key)):
            if p and not os.path.isfile(p):
                reasons.append(label)
    if not _env("FLEET_COORDINATOR_TOKEN"):
        reasons.append("coordinator_token_not_provisioned")
    return (not reasons, reasons)


def _ssl_context() -> Optional[ssl.SSLContext]:
    """A PINNED TLS context: verify the coordinator against FLEET_TLS_CA_FILE
    only (never the ambient system store), hostname checked, TLS 1.2+; load the
    client certificate when mutual TLS is provisioned."""
    ca = _env("FLEET_TLS_CA_FILE")
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.check_hostname = True
    ctx.verify_mode = ssl.CERT_REQUIRED
    ctx.load_verify_locations(cafile=ca)
    cert, key = _env("FLEET_TLS_CLIENT_CERT_FILE"), _env("FLEET_TLS_CLIENT_KEY_FILE")
    if cert and key:
        ctx.load_cert_chain(certfile=cert, keyfile=key)
    return ctx


def wire_envelope(release: dict) -> dict:
    """EXACTLY the signed FleetSignal fields + sig go on the wire — nothing the
    member added for local bookkeeping (fleet_auth, released, held_reason...).
    The coordinator's XI contract is the FleetSignal/v1 envelope, and the
    canonical signed form is reproduced from these fields on both sides."""
    r = release if isinstance(release, dict) else {}
    out = {f: r.get(f) for f in FLEET_SIGNAL_SIG_FIELDS}
    # The signed fields bind the evidence by DIGEST (evidence_digest); the
    # coordinator needs the evidence OBJECT itself to recompute that digest and
    # to attest — so it travels alongside (its integrity is the digest's).
    out["evidence"] = r.get("evidence")
    out["sig"] = r.get("sig")
    return out


def signal_digest(release: dict) -> str:
    """sha256 over the canonical signed form — the value a run record binds."""
    return hashlib.sha256(fleet_signal_canonical(release if isinstance(release, dict) else {})).hexdigest()


def _post_json(url: str, body: dict, token: str, timeout_s: float) -> Tuple[Optional[int], Any, list]:
    """One POST. Returns (http_status, parsed_json_or_None, reasons)."""
    data = json.dumps(body, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST", headers={
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + token,
        "User-Agent": "hexabox-fleet-transport/1",
    })
    ctx = _ssl_context() if url.lower().startswith("https://") else None
    try:
        with urllib.request.urlopen(req, timeout=timeout_s, context=ctx) as resp:
            status = int(getattr(resp, "status", 0) or 0)
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        # The coordinator answered — a 401/403/422 is a decision, not a fault.
        try:
            raw = exc.read()
        except Exception:
            raw = b""
        try:
            parsed = json.loads(raw.decode("utf-8")) if raw else None
        except (ValueError, UnicodeDecodeError):
            parsed = None
        return (int(exc.code), parsed, ["coordinator_http_%d" % int(exc.code)])
    except (urllib.error.URLError, ssl.SSLError, OSError, ValueError) as exc:
        return (None, None, ["transport_error:%s" % type(exc).__name__])
    try:
        return (status, json.loads(raw.decode("utf-8")), [])
    except (ValueError, UnicodeDecodeError):
        return (status, None, ["coordinator_response_not_json"])


def dispatch_release(release: dict, *, now_ts: Optional[float] = None, event_id: Optional[str] = None) -> dict:
    """Transport ONE signed release to the coordinator and, when it answers with
    a lease for THIS member, install it for the CCAS gate. NEVER raises. Returns
    a machine-readable transport record (also written to the audit chain), so a
    run record can bind: what was sent (signal_digest), where, what came back,
    and whether a lease was installed — with named reasons for every refusal.
    `event_id` (the pipeline event that produced the release) binds the audit
    entry to that event's chain, so GET /api/audit/{event_id} shows the wire."""
    from src.shared.fleet_trust import install_lease
    from src.shared.hexa_record import log_event as _log_event

    def log_event(node, port, payload):
        return _log_event(node, port, payload, event_id=event_id)

    now = float(now_ts) if isinstance(now_ts, (int, float)) else time.time()
    rel = release if isinstance(release, dict) else {}
    rec: dict = {
        "schema_version": TRANSPORT_SCHEMA_VERSION,
        "attempted": False, "transported": False,
        "coordinator": None, "http_status": None,
        "accepted": None, "attested": None, "decision": None,
        "lease_offered": False, "lease_installed": False, "lease_expires_at": None,
        "signal_digest": signal_digest(rel),
        "member_agent_id": rel.get("member_agent_id"),
        "cycle_id": rel.get("cycle_id"), "sequence": rel.get("sequence"), "nonce": rel.get("nonce"),
        "reasons": [],
    }
    try:
        auth = rel.get("fleet_auth") if isinstance(rel.get("fleet_auth"), dict) else {}
        if not rel or rel.get("sig") in (None, "", "unsigned") or auth.get("signed") is False:
            rec["reasons"].append("release_unsigned_member_key_not_provisioned")
            log_event("fleet_transport", "mo", {"event": "fleet.transport_refused", **_slim(rec)})
            return rec
        ok, why = transport_configured()
        if not ok:
            rec["reasons"].extend(why)
            log_event("fleet_transport", "mo", {"event": "fleet.transport_refused", **_slim(rec)})
            return rec
        base = _env("FLEET_COORDINATOR_URL").rstrip("/")
        rec["coordinator"] = urlsplit(base).netloc
        try:
            timeout_s = float(_env("FLEET_TRANSPORT_TIMEOUT_S") or "5")
        except ValueError:
            timeout_s = 5.0
        rec["attempted"] = True
        status, body, why = _post_json(base + COORDINATOR_INTAKE_PATH, wire_envelope(rel),
                                       _env("FLEET_COORDINATOR_TOKEN"), timeout_s)
        rec["http_status"] = status
        rec["reasons"].extend(why)
        if not isinstance(body, dict):
            log_event("fleet_transport", "mo", {"event": "fleet.transport_failed", **_slim(rec)})
            return rec
        rec["transported"] = status is not None and 200 <= int(status) < 300
        rec["accepted"] = body.get("accepted") if isinstance(body.get("accepted"), bool) else False
        att = body.get("attestation") if isinstance(body.get("attestation"), dict) else {}
        rec["attested"] = att.get("attested") if isinstance(att.get("attested"), bool) else None
        dec = body.get("decision") if isinstance(body.get("decision"), dict) else {}
        rec["decision"] = dec.get("action")
        if rec["accepted"] is not True:
            for r in (body.get("reasons") or []):
                rec["reasons"].append("coordinator:" + str(r))
            log_event("fleet_transport", "mo", {"event": "fleet.signal_rejected_by_coordinator", **_slim(rec)})
            return rec
        lease = body.get("lease")
        if not isinstance(lease, dict):
            for r in (dec.get("reasons") or []):
                rec["reasons"].append("coordinator:" + str(r))
            rec["reasons"].append("no_lease_in_coordinator_response")
            log_event("fleet_transport", "mo", {"event": "fleet.signal_accepted_no_lease", **_slim(rec)})
            return rec
        rec["lease_offered"] = True
        installed, why = install_lease(lease, now_ts=now)
        rec["lease_installed"] = bool(installed)
        rec["lease_expires_at"] = lease.get("expires_at") if installed else None
        rec["reasons"].extend(why)
        log_event("fleet_transport", "mo", {"event": "fleet.lease_installed" if installed else "fleet.lease_refused",
                                             **_slim(rec)})
        return rec
    except Exception as exc:  # the transport must never take the event path down
        rec["reasons"].append("transport_exception:%s" % type(exc).__name__)
        try:
            log_event("fleet_transport", "mo", {"event": "fleet.transport_failed", **_slim(rec)})
        except Exception:
            pass
        return rec


def _slim(rec: dict) -> dict:
    return {k: rec.get(k) for k in ("coordinator", "http_status", "accepted", "attested", "decision",
                                     "lease_offered", "lease_installed", "lease_expires_at",
                                     "signal_digest", "cycle_id", "sequence", "reasons")}
