"""Artifact-conformance + offline doctrine re-verification engine.

Auto-discovers rules/*.py, partitions gates by GATE_CATEGORY, and writes TWO
separate reports plus a human-readable validator/report.txt. Per Claims Register
C24 artifact conformance is reported SEPARATELY and is never merged into the
doctrine score. This engine MUST NOT write reports/ceve_validation.json — that
file is the factory's authoritative composition-time doctrine attestation.

cwd-independent: every path is resolved from __file__, so it behaves identically
run as `python3 validator/engine.py` from the bundle root or `python3 engine.py`
from inside validator/.
"""
import importlib.util, json, pathlib, sys
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
RULES = HERE / "rules"

def load_rules():
    mods = []
    for f in sorted(RULES.glob("*.py")):
        if f.name.startswith("_"):
            continue
        spec = importlib.util.spec_from_file_location(f.stem, f)
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        if not (hasattr(m, "GATE_ID") and hasattr(m, "evaluate")):
            continue
        mods.append(m)
    return mods

def _run(m, karta):
    cat = getattr(m, "GATE_CATEGORY", "artifact")
    try:
        if not m.applies(karta):
            return {"id": m.GATE_ID, "name": m.GATE_NAME, "kind": m.GATE_KIND, "category": cat, "status": "N_A", "violations": [], "details": "not applicable"}
        r = m.evaluate(karta, ROOT)
        return {"id": m.GATE_ID, "name": m.GATE_NAME, "kind": m.GATE_KIND, "category": cat, **r}
    except Exception as e:
        return {"id": m.GATE_ID, "name": m.GATE_NAME, "kind": m.GATE_KIND, "category": cat, "status": "FAIL", "violations": [{"error": str(e)}], "details": "rule crashed"}

def _census(results):
    """How many gates actually ran, and which ones went silent.

    Fas 3.16 (found by the gate-mutation matrix, A20). The score is a RATIO of
    pass to fail, so a gate that reports N_A leaves it untouched. Delete the
    files a gate inspects and it can declare itself inapplicable - the evidence
    base shrinks and the headline still reads 100/100. A reviewer had no way to
    tell twenty-three gates from fifteen. The verdict semantics are unchanged;
    what changes is that the census is now on the report instead of implied.
    """
    counts = {"passed": 0, "failed": 0, "not_applicable": 0}
    silent = []
    for r in results:
        if r["status"] == "PASS":
            counts["passed"] += 1
        elif r["status"] == "FAIL":
            counts["failed"] += 1
        elif r["status"] == "N_A":
            counts["not_applicable"] += 1
            silent.append(r["id"])
    counts["evaluated"] = counts["passed"] + counts["failed"]
    counts["registered"] = len(results)
    counts["not_applicable_gates"] = sorted(silent)
    return counts


def _summarize(results):
    p = sum(1 for r in results if r["status"] == "PASS")
    f = sum(1 for r in results if r["status"] == "FAIL")
    score = round(100 * p / (p + f)) if (p + f) > 0 else 100
    hard_fails = [r for r in results if r["status"] == "FAIL" and r["kind"] == "hard"]
    verdict = "PASS" if score >= 90 and not hard_fails else "FAIL"
    return score, verdict

def _table(title, rows, score, verdict):
    out = [title, "-" * len(title)]
    if not rows:
        out.append("(no gates in this category)")
    for r in rows:
        out.append(f"  [{r['status']:<5}] {r['id']:<32} {r['name']}")
        if r.get("details"):
            out.append(f"           {r['details']}")
        for v in (r.get("violations") or [])[:5]:
            out.append(f"           ! {json.dumps(v, sort_keys=True)}")
    out.append(f"  => score {score}/100, verdict {verdict}")
    c = _census(rows)
    out.append(f"     gates: {c['registered']} registered, {c['evaluated']} evaluated "
               f"({c['passed']} pass / {c['failed']} fail), "
               f"{c['not_applicable']} not applicable"
               + (": " + ", ".join(c["not_applicable_gates"]) if c["not_applicable_gates"] else ""))
    out.append("")
    return out

def main():
    karta = json.loads((ROOT / "karta.compiled.json").read_text())
    results = [_run(m, karta) for m in load_rules()]
    version = (RULES / "baseline_version.txt").read_text().strip()
    now = datetime.now(timezone.utc).isoformat()
    out_dir = ROOT / "reports"; out_dir.mkdir(exist_ok=True)

    artifact = [r for r in results if r.get("category") == "artifact"]
    doctrine = [r for r in results if r.get("category") == "doctrine"]
    other = [r for r in results if r.get("category") not in ("artifact", "doctrine")]

    a_score, a_verdict = _summarize(artifact)
    (out_dir / "artifact_conformance.json").write_text(json.dumps({
        "kind": "artifact_conformance",
        "note": "Proves the generated code implements what the karta declared. NOT the doctrine score (C24). The authoritative doctrine attestation is reports/ceve_validation.json, written at composition and never overwritten here.",
        "score": a_score, "verdict": a_verdict, "gate_census": _census(artifact),
        "rules_version": version,
        "generated_at": now, "gates": artifact}, indent=2))

    d_score, d_verdict = _summarize(doctrine)
    (out_dir / "doctrine_reverification.json").write_text(json.dumps({
        "kind": "doctrine_reverification",
        "note": "Offline re-verification of the doctrine gates this bundle can re-run itself (the 11 offline-reverifiable of the 19; the remaining 8 are composition-attested — see reports/ceve_validation.json).",
        "score": d_score, "verdict": d_verdict, "gate_census": _census(doctrine),
        "rules_version": version,
        "generated_at": now, "gates": doctrine}, indent=2))

    lines = [
        "HexaBox bundle validator — offline re-verification",
        f"generated_at: {now}",
        f"rules_version: {version}",
        f"karta: {ROOT / 'karta.compiled.json'}",
        "",
    ]
    lines += _table(f"Doctrine re-verification ({len(doctrine)} gates)", doctrine, d_score, d_verdict)
    lines += _table(f"Artifact conformance ({len(artifact)} gates)", artifact, a_score, a_verdict)
    if other:
        o_score, o_verdict = _summarize(other)
        lines += _table(f"Vertical gates ({len(other)} gates)", other, o_score, o_verdict)
    lines.append("reports/ceve_validation.json is the composition-time attestation and is NEVER written by this engine.")
    (HERE / "report.txt").write_text("\n".join(lines) + "\n")

    print("\n".join(lines))
    hard_fail = [r for r in results if r["status"] == "FAIL" and r["kind"] == "hard"]
    sys.exit(0 if not hard_fail else 1)

if __name__ == "__main__":
    main()
