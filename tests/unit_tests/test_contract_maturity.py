"""Contract maturity — every emitted contract carries a MEASURED class.

Fas 2.11d (external assessment #4, finding F): "contract complete" was
undefined per contract. Every contracts/<node>/<port>.schema.json now carries
maturity: platform_complete | open_customer_seam, measured by MATURITY_RULE
(stamped in the file). This test recomputes the rule from the schema field and
asserts the stamp and the ledger agree — the classification can never be a
hand-written claim. domain_complete is NEVER factory-emitted: only the
customer can attest domain completeness after implementing the seams.
"""
import glob
import json


def _recompute(schema):
    props = schema.get("properties") or {}
    req = schema.get("required") or []
    if not props and not req:
        return "open_customer_seam", ["(schema)"]
    seams = []
    for name in sorted(props):
        d = props[name]
        if not isinstance(d, dict):
            seams.append(name)
            continue
        t = d.get("type")
        if t is not None and t != "object":
            continue
        sub = len(d.get("properties") or {}) if isinstance(d.get("properties"), dict) else 0
        req = len(d.get("required") or []) if isinstance(d.get("required"), list) else 0
        if sub == 0 and req == 0:
            seams.append(name)
    return ("open_customer_seam" if seams else "platform_complete"), seams


def test_every_contract_is_stamped_and_the_stamp_is_measured():
    files = sorted(glob.glob("contracts/*/*.schema.json"))
    assert files, "no contract files emitted"
    for path in files:
        with open(path) as f:
            doc = json.load(f)
        assert doc.get("maturity") in ("platform_complete", "open_customer_seam"), path
        assert "domain_complete" != doc.get("maturity"), path
        expected, seams = _recompute(doc.get("schema") or {})
        assert doc["maturity"] == expected, (path, doc["maturity"], expected)
        assert doc.get("open_seams", []) == seams, (path, doc.get("open_seams"), seams)
        assert isinstance(doc.get("maturity_rule"), str) and doc["maturity_rule"], path


def test_ledger_totals_agree_with_the_files():
    with open("contracts/contract_maturity.json") as f:
        ledger = json.load(f)
    files = sorted(glob.glob("contracts/*/*.schema.json"))
    assert ledger["totals"]["total"] == len(files)
    by_key = {}
    for path in files:
        with open(path) as f:
            doc = json.load(f)
        node = path.split("/")[1]
        port = path.split("/")[2].replace(".schema.json", "")
        by_key[(node, port)] = doc["maturity"]
    for row in ledger["contracts"]:
        assert by_key[(row["node"], row["port"])] == row["maturity"], row
    pc = sum(1 for v in by_key.values() if v == "platform_complete")
    assert ledger["totals"]["platform_complete"] == pc
    assert ledger["totals"]["open_customer_seam"] == len(files) - pc
