"""Reference capability (Fas 2.16) - factory-controlled happy-path harness.

DOER_REFERENCE_MODE=1 (explicit opt-in, default OFF) makes every unimplemented
CUSTOMER_SLOT return a CONTRACT-DERIVED reference output (built from the node's
own schemas.json) instead of a blocking stub, and makes the privileged gate's
_apply_ seam perform a side-effect-free REFERENCE execution. Every reference
output is marked "reference": True. This proves the CHASSIS executes the full
happy path through the action gate - it is NOT domain logic, it never claims to
be, and it never runs unless explicitly enabled. Approval provenance is NOT
relaxed: the CCAS gate still requires structured, action-bound, role-scoped,
nonce-fresh, SIGNED approvals to approve gated tiers (Fas 2.13c).
"""
import json
import os
import pathlib
import sys
import uuid

# The exact acknowledgement a production-posture deployment must set to enable
# reference mode. Spelled out so it cannot be typed by accident.
_REFERENCE_ACK = "i-understand-this-is-not-domain-logic"

# Fas 3.3 - the execution ledger reserves on
# (tenant_id, selected_action, idempotency_key) and refuses an action it cannot
# identify, so the reference harness must carry a key. The key is generated ONCE
# PER PROCESS, which is the only shape that satisfies both constraints at once:
#   * STABLE within a run, because idempotency_key is part of the signed
#     canonical_action_ref - a per-call key would change the ref between the
#     harness's probe run and its approved run, and the approvals would no
#     longer bind to the action they were issued for;
#   * DISTINCT between runs, because a constant would let the first reference
#     run execute and every later one be suppressed as a duplicate - the harness
#     would decay into a no-op the second time anyone ran it.
_REFERENCE_IDEMPOTENCY_KEY = "reference-" + uuid.uuid4().hex[:12]


def _production_posture() -> bool:
    """Transport auth ON is the runtime's own production signal (fail-closed
    default), so it is the signal reference mode is judged against."""
    return os.environ.get("ZT_REQUIRE_AUTH", "").strip().lower() not in ("0", "false", "no", "off")


def reference_enabled() -> bool:
    """True only when reference mode is BOTH requested and permitted.

    Fas 3.12 (adversarial finding) — this used to be one env var and nothing
    else. Anyone able to set container env (a compromised sidecar, a mistaken
    ConfigMap, a copied deployment) could flip a fail-closed skeleton into one
    that returns "usable" outputs for unimplemented capabilities and performs
    reference executions after approval. The agent would look like it works.
    That is an honesty switch, and honesty switches do not belong in the hands
    of whoever last edited the environment.

    So reference mode is refused in a PRODUCTION POSTURE. The posture signal is
    the one the runtime already trusts everywhere else: transport auth. With
    ZT_REQUIRE_AUTH on (the fail-closed default), reference mode requires an
    explicit, separate acknowledgement — DOER_REFERENCE_ACK=i-understand-this-is-not-domain-logic
    — so enabling it on a real deployment is a deliberate act, never a typo.
    Every activation is announced on stderr; the pipeline additionally audits it.

    runtime_mode gate (delivery flag) — a "live" build (HEXABOX_RUNTIME_MODE=live
    or a build stamped live in src/shared/runtime_mode.py) DISCLOSES that it
    expects REAL capability bindings, so the disclosed-synthetic reference harness
    is REFUSED there: an unbound capability fails closed instead of returning a
    placeholder that looks like a working agent. In the default "reference" mode
    this is a no-op and behaviour is exactly as before.
    """
    try:
        from src.shared.runtime_mode import is_live
    except Exception:  # pragma: no cover - runtime_mode always ships with the bundle
        def is_live() -> bool:
            return False
    if is_live():
        if os.environ.get("DOER_REFERENCE_MODE", "0") == "1":
            sys.stderr.write(
                "REFUSED: DOER_REFERENCE_MODE=1 but runtime_mode=live — a live build "
                "expects real capability bindings; the disclosed-synthetic reference "
                "harness is disabled so unbound capabilities fail closed." + chr(10))
        return False
    if os.environ.get("DOER_REFERENCE_MODE", "0") != "1":
        return False
    if _production_posture() and os.environ.get("DOER_REFERENCE_ACK", "") != _REFERENCE_ACK:
        sys.stderr.write(
            "REFUSED: DOER_REFERENCE_MODE=1 with transport auth ON (production posture). "
            "Reference mode emits NON-DOMAIN outputs and must never look like a working "
            "agent in production. Set ZT_REQUIRE_AUTH=0 for a local run, or set "
            "DOER_REFERENCE_ACK=" + _REFERENCE_ACK + " to acknowledge deliberately." + chr(10))
        return False
    sys.stderr.write(
        "REFERENCE MODE ACTIVE - outputs are contract-derived placeholders marked "
        "'reference': true, NOT domain results." + chr(10))
    return True


def _schema_for(node_id, port):
    root = pathlib.Path(__file__).resolve().parents[2]
    p = root / "src" / "nodes" / node_id / "schemas.json"
    try:
        doc = json.loads(p.read_text())
    except Exception:
        return {}
    spec = doc.get(port)
    return spec if isinstance(spec, dict) else {}


def _value_for(spec):
    if not isinstance(spec, dict):
        return "reference"
    enum = spec.get("enum")
    if isinstance(enum, list) and enum:
        return enum[0]
    t = spec.get("type")
    if isinstance(t, list):
        t = t[0] if t else None
    if t == "object" or "properties" in spec:
        return _object_for(spec)
    if t == "array":
        return [_value_for(spec.get("items") or {})]
    if t == "integer":
        return 0
    if t == "number":
        return 0.0
    if t == "boolean":
        return False
    if t == "null":
        return None
    return "reference"


def _object_for(spec):
    props = spec.get("properties") or {}
    required = spec.get("required") or []
    out = {}
    for key in required:
        out[key] = _value_for(props.get(key) or {})
    return out


# Fas 2.24d (red-team A5c) — the pipeline calls a node's INPUT-port handler and
# forwards ITS result as the matching OUTPUT envelope, where strict mode enforces
# the OUTPUT contract. So a reference payload for an input port must satisfy the
# port it will be VALIDATED as, not the port it was invoked on. 2.24 fixed this
# for the action selector only; the same hole survived in the generic path and
# an external reviewer hit it at egress. Derived per node from its own schemas —
# never a field list, never a node list.
_FORWARDED_AS = {"xi": "xo", "yi": "yo", "zi": "zo", "mi": "mo"}


def reference_payload(node_id, port):
    """Contract-valid payload for the port this result is ENFORCED as.

    Built from the node's OWN schema (required fields, typed defaults, first enum
    value), so it passes the same strict-contract enforcement as real output
    because it is built FROM the same schema. For an input port the pipeline
    forwards the result as the matching output envelope, so the OUTPUT contract
    is the one that must be satisfied; if the node declares no such schema we
    fall back to the invoked port's own. No extra keys are injected."""
    target = _FORWARDED_AS.get(port, port)
    spec = _schema_for(node_id, target) or _schema_for(node_id, port)
    return _object_for(spec)


def reference_envelope(node_id, port):
    """Typed handler return for an unimplemented slot in REFERENCE MODE.
    Marked, non-blocking, contract-valid - and honest: status is "reference",
    never a claimed domain result."""
    return {
        "node": node_id,
        "port": port,
        "ok": True,
        "status": "reference",
        "usable": True,
        "blocking": False,
        "reference": True,
        "payload": reference_payload(node_id, port),
        "detail": "REFERENCE MODE - contract-derived output, NOT domain logic (DOER_REFERENCE_MODE=1)",
    }


def _declared_reference_action():
    """A declared privileged action name, read from the runtime's OWN routing
    table (_ACTION_ROUTES, derived from the karta at generation). Factory truth
    about THIS agent - never invented, never domain logic.

    Fas 2.22: PREFER a GATED (non-auto) action so the reference harness actually
    exercises the CCAS gate end-to-end (an auto/tier_1 action needs no approval
    and would prove nothing about the gate). Falls back to the first action when
    the karta declares only auto actions."""
    try:
        from runtime.api_server import _ACTION_ROUTES, _ACTION_TIERS
    except Exception:
        try:
            from runtime.api_server import _ACTION_ROUTES
        except Exception:
            return None
        _ACTION_TIERS = {}
    names = sorted(_ACTION_ROUTES)
    for name in names:
        tier = str(_ACTION_TIERS.get(name, "")).lower()
        if tier not in ("", "auto", "tier_1"):
            return name  # a gated action — exercises the gate
    return names[0] if names else None


def reference_selection_envelope(node_id, port):
    """Reference envelope for the ACTION SELECTOR node: on XO it makes an
    HONEST typed selection of the first DECLARED privileged action, so the
    routing contract (H_ACTION_SELECTION) is exercised for real - the gate
    still decides via ccas_decide at its declared tier. The generator wires
    this variant ONLY for the karta's selector node."""
    env = reference_envelope(node_id, port)
    action = _declared_reference_action()
    # The pipeline calls the selector's handle_xi and forwards ITS payload as
    # the XO envelope, where strict mode enforces the XO contract (Fas 2.24 /
    # red-team A5). The selection payload must therefore be XO-contract-complete
    # regardless of the invoking port: build the full ActionProposal from the
    # node's OWN XO schema, then set the honest typed selection on it.
    if action and port in ("xi", "xo"):
        payload = _object_for(_schema_for(node_id, "xo"))
        payload["selected_action"] = action
        # Fas 3.2 — a GATED action must be tenant-scoped (ccas_decide fails closed
        # without it). The harness cannot assume the agent's authored contract
        # DECLARES tenant_id: a lenient payload sub-schema is legitimate policy,
        # and the reference path must exercise the gate for lenient and strict
        # agents alike. So the reference tenant is set explicitly here, marked as
        # reference like everything else this module emits — never inferred, and
        # never a real tenant name.
        payload["tenant_id"] = "reference-tenant"
        # Fas 3.3 - the execution ledger reserves on
        # (tenant_id, selected_action, idempotency_key) and refuses an action it
        # cannot identify. The reference harness must therefore carry a key, and
        # it must be UNIQUE PER RUN: a constant would make the first reference
        # run execute and every later one be suppressed as a duplicate, so the
        # harness would decay into a no-op the second time anyone ran it.
        #
        # Fas 3.19 - SET UNCONDITIONALLY, and the same for tenant_id above. Both
        # used to defer to whatever the contract-derived placeholder already
        # held, which was defensive in exactly the wrong direction: _object_for()
        # fills a declared string field with "reference", that is not empty, so
        # on any agent whose XO contract DECLARES idempotency_key the constant
        # "reference" won and the comment above became a description of the bug.
        # Found on the freshly generated HexaGate Email bundle: the reference
        # suite passed on the first run and failed on the second in the same
        # directory, with the gate reporting approved and the action reporting
        # executed=False. These two fields are harness identity, not domain data
        # - a placeholder is never a better value for them than the one this
        # module owns.
        payload["idempotency_key"] = _REFERENCE_IDEMPOTENCY_KEY
        env["payload"] = payload
    return env


def reference_apply(node_id, port, payload):
    """Side-effect-free REFERENCE execution for the privileged gate's _apply_
    seam. Only reachable AFTER ccas_decide approved the action at its declared
    tier - the gate itself is never bypassed."""
    return {
        "applied": True,
        "reference": True,
        "status": "reference_applied",
        "detail": "REFERENCE MODE - side-effect-free reference execution of the approved action",
        "action": payload,
    }
