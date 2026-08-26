"""fleet_core — MacroHub Fleet-Command deterministic core (platform_complete).

Real, deterministic, offline-runnable logic for the fixed coordinator brain:
  * attest_conformance   — is a member provably CEVE-PASS + genuine identity?
  * diff_drift           — drift from SIGNED snapshots (not heuristics): karta-hash
                           mismatch, CEVE regression, action-rate anomaly, silence.
  * kanon_aggregate      — k-ANONYMOUS cohort aggregation over DISTINCT tenants
                           (never emit a cohort below the k-floor).
  * learn_baseline       — learned fleet baselines (mean/stddev/percentiles) so
                           "abnormal" is measured against signed history, not a
                           hard-coded threshold (HexaLearn Z-loop, v1 statistical).

Pure functions — NO pydantic, NO I/O. The per-node handlers validate the port
contract (pydantic) and then call these. The ONLY seams are documented inline:
the domain cohort-statistic CHOICE and the SLM/RL bind. Cross-vertical standard.
"""
from __future__ import annotations
import math
from typing import Any


# ── authenticated FleetSignal (DD P0) ──────────────────────────────────────────────────────────

# The FleetSignal envelope is AUTHENTICATED: a coordinator trusts nothing a
# member sends until membership, signature, evidence binding, freshness and
# replay protection have ALL been verified fail-closed. Every rejection carries
# a machine-readable reason. Pure function — the Ed25519 verifier is injected
# (the runtime wires the same chain the identity uses); the HMAC reference
# signer exists ONLY for offline tests with explicit ephemeral keys. There is
# NO default key: an absent/unknown member or absent key is a rejection.

# DD P0 FTC-8 (Peter): ONE authority-bearing k-anonymity floor for the whole
# fleet. Both the coordinator's cohort aggregation AND every specialist's
# cohort_store consume THIS single value, so the floor can never be enforced at
# two different numbers. It is 5 by deliberate decision (the vertical/sensitivity
# derivation cannot honestly force a higher floor across a cross-vertical fleet);
# any claim of "k>=10" would be false, so the honest, single-sourced value is 5.
FLEET_K_FLOOR = 5
FLEET_SIGNAL_SCHEMA_VERSION = "fleet_signal/v1"
FLEET_SIGNAL_SIG_FIELDS = (
    "schema_version", "event_type", "vertical", "aggregate_payload",
    "k_count", "cycle_id", "window_start", "window_end",
    "member_agent_id", "karta_hash", "doctrine_version",
    "sequence", "nonce", "emitted_at",
    # DD P0 (2026-08-14, Peter FTC-1): the authority-bearing evidence is bound
    # to the signature via a digest over an explicit versioned evidence object.
    # Everything attest_conformance() / diff_drift() later treat as signed truth
    # now sits under evidence_digest — tampering any evidence field changes the
    # digest and the signature no longer verifies.
    "evidence_digest",
)
FLEET_SIGNAL_MAX_SKEW_S = 300.0  # emitted_at freshness window (+/-)

# ── FleetEvidence/v1 — the authority-bearing evidence object ──────────────
# Peter's P0#1: fleet_signal_canonical signed identity/freshness but NOT
# ceve_verdict, ceve_score, degraded, action_rate or approval_provenance — the
# exact fields attest_conformance() and diff_drift() use to decide health and
# lease renewal. An attacker could sign a FAIL/0/degraded envelope and then
# swap in PASS/100 without breaking the signature. Fix: every field that can
# influence attestation, drift or lease renewal lives in a versioned evidence
# object, and a sha256 digest of its canonical form is a SIGNED field.
FLEET_EVIDENCE_SCHEMA_VERSION = "fleet_evidence/v1"
FLEET_EVIDENCE_FIELDS = (
    "schema_version", "ceve_verdict", "ceve_score", "degraded",
    "action_rate", "approval_provenance", "karta_hash", "doctrine_version",
)


def fleet_evidence_canonical(evidence: dict) -> bytes:
    """Canonical bytes of the versioned evidence object (sorted keys, only the
    declared fields). Deterministic across languages."""
    import json as _cjson
    ev = evidence if isinstance(evidence, dict) else {}
    core = {f: ev.get(f) for f in FLEET_EVIDENCE_FIELDS}
    core["schema_version"] = FLEET_EVIDENCE_SCHEMA_VERSION
    return _cjson.dumps(core, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def fleet_evidence_digest(evidence: dict) -> str:
    """sha256 hex of the canonical evidence — the value bound into the signed
    envelope as evidence_digest."""
    import hashlib as _h
    return _h.sha256(fleet_evidence_canonical(evidence)).hexdigest()


def build_evidence(*, ceve_verdict, ceve_score, degraded, karta_hash, doctrine_version,
                   action_rate=None, approval_provenance=None) -> dict:
    """Assemble a FleetEvidence/v1 object from a member's own conformance state."""
    return {
        "schema_version": FLEET_EVIDENCE_SCHEMA_VERSION,
        "ceve_verdict": ceve_verdict,
        "ceve_score": ceve_score,
        "degraded": bool(degraded),
        "action_rate": action_rate,
        "approval_provenance": approval_provenance,
        "karta_hash": karta_hash,
        "doctrine_version": doctrine_version,
    }


def fleet_signal_canonical(envelope: dict) -> bytes:
    """Canonical byte message the signature covers: sorted-key JSON over the
    signed fields (everything except the sig field itself). Deterministic
    across languages."""
    import json as _cjson
    e = envelope if isinstance(envelope, dict) else {}
    core = {f: e.get(f) for f in FLEET_SIGNAL_SIG_FIELDS}
    return _cjson.dumps(core, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def sign_fleet_signal_hmac(envelope: dict, key: bytes) -> str:
    """REFERENCE signer (offline tests with explicit ephemeral keys only).
    Production uses Ed25519 via the injected signer in fleet_trust."""
    import hashlib as _h, hmac as _hm
    return _hm.new(key, fleet_signal_canonical(envelope), _h.sha256).hexdigest()


def _parse_iso_ts(value) -> float | None:
    """Strict ISO-8601 -> epoch seconds; None when unparseable (a rejection,
    never a silent default)."""
    from datetime import datetime, timezone
    if not isinstance(value, str) or not value:
        return None
    v = value.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(v)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()


def verify_fleet_signal(envelope: dict, member_record: dict | None, now_ts: float,
                        last_sequence: int | None, seen_nonces, verify_sig) -> dict:
    """FAIL-CLOSED envelope verification. Order matters — cheapest first, and
    NOTHING in the envelope is trusted until every check passes:
      1. schema_version is EXACTLY the const (evil/v999 -> rejected)
      2. required fields present
      3. member exists in the SIGNED fleet member registry (member_record)
      4. karta_hash + doctrine_version match the registry binding
      5. emitted_at parses AND is inside the freshness window; window_start<=window_end
      6. sequence is a monotonic advance (replay -> rejected)
      7. nonce unseen inside the window (replay -> rejected)
      8. the evidence object is STRICT: schema_version == fleet_evidence/v1,
         karta_hash + doctrine_version equal BOTH the envelope's and the
         registry's, ceve_verdict in {PASS,FAIL}, ceve_score in [0,100],
         degraded is bool, no unknown fields (DD review v3, P1)
      9. verify_sig(canonical_bytes, sig) is True (bad/absent signature -> rejected)
    verify_sig is INJECTED (Ed25519 in production via fleet_trust; HMAC compare
    only in offline tests with explicit keys). No default key exists."""
    e = envelope if isinstance(envelope, dict) else {}
    reasons: list[str] = []

    if e.get("schema_version") != FLEET_SIGNAL_SCHEMA_VERSION:
        reasons.append("bad_schema_version:" + str(e.get("schema_version")))

    for f in FLEET_SIGNAL_SIG_FIELDS + ("sig",):
        if e.get(f) is None:
            reasons.append("missing_field:" + f)
    if reasons:
        return {"valid": False, "member": e.get("member_agent_id"), "reasons": reasons}

    m = member_record if isinstance(member_record, dict) else None
    if m is None:
        reasons.append("unknown_member:" + str(e.get("member_agent_id")))
    else:
        if m.get("karta_hash") and e.get("karta_hash") != m.get("karta_hash"):
            reasons.append("karta_hash_mismatch")
        if m.get("doctrine_version") and str(e.get("doctrine_version")) != str(m.get("doctrine_version")):
            reasons.append("doctrine_version_mismatch")

    emitted = _parse_iso_ts(e.get("emitted_at"))
    if emitted is None:
        reasons.append("unparseable_emitted_at")
    elif abs(float(now_ts) - emitted) > FLEET_SIGNAL_MAX_SKEW_S:
        reasons.append("stale_or_future_emitted_at")
    ws, we = _parse_iso_ts(e.get("window_start")), _parse_iso_ts(e.get("window_end"))
    if ws is None or we is None:
        reasons.append("unparseable_window")
    elif ws > we:
        reasons.append("window_start_after_end")

    seq = e.get("sequence")
    if not isinstance(seq, int) or seq < 0:
        reasons.append("bad_sequence_type")
    elif last_sequence is not None and seq <= int(last_sequence):
        reasons.append("sequence_replay:" + str(seq) + "<=" + str(last_sequence))

    nonce = str(e.get("nonce"))
    if seen_nonces is not None and nonce in seen_nonces:
        reasons.append("nonce_replay")

    # DD P0 FTC-1: the signed evidence_digest MUST equal the digest recomputed
    # from the envelope's evidence object. A tampered evidence field (CEVE
    # flipped FAIL->PASS, score 0->100, degraded true->false) changes this
    # digest, so the mismatch is caught here even before the signature check —
    # and because evidence_digest is itself a signed field, a re-digest by an
    # attacker also breaks the signature. Belt and suspenders, both cryptographic.
    ev = e.get("evidence")
    if not isinstance(ev, dict):
        reasons.append("missing_evidence_object")
    else:
        recomputed = fleet_evidence_digest(ev)
        if str(e.get("evidence_digest")) != recomputed:
            reasons.append("evidence_digest_mismatch")
        # DD review v3 (P1): a legitimately-signed member could self-report an
        # evidence object with a foreign schema_version or a karta_hash that is
        # not the registry's, and still be attested — the digest/signature prove
        # the member sent it, not that its CONTENT is consistent. Strict evidence
        # schema + binding, fail-closed:
        if ev.get("schema_version") != FLEET_EVIDENCE_SCHEMA_VERSION:
            reasons.append("bad_evidence_schema_version:" + str(ev.get("schema_version")))
        if str(ev.get("karta_hash")) != str(e.get("karta_hash")):
            reasons.append("evidence_karta_hash_not_envelope")
        if m is not None and m.get("karta_hash") and str(ev.get("karta_hash")) != str(m.get("karta_hash")):
            reasons.append("evidence_karta_hash_not_registry")
        if str(ev.get("doctrine_version")) != str(e.get("doctrine_version")):
            reasons.append("evidence_doctrine_not_envelope")
        if m is not None and m.get("doctrine_version") and str(ev.get("doctrine_version")) != str(m.get("doctrine_version")):
            reasons.append("evidence_doctrine_not_registry")
        if ev.get("ceve_verdict") not in ("PASS", "FAIL"):
            reasons.append("bad_evidence_ceve_verdict:" + str(ev.get("ceve_verdict")))
        sc = ev.get("ceve_score")
        if isinstance(sc, bool) or not isinstance(sc, (int, float)) or not (0 <= float(sc) <= 100):
            reasons.append("bad_evidence_ceve_score:" + str(sc))
        if not isinstance(ev.get("degraded"), bool):
            reasons.append("bad_evidence_degraded_type")
        for extra in set(ev.keys()) - set(FLEET_EVIDENCE_FIELDS):
            reasons.append("unknown_evidence_field:" + str(extra))

    if not callable(verify_sig):
        reasons.append("no_signature_verifier")
    elif not reasons:
        try:
            ok = bool(verify_sig(fleet_signal_canonical(e), str(e.get("sig"))))
        except Exception:
            ok = False
        if not ok:
            reasons.append("bad_signature")

    return {"valid": len(reasons) == 0, "member": e.get("member_agent_id"),
            "sequence": seq if isinstance(seq, int) else None, "nonce": nonce,
            "reasons": reasons}


# ── attestation ──────────────────────────────────────────────────────────

# A member is attested only if it is provably conformant. Deterministic gate;
# every rejection carries a machine-readable reason (never a silent degrade).
CEVE_PASS_FLOOR = 90


def attest_conformance(snapshot: dict, doctrine_version: str, signal_verification: dict | None = None) -> dict:
    """Confirm a member is CEVE-PASS + carries a genuine root-chained identity,
    against a NAMED doctrine version. Returns an attestation record; state is one
    of green / degraded / rejected, with reasons.

    SECURITY (DD P0, 2026-08-13): attestation REFUSES an unverified envelope.
    signal_verification is the result of verify_fleet_signal() — membership,
    signature, evidence binding, freshness and replay all checked BEFORE any
    CEVE field is trusted. Absent or invalid verification => rejected. The
    fields in the snapshot prove nothing by themselves; only a signal that
    survived cryptographic verification may attest a member."""
    s = snapshot if isinstance(snapshot, dict) else {}
    reasons: list[str] = []

    sv = signal_verification if isinstance(signal_verification, dict) else None
    if sv is None:
        reasons.append("signal_not_verified:missing_verification")
    elif sv.get("valid") is not True:
        for r in (sv.get("reasons") or ["invalid"]):
            reasons.append("signal_not_verified:" + str(r))

    hexa_id = s.get("hexa_id")
    if not hexa_id:
        reasons.append("missing_hexa_id")

    # DD P0 FTC-1: the authority-bearing evidence is read ONLY from the signed,
    # digest-bound evidence object — never from unsigned top-level fields (that
    # was the hole: an attacker set top-level ceve_verdict=PASS after signing).
    # A verified signal guarantees evidence_digest == digest(evidence), so these
    # fields are exactly what the producer signed.
    ev = s.get("evidence") if isinstance(s.get("evidence"), dict) else None
    if ev is None:
        reasons.append("missing_signed_evidence")

    verdict = str((ev or {}).get("ceve_verdict", "")).upper()
    if verdict != "PASS":
        reasons.append("ceve_verdict_not_pass:" + (verdict or "absent"))

    score = (ev or {}).get("ceve_score")
    if not isinstance(score, (int, float)):
        reasons.append("ceve_score_absent")
    elif score < CEVE_PASS_FLOOR:
        reasons.append("ceve_score_below_floor:" + str(score) + "<" + str(CEVE_PASS_FLOOR))

    member_dv = str((ev or {}).get("doctrine_version", ""))
    if doctrine_version and member_dv and member_dv != str(doctrine_version):
        reasons.append("doctrine_version_mismatch:" + member_dv + "!=" + str(doctrine_version))

    degraded = bool((ev or {}).get("degraded", False))
    if degraded:
        reasons.append("member_degraded")

    attested = len(reasons) == 0
    state = "green" if attested else ("degraded" if degraded and verdict == "PASS" else "rejected")
    return {
        "member": hexa_id,
        "attested": attested,
        "state": state,
        "attested_against": str(doctrine_version) if doctrine_version else None,
        "karta_hash": s.get("karta_hash"),
        "ceve_score": score if isinstance(score, (int, float)) else None,
        "reasons": reasons,
    }


# ── drift from signed evidence ───────────────────────────────────────────

# Drift is a COMPARISON of signed snapshots over time, never a heuristic guess.
# margins are conservative platform defaults; the domain may tighten them.
CEVE_REGRESSION_MARGIN = 5           # points the score may fall before it is drift
ACTION_RATE_ANOMALY_FACTOR = 3.0     # x the member's own baseline rate


def diff_drift(current: dict, baseline: dict, now_ts: float, lease_ttl_s: float) -> dict:
    """Compare a member's CURRENT signed snapshot against its ATTESTED baseline.
    Pure diff — every flag names the signed field that moved. The 'silence' flag
    fires when no fresh attestation arrived within the lease TTL (a compromised
    member that goes dark auto-surfaces here)."""
    cur = current if isinstance(current, dict) else {}
    base = baseline if isinstance(baseline, dict) else {}
    flags: list[str] = []

    # DD P0 FTC-1: read the authority-bearing values from the signed evidence
    # object, not unsigned top-level fields. Both snapshots carry evidence (the
    # coordinator stores the verified evidence on the attested baseline).
    cur_ev = cur.get("evidence") if isinstance(cur.get("evidence"), dict) else {}
    base_ev = base.get("evidence") if isinstance(base.get("evidence"), dict) else {}

    if base_ev.get("karta_hash") is not None and cur_ev.get("karta_hash") != base_ev.get("karta_hash"):
        flags.append("karta_hash_mismatch")

    cs, bs = cur_ev.get("ceve_score"), base_ev.get("ceve_score")
    if isinstance(cs, (int, float)) and isinstance(bs, (int, float)) and cs < bs - CEVE_REGRESSION_MARGIN:
        flags.append("ceve_regression")
    if str(cur_ev.get("ceve_verdict", "")).upper() not in ("", "PASS"):
        flags.append("ceve_verdict_degraded")

    cr, br = cur_ev.get("action_rate"), base_ev.get("action_rate")
    if isinstance(cr, (int, float)) and isinstance(br, (int, float)) and br >= 0 and cr > max(br, 0.0) * ACTION_RATE_ANOMALY_FACTOR:
        flags.append("action_rate_anomaly")

    last = cur.get("last_attested_at")
    if isinstance(last, (int, float)) and isinstance(now_ts, (int, float)) and isinstance(lease_ttl_s, (int, float)):
        if now_ts - last > lease_ttl_s:
            flags.append("silence")

    # None / absent = not reported = ok (only an explicit failing value drifts).
    if str(cur_ev.get("approval_provenance") or "ok").lower() not in ("ok", "healthy"):
        flags.append("approval_provenance_failing")

    severity = "none"
    if flags:
        hard = {"karta_hash_mismatch", "approval_provenance_failing", "silence"}
        severity = "high" if any(f in hard for f in flags) else "elevated"
    return {
        "member": cur.get("hexa_id") or base.get("hexa_id"),
        "drifted": len(flags) > 0,
        "flags": flags,
        "severity": severity,
    }


# ── k-anonymous cohort aggregation ───────────────────────────────────────

def _distinct_tenants(members: list) -> set:
    """k counts DISTINCT tenants, never raw rows — a single tenant emitting N
    signals must not synthesise a fake cohort (cross-tenant-leakage lesson).
    WS-1 (reviewer #4): tenant_id is a REAL tenant identifier bound in the
    signed registry — never the agent id. A row without a bound tenant does not
    count toward k (it is NOT silently counted as its own tenant: eight agents
    of one operator are one tenant, not eight)."""
    out = set()
    for m in members:
        if isinstance(m, dict):
            t = m.get("tenant_id") or m.get("tenant")
            if t not in (None, ""):
                out.add(str(t))
    return out


class CohortBuffer:
    """WS-1 (reviewer #4) — the coordinator's trusted cohort as a TIME-WINDOWED
    buffer instead of an append-only list:
      * per-member REPLACEMENT: one member holds exactly one current row, so a
        chatty member cannot contribute unboundedly (or dominate the rollups);
      * TTL EVICTION: a row older than the window is dropped by sweep(now) —
        a member that reported once ages out of k;
      * SILENCE on the clock: silent_members(now) names every member whose last
        row is older than the window — evaluated from `now`, not only when a
        fresh snapshot happens to arrive.
    All time comes from the caller (testable, no hidden clock)."""

    def __init__(self, ttl_s: float) -> None:
        self.ttl_s = float(ttl_s)
        self._rows: dict = {}   # member_id -> {"row": dict, "seen_at": float}

    def upsert(self, member_id: str, row: dict, now_ts: float) -> None:
        self._rows[str(member_id)] = {"row": dict(row or {}), "seen_at": float(now_ts)}

    def sweep(self, now_ts: float) -> list:
        """Evict rows older than the window; return the evicted member ids."""
        cutoff = float(now_ts) - self.ttl_s
        gone = [m for m, r in self._rows.items() if float(r.get("seen_at", 0.0)) < cutoff]
        for m in gone:
            del self._rows[m]
        return gone

    def silent_members(self, now_ts: float) -> list:
        cutoff = float(now_ts) - self.ttl_s
        return sorted(m for m, r in self._rows.items() if float(r.get("seen_at", 0.0)) < cutoff)

    def rows(self, now_ts: "float | None" = None) -> list:
        """Current rows; with now_ts, only rows still inside the window."""
        if now_ts is None:
            return [r["row"] for r in self._rows.values()]
        cutoff = float(now_ts) - self.ttl_s
        return [r["row"] for r in self._rows.values() if float(r.get("seen_at", 0.0)) >= cutoff]

    def __len__(self) -> int:
        return len(self._rows)


def sweep_silence(baselines: dict, now_ts: float, ttl_s: float) -> list:
    """Clock-driven silence evaluation over the attested baselines: every member
    whose last_attested_at is older than ttl_s — WITHOUT waiting for a snapshot
    from that member (a silent member never sends the snapshot that would have
    flagged it). Returns sorted member ids."""
    cutoff = float(now_ts) - float(ttl_s)
    out = []
    for m, b in (baselines or {}).items():
        try:
            last = float((b or {}).get("last_attested_at") or 0.0)
        except (TypeError, ValueError):
            last = 0.0
        if last < cutoff:
            out.append(str(m))
    return sorted(out)


def kanon_aggregate(members: list, k_minimum: int) -> dict:
    """k-anonymised cohort aggregation. Below the k-floor (measured over DISTINCT
    tenants) the aggregate is SUPPRESSED — the raw members never survive and no
    sub-k pattern is emitted. Above it, only coarse cohort-level rollups + numeric
    summaries cross the boundary. The exact per-domain statistic is a documented
    SEAM (Top-N IOCs vs treatment outcomes vs market signals); the k-floor
    mechanism is fixed."""
    ms = [m for m in (members or []) if isinstance(m, dict)]
    tenants = _distinct_tenants(ms)
    k_count = len(tenants)
    if k_count < int(k_minimum):
        return {"k_satisfied": False, "k_count": k_count, "k_minimum": int(k_minimum), "aggregate": None}

    rollup: dict = {}
    for m in ms:
        for dim in ("vertical", "event_type", "tier"):
            v = m.get(dim)
            if v is None:
                continue
            rollup.setdefault(dim, {})
            rollup[dim][str(v)] = rollup[dim].get(str(v), 0) + 1
    scores = [m.get("ceve_score") for m in ms if isinstance(m.get("ceve_score"), (int, float))]
    numeric = {}
    if scores:
        numeric["ceve_score"] = {"mean": round(sum(scores) / len(scores), 4), "min": min(scores), "max": max(scores)}
    return {
        "k_satisfied": True,
        "k_count": k_count,
        "k_minimum": int(k_minimum),
        "aggregate": {"cohort_size": k_count, "rollup": rollup, "numeric": numeric},
    }


# ── learned fleet baselines (HexaLearn Z-loop, v1 statistical) ────────────

def _percentile(sorted_vals: list, q: float) -> float:
    if not sorted_vals:
        return 0.0
    if len(sorted_vals) == 1:
        return float(sorted_vals[0])
    idx = q * (len(sorted_vals) - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return float(sorted_vals[lo])
    frac = idx - lo
    return float(sorted_vals[lo]) * (1 - frac) + float(sorted_vals[hi]) * frac


def learn_baseline(history: list, metrics: tuple = ("ceve_score", "action_rate")) -> dict:
    """Learn the fleet's NORMAL baselines from signed history — mean/stddev/min/
    max/p50/p95 per metric — so drift-detection measures 'abnormal' against a
    LEARNED, evidence-bound baseline rather than a hard-coded threshold (much
    harder to dispute under scrutiny). Deterministic statistics; binding an SLM/RL
    model to refine the baseline is the documented seam, not the mechanism."""
    hist = [h for h in (history or []) if isinstance(h, dict)]
    out: dict = {"n": len(hist), "metrics": {}}
    for metric in metrics:
        vals = [h.get(metric) for h in hist if isinstance(h.get(metric), (int, float))]
        if not vals:
            continue
        n = len(vals)
        mean = sum(vals) / n
        var = sum((v - mean) ** 2 for v in vals) / n
        sv = sorted(vals)
        out["metrics"][metric] = {
            "n": n,
            "mean": round(mean, 4),
            "stddev": round(math.sqrt(var), 4),
            "min": min(vals),
            "max": max(vals),
            "p50": round(_percentile(sv, 0.50), 4),
            "p95": round(_percentile(sv, 0.95), 4),
        }
    return out


# ── capability-lease (trust is a LEASE, not a grant) ─────────────────────

# Every member capability is a SHORT-LIVED signed lease it must actively renew
# by presenting a fresh clean attestation. Drift OR silence => not renewed =>
# the member's runtime fail-closes its own privileged actions. "Kill" = stop
# renewing (dead-man's switch, by construction). Built on the same primitives
# the CCAS approvals use: signed, expires_at-bound, fail-closed verification
# (clock-manipulation + sovereignty lessons from Fas 3.13 / 3.7).
import hashlib as _hashlib
import hmac as _hmac
import json as _json

# Posture-scaled TTLs (seconds). Lockdown = very short leases (fast fail-closed).
LEASE_TTL_BY_POSTURE = {"normal": 3600, "heightened": 900, "lockdown": 120}

# DD P0 FTC-2 (Peter): the lease is a COORDINATOR-signed capability grant. It is
# bound to the subject (fleet_id + member_agent_id), the exact capability scope,
# the validity window, the posture, and a unique jti+epoch. The coordinator signs
# with an ASYMMETRIC private key; members hold ONLY the public verification key,
# so a member that can verify a lease cannot mint one (the symmetric-HMAC hole).
_LEASE_SIG_FIELDS = (
    "schema_version", "fleet_id", "member_hexa_id", "capability_scope",
    "issued_at", "expires_at", "fleet_posture", "epoch", "jti",
)
LEASE_SCHEMA_VERSION = "fleet_lease/v1"


def lease_canonical(token: dict) -> bytes:
    """Canonical signed bytes of a lease (sorted-key JSON over the signed fields,
    excluding sig/alg). Deterministic across languages."""
    t = token if isinstance(token, dict) else {}
    core = {f: t.get(f) for f in _LEASE_SIG_FIELDS}
    return _json.dumps(core, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def mint_lease(*, fleet_id: str, member_hexa_id: str, capability_scope: list, now_ts: float,
               fleet_posture: str, epoch, sign: "Callable[[bytes], str]", jti: str | None = None) -> dict:
    """Mint a short-lived coordinator-signed capability lease. 'sign' is the
    coordinator's ASYMMETRIC signer (message bytes -> hex signature); the member
    never holds it. TTL is posture-scaled and NEVER unbounded. An EMPTY scope
    authorises nothing (a lease must name the capabilities it grants)."""
    import uuid as _uuid
    ttl = LEASE_TTL_BY_POSTURE.get(str(fleet_posture), LEASE_TTL_BY_POSTURE["normal"])
    token = {
        "schema_version": LEASE_SCHEMA_VERSION,
        "fleet_id": str(fleet_id),
        "member_hexa_id": str(member_hexa_id),
        "capability_scope": sorted(str(s) for s in (capability_scope or [])),
        "issued_at": float(now_ts),
        "expires_at": float(now_ts) + float(ttl),
        "fleet_posture": str(fleet_posture),
        "epoch": epoch,
        "jti": str(jti) if jti else _uuid.uuid4().hex,
    }
    token["alg"] = "ed25519"
    token["sig"] = sign(lease_canonical(token))
    return token


def verify_lease(token: dict, now_ts: float, *, verify: "Callable[[bytes, str], bool]",
                 expected_member: str, required_capability: str,
                 expected_fleet_id: str | None = None, expected_epoch=None) -> dict:
    """FAIL-CLOSED lease verification. Every one of these alone invalidates:
      * missing field / bad coordinator signature (verified with the PUBLIC key)
      * expired / clock-implausible issued_at
      * SUBJECT mismatch: member_hexa_id != this runtime's signed identity
      * SCOPE: required_capability not in capability_scope (empty scope => deny)
      * fleet_id / epoch mismatch (a lease minted for another fleet or a revoked
        epoch is refused)
    A member runtime calls this before every privileged action, passing its OWN
    signed identity as expected_member and the action's capability as required."""
    t = token if isinstance(token, dict) else {}
    reasons: list[str] = []
    for f in _LEASE_SIG_FIELDS + ("sig",):
        if t.get(f) is None:
            reasons.append("missing_field:" + f)
    if t.get("schema_version") not in (None, LEASE_SCHEMA_VERSION):
        reasons.append("bad_lease_schema:" + str(t.get("schema_version")))
    if not reasons:
        if not callable(verify):
            reasons.append("no_lease_verifier")
        else:
            try:
                ok = bool(verify(lease_canonical(t), str(t.get("sig"))))
            except Exception:
                ok = False
            if not ok:
                reasons.append("bad_signature")
        if float(t["expires_at"]) <= float(now_ts):
            reasons.append("expired")
        # Fas 3.13 clock-manipulation: an issued_at in the future is implausible.
        if float(t["issued_at"]) > float(now_ts) + 60:
            reasons.append("issued_in_future")
        # FTC-2 subject binding: the lease must be FOR this runtime's identity.
        if str(t.get("member_hexa_id")) != str(expected_member):
            reasons.append("subject_mismatch:" + str(t.get("member_hexa_id")) + "!=" + str(expected_member))
        # FTC-2 scope binding: the action's capability must be granted; an empty
        # scope grants nothing.
        scope = t.get("capability_scope") or []
        if str(required_capability) not in [str(s) for s in scope]:
            reasons.append("capability_not_in_scope:" + str(required_capability))
        if expected_fleet_id is not None and str(t.get("fleet_id")) != str(expected_fleet_id):
            reasons.append("fleet_id_mismatch")
        if expected_epoch is not None and t.get("epoch") != expected_epoch:
            reasons.append("epoch_mismatch")
    return {"valid": len(reasons) == 0, "reasons": reasons,
            "member": t.get("member_hexa_id"), "scope": t.get("capability_scope")}


def renew_decision(attestation: dict, drift: dict) -> dict:
    """The renewal gate: renew ONLY on a clean, current attestation with no
    drift. Anything else => withhold, with the evidence chained in. Withholding
    IS the default kill: the old lease simply expires and the member fail-closes.
    Deterministic — no discretion, no silent renewal."""
    att = attestation if isinstance(attestation, dict) else {}
    dr = drift if isinstance(drift, dict) else {}
    reasons: list[str] = []
    if att.get("attested") is not True:
        reasons.append("not_attested")
        for r in (att.get("reasons") or []):
            reasons.append("attest:" + str(r))
    if dr.get("drifted") is True:
        reasons.append("drifted")
        for f in (dr.get("flags") or []):
            reasons.append("drift:" + str(f))
    renew = len(reasons) == 0
    return {"renew": renew, "action": "renew" if renew else "withhold", "reasons": reasons,
            "member": att.get("member") or dr.get("member")}
