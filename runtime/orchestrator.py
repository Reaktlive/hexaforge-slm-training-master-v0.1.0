"""HexaBox Runtime Orchestrator.

Zero-dependency Python server (stdlib only) that:
  1. Loads the fleet/agent karta from /app/karta.yaml (single-agent) or
     /app/fleet.yaml (Team Fleet).
  2. Serves the embedded Admin UI on / (and /admin/*) from /app/admin-ui/.
  3. Exposes a JSON API on /api/* for the UI to consume.
  4. Maintains an in-memory SHA-256 audit chain that survives across requests
     in this process (production deployments persist to disk; this stub is
     volatile but the structure is correct).

AUDIT HONESTY: local demo chain — hash-linked but NOT tamper-proof
(in-memory, volatile — this admin server's own chain). Production upgrade path: Postgres-backed chain with
external anchoring (HexaRecord).

The Admin UI is fully static (single HTML file, no build step, no CDN deps)
so it works in air-gapped environments. The API surface is documented inline.

Run with:   python orchestrator.py            (defaults to port 8080)
Or via:     docker compose up                 (uses the bundled Dockerfile)
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import threading
import time
import uuid
from collections import deque
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Optional
from urllib.parse import urlparse, parse_qs

PORT = int(os.environ.get("PORT", "8080"))
# Fas 2.13b — admin surface hardening (external DD). The admin server binds
# LOOPBACK by default; a deployer must explicitly opt into a routable bind AND
# front it with auth. Mutations are FAIL-CLOSED behind ADMIN_API_TOKEN (unset =>
# read-only). CORS is locked down unless an explicit origin is set (the UI is
# same-origin and needs none) — no wildcard.
ADMIN_BIND_HOST = os.environ.get("ADMIN_BIND_HOST", "127.0.0.1")
ADMIN_API_TOKEN = os.environ.get("ADMIN_API_TOKEN", "")
ADMIN_CORS_ORIGIN = os.environ.get("ADMIN_CORS_ORIGIN", "")
FLEET_ID = os.environ.get("FLEET_ID", "unknown")
AGENT_ID = os.environ.get("AGENT_ID", "unknown")
RUNTIME_LOCATION = os.environ.get("RUNTIME_LOCATION", "studio_edge")
STATIC_DIR = os.environ.get("ADMIN_UI_DIR", "/app/admin-ui")
KARTA_PATH = os.environ.get("KARTA_PATH", "/app/karta.yaml")
FLEET_PATH = os.environ.get("FLEET_PATH", "/app/fleet.yaml")
CONTRACTS_PATH = os.environ.get("CONTRACTS_PATH", "/app/contracts/all_contracts.json")

# ---------------------------------------------------------------------------
# In-memory state — would be backed by a real store in production
# ---------------------------------------------------------------------------

_STATE_LOCK = threading.Lock()

class RuntimeState:
    def __init__(self) -> None:
        self.bundle_meta: dict[str, Any] = {
            "fleet_id": FLEET_ID,
            "agent_id": AGENT_ID,
            "fleet_name": None,
            "agent_name": None,
            "runtime_location": RUNTIME_LOCATION,
            "session_id": str(uuid.uuid4()),
            "shadow_mode": True,  # default ON for safe rollout
        }
        self.topology: dict[str, Any] = {"nodes": [], "edges": []}
        self.config: dict[str, Any] = {
            "shadow_mode": True,
            "federation_enabled": False,
            "k_minimum": 5,
        }
        # Audit chain — deque-backed, capped to last 1000 events.
        self.audit: deque[dict[str, Any]] = deque(maxlen=1000)
        self._audit_seq = 0
        self._prev_hash = "0" * 64
        # Event throughput tracking — last 60 minutes of buckets.
        self.events: deque[dict[str, Any]] = deque(maxlen=500)
        self.health: dict[str, Any] = {
            "events_per_min": 0,
            "p95_latency_ms": 0,
            "doctrine_score": 100,
            "error_rate": 0.0,
            "auto_resolve_pct": 0,
            "auto_respond_pct": 0,
            "escalate_pct": 100,
            "k_minimum": 5,
            "cohort_signals_today": 0,
        }

    def emit_audit(self, event_type: str, payload: Optional[dict[str, Any]] = None, node_id: Optional[str] = None) -> str:
        """Append a SHA-256 chained audit event. Returns the new event's hash."""
        with _STATE_LOCK:
            self._audit_seq += 1
            ts = datetime.now(timezone.utc).isoformat()
            base = {
                "sequence_num": self._audit_seq,
                "event_type": event_type,
                "ts": ts,
                "node_id": node_id,
                "payload": payload or {},
                "prev_hash": self._prev_hash,
            }
            digest = hashlib.sha256(json.dumps(base, sort_keys=True).encode()).hexdigest()
            entry = {**base, "this_hash": digest}
            self.audit.appendleft(entry)
            self._prev_hash = digest
            return digest


STATE = RuntimeState()


# ---------------------------------------------------------------------------
# Karta / fleet loading
# ---------------------------------------------------------------------------

def _parse_minimal_yaml(text: str) -> dict[str, Any]:
    """Very small YAML subset parser — enough to read the karta files we
    generate from Doable. Not a general YAML parser."""
    out: dict[str, Any] = {}
    lines = text.splitlines()
    current_section: Optional[str] = None
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    cur_node: Optional[dict[str, Any]] = None
    in_topology = False
    for raw in lines:
        line = raw.rstrip()
        if not line or line.strip().startswith("#"):
            continue
        if not line.startswith(" "):
            # Top-level key
            if ":" in line:
                k, _, v = line.partition(":")
                key = k.strip(); val = v.strip()
                if key == "topology":
                    in_topology = True
                    current_section = None
                    out["topology"] = {"nodes": nodes, "edges": edges}
                    continue
                if val:
                    out[key] = val.strip('"')
                else:
                    out[key] = {}
                    current_section = key
                in_topology = key == "topology" or in_topology
            continue
        if in_topology:
            stripped = line.lstrip()
            indent = len(line) - len(stripped)
            if stripped.startswith("nodes:"):
                cur_section_name = "nodes"
                continue
            if stripped.startswith("edges:"):
                cur_section_name = "edges"
                continue
            if stripped.startswith("- id:") and indent <= 4:
                cur_node = {"id": stripped.split("id:", 1)[1].strip()}
                nodes.append(cur_node)
                continue
            if stripped.startswith("- ") and "from:" in stripped and "to:" in stripped:
                # inline { from: x.XO, to: y.XI }
                m = re.search(r"from:\s*([\w\.]+)\s*,\s*to:\s*([\w\.]+)", stripped)
                if m:
                    src, tgt = m.group(1), m.group(2)
                    src_node = src.split(".")[0]; tgt_node = tgt.split(".")[0]
                    edges.append({"source_node": src_node, "target_node": tgt_node})
                continue
            if cur_node and ":" in stripped:
                k, _, v = stripped.partition(":")
                key = k.strip(); val = v.strip()
                if key in ("type", "role", "extends_template"):
                    cur_node[key] = val.strip('"')
    return out


def load_topology() -> None:
    """Load karta.yaml (single-agent) or fleet.yaml (Team Fleet) into STATE.topology."""
    karta_path = KARTA_PATH if os.path.exists(KARTA_PATH) else (FLEET_PATH if os.path.exists(FLEET_PATH) else None)
    if not karta_path:
        STATE.emit_audit("topology_load_failed", {"reason": "no karta or fleet yaml found"})
        return
    try:
        with open(karta_path, "r", encoding="utf-8") as f:
            raw = f.read()
        parsed = _parse_minimal_yaml(raw)
        nodes = parsed.get("topology", {}).get("nodes", [])
        edges = parsed.get("topology", {}).get("edges", [])
        # Enrich with placeholder runtime stats
        for n in nodes:
            n.setdefault("role", _infer_role_from_id(n.get("id", "")))
            n.setdefault("ports", [{"id": p} for p in ["XI", "XO", "MI", "MO"]])
            n.setdefault("slm_binding", "gemini-2.5-flash")
            n.setdefault("confidence_threshold", 0.75)
            n.setdefault("throughput_per_min", 0.0)
            n.setdefault("decisions_last_hour", 0)
            n.setdefault("avg_confidence", 0.0)
            n.setdefault("escalations_last_hour", 0)
        STATE.topology = {"nodes": nodes, "edges": edges}
        STATE.bundle_meta["fleet_name"] = parsed.get("fleet_name") or parsed.get("name")
        STATE.bundle_meta["agent_name"] = parsed.get("name")
        STATE.emit_audit("topology_loaded", {"node_count": len(nodes), "edge_count": len(edges)})
    except Exception as e:
        STATE.emit_audit("topology_load_failed", {"reason": str(e)[:200]})


def _infer_role_from_id(node_id: str) -> str:
    n = node_id.lower()
    if "intake" in n or "ingress" in n: return "ingress"
    if "egress" in n: return "egress"
    if any(k in n for k in ["hub", "macro", "cohort", "escalation"]): return "coordinator"
    if any(k in n for k in ["gate", "validator", "safety"]): return "governance"
    if any(k in n for k in ["competency", "hexalearn", "learning", "state_store", "classifier", "decision", "enrichment", "anomaly", "signature", "behavior", "triager"]): return "hexalearn"
    return "core"


# ---------------------------------------------------------------------------
# HTTP handler
# ---------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:  # quieter logs
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")

    # ----- helpers -----
    def _json(self, status: int, body: Any) -> None:
        data = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        if ADMIN_CORS_ORIGIN:
            self.send_header("Access-Control-Allow-Origin", ADMIN_CORS_ORIGIN)
        self.end_headers()
        self.wfile.write(data)

    def _read_body(self) -> Optional[dict[str, Any]]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0: return None
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            return None

    def _require_admin_token(self) -> bool:
        # Fas 2.13b — fail-closed guard for mutating endpoints. With no
        # ADMIN_API_TOKEN set the default package is READ-ONLY (no mutation is
        # possible); when set, a matching Bearer token is required.
        if not ADMIN_API_TOKEN:
            self._json(403, {"error": "admin_mutations_disabled",
                             "detail": "set ADMIN_API_TOKEN to enable mutations; default package is read-only"})
            return False
        if self.headers.get("Authorization", "") != "Bearer " + ADMIN_API_TOKEN:
            self._json(403, {"error": "forbidden", "detail": "missing or invalid admin bearer token"})
            return False
        return True

    # ----- routing -----
    def do_OPTIONS(self) -> None:
        self.send_response(204)
        if ADMIN_CORS_ORIGIN:
            self.send_header("Access-Control-Allow-Origin", ADMIN_CORS_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/" or path == "/admin" or path == "/admin/":
            return self._serve_static("index.html")
        if path.startswith("/admin/"):
            return self._serve_static(path[len("/admin/"):])
        if path == "/api/bundle":
            return self._json(200, STATE.bundle_meta)
        if path == "/api/topology":
            return self._json(200, STATE.topology)
        if path == "/api/events":
            return self._json(200, {"events": list(STATE.events)[:50]})
        if path == "/api/audit":
            return self._json(200, {"events": list(STATE.audit)[:50]})
        if path == "/api/config":
            return self._json(200, STATE.config)
        if path == "/api/health":
            return self._json(200, STATE.health)
        if path == "/healthz":
            return self._json(200, {"ok": True})
        return self._json(404, {"error": "not_found", "path": path})

    def do_PUT(self) -> None:
        if not self._require_admin_token():
            return
        path = urlparse(self.path).path
        if path == "/api/config":
            body = self._read_body() or {}
            with _STATE_LOCK:
                STATE.config.update(body)
                if "shadow_mode" in body:
                    STATE.bundle_meta["shadow_mode"] = bool(body["shadow_mode"])
            STATE.emit_audit("config_updated", body)
            return self._json(200, STATE.config)
        # D19 — per-node binding edit: PUT /api/config/nodes/<node_id>
        if path.startswith("/api/config/nodes/"):
            node_id = path[len("/api/config/nodes/"):]
            if not node_id:
                return self._json(400, {"error": "missing_node_id"})
            body = self._read_body() or {}
            slm = body.get("slm_binding")
            threshold = body.get("confidence_threshold")
            if slm is None and threshold is None:
                return self._json(400, {"error": "no_changes"})
            if threshold is not None:
                try:
                    threshold = float(threshold)
                    if threshold < 0.5 or threshold > 0.95:
                        return self._json(400, {"error": "threshold_out_of_range"})
                except (TypeError, ValueError):
                    return self._json(400, {"error": "invalid_threshold"})
            updated = False
            with _STATE_LOCK:
                for n in STATE.topology.get("nodes", []):
                    if n.get("id") == node_id:
                        if slm is not None: n["slm_binding"] = str(slm)
                        if threshold is not None: n["confidence_threshold"] = threshold
                        updated = True
                        break
            if not updated:
                return self._json(404, {"error": "node_not_found", "node_id": node_id})
            STATE.emit_audit("node_binding_updated", {
                "node_id": node_id,
                "slm_binding": slm,
                "confidence_threshold": threshold,
            }, node_id=node_id)
            return self._json(200, {
                "node_id": node_id,
                "slm_binding": slm,
                "confidence_threshold": threshold,
            })
        return self._json(404, {"error": "not_found", "path": path})

    def do_POST(self) -> None:
        if not self._require_admin_token():
            return
        path = urlparse(self.path).path
        if path == "/api/test-run":
            body = self._read_body() or {}
            event = body.get("event") or {}
            return self._handle_test_run(event)
        return self._json(404, {"error": "not_found", "path": path})

    def _handle_test_run(self, event: dict[str, Any]) -> None:
        """Run a synthetic event through the topology, emit audit, return trace.

        This is the stub implementation — production wires through dispatchLlm
        on each AI-bearing node. For UI demo purposes we emit a plausible
        trace so the operator can see the mechanism even before LLMs are wired.
        """
        nodes = STATE.topology.get("nodes", [])
        trace = []
        start = time.time()
        for n in nodes:
            if n.get("role") in ("ingress", "egress"):
                trace.append({
                    "node_id": n["id"],
                    "model": None,
                    "duration_ms": 2,
                    "reasoning": f"{n['role']} bookend — passthrough",
                })
                continue
            trace.append({
                "node_id": n["id"],
                "model": n.get("slm_binding", "gemini-2.5-flash"),
                "duration_ms": 85 + (len(trace) * 12),
                "reasoning": f"verdict via {n.get('slm_binding', 'default')} — confidence 0.82",
            })
        total_ms = int((time.time() - start) * 1000)
        verdict = "true_positive" if event.get("severity") in ("high", "critical") else "false_positive"
        confidence = 0.91 if verdict == "true_positive" else 0.78
        audit_hash = STATE.emit_audit("test_run_completed", {
            "event_id": event.get("event_id"),
            "verdict": verdict,
            "confidence": confidence,
            "total_ms": total_ms,
        })
        # Also push to recent events stream for visibility in the Events tab.
        STATE.events.appendleft({
            "ts": datetime.now(timezone.utc).isoformat(),
            "source": event.get("source", "test"),
            "severity": event.get("severity", "medium"),
            "verdict": verdict,
            "confidence": confidence,
            "action": "escalate" if confidence < 0.85 else "auto_resolve",
            "audit_hash": audit_hash,
        })
        return self._json(200, {
            "trace": trace,
            "verdict": verdict,
            "confidence": confidence,
            "audit_hash": audit_hash,
            "total_ms": total_ms,
        })

    def _serve_static(self, rel_path: str) -> None:
        rel_path = rel_path or "index.html"
        # Prevent directory traversal.
        if ".." in rel_path or rel_path.startswith("/"):
            return self._json(403, {"error": "forbidden"})
        full = os.path.join(STATIC_DIR, rel_path)
        if not os.path.isfile(full):
            return self._json(404, {"error": "not_found", "path": rel_path})
        ctype = "text/html; charset=utf-8" if rel_path.endswith(".html") else \
                "application/javascript" if rel_path.endswith(".js") else \
                "text/css" if rel_path.endswith(".css") else \
                "application/json" if rel_path.endswith(".json") else "application/octet-stream"
        try:
            with open(full, "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self._json(500, {"error": "static_read_failed", "message": str(e)})


# ---------------------------------------------------------------------------
# Boot
# ---------------------------------------------------------------------------

def main() -> None:
    print(f"[orchestrator] fleet={FLEET_ID} agent={AGENT_ID} runtime={RUNTIME_LOCATION}")
    print(f"[orchestrator] loading topology from {KARTA_PATH} or {FLEET_PATH}")
    load_topology()
    STATE.emit_audit("session_started", {
        "session_id": STATE.bundle_meta["session_id"],
        "runtime_location": RUNTIME_LOCATION,
    })
    if not os.path.isdir(STATIC_DIR):
        print(f"[orchestrator] WARNING: admin-ui dir not found at {STATIC_DIR} — Admin UI will 404")
    print(f"[orchestrator] starting HTTP server on {ADMIN_BIND_HOST}:{PORT}")
    print(f"[orchestrator] Admin UI: http://localhost:{PORT}/ (bind {ADMIN_BIND_HOST}; mutations {'ENABLED' if ADMIN_API_TOKEN else 'read-only'})")
    httpd = ThreadingHTTPServer((ADMIN_BIND_HOST, PORT), Handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        STATE.emit_audit("session_completed", {})
        print("\n[orchestrator] shutting down")


if __name__ == "__main__":
    main()
