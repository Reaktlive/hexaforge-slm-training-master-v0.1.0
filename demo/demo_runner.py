"""Drive synthetic events through hexaforge_slm_training_master_intake_octa.XI at ~50 events/sec.

Loads demo/synthetic_data/events.jsonl, posts to the FastAPI endpoint, writes
demo/demo_dashboard/results.json with simple aggregates the dashboard reads.
"""
import json
import os
import time
from urllib.request import Request, urlopen

# Fas 2.10e (extern DD på B9, punkt 5): demon kör HELA pipelinen
# (/api/events = run_pipeline), inte bara ingressnoden. Med obundna
# stubbar visar den ÄRLIGT degraded_blocking_stub + hold — det är
# fail-closed-arkitekturens bevis, inte ett fel.
URL = os.environ.get("DOER_URL", "http://localhost:8000/api/events")
HERE = os.path.dirname(os.path.abspath(__file__))
EVENTS_PATH = os.path.join(HERE, "synthetic_data", "events.jsonl")
RESULTS_PATH = os.path.join(HERE, "demo_dashboard", "results.json")
RATE = 50            # events/sec — from input_model.volume.events_per_sec_avg
TICK = 1.0 / max(1, RATE) # seconds between sends
# Fas 2.9c: ZT-auth är PÅ även i demon (fail-closed, Fas 2.5). Tokenen
# matchar demo-identiteten i demo/docker-compose.demo.yml — lokal
# demokonfig, aldrig en produktionscredential.
TOKEN = os.environ.get("DEMO_TOKEN", "demo-token")


def main():
    events_processed = 0
    incidents_triaged = 0
    escalated = 0
    held_fail_closed = 0
    mo_signals = 0
    statuses = {}
    dispositions = {}
    blocking_capabilities = set()
    cohort_last = None
    latencies = []
    if not os.path.exists(EVENTS_PATH):
        print(f"missing {EVENTS_PATH}; nothing to do"); return
    with open(EVENTS_PATH) as f:
        for line in f:
            line = line.strip()
            if not line: continue
            evt = json.loads(line)
            # PG-1 — baseline contract requires 'source'; synthetic jsonl from
            # placeholder generators may lack it.
            evt.setdefault("source", "demo_runner")
            t0 = time.time()
            try:
                req = Request(URL, data=json.dumps(evt).encode(),
                              headers={"content-type": "application/json",
                                       "authorization": f"Bearer {TOKEN}"})
                with urlopen(req, timeout=30) as r:
                    body = json.loads(r.read() or b"{}")
                    events_processed += 1
                    # Fas 2.10e — räkna ur AGENTENS RESPONS, aldrig ur
                    # input-flaggor (dashboarden mätte förr syntetdatan,
                    # inte agenten).
                    status = str(body.get("status", ""))
                    disposition = str(body.get("disposition", ""))
                    statuses[status] = statuses.get(status, 0) + 1
                    dispositions[disposition] = dispositions.get(disposition, 0) + 1
                    if status == "ok":
                        incidents_triaged += 1
                    if disposition == "hold" or status.startswith("degraded"):
                        held_fail_closed += 1
                    bc = body.get("blocking_capabilities")
                    if isinstance(bc, list):
                        for cap in bc:
                            blocking_capabilities.add(str(cap))
                    cohort = body.get("cohort")
                    if isinstance(cohort, dict):
                        mo_signals += 1
                        cohort_last = cohort
                    if body.get("verdict") in ("escalate", "escalated") or disposition == "escalate":
                        escalated += 1
            except Exception as e:
                print("err", e)
            latencies.append((time.time() - t0) * 1000)
            time.sleep(TICK)
    avg_lat = sum(latencies) / len(latencies) if latencies else 0
    out = {
        "events_processed": events_processed,
        "incidents_triaged": incidents_triaged,
        "escalated_to_soc": escalated,
        "held_fail_closed": held_fail_closed,
        "statuses": statuses,
        "dispositions": dispositions,
        "blocking_capabilities": sorted(blocking_capabilities),
        "mo_signals": mo_signals,
        "cohort": cohort_last,
        "avg_latency_ms": avg_lat,
        "rate_target": RATE,
        "profile": "request-response-v1",
    }
    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
