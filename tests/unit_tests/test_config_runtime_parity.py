"""Config/runtime parity — the barrier timeout knob is actually read.

Fas 2.13d (external DD): BARRIER_TIMEOUT_MS was hardcoded in the runtime while
.env.example documented a different value. This proves the runtime constant is
read from the environment (skips on a serial karta that ships no barrier).
"""
import importlib
import os

import pytest


def _load():
    import src.shared.orchestrator as o
    importlib.reload(o)
    return o


def test_barrier_timeout_is_read_from_env():
    m = _load()
    if not hasattr(m, "BARRIER_TIMEOUT_MS"):
        pytest.skip("serial karta — no barrier in this bundle")
    os.environ.pop("BARRIER_TIMEOUT_MS", None)
    default = _load().BARRIER_TIMEOUT_MS
    os.environ["BARRIER_TIMEOUT_MS"] = "77000"
    try:
        assert _load().BARRIER_TIMEOUT_MS == 77000, "BARRIER_TIMEOUT_MS must be read from the environment"
    finally:
        os.environ.pop("BARRIER_TIMEOUT_MS", None)
    assert _load().BARRIER_TIMEOUT_MS == default, "default must be stable when env is unset"
