"""H2 Port Independence — universal. Static check that Mi/Mo logic isn't bled into Xi/Xo."""
import re, pathlib
GATE_ID = "ARTIFACT_PORT_INDEPENDENCE"; GATE_NAME = "Port Independence"; GATE_KIND = "hard"
GATE_CATEGORY = "artifact"
def applies(karta): return True
def evaluate(karta, root: pathlib.Path):
    violations = []
    for n in karta.get("topology", {}).get("nodes", []):
        nd = root / "src" / "nodes" / n["id"]
        declared = {str(p).upper() for p in (n.get("ports") or [])}
        for fname in ("port_xi.py", "port_xo.py"):
            f = nd / fname
            # Fas 3.16 (found by the gate-mutation matrix, A20) — a DECLARED
            # port whose handler file is absent used to be silently skipped, so
            # deleting every port file left this gate reporting PASS on an
            # artifact with no ports at all. A gate that goes green when its
            # subject is gone is not evidence. Ports the karta does NOT declare
            # are still skipped: that is a real topology, not a missing file.
            if fname[5:7].upper() not in declared:
                continue
            if not f.exists():
                violations.append({"node": n["id"], "file": str(f),
                                   "fix_hint": "The karta declares this port; its handler file is missing."})
                continue
            txt = f.read_text(errors="ignore")
            if re.search(r"\bmacro_signal|enforce_contract|cohort_payload\b", txt):
                violations.append({"node": n["id"], "file": str(f), "fix_hint": "Move Mi/Mo logic into port_mi.py / port_mo.py."})
    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": "Static Mi/Mo bleed scan over every DECLARED Xi/Xo handler (a declared port with no file is a violation, not a skip)."}
