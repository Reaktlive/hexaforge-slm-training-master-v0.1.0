"""H_CCAS_TIER_RUNTIME — every DECLARED tier is HANDLED in runtime ccas_gate.py.

The clinical T4 bug: a karta DECLARES a tier (privileged_actions[].tier or a
tier_policy value, e.g. dual_approval) that the generated src/shared/ccas_gate.py
does NOT handle, so ccas_decide(tier=...) falls through to
{"status":"denied","route":"drop"} and the approval flow is permanently
unreachable. SUBSTANCE: strip comments + string literals from ccas_gate.py FIRST;
a tier is "handled" iff it is a key in the EXECUTABLE _LEGACY_TIER_MAP literal,
or it equals a canonical TIER_n that has an executable '== TIER_n' branch in
ccas_decide. A tier mentioned only in a comment/docstring does NOT count.
"""
import re, pathlib
GATE_ID = "ARTIFACT_CCAS_TIER_RUNTIME"; GATE_NAME = "CCAS Tier Runtime Coverage"; GATE_KIND = "hard"
GATE_CATEGORY = "artifact"

CANONICAL_TIERS = ("tier_1", "tier_2", "tier_3", "tier_4")


def _strip_py(text: str) -> str:
    out = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == "#":
            while i < n and text[i] != "\n":
                i += 1
            continue
        if c == '"' or c == "'":
            q = c
            triple = text[i + 1 : i + 3] == q * 2
            closer = q * 3 if triple else q
            i += len(closer)
            while i < n:
                if text[i] == "\\":
                    i += 2
                    continue
                if text.startswith(closer, i):
                    i += len(closer)
                    break
                i += 1
            out.append(" ")
            continue
        out.append(c)
        i += 1
    return "".join(out)


def _declared_tiers(karta) -> set:
    tiers = set()
    meta = karta.get("metadata", {}) or {}
    for a in (meta.get("privileged_actions") or []):
        if isinstance(a, dict):
            t = a.get("tier")
            if isinstance(t, str) and t:
                tiers.add(t)
    tp = meta.get("tier_policy")
    if isinstance(tp, dict):
        for v in tp.values():
            if isinstance(v, str) and v:
                tiers.add(v)
    return tiers


def applies(karta):
    return len(_declared_tiers(karta)) > 0


def evaluate(karta, root: pathlib.Path):
    declared = _declared_tiers(karta)
    if not declared:
        return {"status": "PASS", "violations": [],
                "details": "No privileged tiers declared — runtime coverage vacuously satisfied."}

    ccas = root / "src" / "shared" / "ccas_gate.py"
    if not ccas.exists():
        return {"status": "FAIL",
                "violations": [{"fix_hint": f"declared tier '{t}' has NO runtime: src/shared/ccas_gate.py is missing."} for t in sorted(declared)],
                "details": "ccas_gate.py missing."}

    raw = ccas.read_text(errors="ignore")
    stripped = _strip_py(raw)

    # Executable canonical branches: '== TIER_n' surviving the strip.
    canonical_branch = set()
    for canon in CANONICAL_TIERS:
        if re.search(r"==\s*" + canon.upper() + r"\b", stripped):
            canonical_branch.add(canon)

    # Executable alias map: require the assignment token in STRIPPED source
    # (real code, not a commented-out block), then read alias keys + canonical
    # values from the RAW map body (the stripper collapses the quoted keys).
    alias_to_canonical = {}
    if re.search(r"_LEGACY_TIER_MAP\s*=\s*\{", stripped):
        m = re.search(r"_LEGACY_TIER_MAP\s*=\s*\{(.*?)\}", raw, re.S)
        if m:
            # Map body uses double- or single-quoted alias keys -> TIER_n consts.
            for k, v in re.findall(r'"([\w-]+)"\s*:\s*(TIER_\d)\b', m.group(1)):
                alias_to_canonical[k] = v.lower()
            for k, v in re.findall(r"'([\w-]+)'\s*:\s*(TIER_\d)\b", m.group(1)):
                alias_to_canonical[k] = v.lower()

    def handled(tier: str) -> bool:
        if tier in CANONICAL_TIERS:
            return tier in canonical_branch
        canon = alias_to_canonical.get(tier)
        return canon is not None and canon in canonical_branch

    violations = []
    for tier in sorted(declared):
        if handled(tier):
            continue
        violations.append({"fix_hint":
            f"declared tier '{tier}' is NOT handled in runtime src/shared/ccas_gate.py — "
            f"ccas_decide(tier=\"{tier}\") falls through to denied/drop so the approval flow is "
            f"permanently unreachable. Add it to _LEGACY_TIER_MAP and/or a '== TIER_n' branch."})

    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": (f"Verified {len(declared) - len(violations)}/{len(declared)} declared tier(s) "
                        f"({', '.join(sorted(declared))}) handled in executable ccas_gate.py "
                        f"(comment-stripped: {len(canonical_branch)} branch(es), {len(alias_to_canonical)} alias entr(ies)).")}
