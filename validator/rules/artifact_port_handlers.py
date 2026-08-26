"""H1 Port Existence — SUBSTANCE: port file must define an executable handler.

Strips comments + string literals from port_<p>.py before any analysis, then
requires an executable handler def (receive_<p>/handle_<p>, or any def …(payload))
to survive the strip. An empty or docstring-only port file (the file exists but
defines nothing) FAILS — the old f.exists() check was gameable by an empty file.
"""
import re, pathlib
GATE_ID = "ARTIFACT_PORT_HANDLERS"; GATE_NAME = "Port Existence"; GATE_KIND = "hard"
GATE_CATEGORY = "artifact"

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

def _has_handler(stripped: str, port: str) -> bool:
    lower = re.sub(r"[^a-z0-9_]", "", port.lower())
    named = re.compile(r"^\s*(?:async\s+)?def\s+(?:receive_" + lower + r"|handle_" + lower + r")\s*\(", re.M)
    if named.search(stripped):
        return True
    generic = re.compile(r"^\s*(?:async\s+)?def\s+\w+\s*\(\s*payload\b", re.M)
    return bool(generic.search(stripped))

def applies(karta): return True

def evaluate(karta, root: pathlib.Path):
    violations = []
    count = 0
    for n in karta.get("topology", {}).get("nodes", []):
        nd = root / "src" / "nodes" / n["id"]
        for p in n.get("ports", []):
            count += 1
            f = nd / f"port_{p.lower()}.py"
            if not f.exists():
                violations.append({"node": n["id"], "port": p, "file": str(f), "fix_hint": "Port handler file missing."}); continue
            code = _strip_py(f.read_text(errors="ignore"))
            if not _has_handler(code, p):
                violations.append({"node": n["id"], "port": p, "file": str(f),
                                   "fix_hint": f"Port file exists but defines no handler (expected an executable def receive_{p.lower()}/handle_{p.lower()} or def …(payload) — an empty/stub-empty port file does not satisfy H1)."})
    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": f"Verified an executable port handler def in {count} port file(s) (comment-stripped)."}
