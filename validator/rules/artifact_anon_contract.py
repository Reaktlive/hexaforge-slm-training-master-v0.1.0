"""H3 Anonymization Contract — applies if any node has Mo."""
import json, pathlib
GATE_ID = "ARTIFACT_ANON_CONTRACT"; GATE_NAME = "Anonymization Contract"; GATE_KIND = "hard"
GATE_CATEGORY = "artifact"
def applies(karta):
    return any("MO" in n.get("ports", []) for n in karta.get("topology", {}).get("nodes", []))
def evaluate(karta, root: pathlib.Path):
    violations = []
    for n in karta.get("topology", {}).get("nodes", []):
        if "MO" not in n.get("ports", []): continue
        sf = root / "src" / "nodes" / n["id"] / "schemas.json"
        if not sf.exists():
            violations.append({"node": n["id"], "fix_hint": "schemas.json missing."}); continue
        s = json.loads(sf.read_text())
        mo = s.get("mo", {})
        ac = mo.get("anonymization_contract")
        if not ac:
            violations.append({"node": n["id"], "port": "mo", "fix_hint": "Add anonymization_contract to mo schema."}); continue
        for f in ("aggregated_fields", "k_anonymized_fields", "retention_policy", "geographic_scope"):
            if f not in ac:
                violations.append({"node": n["id"], "port": "mo", "missing": f, "fix_hint": f"Add {f} to anonymization_contract."})
        # Doctrine k-floor: the declared k_minimum must be a real integer >= the
        # doctrine floor (5; higher floors for sensitive verticals are enforced at
        # composition). A sub-floor or missing k_minimum is a FAIL — a declared
        # floor that gates nothing is not a floor.
        _floor = 5
        try:
            _kf = karta.get("k_floor") or (karta.get("metadata") or {}).get("k_floor")
            if isinstance(_kf, int) and _kf > _floor:
                _floor = _kf
        except Exception:
            pass
        _km = ac.get("k_minimum")
        if _km is None:
            violations.append({"node": n["id"], "port": "mo", "missing": "k_minimum", "fix_hint": f"anonymization_contract must declare k_minimum >= {_floor}."})
        elif not isinstance(_km, int) or _km < _floor:
            violations.append({"node": n["id"], "port": "mo", "k_minimum": _km, "fix_hint": f"k_minimum must be an integer >= {_floor} (doctrine k-floor)."})
        for r in ac.get("k_anonymized_fields", []) or []:
            if isinstance(r, dict) and r.get("k", 0) < 5:
                violations.append({"node": n["id"], "port": "mo", "field": r.get("field"), "fix_hint": "k must be >= 5."})
    return {"status": "PASS" if not violations else "FAIL", "violations": violations, "details": "Mo anonymization contract check."}
