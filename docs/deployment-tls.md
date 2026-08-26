# Deployment: TLS + Zero Trust transport auth (A3)

This bundle's transport posture is **fail-closed by construction**:

| Env | Default | Meaning |
| --- | --- | --- |
| `ZT_REQUIRE_AUTH` | **ON when unset** | Every non-health endpoint requires a verified bearer credential (401 without, 403 on missing scope). `/healthz` is always open for liveness probes. |
| `ZT_IDENTITIES` | empty | JSON map `{"<token>": {"identity": str, "scopes": [...], "expires_at": iso\|null}}`. Empty map + auth ON ⇒ every caller is rejected — provision identities before serving traffic. |
| `BIND_HOST` | `0.0.0.0` | Bind host for the guarded entrypoints (`python -m runtime.serve`, `python -m src.main`). |
| `INGEST_ALLOWED_SOURCES` | empty | Comma-separated source allowlist enforced by POST /api/events (Fas 2.11c). Empty/unset = allow-all (dev). Configured ⇒ an unknown `source` is rejected 403 fail-closed; caller-set duplicate `event_id`s are rejected 409 (process-wide dedup at the composed door). |

## The serve-guard

`ZT_REQUIRE_AUTH=0` is an **explicit dev opt-out, never an internet
posture**. Both entrypoints route through the single-source guard
(`src.shared.zt_auth.serve_guard`) — `python -m runtime.serve` (the
pipeline API; the Dockerfile CMD) and `python -m src.main` — and refuse to
start when auth is off and the bind host is not loopback:

```
REFUSED: ZT_REQUIRE_AUTH=0 (transport auth off) with non-loopback bind host '0.0.0.0'.
```

Dev quickstart (loopback only):

```bash
ZT_REQUIRE_AUTH=0 BIND_HOST=127.0.0.1 python -m runtime.serve
```

Production (fail-closed default — just provision identities):

```bash
export ZT_IDENTITIES='{"<token>":{"identity":"ops@example.com","scopes":["events:write","incidents:read","audit:read","autonomy:read"],"expires_at":null}}'
python -m runtime.serve
```

## TLS termination

The runtime serves plain HTTP; terminate TLS in front of it (reverse proxy /
ingress / service mesh). Rules the proxy MUST follow:

1. **Terminate TLS** and forward to the bundle over the pod/host-local network.
2. **Overwrite** the mTLS subject header on EVERY request when
   `ZT_MTLS_ENABLED=1` — a client must never be able to inject
   `ZT_MTLS_SUBJECT_HEADER` (default `x-client-cert-subject`) itself.
   The proxy verifies the client certificate and passes the subject DN;
   `zt_auth.py` maps it via `ZT_MTLS_IDENTITIES`.
3. Keep `/healthz` reachable for orchestrator probes (it is
   unauthenticated by design — it exposes liveness only, no data).
4. When TLS is terminated at a trusted proxy and the app cannot observe the
   transport, set `EGRESS_CHANNEL_ENCRYPTED=1` so the egress-policy
   encryption gate (T-04-025) reflects the real channel property.

## Runtime-terminated TLS and mutual TLS (B1 — fleet transport)

Since the closed fleet loop, the runtime can terminate TLS ITSELF — so two
fleet containers speak mutually-authenticated TLS with no proxy in between:

| env | effect |
|---|---|
| `TLS_CERT_FILE` + `TLS_KEY_FILE` | serve https (both must be set; a half pair refuses to start) |
| `TLS_CLIENT_CA_FILE` | when set, a client certificate signed by this CA is REQUIRED at the handshake (mutual TLS) — an unauthenticated TLS client never reaches a route |

Both entrypoints (`runtime.serve`, the Dockerfile CMD, and `python -m src.main`)
apply the same posture (`runtime.serve.tls_kwargs`). Zero-Trust bearer
identities (`ZT_IDENTITIES`) still apply on top: mTLS authenticates the
CHANNEL, the bearer identifies the CALLER, and the Ed25519 FleetSignal
signature authenticates the fleet MEMBER — three layers, none of them
optional in the fleet posture. The member side pins the coordinator's CA
(`FLEET_TLS_CA_FILE`) and presents its client certificate
(`FLEET_TLS_CLIENT_CERT_FILE`/`_KEY_FILE`); see docs/fleet-transport.md.

## Composition with CCAS

ZT gates the TRANSPORT (who is on the wire); CCAS gates ACTIONS
(approve/deny tiers) downstream, unchanged. A request passes ZT first; the
authenticated identity is bound into the audit chain so state-changing calls
are attributable to a verified caller.

## Cohort HMAC secret (MO boundary) — production lifecycle

Tenant k-anonymity counts DISTINCT tenants via
`tenant_cohort_key = HMAC-SHA256(secret, tenant_id)`. The pseudonyms are
only stable while the secret is stable — **a new secret makes the same
tenant count as a new tenant against older records, breaking k-count
continuity across restarts**.

Production requirement (pick ONE):

1. `COHORT_HMAC_SECRET` provisioned from your secret manager (preferred —
   consistent across replicas by construction), or
2. the auto-generated key file (created once, mode 0600, next to the store)
   placed on the SAME durable volume as the cohort store: set
   `COHORT_STORE_PATH` to a persistent mount so store + key survive
   restarts together.

An ephemeral container filesystem with neither is a DEV-ONLY posture: the
cohort itself also disappears on restart, so k-continuity is moot — but
never run production cohort accumulation that way.
