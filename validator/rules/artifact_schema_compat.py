"""H4 Schema Compatibility — universal. target.required must be subset of source.properties.

blocker2 (envelope/payload split): a port schema may nest a per-node PAYLOAD
sub-schema under properties.payload. When it does, cross-edge DOMAIN alignment
lives there, so this gate ALSO recurses — target payload.required must be a
subset of source payload.properties — otherwise moving domain fields under the
payload sub-schema would silently stop being checked."""
import json, pathlib
GATE_ID = "ARTIFACT_SCHEMA_COMPAT"; GATE_NAME = "Schema Compatibility"; GATE_KIND = "hard"
GATE_CATEGORY = "artifact"
def applies(karta): return True
def _schemas(root, node_id):
    # Fas 3.16 (gate-mutation matrix, A20) — None means "no contract file at
    # all", which is a VIOLATION for a wired edge. Returning {} here (the old
    # behaviour) made an absent contract indistinguishable from a contract that
    # requires nothing, so deleting every schemas.json left this gate reporting
    # PASS over 28 edges. The karta twin (H12) has always called that out; the
    # artifact twin had drifted away from it.
    f = root / "src" / "nodes" / node_id / "schemas.json"
    return json.loads(f.read_text()) if f.exists() else None
def _payload_subschema(port_schema):
    # The per-node payload sub-schema, when the port contract nests one under
    # properties.payload as an object schema. Absent / non-object => {} (lenient).
    pay = (port_schema.get("properties") or {}).get("payload")
    return pay if isinstance(pay, dict) else {}
def evaluate(karta, root: pathlib.Path):
    violations = []
    for e in karta.get("topology", {}).get("edges", []):
        sa, sp = e["source_agent"], e["source_port"].lower()
        ta, tp = e["target_agent"], e["target_port"].lower()
        s_all = _schemas(root, sa); t_all = _schemas(root, ta)
        absent = False
        for agent, port, contracts in ((sa, sp, s_all), (ta, tp, t_all)):
            if contracts is None:
                violations.append({"edge": f"{sa}.{sp}->{ta}.{tp}", "node": agent,
                                   "fix_hint": f"{agent} ships no src/nodes/{agent}/schemas.json; every wired port must carry a contract."})
                absent = True
            elif port not in contracts:
                violations.append({"edge": f"{sa}.{sp}->{ta}.{tp}", "node": agent, "port": port,
                                   "fix_hint": f"{agent}.{port} is wired but declares no contract."})
                absent = True
        if absent:
            continue
        s = s_all.get(sp, {}); t = t_all.get(tp, {})
        s_props = set((s.get("properties") or {}).keys())
        for r in t.get("required", []) or []:
            if r not in s_props:
                violations.append({"edge": f"{sa}.{sp}->{ta}.{tp}", "missing_required": r, "fix_hint": f"Source must produce '{r}'."})
        # Recurse into the payload sub-schema so domain alignment is still checked
        # after the envelope/payload split (target payload.required ⊆ source payload.properties).
        s_pay = _payload_subschema(s); t_pay = _payload_subschema(t)
        s_pay_props = set((s_pay.get("properties") or {}).keys())
        for r in t_pay.get("required", []) or []:
            if r not in s_pay_props:
                violations.append({"edge": f"{sa}.{sp}->{ta}.{tp}", "missing_required": f"payload.{r}", "fix_hint": f"Source payload must produce '{r}'."})
    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": f"Checked {len(karta.get('topology',{}).get('edges',[]))} edges (envelope + payload sub-schema)."}
