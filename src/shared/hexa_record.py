"""HexaRecord — append-only, hash-linked forensic audit chain.

Each entry commits to the previous one: entry_hash = sha256(prev_hash | core),
so any retroactive edit breaks every downstream link (tamper-evident).

AUDIT BINDING (v2, Fas 2.11a): the hashed core binds WHO / WHAT-IN / WHAT-OUT:

  * ``principal``     — the authenticated caller identity, established at the
    transport boundary (zt_guard -> ``set_principal``) and carried by a
    contextvar so EVERY audit append in that request context inherits it.
    Explicit ``None`` means "no principal was established at this site" —
    absence is visible and hashed, never silent.
  * ``input_sha256``  — canonical sha256 of the EXACT input the node handler
    received (the merged envelope+payload), when the write site provides it.
  * ``output_sha256`` — canonical sha256 of the EXACT result the handler
    returned, when the write site provides it.

All three live INSIDE the hashed core (_CORE_KEYS), so tampering with any of
them breaks verify_chain — attribution and data binding are tamper-evident,
not annotations. ``canonical_sha256`` is the ONE canonicalisation (sorted-key
JSON) shared by writers, verifiers and tests — no drift.

AUDIT HONESTY: local file-backed chain — hash-linked and tamper-EVIDENT, but
not tamper-PROOF against an adversary who rewrites the whole file. Production
upgrade path: Postgres-backed chain with external anchoring. The chain binds
the sha256 of input/output — never the raw data (PII/GDPR floor: forensic
equality checks recompute the hash from the disputed data).
"""
import hashlib
import json
import os
import threading
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.shared import state_paths

try:  # POSIX advisory file locking — the chain append must be transactional
    import fcntl  # type: ignore
except Exception:  # pragma: no cover - non-POSIX platforms
    # fcntl is POSIX-only. On non-POSIX platforms (e.g. Windows) there is no
    # cross-process advisory lock here: the append falls back to the in-process
    # _APPEND_LOCK only, which is sufficient for a single-process deployment
    # (the containerised default) but NOT for multi-process writers.
    fcntl = None  # type: ignore


# In-process serialisation (threads/async workers share one interpreter);
# fcntl.flock serialises ACROSS processes. Together they make the
# read-head -> compute-hash -> append sequence atomic, so concurrent writers
# can never fork the chain by committing to the same prev_hash.
_APPEND_LOCK = threading.Lock()


try:  # structlog is optional — the audit chain must never depend on it
    import structlog  # type: ignore

    _log = structlog.get_logger("hexa_record")
except Exception:  # pragma: no cover - stdlib fallback when structlog is absent
    import logging

    class _StdlibLogAdapter:
        """Minimal structlog-compatible shim (kwargs -> JSON payload)."""

        def __init__(self, name: str) -> None:
            self._logger = logging.getLogger(name)

        def info(self, event: str, **kw: Any) -> None:
            self._logger.info("%s %s", event, json.dumps(kw, default=str, sort_keys=True))

        def warning(self, event: str, **kw: Any) -> None:
            self._logger.warning("%s %s", event, json.dumps(kw, default=str, sort_keys=True))

        def error(self, event: str, **kw: Any) -> None:
            self._logger.error("%s %s", event, json.dumps(kw, default=str, sort_keys=True))

    _log = _StdlibLogAdapter("hexa_record")


LOG_PATH = os.environ.get("HEXA_RECORD_PATH", "./hexa_record.jsonl")
GENESIS = "0" * 64

# Sentinel: distinguishes "caller did not provide input/output" from a
# legitimate None value (a blocking stub's None result is real data and
# must be hashable as such).
AUDIT_UNSET = object()

# Request-scoped principal (Fas 2.11a). Set ONCE at the transport boundary
# (zt_guard) and inherited by every audit append in that request's task
# context — handlers never thread it manually. contextvars are task-local,
# so concurrent requests can never bleed principals into each other.
_CURRENT_PRINCIPAL: ContextVar[Optional[str]] = ContextVar(
    "hexa_record_principal", default=None
)


def set_principal(principal: Optional[str]) -> Any:
    """Bind the authenticated caller identity for the CURRENT request context.

    Called by the transport guard (zt_guard) after credential verification —
    with the verified identity, or the explicit marker "auth_disabled" for the
    loopback-confined dev opt-out. Returns the contextvar token (tests may
    reset with it); request tasks die with their context, so no manual reset
    is required on the serving path.
    """
    return _CURRENT_PRINCIPAL.set(principal)


def reset_principal(token: Any) -> None:
    """Restore the principal to its pre-set value (tests / manual scopes).

    Serving code never needs this — each request task's context dies with the
    request — but same-process tests must not leak a principal forward.
    """
    _CURRENT_PRINCIPAL.reset(token)


def current_principal() -> Optional[str]:
    """The principal bound to the current request context (None outside one)."""
    return _CURRENT_PRINCIPAL.get()


def canonical_sha256(payload: Any) -> str:
    """THE canonical payload hash: sha256 over sorted-key JSON.

    Single source for writers, verify_chain and tests — a forensic equality
    check recomputes this from the disputed data and compares against the
    chain's hashed core.
    """
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, default=str).encode()
    ).hexdigest()


# Internal alias (kept so existing call sites read unchanged).
_sha256 = canonical_sha256


def _entry_hash(prev_hash: str, core: Dict[str, Any]) -> str:
    return _sha256({"prev_hash": prev_hash, "core": core})


def _core(
    node_id: str,
    port: str,
    payload: Any,
    ccas_decision: Optional[dict],
    event_id: Optional[str] = None,
    principal: Any = AUDIT_UNSET,
    input_payload: Any = AUDIT_UNSET,
    output_payload: Any = AUDIT_UNSET,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    core = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "node_id": node_id,
        "port": port,
        "payload_sha256": _sha256(payload),
        # v2 — WHO: explicit in EVERY entry (None = "not established", visible
        # and hashed). Falls back to the request-context principal so in-node
        # log_event calls inherit attribution without signature churn.
        "principal": (
            _CURRENT_PRINCIPAL.get() if principal is AUDIT_UNSET else principal
        ),
    }
    if event_id is not None:
        core["event_id"] = event_id
    # Fas 2.11b — korrelationskedjan: callerns request_id binds i den HASHADE
    # kärnan när det finns (frånvaro = nyckeln saknas, ärligt), så den
    # forensiska frågan "vilket anrop skapade den här posten?" har ett
    # manipulationssynligt svar.
    if request_id is not None:
        core["request_id"] = request_id
    if ccas_decision is not None:
        core["ccas_decision"] = ccas_decision
    # v2 — WHAT-IN / WHAT-OUT: bound only when the write site actually has the
    # data (absent key = "site did not provide", never a fabricated hash).
    if input_payload is not AUDIT_UNSET:
        core["input_sha256"] = _sha256(input_payload)
    if output_payload is not AUDIT_UNSET:
        core["output_sha256"] = _sha256(output_payload)
    return core


# Field order matters for hashing: _entry_hash sorts keys, so the reconstruction
# in verify_chain only needs the SAME key set as _core produced. v2 adds the
# binding fields — they sit INSIDE the hash, so tampering with principal or
# either data hash breaks the chain.
_CORE_KEYS = (
    "ts",
    "node_id",
    "port",
    "payload_sha256",
    "event_id",
    "principal",
    "input_sha256",
    "output_sha256",
    "request_id",
)


def _path(path: Optional[str] = None) -> str:
    return path or os.environ.get("HEXA_RECORD_PATH", LOG_PATH)


def read_chain(path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Read the file-backed chain (forensic inspection / verification)."""
    p = _path(path)
    if not os.path.exists(p):
        return []
    out: List[Dict[str, Any]] = []
    with state_paths.open_state(p, "r", encoding=None) as f:
        for line in f:
            if line.strip():
                out.append(json.loads(line))
    return out


def read_chain_for_event(event_id: str, path: Optional[str] = None) -> List[Dict[str, Any]]:
    """The AUTHORITATIVE audit view for one event: the hash-linked entries only.

    /api/audit/<event_id> serves this — not the volatile in-memory cache.
    """
    return [rec for rec in read_chain(path) if rec.get("event_id") == event_id]


def chain_head(path: Optional[str] = None) -> str:
    """The latest entry_hash, or GENESIS on an empty chain."""
    chain = read_chain(path)
    if not chain:
        return GENESIS
    return str(chain[-1].get("entry_hash") or GENESIS)


def _head_path(path: Optional[str] = None) -> str:
    """Sidecar holding the chain HEAD (count + last entry_hash).

    Resolved through _path() exactly like the chain itself. Reading the
    import-time LOG_PATH here instead would pair the head of one chain with the
    entries of another whenever HEXA_RECORD_PATH is set after import - which is
    how every isolated test, and every re-pointed deployment, runs.
    """
    return _path(path) + ".head"


def _write_head(path: Optional[str], count: int, entry_hash: str) -> None:
    """Record the high-water mark after every append.

    Fas 3.9 (adversarial finding) — a hash chain detects a MODIFIED link, but
    truncation removes links and leaves a perfectly valid shorter chain. Proven
    on the real signed bundle: deleting the last two entries left verify_chain
    returning True. An attacker with file access would delete exactly the
    entries covering their own actions.

    A head sidecar raises the bar honestly: the tail cannot be dropped without
    ALSO rewriting the head. It does not make the chain tamper-PROOF — an
    attacker who can write both files can still rewrite both, which is precisely
    why the artifact says tamper-EVIDENT and why external anchoring (a signed
    checkpoint shipped off-host) is a deployment binding, not a property this
    file can provide alone.
    """
    try:
        with state_paths.open_state(_head_path(path), "w") as f:
            f.truncate(0)
            json.dump({"count": count, "entry_hash": entry_hash}, f)
            f.flush()
            os.fsync(f.fileno())
    except (OSError, state_paths.StatePathRefused):
        pass  # the chain itself is authoritative; a missing head only weakens detection


def _core_of(rec: Dict[str, Any]) -> Dict[str, Any]:
    """Rebuild the hashed core of an existing entry, exactly as append wrote it."""
    core = {k: rec[k] for k in _CORE_KEYS if k in rec}
    if "ccas_decision" in rec:
        core["ccas_decision"] = rec["ccas_decision"]
    return core


def _count_from_head(path: Optional[str], tail_hash: str) -> Optional[int]:
    """The entry count the head sidecar vouches for, or None if it cannot.

    Trusted ONLY when the sidecar names the same entry the file's tail does:
    that pair was written together under the append lock, so agreement means
    the sidecar is current. Disagreement means re-count — never guess.
    """
    try:
        with open(_head_path(path), encoding="utf-8") as f:
            head = json.load(f)
    except (OSError, ValueError):
        return None
    if not isinstance(head, dict) or head.get("entry_hash") != tail_hash:
        return None
    try:
        count = int(head.get("count"))
    except (TypeError, ValueError):
        return None
    return count if count >= 0 else None


def chain_status(path: Optional[str] = None) -> dict:
    """Full verdict: links intact AND nothing removed from the tail."""
    entries = read_chain(path)
    prev = GENESIS
    for rec in entries:
        core = _core_of(rec)
        if rec.get("prev_hash") != prev:
            return {"ok": False, "reason": "broken_link", "count": len(entries)}
        if rec.get("entry_hash") != _entry_hash(prev, core):
            return {"ok": False, "reason": "entry_hash_mismatch", "count": len(entries)}
        prev = rec["entry_hash"]
    try:
        with open(_head_path(path), encoding="utf-8") as f:
            head = json.load(f)
    except (OSError, ValueError):
        return {"ok": True, "reason": "no_head_recorded", "count": len(entries),
                "truncation_detectable": False}
    if int(head.get("count") or 0) > len(entries):
        return {"ok": False, "reason": "truncated", "count": len(entries),
                "expected_count": head.get("count")}
    if head.get("entry_hash") and prev != head.get("entry_hash") and len(entries) <= int(head.get("count") or 0):
        return {"ok": False, "reason": "head_mismatch", "count": len(entries)}
    return {"ok": True, "reason": "intact", "count": len(entries), "truncation_detectable": True}


def verify_chain(path: Optional[str] = None) -> bool:
    """True iff every link is intact AND the tail has not been removed.

    A thin delegation on purpose: two independent re-implementations of the
    hashed core is exactly how a chain check drifts from what append actually
    signs, and a link verifier that disagrees with the writer fails open or
    fails noisily for the wrong reason. One definition, one verdict.
    """
    return bool(chain_status(path).get("ok"))


# Fas 3.14 — how much of the file's TAIL an append reads. A chain entry is a few
# hundred bytes, so the last record is effectively always inside this window;
# the window only grows (x4, from _last_record) when one entry is bigger than
# it. What matters is that it is a CONSTANT: it does not depend on how long the
# chain is, which is the whole point of this phase.
_TAIL_READ_BLOCK = 8192


def _last_record(fd: int, size: int) -> Optional[Dict[str, Any]]:
    """The LAST record, read by seeking to the tail — never by scanning.

    Fas 3.14 (adversarial finding). Until now every append re-read and
    json-parsed the ENTIRE chain to find prev_hash. Append is O(n) in chain
    length, so a run is O(n^2), and the audit write sits on the critical path of
    every node execution and is fail-closed — it cannot be skipped or deferred.

    Measured on the real signed bundle: 0.25 ms/event over 200 events,
    1.46 ms/event over 2000, and rising. That is a remote, unauthenticated,
    zero-privilege denial of service: send traffic. No exploit, no credential,
    no access to the host — just use the agent as intended, for long enough.

    os.pread reads at an absolute offset without disturbing the position of the
    locked handle, so this is safe to do while holding the append lock.

    HONEST NARROWING: the old full scan also refused to append when ANY line in
    the chain was corrupt. This one only guarantees that the TAIL parses. That
    is deliberate — parsing every line on every append IS the DoS — and it costs
    nothing that mattered: whole-chain integrity was never established by
    append, it is established by chain_status()/verify_chain(), which still read
    and re-hash every link. What append must not do is silently re-root the
    chain on a torn write, and that is exactly the tail.
    """
    if size <= 0:
        return None
    window = _TAIL_READ_BLOCK
    while True:
        offset = max(0, size - window)
        chunk = os.pread(fd, size - offset, offset)
        stripped = chunk.rstrip()
        if not stripped:
            return None
        nl = stripped.rfind(chr(10).encode("ascii"))
        if nl != -1:
            line = stripped[nl + 1:]
            break
        if offset == 0:
            line = stripped
            break
        window *= 4
    try:
        rec = json.loads(line.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        # a torn/corrupt tail must not silently re-root the chain
        raise RuntimeError("hexa_record: corrupt chain tail — refusing to append")
    return rec if isinstance(rec, dict) else None


def _head_from_open_file(f: Any) -> str:
    """Read the chain head from an ALREADY-LOCKED file handle (no re-open)."""
    f.flush()
    size = os.fstat(f.fileno()).st_size
    rec = _last_record(f.fileno(), size)
    if rec is None:
        return GENESIS
    return str(rec.get("entry_hash") or GENESIS)


def log_event(
    node_id: str,
    port: str,
    payload: Any,
    ccas_decision: Optional[dict] = None,
    event_id: Optional[str] = None,
    principal: Any = AUDIT_UNSET,
    input_payload: Any = AUDIT_UNSET,
    output_payload: Any = AUDIT_UNSET,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Append one tamper-evident entry to the audit chain — TRANSACTIONALLY.

    The read-head -> compute-hash -> append sequence runs while holding BOTH an
    in-process lock and an exclusive advisory file lock (fcntl.flock), so
    two concurrent writers can never commit to the same prev_hash and fork
    the chain. Returns the appended record.

    v2 binding: ``principal`` defaults to the request-context principal set by
    the transport guard; ``input_payload``/``output_payload`` (when provided)
    are canonically hashed into the core as ``input_sha256``/``output_sha256``.
    """
    p = _path()
    # Fas 3.15 — the state path is attacker-reachable surface: containment is
    # checked BEFORE any directory is created, so a refused path never leaves a
    # tree behind where it was told to.
    state_paths.ensure_parent(p)
    core = _core(
        node_id, port, payload, ccas_decision, event_id,
        principal=principal,
        input_payload=input_payload,
        output_payload=output_payload,
        request_id=request_id,
    )
    with _APPEND_LOCK:
        # Fas 3.15 — O_NOFOLLOW: the agent must never write its own audit trail
        # through a symlink someone else planted in the state volume.
        with state_paths.open_state(p, "a+", encoding=None) as f:
            if fcntl is not None:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                prev = _head_from_open_file(f)
                # Fas 3.9 — the recorded high-water mark must be exact, and
                # Fas 3.14 — establishing it must not cost a full scan per
                # append. The head sidecar was written under THIS lock next to
                # the entry whose hash it names, so when its entry_hash still
                # matches the tail the count it carries is exact and free. It
                # only falls back to counting when the sidecar is missing or
                # stale (first append after an upgrade, or a chain someone
                # appended to without it) — once, not once per event.
                _chain_len = _count_from_head(p, prev)
                if _chain_len is None:
                    f.seek(0)
                    _chain_len = sum(1 for _line in f if _line.strip())
                rec = {**core, "prev_hash": prev, "entry_hash": _entry_hash(prev, core)}
                f.seek(0, os.SEEK_END)
                f.write(json.dumps(rec) + "\n")
                f.flush()
                os.fsync(f.fileno())
                # Fas 3.9 — record the new high-water mark INSIDE the lock, so a
                # dropped tail cannot pass as a shorter-but-valid chain.
                _chain_len += 1
                _write_head(p, _chain_len, rec["entry_hash"])
            finally:
                if fcntl is not None:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    _log.info("hexa_record", **rec)
    return rec
