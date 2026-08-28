# The gate, traced — one privileged action through the real code

*A companion to `HOW_IT_WORKS.md`. This follows a single consequential request — "bind this trained adapter into a fleet agent", a declared privileged action — hop by hop through the actual files in this repo. Every block below is verbatim from the source; open the file and read along. The point: every guard sits **before** the side effect, the side effect is **unreachable** until all of them pass, and knowing exactly how it works does not help you get past it.*

File under trace: `src/nodes/hexaforge_slm_training_master_bind_adapter_to_fleet_agent_approval_gate_hexa/handler.py` and `src/shared/ccas_gate.py`.

---

## Hop 0 — the request arrives at a side-effect port

Consequential actions leave a node only through its **Yo/Xo port**. The port is a typed endpoint; a malformed body is a `422` before anything runs. It then calls the gate, and only calls the node's handler if the gate approved:

```python
# src/nodes/…_decision_hexa/port_yo.py
validated = HexaforgeSlmTrainingMasterDecisionHexaYoSchema(**payload)   # typed contract, or 422
validate_contract(node_id="…decision_hexa", port="yo", payload=validated.model_dump())
decision = ccas_decide(action=validated.model_dump(), tier="auto")     # the GATE
if decision["status"] != "approved":
    return {"status": "pending", "decision": decision}                 # side effect NEVER runs
return await handle_yo({**payload, **validated.model_dump(...)})        # only past the gate
```

**Why it matters:** the *port* decides whether to call the handler — the handler cannot invoke itself around the gate.

## Hop 1 — the privileged node re-asserts its declared tier

The privileged handler doesn't trust a generic default. It calls the gate at the action's **declared** tier, and a doctrine gate (`H_PRIVILEGED_ACTION_DECLARED`) rejects at build time any bundle where a privileged port skips this:

```python
# …bind_adapter_to_fleet_agent_approval_gate_hexa/handler.py — handle_xo
decision = ccas_decide(action=payload, tier="human")     # DECLARED tier, not a default
if decision["status"] != "approved":
    # Held for human approval — DO NOT execute the side effect.
    return { …, "ok": False, "status": decision["status"], "ccas_decision": decision, … }
```

**Why it matters:** "held" is the default outcome. The action stops here unless every downstream condition is met.

## Hop 2 — the gate: capability lease, scope-bound, fail-closed

Inside `ccas_decide`, before any tier logic, a fleet member must present a valid, signature-verified **capability lease** for *this specific action* — decided by the runtime's own signed identity, not an operator flag. No development default key exists; absent/expired/wrong-scope **denies**:

```python
# src/shared/ccas_gate.py — ccas_decide
from src.shared.fleet_trust import fleet_managed, require_fleet_lease
if fleet_managed():
    _capability = str(action.get("selected_action") or action.get("name") or …)
    _lease_ok, _lease_reasons = require_fleet_lease(_capability)   # scoped to THIS capability
    if not _lease_ok:
        return {"status": "denied", "route": "fleet_lease_gate",
                "reason": "fleet capability lease invalid or absent for '%s': %s" % (…)}
```

**Why it matters:** a lease scoped to other capabilities cannot authorise this one, and broken lease infrastructure fails closed — it never defaults open.

## Hop 3 — freshness: a rolled-back clock withholds the release

An approval's validity rests on `expires_at`, which rests on the clock. If the clock is proven to have moved backwards, the freshness verdict is worthless, so an otherwise-approved decision is **withheld**, not granted:

```python
# src/shared/ccas_gate.py — ccas_decide (wrapper, covers every releasing branch)
if clock == "rollback_detected" and decision.get("status") == "approved":
    return {"status": "pending", "route": "approval_queue",
            "reason": "clock rollback detected: … approval freshness cannot be judged; release withheld"}
```

**Why it matters:** the release rule is applied once, on the wrapper, so no branch can release on evidence known to be unreliable.

## Hop 4 — executor-boundary integrity (confused-deputy defense)

Even with an approval in hand, the action about to run must be **byte-identical** to the action the gate approved. The handler re-derives the content hash and refuses on any drift:

```python
# …bind_adapter…/handler.py — after approval
approved_ref = decision.get("action_ref")
if not approved_ref or canonical_action_ref(payload) != approved_ref:
    return { …, "status": "integrity_error", … }     # fail-closed on ANY drift
```

**Why it matters:** an approval issued for one action body can never be redirected to drive a different side effect.

## Hop 5 — real idempotency: reserve the right to run, once

Before the side effect, the handler atomically **reserves** execution. A duplicate returns the earlier outcome instead of repeating it; an unavailable ledger refuses to execute at all:

```python
# …bind_adapter…/handler.py
try:
    _claim, _prior = reserve(payload)
except ExecutionLedgerUnavailable as _e:
    return { …, "executed": False, "status": "execution_ledger_unavailable", … }   # no reservation → no side effect
if _claim == "duplicate":
    return { …, "executed": False, "status": "duplicate_suppressed", "prior_execution": _prior }
```

**Why it matters:** no side effect happens without a reservation; a replay cannot double-execute.

## Hop 6 — the side effect: the CUSTOMER_SLOT, fail-closed

Only now is the actual effect reached — and in the delivered skeleton it is an honest fail-closed stub. Reference mode (opt-in, posture-gated) is the *only* other path, and it is reachable **only after** the gate approved:

```python
# …bind_adapter…/handler.py — _apply_xo
async def _apply_xo(payload: dict) -> dict:
    # CUSTOMER_SLOT: implement the real privileged side effect INSIDE the gate.
    # The ccas_decide() gate in handle_xo is platform infra and MUST stay.
    if reference_enabled():
        return reference_apply("…bind_adapter…", "xo", payload)     # side-effect-free, disclosed
    return {"applied": False, "status": "not_implemented", "action": payload}   # FAIL-CLOSED: unwired seam never claims execution
```

**Why it matters:** an unwired seam never *claims* it executed. The gate is above this line; the customer's real integration goes here, under the same gate.

## Hop 7 — the ledger records what actually happened, not a word

The outcome is read from the seam's own result — one decision for the durable ledger and the response, so they can never disagree:

```python
# …bind_adapter…/handler.py
_executed, _outcome = classify_apply_result(result)     # ONE classification
complete(payload, _outcome, result if isinstance(result, dict) else None)
# "ok" means the GATE could process the call; "executed" follows the REAL side effect.
```

**Why it matters:** the audit record is evidence of what ran, not of what was intended — a `not_implemented` seam is never written as "succeeded".

---

## What the trace shows

Read top to bottom, the side effect at Hop 6 is reachable only after: a typed contract (Hop 0), the declared tier re-asserted (Hop 1), a scoped capability lease (Hop 2), a fresh clock (Hop 3), byte-identical content (Hop 4), and a single-use execution reservation (Hop 5) — each **fail-closed**, each **before** the effect. None of them is a model judgement; all are deterministic code you can read here. That is what "the model reasons, the rule decides, the gate enforces" means in practice — and why reading the code doesn't give you a way around it.

*Trace it yourself against the signed build: `v0.1.0` release → `python3 verify_identity.py . --trusted-root <fingerprint>`; then open the two files above.*
