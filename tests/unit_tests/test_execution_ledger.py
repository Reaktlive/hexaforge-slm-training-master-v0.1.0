"""Fas 3.5 — runtime proof that idempotency is ENFORCED, not documented.

Neutering reserve() must break these tests. That is the whole contract of this
file: it exists so the bundle's OWN suite notices if the reservation disappears.
"""
import threading

import pytest

from src.shared.execution_ledger import (
    ExecutionLedgerUnavailable,
    execution_key,
    reserve,
)

ACTION = {"tenant_id": "t-1", "selected_action": "quarantine_message",
          "idempotency_key": "IDEM-1", "target_asset": "m1"}


@pytest.fixture(autouse=True)
def _fresh_ledger(tmp_path, monkeypatch):
    monkeypatch.setenv("EXECUTION_LEDGER_PATH", str(tmp_path / "execution_ledger.jsonl"))


def test_a_replay_with_the_same_key_is_suppressed():
    first, _ = reserve(dict(ACTION))
    second, prior = reserve(dict(ACTION))
    assert first == "reserved"
    assert second == "duplicate", "a replayed idempotency key was granted a second execution"
    assert prior, "a duplicate must carry the prior outcome so the caller need not re-execute"


def test_a_different_tenant_is_a_different_execution():
    reserve(dict(ACTION))
    other, _ = reserve(dict(ACTION, tenant_id="t-2"))
    assert other == "reserved", "the reservation must be scoped per tenant"


def test_exactly_one_of_many_concurrent_workers_wins():
    won = []

    def worker():
        try:
            if reserve(dict(ACTION))[0] == "reserved":
                won.append(1)
        except Exception:  # noqa: BLE001 — a refusal is safe; a double claim is not
            pass

    threads = [threading.Thread(target=worker) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(won) == 1, "more than one worker claimed the same key: %d" % len(won)


def test_an_unidentifiable_action_is_refused():
    assert execution_key({"selected_action": "x"}) == ""
    with pytest.raises(ExecutionLedgerUnavailable):
        reserve({"selected_action": "x"})
