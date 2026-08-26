"""fleet_trust — runtime trust plane for AUTHENTICATED fleet orchestration.

DD P0 (2026-08-13): a coordinator trusts NOTHING a member sends until
membership, signature, evidence binding, freshness and replay protection have
ALL been verified; a member holds a valid capability lease before any
privileged action. Both sides wired here:

  PRODUCER (member):    stamp_and_sign(envelope) — stamps identity + freshness
      + anti-replay fields and signs with the provisioned Ed25519 member key
      (FLEET_MEMBER_KEY). Without a key the envelope is explicitly UNSIGNED —
      a coordinator rejects it (the trust decision fail-closes at the consumer).
  CONSUMER (hub):       verify_envelope(envelope) — loads the SIGNED fleet
      member registry (FLEET_MEMBER_REGISTRY), verifies via
      fleet_core.verify_fleet_signal, advances replay state only on success.
  MEMBER GUARD:         require_fleet_lease(capability) — verifies the current
      coordinator-signed capability lease (FLEET_LEASE_PATH) with the
      coordinator's PUBLIC key (from the signed registry). MANDATORY for a
      fleet-managed member (fleet_managed(), from identity.json — not an env
      flag): the lease must be for THIS member (subject) and grant the action's
      capability (scope). Called on every privileged action by ccas_decide.

NO DEFAULT KEYS: absent registry, unknown member, absent key and absent lease
are all rejections — never fallbacks. Key formats are EXPLICIT:
  FLEET_MEMBER_KEY         = "ed25519:<64-hex seed>" | "hmac:<hex>"  (member signal key; hmac = offline reference)
  FLEET_LEASE_SIGNING_KEY  = "ed25519:<64-hex seed>"  (coordinator-PRIVATE lease key — hub only)
  registry                 = {"fleet_id", "lease_pubkey_hex", "lease_epoch",
                              "members": {id: {"karta_hash", "doctrine_version",
                                               "pubkey_hex", "capability_scope"}}}
"""
from __future__ import annotations

import hashlib
import hmac as _hmac
import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional, Tuple

from src.shared.fleet_core import (
    fleet_signal_canonical,
    verify_fleet_signal,
    verify_lease,
)
from src.shared.ed25519_verify import _B, _H, _L, _inv, _p, _scalarmult, ed25519_verify


# ── Ed25519 signing (pure python, SAME curve arithmetic as the shipped
#    verifier — one implementation family, not two) ───────────────────────

def _encodeint(y: int) -> bytes:
    return y.to_bytes(32, "little")


def _encodepoint(P) -> bytes:
    (x, y, z, t) = P
    zi = _inv(z)
    x = (x * zi) % _p
    y = (y * zi) % _p
    bits = bytearray(_encodeint(y))
    if x & 1:
        bits[31] |= 0x80
    return bytes(bits)


def _clamped_scalar(h: bytes) -> int:
    return 2 ** 254 + sum(2 ** i * ((h[i // 8] >> (i % 8)) & 1) for i in range(3, 254))


def ed25519_sign(seed: bytes, message: bytes) -> bytes:
    """RFC 8032 Ed25519 signature from a 32-byte seed."""
    if len(seed) != 32:
        raise ValueError("ed25519 seed must be exactly 32 bytes")
    h = _H(seed)
    a = _clamped_scalar(h)
    prefix = h[32:]
    A = _encodepoint(_scalarmult(_B, a))
    r = int.from_bytes(_H(prefix + message), "little") % _L
    R = _encodepoint(_scalarmult(_B, r))
    k = int.from_bytes(_H(R + A + message), "little") % _L
    S = (r + k * a) % _L
    return R + _encodeint(S)


def ed25519_public_key(seed: bytes) -> bytes:
    return _encodepoint(_scalarmult(_B, _clamped_scalar(_H(seed))))


# ── member identity (from the signed bundle on disk) ─────────────────────

def _bundle_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _identity() -> dict:
    try:
        return json.loads((_bundle_root() / "identity.json").read_text())
    except (OSError, ValueError):
        return {}


def _karta_hash() -> str:
    try:
        return hashlib.sha256((_bundle_root() / "karta.compiled.json").read_bytes()).hexdigest()
    except OSError:
        return ""


def _doctrine_version() -> str:
    ident = _identity()
    for key in ("rules_version", "doctrine_version"):
        if ident.get(key):
            return str(ident.get(key))
    return str(os.environ.get("FLEET_DOCTRINE_VERSION", ""))


def _member_key() -> Optional[Tuple[str, bytes]]:
    """(mode, key_bytes) from FLEET_MEMBER_KEY, or None. NO default."""
    raw = str(os.environ.get("FLEET_MEMBER_KEY", ""))
    for mode in ("ed25519", "hmac"):
        if raw.startswith(mode + ":"):
            try:
                return (mode, bytes.fromhex(raw.split(":", 1)[1]))
            except ValueError:
                return None
    return None


_SEQ_STATE: dict = {"sequence": 0}


class FleetStateError(RuntimeError):
    """B2 (WS-1): durable fleet state (producer sequence / consumer replay
    high-water) is REQUIRED for a fleet-managed runtime, and a failure to read
    or persist it is a hard, named error — never an in-memory fallback that
    silently restarts the sequence at 1 or reopens the replay window."""


def _next_sequence() -> int:
    """Monotonic producer sequence. B2 (WS-1) FAIL-CLOSED:
      * fleet-managed + no FLEET_SEQ_PATH  -> FleetStateError (the signal is
        refused upstream: an in-memory counter would restart at 1 after every
        restart and the coordinator would rightly refuse the member forever —
        or worse, accept a replayed window);
      * state file exists but is corrupt    -> FleetStateError (never "0");
      * persistence write fails             -> FleetStateError (the number is
        NOT handed out: a sequence that was never durably recorded must not be
        signed).
    A genuine standalone (non-fleet) runtime without a path keeps the in-memory
    counter (dev/reference posture)."""
    path = str(os.environ.get("FLEET_SEQ_PATH", ""))
    if not path:
        if fleet_managed():
            raise FleetStateError("sequence_state_not_durable: FLEET_SEQ_PATH is required for a fleet-managed member")
        _SEQ_STATE["sequence"] = int(_SEQ_STATE["sequence"]) + 1
        return _SEQ_STATE["sequence"]
    pth = Path(path)
    if pth.exists():
        try:
            raw = pth.read_text().strip()
            current = int(raw) if raw else 0
        except (OSError, ValueError) as exc:
            raise FleetStateError("sequence_state_corrupt: %s" % type(exc).__name__)
    else:
        current = 0  # first boot: nothing recorded yet
    nxt = max(current, int(_SEQ_STATE["sequence"])) + 1
    try:
        pth.parent.mkdir(parents=True, exist_ok=True)
        tmp = pth.with_suffix(pth.suffix + ".tmp")
        tmp.write_text(str(nxt))
        os.replace(str(tmp), str(pth))  # atomic within a filesystem
    except OSError as exc:
        raise FleetStateError("sequence_state_write_failed: %s" % type(exc).__name__)
    _SEQ_STATE["sequence"] = nxt
    return nxt


def _local_conformance() -> dict:
    """The member's OWN shipped conformance verdict (reports/ceve_validation.json)
    — the same signed-at-composition score the Driver View reads. The honest
    source of ceve_verdict/ceve_score for this member's evidence; absent/unreadable
    yields a fail-closed FAIL/0 (a member that cannot prove conformance is not
    conformant), never a fabricated PASS."""
    try:
        data = json.loads((_bundle_root() / "reports" / "ceve_validation.json").read_text())
    except (OSError, ValueError):
        return {"verdict": "FAIL", "score": 0}
    return data if isinstance(data, dict) else {"verdict": "FAIL", "score": 0}


def _local_evidence(karta_hash: str, doctrine_version: str, overrides: Optional[dict] = None) -> dict:
    """FleetEvidence/v1 for this member. Authority-bearing CEVE fields come from
    the shipped conformance report; degraded/action_rate/approval_provenance may
    be supplied by the caller (live runtime signals) and default to a
    conservative posture."""
    from src.shared.fleet_core import build_evidence
    conf = _local_conformance()
    ov = overrides if isinstance(overrides, dict) else {}
    return build_evidence(
        ceve_verdict=str(conf.get("verdict") or "FAIL").upper(),
        ceve_score=conf.get("score") if isinstance(conf.get("score"), (int, float)) else 0,
        degraded=bool(ov.get("degraded", False)),
        karta_hash=karta_hash,
        doctrine_version=doctrine_version,
        action_rate=ov.get("action_rate"),
        approval_provenance=ov.get("approval_provenance", "ok"),
    )


def stamp_and_sign(envelope: dict) -> dict:
    """Stamp member identity + freshness + anti-replay fields, attach the SIGNED
    FleetEvidence/v1 object + its digest, and SIGN the canonical envelope.
    Without a provisioned FLEET_MEMBER_KEY the envelope is explicitly UNSIGNED
    (sig="unsigned", fleet_auth.signed=False): shape-valid so the producer
    pipeline keeps running honestly, but a coordinator REJECTS it — the trust
    decision always fail-closes at the consumer boundary."""
    from src.shared.fleet_core import fleet_evidence_digest
    env = dict(envelope if isinstance(envelope, dict) else {})
    ident = _identity()
    env["member_agent_id"] = str(ident.get("agent_id") or os.environ.get("FLEET_MEMBER_ID") or "unprovisioned")
    kh = _karta_hash() or "unprovisioned"
    dv = _doctrine_version() or "unprovisioned"
    env["karta_hash"] = kh
    env["doctrine_version"] = dv
    # DD P0 FTC-1: bind the authority-bearing evidence. A caller may pass a raw
    # 'evidence' dict (live runtime posture); otherwise it is built from the
    # member's own shipped conformance. The digest is a SIGNED field.
    ev_override = env.get("evidence") if isinstance(env.get("evidence"), dict) else None
    env["evidence"] = ev_override or _local_evidence(kh, dv)
    env["evidence_digest"] = fleet_evidence_digest(env["evidence"])
    env["nonce"] = uuid.uuid4().hex
    env["emitted_at"] = datetime.now(timezone.utc).isoformat()
    try:
        env["sequence"] = _next_sequence()
    except FleetStateError as exc:
        # B2: no durable sequence -> the signal is explicitly UNSIGNED with the
        # named reason. It never leaves (fleet_transport refuses an unsigned
        # release) and it never restarts a fresh in-memory count at 1.
        env["sequence"] = None
        env["sig"] = "unsigned"
        env["fleet_auth"] = {"signed": False, "reason": str(exc)}
        return env
    key = _member_key()
    if key is None:
        env["sig"] = "unsigned"
        env["fleet_auth"] = {"signed": False, "reason": "FLEET_MEMBER_KEY not provisioned"}
        return env
    mode, kb = key
    msg = fleet_signal_canonical(env)
    if mode == "ed25519":
        env["sig"] = ed25519_sign(kb, msg).hex()
    else:
        env["sig"] = _hmac.new(kb, msg, hashlib.sha256).hexdigest()
    env["fleet_auth"] = {"signed": True, "alg": mode}
    return env


# ── consumer side (coordinator) ──────────────────────────────────────────

def load_registry() -> Optional[dict]:
    """The SIGNED fleet member registry (fleet manifest projection). Absent or
    unreadable -> None, and every verification rejects with no_member_registry.

    DD P0 FTC-7 (Peter): the runtime registry is BOUND to the signed fleet
    manifest trust anchor. When FLEET_MANIFEST_PATH is provided, the sha256 of
    the registry file on disk MUST equal the registry_sha256 recorded in the
    manifest's SIGNED body (bound at build time by fleet_manifest.build_manifest).
    A registry that does not match the signed anchor is refused (returns None ->
    no_member_registry) — the registry is no longer freely editable at runtime."""
    path = str(os.environ.get("FLEET_MEMBER_REGISTRY", ""))
    if not path:
        return None
    try:
        raw = Path(path).read_bytes()
        data = json.loads(raw)
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    manifest_path = str(os.environ.get("FLEET_MANIFEST_PATH", ""))
    # WS-1 (reviewer #2): in a FLEET-MANAGED posture the manifest anchor AND
    # its external pin are MANDATORY — no pin = no registry, not opt-in. A
    # registry loaded without both would be freely editable at runtime (add a
    # member, raise a scope) with nothing to refuse it. Standalone (non-fleet)
    # runtimes may still load a plain registry (reference/dev posture).
    if fleet_managed() and (not manifest_path or not str(os.environ.get("FLEET_MANIFEST_PUBKEY", "")).strip()):
        return None
    if manifest_path:
        try:
            manifest = json.loads(Path(manifest_path).read_text())
        except (OSError, ValueError):
            return None  # a manifest was declared but is unreadable -> fail-closed
        # DD P0 (Peter): verify the manifest's OWN Ed25519 signature against an
        # EXTERNALLY-PINNED public key before trusting anything it binds. Without
        # this, a registry + manifest could be replaced together (the manifest
        # self-certifies). The pinned key is supplied out-of-band as
        # FLEET_MANIFEST_PUBKEY (hex); when set, an absent/invalid signature is a
        # fail-closed rejection. (Absent pin = demo/degraded posture, disclosed.)
        pinned = str(os.environ.get("FLEET_MANIFEST_PUBKEY", ""))
        if pinned:
            sigblock = manifest.get("signature") if isinstance(manifest.get("signature"), dict) else {}
            sig_hex = sigblock.get("sig")
            body = {k: v for k, v in manifest.items() if k != "signature"}
            canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
            try:
                ok = bool(sig_hex) and ed25519_verify(bytes.fromhex(pinned), bytes.fromhex(str(sig_hex)), canonical)
            except (ValueError, TypeError):
                ok = False
            if not ok:
                return None  # manifest signature does not verify against the pinned key
        anchor = ((manifest.get("body") or {}).get("registry_sha256")
                  if isinstance(manifest.get("body"), dict) else None) or manifest.get("registry_sha256")
        # DD P0 (external review 2026-08-15): the manifest builder binds the
        # sha256 of the CANONICAL registry projection (sorted keys, compact
        # separators, default=str) — but this runtime hashed the registry file's
        # RAW BYTES. A registry written with any other formatting (the delivered
        # one was indent=2) therefore never matched: with the delivered manifest,
        # the delivered registry and a correctly pinned key, load_registry()
        # returned None and every signal was refused as no_member_registry — the
        # "secure configuration" did not work with the delivered files. Hash the
        # SAME canonical form as the builder and verifier, so builder == verifier
        # == runtime by construction, independent of file formatting.
        canonical_registry = json.dumps(data, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
        if not anchor or hashlib.sha256(canonical_registry).hexdigest() != str(anchor):
            return None  # registry does not match the signed manifest anchor
    return data


def coordinator_lease_signer() -> Optional[Callable[[bytes], str]]:
    """The coordinator's PRIVATE lease signer (Ed25519), from
    FLEET_LEASE_SIGNING_KEY = "ed25519:<64-hex seed>". Returns a
    message-bytes -> hex-signature closure, or None when unprovisioned. This key
    lives ONLY on the coordinator; members never hold it (Peter FTC-2)."""
    raw = str(os.environ.get("FLEET_LEASE_SIGNING_KEY", ""))
    if not raw.startswith("ed25519:"):
        return None
    try:
        seed = bytes.fromhex(raw.split(":", 1)[1])
    except ValueError:
        return None
    if len(seed) != 32:
        return None

    def _sign(msg: bytes) -> str:
        return ed25519_sign(seed, msg).hex()
    return _sign


def member_capability_scope(member_id: str) -> list:
    """The privileged capabilities the SIGNED registry declares for a member —
    the exact scope the coordinator mints a lease for. Unknown member / no
    declared scope -> [] (an empty scope authorises nothing, FTC-2)."""
    reg = load_registry() or {}
    members = reg.get("members") if isinstance(reg.get("members"), dict) else {}
    m = members.get(str(member_id))
    scope = m.get("capability_scope") if isinstance(m, dict) else None
    return [str(s) for s in scope] if isinstance(scope, list) else []


def _member_verify_fn(member: dict) -> Optional[Callable[[bytes, str], bool]]:
    pub = member.get("pubkey_hex")
    if isinstance(pub, str) and pub:
        def _v(msg: bytes, sig_hex: str) -> bool:
            try:
                return ed25519_verify(bytes.fromhex(pub), bytes.fromhex(str(sig_hex)), msg)
            except (ValueError, TypeError):
                return False
        return _v
    hk = member.get("hmac_key_hex")
    if isinstance(hk, str) and hk:
        def _h(msg: bytes, sig_hex: str) -> bool:
            expected = _hmac.new(bytes.fromhex(hk), msg, hashlib.sha256).hexdigest()
            return _hmac.compare_digest(str(sig_hex), expected)
        return _h
    return None


class ReplayState:
    """Per-member replay protection: highest accepted sequence + nonces seen
    inside twice the freshness window (older nonces cannot verify anyway).

    DD P0 FTC-5 (Peter): the high-water marks are DURABLE. In-memory-only state
    reset the sequence floor on every coordinator restart, reopening a replay
    window for the length of the freshness window (5 min). When a path is given
    (FLEET_REPLAY_PATH, wired by default under the state dir), the state is
    loaded on construction and every advance is persisted atomically (temp +
    os.replace), so a restarted coordinator still rejects a already-accepted
    envelope."""

    def __init__(self, path: "Optional[str]" = None) -> None:
        self.last_sequence: dict = {}
        self.nonces: dict = {}
        self._path = str(path) if path else str(os.environ.get("FLEET_REPLAY_PATH", ""))
        self._load()

    @property
    def durable(self) -> bool:
        return bool(self._path)

    def _load(self) -> None:
        """B2 (WS-1): a state file that EXISTS but cannot be read or parsed, or
        has the wrong shape, is a HARD error (FleetStateError) — never an empty
        state that would reopen the replay window. A missing file is a first
        boot (nothing accepted yet)."""
        if not self._path:
            return
        p = Path(self._path)
        if not p.exists():
            return
        try:
            data = json.loads(p.read_text())
        except (OSError, ValueError) as exc:
            raise FleetStateError("replay_state_corrupt: %s" % type(exc).__name__)
        if not isinstance(data, dict) or not isinstance(data.get("last_sequence"), dict) \
                or not isinstance(data.get("nonces"), dict):
            raise FleetStateError("replay_state_corrupt: wrong shape")
        try:
            self.last_sequence = {str(k): int(v) for k, v in data["last_sequence"].items()}
            self.nonces = {str(k): dict(v) for k, v in data["nonces"].items()}
        except (TypeError, ValueError) as exc:
            raise FleetStateError("replay_state_corrupt: %s" % type(exc).__name__)

    def _persist(self, last_sequence: dict, nonces: dict) -> None:
        if not self._path:
            return
        try:
            p = Path(self._path)
            p.parent.mkdir(parents=True, exist_ok=True)
            tmp = p.with_suffix(p.suffix + ".tmp")
            tmp.write_text(json.dumps({"last_sequence": last_sequence, "nonces": nonces}))
            os.replace(str(tmp), str(p))  # atomic within a filesystem
        except OSError as exc:
            raise FleetStateError("replay_state_write_failed: %s" % type(exc).__name__)

    def advance(self, member: str, sequence: int, nonce: str, now_ts: float) -> None:
        """Advance the high-water for `member` — DURABLY FIRST. The in-memory
        view changes only after the new state is on disk; a persistence failure
        raises and leaves memory untouched, so the caller refuses the signal
        (B2: never swallowed)."""
        new_seq = dict(self.last_sequence)
        new_seq[member] = max(int(new_seq.get(member, -1)), int(sequence))
        new_nonces = {k: dict(v) for k, v in self.nonces.items()}
        bucket = new_nonces.setdefault(member, {})
        bucket[str(nonce)] = float(now_ts)
        cutoff = float(now_ts) - 600.0
        for n, ts in list(bucket.items()):
            if ts < cutoff:
                del bucket[n]
        self._persist(new_seq, new_nonces)
        self.last_sequence = new_seq
        self.nonces = new_nonces


_REPLAY = ReplayState()


def verify_envelope(envelope: dict, now_ts: Optional[float] = None, state: Optional[ReplayState] = None) -> dict:
    """FULL consumer-side verification, fail-closed: registry -> membership ->
    fleet_core.verify_fleet_signal (version const, field presence, evidence
    binding, freshness, sequence/nonce replay, signature). Replay state
    advances ONLY on a fully valid envelope."""
    st = state if isinstance(state, ReplayState) else _REPLAY
    now = float(now_ts) if isinstance(now_ts, (int, float)) else time.time()
    e = envelope if isinstance(envelope, dict) else {}
    # B2 (WS-1): a fleet-managed consumer without DURABLE replay state refuses
    # every signal — an in-memory high-water is a replay window after restart.
    if fleet_managed() and not st.durable:
        return {"valid": False, "member": e.get("member_agent_id"), "reasons": ["replay_state_not_durable"]}
    reg = load_registry()
    if reg is None:
        return {"valid": False, "member": e.get("member_agent_id"), "reasons": ["no_member_registry"]}
    members = reg.get("members") if isinstance(reg.get("members"), dict) else {}
    member_id = str(e.get("member_agent_id"))
    member = members.get(member_id)
    verify_fn = _member_verify_fn(member) if isinstance(member, dict) else None
    if isinstance(member, dict) and verify_fn is None:
        return {"valid": False, "member": member_id, "reasons": ["member_has_no_key"]}
    result = verify_fleet_signal(
        e, member if isinstance(member, dict) else None, now,
        st.last_sequence.get(member_id) if member_id in st.last_sequence else None,
        (st.nonces.get(member_id) or {}).keys(), verify_fn,
    )
    if result.get("valid"):
        try:
            st.advance(member_id, int(e.get("sequence")), str(e.get("nonce")), now)
        except FleetStateError as exc:
            # B2: the high-water could not be persisted -> the signal is REFUSED
            # (never accepted on the strength of an in-memory advance).
            return {"valid": False, "member": member_id, "reasons": ["replay_persist_failed:" + str(exc)]}
    return result


def registry_k_policy() -> dict:
    """The SIGNED k-policy the manifest projection carries (fleet_manifest
    to_registry). {} when absent."""
    reg = load_registry() or {}
    kp = reg.get("k_policy")
    return dict(kp) if isinstance(kp, dict) else {}


def fleet_k_floor(role: str = "fleet") -> int:
    """WS-1 (reviewer #4): the k floor is a RUNTIME AUTHORITY sourced from the
    signed manifest, never only a code constant. Effective floor =
    max(code constant FLEET_K_FLOOR, signed policy floor for `role`) where role
    is "fleet" (coordinator aggregation, k_policy.fleet_floor) or "member"
    (a member's cohort store, k_policy.member_floor). A signed manifest that
    RAISES the floor changes runtime behaviour; a manifest edit without a
    re-sign is refused at load (load_registry -> None), so the policy can only
    come from the anchor. The code constant is a floor, never a ceiling."""
    from src.shared.fleet_core import FLEET_K_FLOOR
    kp = registry_k_policy()
    key = "member_floor" if str(role) == "member" else "fleet_floor"
    val = kp.get(key)
    try:
        signed = int(val) if val is not None else 0
    except (TypeError, ValueError):
        signed = 0
    return max(int(FLEET_K_FLOOR), signed)


def member_tenant(member_id: str) -> Optional[str]:
    """The operating TENANT the signed registry binds a member to (or None). k
    counts DISTINCT tenants — a member without a bound tenant never counts
    toward k (it is not silently counted as its own tenant)."""
    reg = load_registry() or {}
    members = reg.get("members") if isinstance(reg.get("members"), dict) else {}
    m = members.get(str(member_id))
    t = m.get("tenant_id") if isinstance(m, dict) else None
    return str(t) if t not in (None, "") else None


def registry_doctrine_version() -> str:
    reg = load_registry() or {}
    return str(reg.get("doctrine_version") or os.environ.get("FLEET_DOCTRINE_VERSION", ""))


# ── fleet-managed identity (FTC-3) ───────────────────────────────────────

def fleet_managed() -> bool:
    """Is THIS runtime a fleet-managed member? A durable, SIGNED fact from the
    identity — NOT an operator env flag. Enforcement is by construction, not
    opt-in (Peter FTC-3 / DD P0 2026-08-14):

    A member is fleet-managed when its signed identity places it in a fleet. That
    is true when EITHER the identity carries an explicit "fleet_managed: true"
    OR it carries an "owner.fleet_id" (assignment to a fleet is itself the
    signed fact that makes lease enforcement mandatory). Deriving from
    owner.fleet_id means a delivered specialist enforces leases by DEFAULT — a
    fleet-assigned agent with no lease infrastructure fail-closes every
    privileged action, which is the intended posture. A genuine standalone
    (non-fleet) agent carries neither field and is not lease-gated.
    FLEET_MANAGED=1 may force it ON for tests, never OFF."""
    ident = _identity()
    if bool(ident.get("fleet_managed")):
        return True
    owner = ident.get("owner")
    if isinstance(owner, dict) and owner.get("fleet_id"):
        return True
    if ident.get("fleet_id"):
        return True
    return str(os.environ.get("FLEET_MANAGED", "")).lower() in ("1", "true", "yes")


# ── member lease guard (called by ccas_decide) ───────────────────────────

def _coordinator_lease_pubkey() -> str:
    """The coordinator's PUBLIC lease-verification key, taken from the SIGNED
    registry/manifest trust anchor (lease_pubkey_hex), with an env override for
    offline tests. Members hold ONLY this public key — never the signing seed —
    so a member cannot mint its own lease (Peter FTC-2)."""
    reg = load_registry() or {}
    return str(reg.get("lease_pubkey_hex") or os.environ.get("FLEET_LEASE_PUBKEY", ""))


def require_fleet_lease(capability: str, now_ts: Optional[float] = None) -> Tuple[bool, list]:
    """Verify the member's CURRENT capability lease before a privileged action.
    FAIL-CLOSED: no coordinator pubkey, no lease file, bad signature, expiry,
    SUBJECT mismatch (lease not for this runtime's signed identity), or the
    action's CAPABILITY not in the lease scope — each is a deny with a named
    reason. The lease is the coordinator-signed token at FLEET_LEASE_PATH,
    verified with the coordinator's PUBLIC key. No default key."""
    now = float(now_ts) if isinstance(now_ts, (int, float)) else time.time()
    pub = _coordinator_lease_pubkey()
    if not pub:
        return (False, ["lease_pubkey_not_provisioned"])
    local_id = str(_identity().get("agent_id") or "")
    if not local_id:
        return (False, ["local_identity_absent"])
    path = str(os.environ.get("FLEET_LEASE_PATH", ""))
    if not path:
        return (False, ["lease_path_not_configured"])
    try:
        token = json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return (False, ["lease_unreadable"])
    reg = load_registry() or {}

    def _v(msg: bytes, sig_hex: str) -> bool:
        try:
            return ed25519_verify(bytes.fromhex(pub), bytes.fromhex(str(sig_hex)), msg)
        except (ValueError, TypeError):
            return False

    result = verify_lease(
        token, now, verify=_v, expected_member=local_id,
        required_capability=str(capability),
        expected_fleet_id=reg.get("fleet_id"),
        expected_epoch=reg.get("lease_epoch"),
    )
    if result.get("valid") is not True:
        return (False, [str(r) for r in (result.get("reasons") or ["invalid"])])
    return (True, [])


# ── lease installation (the RETURN half of the wire, blocker B1) ─────────

def install_lease(token: dict, now_ts: Optional[float] = None) -> Tuple[bool, list]:
    """Install a coordinator-minted lease for THIS member at FLEET_LEASE_PATH —
    but ONLY after verifying it exactly as require_fleet_lease will: signed by
    the coordinator's PUBLIC lease key (from the signed registry / manifest
    anchor), subject == this runtime's signed identity, unexpired, right fleet
    and epoch, and a NON-EMPTY capability scope (an empty-scope lease grants
    nothing and is not worth installing). A lease that fails any check is NOT
    written — the previously installed lease (if any) is left untouched, so a
    coordinator cannot downgrade a member by returning garbage. The write is
    atomic (temp + os.replace) so the CCAS gate never reads a torn file.
    Returns (installed, reasons)."""
    now = float(now_ts) if isinstance(now_ts, (int, float)) else time.time()
    t = token if isinstance(token, dict) else {}
    pub = _coordinator_lease_pubkey()
    if not pub:
        return (False, ["lease_pubkey_not_provisioned"])
    local_id = str(_identity().get("agent_id") or "")
    if not local_id:
        return (False, ["local_identity_absent"])
    path = str(os.environ.get("FLEET_LEASE_PATH", ""))
    if not path:
        return (False, ["lease_path_not_configured"])
    scope = t.get("capability_scope") if isinstance(t.get("capability_scope"), list) else []
    if not scope:
        return (False, ["lease_scope_empty"])
    reg = load_registry() or {}

    def _v(msg: bytes, sig_hex: str) -> bool:
        try:
            return ed25519_verify(bytes.fromhex(pub), bytes.fromhex(str(sig_hex)), msg)
        except (ValueError, TypeError):
            return False

    result = verify_lease(
        t, now, verify=_v, expected_member=local_id,
        required_capability=str(scope[0]),
        expected_fleet_id=reg.get("fleet_id"),
        expected_epoch=reg.get("lease_epoch"),
    )
    if result.get("valid") is not True:
        return (False, [str(r) for r in (result.get("reasons") or ["invalid"])])
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(p.suffix + ".tmp")
        tmp.write_text(json.dumps(t, sort_keys=True))
        os.replace(str(tmp), str(p))  # atomic within a filesystem
    except OSError as exc:
        return (False, ["lease_write_failed:%s" % type(exc).__name__])
    return (True, [])

# ── lease installation (the RETURN half of the wire, blocker B1) ─────────

def install_lease(token: dict, now_ts: Optional[float] = None) -> Tuple[bool, list]:
    """Install a coordinator-minted lease for THIS member at FLEET_LEASE_PATH —
    but ONLY after verifying it exactly as require_fleet_lease will: signed by
    the coordinator's PUBLIC lease key (from the signed registry / manifest
    anchor), subject == this runtime's signed identity, unexpired, right fleet
    and epoch, and a NON-EMPTY capability scope (an empty-scope lease grants
    nothing and is not worth installing). A lease that fails any check is NOT
    written — the previously installed lease (if any) is left untouched, so a
    coordinator cannot downgrade a member by returning garbage. The write is
    atomic (temp + os.replace) so the CCAS gate never reads a torn file.
    Returns (installed, reasons)."""
    now = float(now_ts) if isinstance(now_ts, (int, float)) else time.time()
    t = token if isinstance(token, dict) else {}
    pub = _coordinator_lease_pubkey()
    if not pub:
        return (False, ["lease_pubkey_not_provisioned"])
    local_id = str(_identity().get("agent_id") or "")
    if not local_id:
        return (False, ["local_identity_absent"])
    path = str(os.environ.get("FLEET_LEASE_PATH", ""))
    if not path:
        return (False, ["lease_path_not_configured"])
    scope = t.get("capability_scope") if isinstance(t.get("capability_scope"), list) else []
    if not scope:
        return (False, ["lease_scope_empty"])
    reg = load_registry() or {}

    def _v(msg: bytes, sig_hex: str) -> bool:
        try:
            return ed25519_verify(bytes.fromhex(pub), bytes.fromhex(str(sig_hex)), msg)
        except (ValueError, TypeError):
            return False

    result = verify_lease(
        t, now, verify=_v, expected_member=local_id,
        required_capability=str(scope[0]),
        expected_fleet_id=reg.get("fleet_id"),
        expected_epoch=reg.get("lease_epoch"),
    )
    if result.get("valid") is not True:
        return (False, [str(r) for r in (result.get("reasons") or ["invalid"])])
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(p.suffix + ".tmp")
        tmp.write_text(json.dumps(t, sort_keys=True))
        os.replace(str(tmp), str(p))  # atomic within a filesystem
    except OSError as exc:
        return (False, ["lease_write_failed:%s" % type(exc).__name__])
    return (True, [])
