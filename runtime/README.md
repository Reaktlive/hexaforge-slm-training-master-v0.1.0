# Self-hosted Admin UI

Zero-dependency Python orchestrator that serves a JSON API + Admin UI on port 8080.

## Quick start

```bash
# Option A: docker compose (recommended — runs alongside the FastAPI doer)
docker compose -f deploy/docker-compose.yml up admin-ui

# Option B: bare Python 3.10+
cd runtime
KARTA_PATH=../karta.yaml ADMIN_UI_DIR=./admin-ui python3 orchestrator.py
```

Then open http://localhost:8080/ — Admin UI lands on the Topology view.

## Endpoints

- GET  /api/bundle    — bundle metadata
- GET  /api/topology  — fleet nodes + edges
- GET  /api/events    — recent ingested events
- GET  /api/audit     — SHA-256 chained audit log (local demo chain — NOT tamper-proof; see below)
- GET  /api/config    — config flags
- PUT  /api/config    — toggle flags (audited)
- GET  /api/health    — operational metrics
- POST /api/test-run  — run a synthetic event through the topology

## Audit honesty

AUDIT HONESTY: local demo chain — hash-linked but NOT tamper-proof
(in-memory, volatile — this admin server's own chain). Production upgrade
path: Postgres-backed chain with external anchoring (HexaRecord).
