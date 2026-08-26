"""Orchestrator — barrier sync + the single guarded app accessor.

Fas 2.13a (P0 — external DD found an auth bypass): before this round build_app()
assembled its OWN FastAPI app by mounting every node's raw port routers
(src/nodes/*/port_*.py) with NO transport auth, and deploy/start.sh served it
via 'python -m src.main' — 214 unauthenticated routes, including the YO
side-effect ports. The pipeline never uses those HTTP routes (nodes run
in-process via 'await node.handle_xi(...)'), nothing in the bundle consumes
them, and they ARE the bypass. Per Option 1 (one locked door, minimal surface)
build_app() now returns the SINGLE GUARDED app — runtime/api_server.py, where
every route carries Depends(zt_guard) — so the deploy entrypoint and the
Dockerfile CMD (runtime.serve) converge on the same authenticated app. The raw
per-node routers stay on disk (they define the node port handlers the H1 port-
existence doctrine validates) but are mounted by NO served entrypoint. The
import is deferred inside build_app() to avoid a load-time cycle (api_server
imports run_branches from this module at its own module top).
"""
import asyncio
import os
from fastapi import FastAPI


def build_app() -> FastAPI:
    """Return the one guarded application (runtime/api_server.py).

    Single source: the deploy entrypoint (src/main.py -> build_app()) and the
    Dockerfile CMD (runtime.serve -> runtime.api_server:app) serve the SAME
    authenticated app object — every route requires a verified caller
    (Depends(zt_guard)); only /healthz is open for liveness probes."""
    from runtime.api_server import app  # deferred: avoids load-time import cycle
    return app


# ---- Barrier sync for parallel branches converging on the join node ----
# EXPECTED_BRANCHES is derived from the karta edge topology at generation
# time: the largest number of DISTINCT XO fan-out targets from a single node
# when that fan-out is >= 2, else 0 (serial map). The exact same derivation
# is used by the Purity Gate detector (deriveParallelBranches in
# bundlePurityGate.ts) and by tests/unit_tests/test_topology_parity.py in
# this bundle — the three MUST stay semantically aligned.
EXPECTED_BRANCHES = 17
# Fas 2.13d (external DD) — config/runtime parity: this is READ FROM THE
# ENVIRONMENT (it was a hardcoded 5000 while .env.example documented 120000 — a
# generated knob that looked active but wasn't). The default now matches the
# documented .env.example value; BARRIER_TIMEOUT_MS=... in the environment
# actually changes the barrier wait.
BARRIER_TIMEOUT_MS = int(os.environ.get("BARRIER_TIMEOUT_MS", "120000"))

class Barrier:
    def __init__(self, expected: int):
        self.expected = expected
        self.received: list = []
        self._event = asyncio.Event()

    async def submit(self, branch: str, payload: dict, timeout_ms: int = BARRIER_TIMEOUT_MS):
        self.received.append({"branch": branch, "payload": payload})
        if len(self.received) >= self.expected:
            self._event.set()
        try:
            await asyncio.wait_for(self._event.wait(), timeout=timeout_ms / 1000)
        except asyncio.TimeoutError:
            return {"partial": True, "received": self.received}
        return {"partial": False, "received": self.received}


async def run_branches(*branch_coros):
    """Run the karta's parallel branches concurrently with a barrier.

    Node handlers are async coroutines, so concurrency uses asyncio.gather
    (no thread pool needed). The asyncio.wait_for wrapper is the barrier:
    ALL branches must complete before the join node may execute; a stalled
    branch raises asyncio.TimeoutError after BARRIER_TIMEOUT_MS so callers
    can emit an honest partial result instead of hanging forever.
    """
    return await asyncio.wait_for(
        asyncio.gather(*branch_coros),
        timeout=BARRIER_TIMEOUT_MS / 1000,
    )
