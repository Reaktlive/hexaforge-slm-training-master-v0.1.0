"""H8 HexaSource Provenance — SUBSTANCE: executable provenance call beside the AI call.

Strips comments + string literals before any analysis. AI usage is detected by
a real import statement of a provider SDK (or an @ai_call decorator), scanned in
node handlers AND src/shared/llm_binding.py. Each AI-using file must carry an
executable register_llm_call()/record_provenance() call inside a function — a
docstring-mention or a bare module-scope statement never satisfies the gate.
"""
import re, pathlib
GATE_ID = "ARTIFACT_PROVENANCE_CALL"; GATE_NAME = "HexaSource Provenance"; GATE_KIND = "hard"
GATE_CATEGORY = "artifact"
AI_LIBS = ("openai", "anthropic", "huggingface", "cohere", "mistralai")

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

def _detects_ai(code: str) -> bool:
    for lib in AI_LIBS:
        if re.search(r"(?m)^\s*(?:import\s+" + lib + r"(?:\s|\.|$)|from\s+" + lib + r"(?:\.[\w.]+)?\s+import\b)", code):
            return True
    return bool(re.search(r"@ai_call\b", code))

def _function_bodies(code: str):
    """Body text of every def, handling multi-line signatures (a column-0
    ') -> T:' terminator must not prematurely close the body — that gap hid the
    PG-6 run_bound_completion register_llm_call from the gate)."""
    lines = code.split("\n")
    header = re.compile(r"^(\s*)(?:async\s+)?def\s+\w+\s*\(")
    bodies = []
    i = 0
    while i < len(lines):
        m = header.match(lines[i])
        if not m:
            i += 1; continue
        indent = len(m.group(1))
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
        bodies.append("\n".join(body))
        i = j if j > i else i + 1
    return bodies

_PROV_RE = re.compile(r"\b(?:register_llm_call|record_provenance)\s*\(")

def _scan(root):
    found = []
    nodes_dir = root / "src" / "nodes"
    if nodes_dir.exists():
        for n_dir in nodes_dir.glob("*"):
            h = n_dir / "handler.py"
            if h.exists():
                code = _strip_py(h.read_text(errors="ignore"))
                if _detects_ai(code):
                    found.append((n_dir.name, h, code))
    binding = root / "src" / "shared" / "llm_binding.py"
    if binding.exists():
        code = _strip_py(binding.read_text(errors="ignore"))
        if _detects_ai(code):
            found.append(("llm_binding", binding, code))
    return found

def applies(karta):
    return True  # recheck against the file tree in evaluate

def evaluate(karta, root: pathlib.Path):
    found = _scan(root); violations = []
    if not found:
        return {"status": "N_A", "violations": [], "details": "No genuine AI SDK import detected in executable code."}
    for name, path, code in found:
        if not _PROV_RE.search(code):
            violations.append({"node": name, "file": str(path),
                               "fix_hint": "AI SDK invoked but no executable register_llm_call()/record_provenance() call accompanies it — provenance declared but not recorded (keyword theatre does not satisfy H8)."})
            continue
        if not any(_PROV_RE.search(b) for b in _function_bodies(code)):
            violations.append({"node": name, "file": str(path),
                               "fix_hint": "register_llm_call()/record_provenance() is not inside any function body — move it onto the AI call path so it executes per call."})
    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": f"Verified executable provenance call in {len(found)} AI-using file(s) (comment-stripped)."}
