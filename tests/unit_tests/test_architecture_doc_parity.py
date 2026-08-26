"""Architecture-doc parity — the prose is DERIVED from compiled edges.

Fas 2.11e (external assessment #4, finding C): the data-flow prose used to be
a role-derived flat fan-out ("all HB nodes as parallel siblings") while the
real chain wires approval gates DOWNSTREAM of their action nodes. The doc is
now generated from the compiled XO->XI edge set; this test mirrors the same
derivation from karta.compiled.json and asserts every branch line appears in
docs/architecture.md verbatim — doc and topology can never drift apart.
"""
import json


def _flow_branches():
    with open("karta.compiled.json") as f:
        karta = json.load(f)
    edges = karta.get("topology", {}).get("edges", [])
    primary = [e for e in edges
               if str(e.get("source_port", e.get("from_port", ""))).upper() == "XO"
               and str(e.get("target_port", e.get("to_port", ""))).upper() == "XI"]
    children, parents = {}, {}
    for e in primary:
        f_, t_ = e.get("source_agent") or e.get("from"), e.get("target_agent") or e.get("to")
        children.setdefault(f_, []).append(t_)
        parents.setdefault(t_, []).append(f_)
    all_nodes = set(children) | set(parents)
    ingress = sorted(n for n in all_nodes if not parents.get(n))
    joins = sorted(n for n in all_nodes if len(parents.get(n, [])) > 1)
    if not primary or not ingress:
        return []
    def walk(start):
        seen, parts, cur = set(), [], start
        while cur and cur not in seen:
            seen.add(cur)
            parts.append(cur)
            if cur in joins:
                break
            nxt = sorted(children.get(cur, []))
            if not nxt:
                break
            if len(nxt) > 1:
                parts.append("(fans out to %s)" % ", ".join(nxt))
                break
            cur = nxt[0]
            if cur in joins:
                parts.append(cur)
                break
        return " → ".join(parts)
    heads = sorted(children.get(ingress[0], []))
    return [walk(h) for h in heads]


def test_every_branch_line_in_the_doc_matches_compiled_edges():
    branches = _flow_branches()
    with open("docs/architecture.md") as f:
        doc = f.read()
    assert "from the compiled edge set" in doc, "doc no longer claims edge derivation"
    for b in branches:
        assert b in doc, "branch chain missing from architecture.md: %r" % b


def test_doc_never_claims_the_flat_sibling_fanout():
    with open("docs/architecture.md") as f:
        doc = f.read()
    assert "fan-out to parallel HBs (" not in doc, (
        "role-derived flat fan-out prose is back — the doc must derive from edges")
