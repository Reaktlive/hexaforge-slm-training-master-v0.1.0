"""H6 Macro Hub Compliance — SUBSTANCE: a stub hub must really return HTTP 501.

Strips comments + string literals from the hub handler before any analysis,
then requires 501 in a real return/raise context (the old '501' substring check
was gameable by a comment, a version string, or a timeout literal like 5010).
A pipeline hub is never asked to emit 501; it must carry internal_topology.
"""
import re, pathlib
GATE_ID = "ARTIFACT_MACROHUB_HANDLER"; GATE_NAME = "Macro Hub Compliance"; GATE_KIND = "hard"
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

def _returns_501(code: str) -> bool:
    if re.search(r"\bHTTPException\s*\(\s*(?:status_code\s*=\s*)?501\b", code):
        return True
    if re.search(r"\bstatus_code\s*=\s*501\b", code):
        return True
    if re.search(r"\b(?:JSON)?Response\s*\([^)]*\b501\b", code):
        return True
    return False

def _hub(karta):
    for n in karta.get("topology", {}).get("nodes", []):
        if n["id"] == "macro_hub" or n.get("type", "").startswith("MacroHub"): return n
    return None
def applies(karta): return _hub(karta) is not None
def evaluate(karta, root: pathlib.Path):
    hub = _hub(karta); violations = []
    h = root / "src" / "nodes" / hub["id"] / "handler.py"
    if not h.exists():
        violations.append({"node": hub["id"], "fix_hint": "macro_hub handler missing."})
    else:
        kind = (hub.get("type") or "hexabox-stub").lower()
        if "stub" in kind:
            code = _strip_py(h.read_text(errors="ignore"))
            if not _returns_501(code):
                violations.append({"node": hub["id"], "file": str(h),
                                   "fix_hint": "Stub macro_hub must DEMONSTRABLY return HTTP 501 — an executable HTTPException(status_code=501)/status_code=501/Response(...501...) in code, not the digits '501' loose in a comment, version, or timeout (keyword theatre does not satisfy H6)."})
        elif "pipeline" in kind:
            if not hub.get("internal_topology"):
                violations.append({"node": hub["id"], "fix_hint": "Pipeline macro_hub requires internal_topology."})
    return {"status": "PASS" if not violations else "FAIL", "violations": violations, "details": "Macro hub mode check (comment-stripped; stub requires executable 501, pipeline requires internal_topology)."}
