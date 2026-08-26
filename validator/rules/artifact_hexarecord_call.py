"""H7 HexaRecord Logging — SUBSTANCE: executable log_event() on the YO return path.

Strips comments + string literals from port_yo.py before any analysis, then
requires log_event(...) to be CALLED inside the YO handler function
(receive_yo / handle_yo). Keyword presence in a comment/docstring is never
sufficient (the old grep was gameable by emitting '# log_event(').
"""
import re, pathlib
GATE_ID = "ARTIFACT_HEXARECORD_CALL"; GATE_NAME = "HexaRecord Logging"; GATE_KIND = "hard"
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

def _iter_functions(stripped: str):
    """Yield (header_line, body) for each def, handling multi-line signatures."""
    lines = stripped.split("\n")
    header = re.compile(r"^(\s*)(?:async\s+)?def\s+\w+\s*\(")
    i = 0
    while i < len(lines):
        m = header.match(lines[i])
        if not m:
            i += 1; continue
        indent = len(m.group(1)); header_line = lines[i]
        # Skip past a (possibly multi-line) signature: track bracket depth until
        # a line ends with ':' at depth 0.
        depth = 0; sig_end = i
        for j in range(i, len(lines)):
            for ch in lines[j]:
                if ch in "([{": depth += 1
                elif ch in ")]}": depth -= 1
            sig_end = j
            if depth <= 0 and re.search(r":\s*$", lines[j]):
                break
        body = []; j = sig_end + 1
        while j < len(lines):
            nxt = lines[j]
            if nxt.strip() == "":
                body.append(nxt); j += 1; continue
            ind = len(nxt) - len(nxt.lstrip())
            if ind <= indent:
                break
            body.append(nxt); j += 1
        yield header_line, "\n".join(body)
        i = j if j > i else i + 1

def _function_body(stripped: str, names) -> str:
    """Body of the first top-level def whose name is in `names` (or '')."""
    alt = "|".join(re.escape(x) for x in names)
    header_re = re.compile(r"^\s*(?:async\s+)?def\s+(?:" + alt + r")\s*\(")
    for header_line, body in _iter_functions(stripped):
        if header_re.match(header_line):
            return body
    return ""

def applies(karta): return True

def evaluate(karta, root: pathlib.Path):
    violations = []
    audited = 0
    call_re = re.compile(r"\blog_event\s*\(")
    for n in karta.get("topology", {}).get("nodes", []):
        if "YO" not in n.get("ports", []): continue
        f = root / "src" / "nodes" / n["id"] / "port_yo.py"
        if not f.exists():
            violations.append({"node": n["id"], "fix_hint": "port_yo.py missing."}); continue
        audited += 1
        code = _strip_py(f.read_text(errors="ignore"))
        body = _function_body(code, ["receive_yo", "handle_yo"])
        if body and call_re.search(body):
            continue
        if call_re.search(code):
            violations.append({"node": n["id"], "port": "yo",
                               "fix_hint": "log_event() appears but not as an executable call inside the YO handler (receive_yo/handle_yo) — move the call onto the YO return path."})
        else:
            violations.append({"node": n["id"], "port": "yo",
                               "fix_hint": "YO return path never CALLS log_event() — audit logging declared but not performed (keyword theatre does not satisfy H7)."})
    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": f"Verified executable log_event() on the YO return path of {audited} YO port(s) (comment-stripped)."}
