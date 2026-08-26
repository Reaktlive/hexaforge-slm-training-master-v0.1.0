"""ARTIFACT_CONTRACT_COMPLETENESS — declared-form measurement (report, never blocking).

Fas 2.4: counts declared-but-unenforced FORM in the authored contracts —
empty properties, missing required, additionalProperties:false, hard
constraints. Leniency is DECLARED policy (blocker2): payload sub-schemas are
deliberately lenient extension points, so incompleteness is MEASURED AND
DISCLOSED here, never punished. Enforcement of what IS declared is proven
separately by ARTIFACT_STRICT_CONTRACT_E2E (enforcement completeness).
This rule's kind is "report": it can PASS or be N_A — it FAILs never.
"""
import glob, json, os, pathlib
GATE_ID = "ARTIFACT_CONTRACT_COMPLETENESS"; GATE_NAME = "Contract Completeness (measurement)"; GATE_KIND = "report"
GATE_CATEGORY = "artifact"

def applies(karta):
    return True  # N_A is decided on evidence (no contracts), not topology

def evaluate(karta, root: pathlib.Path):
    paths = glob.glob(os.path.join(str(root), "contracts", "**", "*.schema.json"), recursive=True)
    if not paths:
        return {"status": "N_A", "violations": [], "details": "No authored contracts in bundle."}
    total = empty = noreq = addf = hard = unparseable = 0
    for p in sorted(paths):
        try:
            d = json.load(open(p))
        except (OSError, ValueError):
            unparseable += 1
            continue
        sch = d.get("schema") if isinstance(d.get("schema"), dict) else {}
        total += 1
        if not (sch.get("properties") or {}):
            empty += 1
        if not (sch.get("required") or []):
            noreq += 1
        if sch.get("additionalProperties") is False:
            addf += 1
        if (d.get("constraints") or {}).get("hard") or (sch.get("constraints") or {}).get("hard"):
            hard += 1
    note = (" %d unparseable file(s) skipped (schema validity is ARTIFACT_SCHEMA_COMPAT's concern)." % unparseable) if unparseable else ""
    return {"status": "PASS", "violations": [],
            "details": ("Contract completeness (measurement, never blocking): %d contracts — "
                        "%d with empty properties, %d without required, %d with "
                        "additionalProperties:false, %d with hard constraints. Leniency is "
                        "DECLARED policy (blocker2): payload sub-schemas stay lenient by design; "
                        "enforcement of what IS declared is proven by ARTIFACT_STRICT_CONTRACT_E2E.%s")
                       % (total, empty, noreq, addf, hard, note)}
