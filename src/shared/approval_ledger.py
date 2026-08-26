"""Persistent approval-consumption ledger (Fas 2.17) - anti-replay across calls.

An approval that has RELEASED an action is consumed forever: ccas_decide
records (action_ref, approver_principal, nonce) here BEFORE returning
"approved", and _valid_approver_principals rejects any approval whose tuple is
already consumed. So the same signed approvals can never release a second
action - not in this call, not in a later one.

Fail-closed by construction:
  * unreadable ledger  -> freshness cannot be proven -> approvals invalid.
  * unwritable ledger  -> consumption cannot be recorded -> NO release
    (LedgerUnavailable raised before "approved" is returned).
  * malformed expires_at on an approval -> that approval invalid.

The path is read per call from CCAS_LEDGER_PATH (default ./ccas_approvals.jsonl,
a runtime output - never delivered, never committed). This local file is the
SKELETON ledger; bind a shared store (DB) for multi-replica production the same
way hexa_record documents DATABASE_URL.

Fas 3.14 - A MEASURED SCALING BOUNDARY, stated rather than discovered.
Single-use requires knowing the whole consumed SET, so consume() reads every
record under the lock. That cost is linear in ledger size: measured on the real
signed bundle at 0.12 ms per check over 100 entries, 1.0 ms over 1 000, 9.7 ms
over 10 000 and 49 ms over 50 000. It is bounded by APPROVALS CONSUMED, not by
traffic - only a released gated action writes here - so it is not the flood
surface the audit chain was (see hexa_record, Fas 3.14, where the same shape
WAS remotely reachable and was removed). It is left linear deliberately: the
full-set read under an exclusive lock is what makes single-use atomic, which is
the strongest property this file has and the one A2/A11 prove. Trading it for
an index in a skeleton would be trading a proven guarantee for a benchmark. A
production deployment binds a store with a real compare-and-set and an index;
that is the documented CUSTOMER step, and this is the number it is measured
against.

Fas 2.22 (external DD, Peter #3) - single-use is ATOMIC on one host: consume()
takes an exclusive OS advisory lock (fcntl.flock LOCK_EX) around the whole
read-existing -> append-missing cycle, so two callers racing to consume the SAME
(action_ref, approver_principal, nonce) tuple serialise and the tuple is written
AT MOST ONCE. flock is advisory and per-host: multi-replica single-use is a
customer binding (a shared store with a real compare-and-set), declared here,
never silently claimed.
"""
import fcntl
import json
import os
import time

from src.shared import state_paths


class LedgerUnavailable(RuntimeError):
    """Raised when a consumption record cannot be durably written - the caller
    must NOT release the action (no release without a ledger record)."""


def _path() -> str:
    # Fas 3.15 — containment is enforced at every open (state_paths), not here:
    # a path that merely LOOKS safe is not the property that matters.
    return os.environ.get("CCAS_LEDGER_PATH", "./ccas_approvals.jsonl")


def _entries():
    """All consumption records, or None when the ledger cannot be read
    (None => caller must treat every approval as unverifiable => invalid)."""
    p = _path()
    if not os.path.exists(p):
        return []
    try:
        out = []
        with state_paths.open_state(p, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except ValueError:
                    # A corrupt line means the ledger's integrity is in doubt.
                    return None
        return out
    except (OSError, state_paths.StatePathRefused):
        return None


def is_consumed(action_ref: str, approver: str, nonce: str):
    """True when this approval tuple has already released an action, OR when
    the ledger cannot be read (fail-closed: unprovable freshness = consumed)."""
    entries = _entries()
    if entries is None:
        return True
    for e in entries:
        if (
            str(e.get("action_ref")) == str(action_ref)
            and str(e.get("approver_principal")) == str(approver)
            and str(e.get("nonce")) == str(nonce)
        ):
            return True
    return False


def high_water_ts() -> float:
    """The newest timestamp this ledger has ever recorded, or 0.0 when empty.

    Fas 3.13 (adversarial finding) — approval freshness (expires_at) is judged
    against time.time(). Nothing in a container makes that clock trustworthy:
    move it back a day and every expired approval is valid again, which was
    demonstrated on the real signed bundle.

    Time cannot be verified without a trusted source, so this does not pretend
    to. What it does is make ROLLBACK detectable using only what is already on
    disk: the ledger is append-only, so the highest timestamp it contains is a
    floor the clock must never go below. Beating it requires rewriting the
    ledger too - the same bar as the audit chain's head sidecar, and the same
    honest limit.
    """
    try:
        with state_paths.open_state(_path() + ".hw", "r") as f:
            return float(json.load(f).get("high_water_ts") or 0.0)
    except (OSError, ValueError, TypeError, AttributeError, state_paths.StatePathRefused):
        pass
    # No sidecar (a ledger written before this existed, or an unwritable state
    # dir): re-derive it once from the entries rather than reporting no floor,
    # which would silently disable rollback detection.
    newest = 0.0
    try:
        for e in _entries() or []:
            try:
                ts = float(e.get("ts") or 0.0)
            except (TypeError, ValueError):
                continue
            if ts > newest:
                newest = ts
    except Exception:  # noqa: BLE001 - an unreadable ledger is handled by the caller
        return 0.0
    return newest


def _bump_high_water(ts: float) -> None:
    """Raise the recorded high-water mark. It can only ever go UP.

    Fas 3.14 — 3.13 derived this floor by scanning the whole ledger on every
    decision, which is the very cost this phase is removing. Written here under
    the same exclusive lock as the append, so the pair stays consistent.

    Fas 3.13 — max(), never assignment. A write performed while the clock is
    already rolled back carries a LOW timestamp; letting it overwrite the mark
    would let an attacker lower the floor and walk the clock backwards one
    consumption at a time. A ratchet that can be turned down is not a ratchet.
    """
    hw = _path() + ".hw"
    current = 0.0
    try:
        with state_paths.open_state(hw, "r") as f:
            current = float(json.load(f).get("high_water_ts") or 0.0)
    except (OSError, ValueError, TypeError, AttributeError, state_paths.StatePathRefused):
        current = 0.0
    if ts <= current:
        return
    try:
        with state_paths.open_state(hw, "w") as f:
            json.dump({"high_water_ts": ts}, f)
            f.flush()
            os.fsync(f.fileno())
    except (OSError, state_paths.StatePathRefused):
        pass  # a missing sidecar degrades detection; high_water_ts() re-derives it


def consume(action_ref: str, approvals) -> int:
    """Durably and ATOMICALLY record the approvals that are about to release an
    action. MUST be called before "approved" is returned. Returns the number of
    tuples NEWLY written (0 when every tuple was already consumed).

    Fas 2.22 (external DD, Peter #3 — single-use race): the whole
    read-existing -> append-missing cycle runs inside an exclusive OS advisory
    lock (fcntl.flock LOCK_EX) held on the ledger file, so two callers racing to
    consume the SAME (action_ref, approver_principal, nonce) tuple serialise —
    the first writes it, the second sees it already present and writes nothing.
    A tuple is therefore consumed AT MOST ONCE: an approval releases an action
    exactly one time, even under concurrency (no double release). Raises
    LedgerUnavailable on any write/lock failure OR a corrupt ledger (the caller
    must then NOT release). NOTE — single-host grade: flock is advisory and
    per-host; multi-replica single-use is a customer binding (shared store with
    a real compare-and-set), never silently claimed here."""
    ts = time.time()
    candidates = []
    for a in approvals or []:
        if not isinstance(a, dict):
            continue
        candidates.append({
            "ts": ts,
            "action_ref": str(action_ref),
            "approver_principal": str(a.get("approver_principal") or ""),
            "nonce": str(a.get("nonce") or ""),
        })
    if not candidates:
        return 0
    try:
        fd = state_paths.open_state_fd(_path(), os.O_RDWR | os.O_CREAT)
    except state_paths.StatePathRefused as e:
        raise LedgerUnavailable(str(e))
    except OSError as e:
        raise LedgerUnavailable("approval ledger not writable: %s" % e)
    try:
        with os.fdopen(fd, "r+", encoding="utf-8") as f:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            except OSError as e:
                raise LedgerUnavailable("approval ledger not lockable: %s" % e)
            # Re-read the WHOLE ledger under the lock: the set of tuples that
            # have already released an action. Any corrupt line means integrity
            # is in doubt — refuse to consume (fail-closed), same stance as
            # is_consumed's unreadable-ledger branch.
            f.seek(0)
            seen = set()
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except ValueError:
                    raise LedgerUnavailable("approval ledger corrupt — refusing to consume")
                seen.add((
                    str(rec.get("action_ref")),
                    str(rec.get("approver_principal")),
                    str(rec.get("nonce")),
                ))
            f.seek(0, os.SEEK_END)
            written = 0
            for r in candidates:
                key = (r["action_ref"], r["approver_principal"], r["nonce"])
                if key in seen:
                    continue  # already consumed — idempotent no-op (single-use)
                seen.add(key)
                f.write(json.dumps(r, sort_keys=True))
                f.write(chr(10))
                written += 1
            f.flush()
            os.fsync(f.fileno())
            # Fas 3.13/3.14 — raise the clock floor while still holding the
            # lock, so the mark can never describe a state the ledger has not
            # durably reached.
            if written:
                _bump_high_water(ts)
            return written
    except LedgerUnavailable:
        raise
    except OSError as e:
        raise LedgerUnavailable("approval ledger write failed: %s" % e)
