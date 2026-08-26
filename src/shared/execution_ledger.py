"""Execution ledger - at-most-once side effects per idempotency key (Fas 3.3).

The ActionProposal contract declares an idempotency_key whose stated purpose is
that a replayed proposal cannot double-execute. Until Fas 3.3 that was
DOCUMENTATION: the approval ledger (src/shared/approval_ledger.py) makes an
APPROVAL single-use, but a NEW, validly-signed approval carrying the SAME
idempotency key executed the side effect again. Two runs of the same Tier-1
proposal both returned approved+executed.

This module is the missing half: a reservation taken BEFORE the side effect,
keyed on the action's identity rather than on the approval.

    key = (tenant_id, selected_action, idempotency_key)

    reserve(...) -> "reserved"  : this caller owns the execution
                 -> "duplicate" : someone already owns/completed it; the prior
                                  outcome is returned so a replay can answer
                                  WITHOUT a second side effect

Atomicity: the read-existing -> append-missing cycle runs under an exclusive
advisory lock (fcntl.flock LOCK_EX) held on the ledger file, so two callers
racing on the same key produce exactly ONE reservation. Same guarantee, same
grade, and the same honest limit as the approval ledger: flock is advisory and
PER HOST. Multi-replica exactly-once needs a shared compare-and-set store (a DB
unique constraint on the key) bound at EXECUTION_LEDGER_BACKEND - the seam is
here, the distributed store is a deployment binding.

Failure semantics are declared, not implied:
  * ledger unreadable/unwritable/corrupt -> ExecutionLedgerUnavailable. The
    caller MUST NOT execute (no side effect without a reservation).
  * reserved but never completed (crash between reservation and commit) -> the
    record stays "reserved" and a replay reports status="indeterminate": the
    system does not know whether the side effect happened, and says so instead
    of guessing. Effectively-once under documented failure semantics - never a
    claim of absolute exactly-once across external systems.
"""
import fcntl
import json
import os
import time

from src.shared.canonical_identity import canonical_identity

from src.shared import state_paths


class ExecutionLedgerUnavailable(RuntimeError):
    """The reservation could not be durably taken - the caller must NOT execute."""


def _path() -> str:
    return os.environ.get("EXECUTION_LEDGER_PATH", "./execution_ledger.jsonl")


def execution_key(action) -> str:
    """(tenant_id, selected_action, idempotency_key) - the identity of ONE
    intended side effect. Empty when the action cannot be identified, which the
    caller must treat as non-idempotent and refuse."""
    if not isinstance(action, dict):
        return ""
    tenant = action.get("tenant_id") or action.get("tenant") or ""
    name = action.get("selected_action") or ""
    key = action.get("idempotency_key") or ""
    # Fas 3.25 — the SAME canonicalisation the approval reference uses. A strip()
    # here and a casefold() there is what let one approved action execute twice.
    tenant, name, key = (canonical_identity(tenant), canonical_identity(name),
                         str(key).strip())
    if not (tenant and name and key):
        return ""
    return json.dumps([tenant, name, key], separators=(",", ":"), sort_keys=True)


def _read_locked(f):
    out = []
    f.seek(0)
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except ValueError:
            raise ExecutionLedgerUnavailable("execution ledger has a corrupt line")
    return out


def reserve(action) -> tuple:
    """Atomically claim the right to execute this action ONCE.

    Returns ("reserved", record) when this caller owns the execution, or
    ("duplicate", prior) when the key is already claimed - prior carries the
    earlier outcome ("succeeded"/"failed"/"indeterminate") so a replay can
    answer without repeating the side effect.

    Fas 3.25 — a prior outcome of "not_applied" (approved and reserved, but the
    CUSTOMER_SLOT was unwired, so nothing happened) does NOT suppress: it is
    re-claimable, because idempotency exists to stop a repeat of a real side
    effect, not to permanently forbid one that never occurred."""
    key = execution_key(action)
    if not key:
        raise ExecutionLedgerUnavailable(
            "action lacks tenant_id/selected_action/idempotency_key - cannot be made idempotent")
    # Fas 3.40 (external DD P2) — a REFUSED path is an unavailable ledger.
    #
    # state_paths raises StatePathRefused (a RuntimeError) when a store resolves
    # outside DOER_STATE_ROOT or through a symlink. This module only caught
    # OSError, and the approval gate only catches ExecutionLedgerUnavailable —
    # so a misconfigured deployment did not fail closed, it raised an unhandled
    # exception straight out of a privileged action and became a 500.
    #
    # 3.37 taught /readyz to use the same guard, which lowers the odds under
    # normal orchestration. It does not remove them: configuration can change
    # after the probe, and an endpoint can be reached while readiness is red.
    # The refusal must be handled where the ledger is actually used.
    try:
        fd = state_paths.open_state_fd(_path(), os.O_RDWR | os.O_CREAT)
    except state_paths.StatePathRefused as e:
        raise ExecutionLedgerUnavailable("execution ledger path refused: %s" % e)
    except OSError as e:
        raise ExecutionLedgerUnavailable("execution ledger not writable: %s" % e)
    try:
        with os.fdopen(fd, "r+", encoding="utf-8") as f:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            except OSError as e:
                raise ExecutionLedgerUnavailable("execution ledger not lockable: %s" % e)
            entries = _read_locked(f)
            claimed = [e for e in entries if e.get("key") == key]
            if claimed:
                prior = claimed[-1]
                if prior.get("status") == "reserved":
                    # Reserved but never completed: a crash between the side
                    # effect and its commit. We do not know if it happened.
                    prior = dict(prior, status="indeterminate")
                # Fas 3.25 (external DD) — IDEMPOTENCY PROTECTS AGAINST REPEATING
                # WHAT HAPPENED, NOT AGAINST DOING WHAT NEVER DID.
                #
                # A prior outcome of not_applied means the gate approved and
                # reserved correctly and the CUSTOMER_SLOT was unwired, so no
                # side effect occurred. Suppressing the retry would permanently
                # block the action the moment the customer finally binds the
                # integration — and would answer the replay with a success that
                # never happened. So the claim is re-opened.
                #
                # succeeded / failed / indeterminate all stay suppressed:
                # indeterminate especially, because "we do not know whether the
                # side effect fired" must never resolve to "do it again".
                if prior.get("status") != "not_applied":
                    return ("duplicate", prior)
            rec = {"key": key, "status": "reserved", "ts": time.time()}
            f.seek(0, os.SEEK_END)
            f.write(json.dumps(rec, separators=(",", ":")) + chr(10))
            f.flush()
            os.fsync(f.fileno())
            return ("reserved", rec)
    except ExecutionLedgerUnavailable:
        raise
    except state_paths.StatePathRefused as e:
        raise ExecutionLedgerUnavailable("execution ledger path refused: %s" % e)
    except OSError as e:
        raise ExecutionLedgerUnavailable("execution ledger write failed: %s" % e)


def classify_apply_result(result):
    """Classify what a customer _apply_ seam returned. Returns (executed, outcome).

    Fas 3.37 (external DD, counter-proof) — ONE decision, used everywhere.

    Until now three places decided whether a privileged side effect had run,
    and they did not agree. The approval gate wrote the LEDGER outcome from
    bool(result.get("applied")) while its own HTTP response and the
    pipeline composite both used ... is True. A seam returning the string
    "false" was therefore recorded as succeeded in the durable ledger
    and reported as executed=false in the same transaction — two
    contradictory truths about a privileged action, four lines apart.

    The loose test drove the ledger, which is the worst place for it: the
    reservation then suppressed the legitimate retry with a success that never
    happened.

    Rules, and they are deliberately unforgiving about a side effect:
      - applied is True  -> executed, outcome "succeeded".
      - applied is False/absent -> not executed; the status then decides
        between "not_applied" (an unwired slot) and "failed".
      - applied present but NOT a bool -> the seam's contract is broken.
        A privileged execution must never be inferred from a truthy string or
        number, so this is "indeterminate" — never "succeeded".
      - a non-dict result -> "indeterminate" for the same reason.

    Callers must use BOTH returned values from the same call. Deriving
    executed separately is what created the contradiction this replaces.
    """
    if not isinstance(result, dict):
        return False, "indeterminate"
    applied = result.get("applied")
    if applied is True:
        return True, "succeeded"
    if applied is not False and applied is not None:
        # Present, but not a boolean. Refuse to guess about a side effect.
        return False, "indeterminate"
    status = result.get("status")
    if status == "not_implemented":
        # An unwired CUSTOMER_SLOT. Not a failure of this run — the action was
        # approved and reserved correctly; nothing was bound to perform it.
        # Its own outcome, so a later wired retry is not answered with a
        # success that never happened.
        return False, "not_applied"
    if status in ("failed", "error"):
        return False, "failed"
    return False, "indeterminate"


def complete(action, status: str, detail=None) -> None:
    """Record the OUTCOME of a reserved execution (succeeded/failed). A replay
    then returns this instead of executing again."""
    key = execution_key(action)
    if not key:
        return
    try:
        fd = state_paths.open_state_fd(_path(), os.O_RDWR | os.O_CREAT)
        with os.fdopen(fd, "r+", encoding="utf-8") as f:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            except OSError as e:
                raise ExecutionLedgerUnavailable("execution ledger not lockable: %s" % e)
            rec = {"key": key, "status": str(status), "detail": detail, "ts": time.time()}
            f.seek(0, os.SEEK_END)
            f.write(json.dumps(rec, separators=(",", ":"), default=str) + chr(10))
            f.flush()
            os.fsync(f.fileno())
    except ExecutionLedgerUnavailable:
        raise
    except state_paths.StatePathRefused as e:
        # Worse here than in reserve(): a throw means the OUTCOME of a side
        # effect that may already have run is never recorded at all.
        raise ExecutionLedgerUnavailable("execution ledger path refused: %s" % e)
    except OSError as e:
        raise ExecutionLedgerUnavailable("execution ledger write failed: %s" % e)
