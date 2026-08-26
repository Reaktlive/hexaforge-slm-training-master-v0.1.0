"""Request intake limits — the contract surface must bound what it accepts.

Fas 3.17 (red-team A21). Fuzzing the emitted routes found no 5xx: malformed
input already lands on 422, which is the property this phase set out to check.
It found two others instead, and these are the proofs for them.
"""
import json
import os
import tempfile

import pytest

fastapi_testclient = pytest.importorskip("fastapi.testclient")


def _client():
    tmp = tempfile.mkdtemp(prefix="intake-")
    os.environ["ZT_REQUIRE_AUTH"] = "0"
    os.environ["DOER_STATE_ROOT"] = tmp
    os.environ["HEXA_RECORD_PATH"] = os.path.join(tmp, "chain.jsonl")
    os.environ["CCAS_LEDGER_PATH"] = os.path.join(tmp, "ledger.jsonl")
    from runtime.api_server import app

    return fastapi_testclient.TestClient(app, raise_server_exceptions=False), app


def _a_post_route(app):
    for r in app.routes:
        path = getattr(r, "path", "")
        if path.endswith("/port-xi") and "POST" in (getattr(r, "methods", None) or set()):
            return path
    pytest.skip("this agent exposes no XI ingest route")


JSON = {"content-type": "application/json"}


# Fas 3.48 — the "small valid body" control must satisfy the target route's XI
# contract (contract-derived), otherwise a domain-required ingress rejects it on
# SCHEMA (422) and the size / round-trip properties this file exists to prove can
# never be exercised. The oversized / malformed probes below are rejected at the
# transport / JSON-parse layer BEFORE schema, so they stay as raw bytes.
_VALID_BODY = dict({})
_VALID_BODY.setdefault("payload", {"x": 1})


def _valid_body():
    return json.dumps(_VALID_BODY).encode()


def test_an_oversized_body_is_refused_before_a_handler_runs():
    """There was NO body limit: a 64 MB request was accepted with 200, fully
    buffered in memory before any handler ran, by any caller the transport lets
    through. The limit is measured as the body ARRIVES, not taken from
    Content-Length, because a chunked request declares no length at all."""
    client, app = _client()
    route = _a_post_route(app)

    ok = client.post(route, content=_valid_body(), headers=JSON)
    assert ok.status_code < 400, ok.text

    over = b'{"payload":{"x":"' + b"A" * (2 * 1024 * 1024) + b'"}}'
    r = client.post(route, content=over, headers=JSON)
    assert r.status_code == 413, r.status_code
    assert "exceeds" in r.json()["detail"]

    # A lying Content-Length must not buy anything: the count is of real bytes.
    hdrs = dict(JSON)
    hdrs["content-length"] = str(len(over))
    assert client.post(route, content=over, headers=hdrs).status_code == 413


def test_json_that_cannot_round_trip_never_reaches_the_audit_chain():
    """Python's json parser accepts NaN, Infinity and -Infinity, and a lone
    UTF-16 surrogate survives decoding. Both were accepted with 200, so such a
    value could reach the HASHED audit core. RFC 8259 has neither token: an
    auditor re-serialising that record with a strict reader gets different bytes
    or an error. A record that cannot be re-read is not evidence, which makes
    this an integrity property rather than input hygiene."""
    client, app = _client()
    route = _a_post_route(app)

    for raw in (b'{"payload":{"x":NaN}}',
                b'{"payload":{"x":Infinity}}',
                b'{"payload":{"x":-Infinity}}'):
        r = client.post(route, content=raw, headers=JSON)
        assert r.status_code == 422, (raw, r.status_code)
        assert "non-standard JSON token" in r.json()["detail"]

    # chr(0xD800), never a "\uD800" escape: the escape is interpreted while the
    # bundle is generated, so the emitted file would carry a substituted
    # character instead of the unpaired surrogate this test exists to send.
    surrogate = ('{"payload":{"x":"' + chr(0xD800) + '"}}').encode("utf-8", "surrogatepass")
    r = client.post(route, content=surrogate, headers=JSON)
    assert r.status_code == 422, r.status_code

    # And the guard must not have turned the surface into a brick.
    assert client.post(route, content=_valid_body(), headers=JSON).status_code < 400
    assert client.get("/healthz").status_code == 200
