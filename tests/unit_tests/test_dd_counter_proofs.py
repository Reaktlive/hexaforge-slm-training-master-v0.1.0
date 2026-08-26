"""Fas 3.40 — the external DD counter-proofs, as tests the BUNDLE carries.

External DD, verbatim: "the bundle's own tests lack targeted regression tests"
for the findings that were fixed, and "the image-provenance tests mainly search
for text fragments in the workflow file. That explains why the 100/100 gate
passes while the attack works."

The point stands, and it is about WHERE the proof lives. The factory red-team
(tools/redteam) executes these attacks, but it does not ship with the bundle —
so a receiver re-running the delivered suite could not see them. Each fix now
has a test HERE, in the artifact, driving the real shipped code.

What each one pins, and the defect it would have caught:

  1. A closed contract refuses an undeclared field. An extra key used to pass
     strict enforcement, leave canonical_action_ref unchanged, and still reach
     the executor — so an approval valid for the clean action authorised the
     modified one.
  2. applied must be a real bool. "false" (the string) was truthy, so the
     durable ledger recorded "succeeded" while the same response said
     executed=false, and the reservation then suppressed the legitimate retry.
  3. A state store outside DOER_STATE_ROOT fails CLOSED. StatePathRefused is a
     RuntimeError; the ledger caught only OSError and the gate catches only
     ExecutionLedgerUnavailable, so a misconfiguration raised straight out of a
     privileged action as a 500 instead of holding.

Deliberately NOT covered here: the image-provenance circularity. It cannot be
closed from inside the bundle — the verifier and the manifest come from the same
checkout, so an attacker who can change one can change both. Closing it needs a
verifier with an external trust anchor. Writing a test that passes without that
would be the false assurance the DD is complaining about, so there is none.
"""
import json
import os
import pathlib
import tempfile

import pytest


# ---------------------------------------------------------------- 1. contract
_ROOT = pathlib.Path(__file__).resolve().parents[2]


def _shipped_contracts():
    """(node_id, port, closed) for every contract schema the bundle ships."""
    out = []
    for f in sorted(_ROOT.glob("contracts/*/*.schema.json")):
        doc = json.loads(f.read_text(encoding="utf-8"))
        sub = doc.get("schema") or {}
        out.append((f.parent.name, f.name.split(".")[0],
                    sub.get("additionalProperties") is False))
    return out


def _sample_for(model):
    """A minimal payload satisfying the model's required fields."""
    sample = {}
    for fname, field in model.model_fields.items():
        if not field.is_required():
            continue
        ann = str(field.annotation)
        if "float" in ann or "int" in ann:
            sample[fname] = 1
        elif "dict" in ann or "Dict" in ann:
            sample[fname] = {}
        elif "list" in ann or "List" in ann:
            sample[fname] = []
        else:
            sample[fname] = "x"
    return sample


def test_a_closed_schema_produces_a_closed_model():
    """Enumerate SCHEMAS, never models.

    The defect this pins read the closed flag off a property that did not exist
    on the contract object, so the condition was silently always false and NO
    model was closed. A check that enumerates MODELS cannot tell that state
    apart from a topology which legitimately declares nothing closed - both find
    zero. Driving it from the shipped schemas means "zero closed models" can
    only pass when zero schemas asked for one.

    It holds in both directions on purpose: a model must not be closed either
    when its schema is open, because narrowing an open payload to the declared
    fields silently deletes data the contract permits.
    """
    from src.shared.ceve_runtime import model_for, _model_forbids_extras
    shipped = _shipped_contracts()
    assert shipped, "no contract schemas shipped - this check has nothing to stand on"
    for node_id, port, closed in shipped:
        model = model_for(node_id, port)
        assert model is not None, "%s.%s ships a schema but no model" % (node_id, port)
        assert _model_forbids_extras(model) is closed, (
            "%s.%s: schema closed=%s, model closed=%s"
            % (node_id, port, closed, _model_forbids_extras(model)))


def test_a_closed_model_refuses_an_undeclared_field():
    """An extra key used to pass strict enforcement, leave canonical_action_ref
    unchanged, and still reach the executor - so an approval issued for the
    clean action authorised the modified one."""
    from src.shared.ceve_runtime import model_for
    closed = [(n, p) for n, p, c in _shipped_contracts() if c]
    if not closed:
        # Vacuous, and that is a MEASURED fact about this topology rather than
        # an unknown: the test above proved no shipped schema asks to be closed.
        pytest.skip("this topology closes no contract (proven above, not assumed)")
    for node_id, port in closed:
        model = model_for(node_id, port)
        clean = _sample_for(model)
        model(**clean)  # the clean form must still be accepted
        with pytest.raises(Exception):
            model(**dict(clean, executor_override="release_instead"))


def test_strict_enforcement_returns_the_validated_form():
    from src.shared.ceve_runtime import enforce_payload
    os.environ["DOER_STRICT_CONTRACTS"] = "1"
    # An OPEN contract must come back unchanged: validation may reject, never
    # silently discard fields the contract permits.
    payload = {"anything": "kept", "more": [1, 2]}
    out = enforce_payload("no_such_node", "xo", dict(payload))
    assert out == payload


# ------------------------------------------------------------------ 2. applied
@pytest.mark.parametrize(
    "result,expect_executed,expect_outcome",
    [
        ({"applied": True, "status": "ok"}, True, "succeeded"),
        ({"applied": False, "status": "not_implemented"}, False, "not_applied"),
        ({"applied": "false", "status": "not_implemented"}, False, "indeterminate"),
        ({"applied": "no"}, False, "indeterminate"),
        ({"applied": 1}, False, "indeterminate"),
        ({"status": "failed"}, False, "failed"),
        ("not a dict", False, "indeterminate"),
    ],
)
def test_applied_must_be_a_real_bool(result, expect_executed, expect_outcome):
    from src.shared.execution_ledger import classify_apply_result
    executed, outcome = classify_apply_result(result)
    assert executed is expect_executed
    assert outcome == expect_outcome


def test_executed_and_outcome_can_never_disagree():
    from src.shared.execution_ledger import classify_apply_result
    for result in ({"applied": "false"}, {"applied": 1}, {"applied": [1]},
                   {"applied": True}, {"applied": False}, {}, None):
        executed, outcome = classify_apply_result(result)
        assert (outcome == "succeeded") == executed


# --------------------------------------------------------------- 3. state path
def test_ledger_outside_state_root_fails_closed(monkeypatch):
    from src.shared import execution_ledger as EL
    root = tempfile.mkdtemp()
    outside = tempfile.mkdtemp()
    monkeypatch.setenv("DOER_STATE_ROOT", root)
    monkeypatch.setenv("EXECUTION_LEDGER_PATH", os.path.join(outside, "execution_ledger.jsonl"))
    action = {"selected_action": "a", "tenant_id": "t", "idempotency_key": "k", "target_asset": "m"}
    # Both entry points must raise the CONTROLLED error the gate handles —
    # never StatePathRefused, which bubbles out as a 500.
    with pytest.raises(EL.ExecutionLedgerUnavailable):
        EL.reserve(action)
    with pytest.raises(EL.ExecutionLedgerUnavailable):
        EL.complete(action, "succeeded", None)


def test_ledger_inside_state_root_works(monkeypatch):
    """Positive control: the refusal above must be the confinement, not breakage."""
    from src.shared import execution_ledger as EL
    root = tempfile.mkdtemp()
    monkeypatch.setenv("DOER_STATE_ROOT", root)
    monkeypatch.setenv("EXECUTION_LEDGER_PATH", os.path.join(root, "execution_ledger.jsonl"))
    action = {"selected_action": "a", "tenant_id": "t", "idempotency_key": "k2", "target_asset": "m"}
    state, _rec = EL.reserve(action)
    assert state == "reserved"
    EL.complete(action, "succeeded", None)
