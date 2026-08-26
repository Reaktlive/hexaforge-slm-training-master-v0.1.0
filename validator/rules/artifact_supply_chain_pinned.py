"""ARTIFACT_SUPPLY_CHAIN_PINNED — the build supply chain is pinned.

Fas 2.14a (external DD, Peter #5). GitHub Actions ran on floating major tags
(actions/checkout@v4) and the Dockerfile installed unpinned packages
(pip install anthropic httpx pytest). This gate re-derives, at receiver time,
that every workflow uses: is pinned to a 40-hex commit SHA, that no unpinned
pip install of a named package ships in the Dockerfile/workflows, and that a
Dependabot config keeps the pins current (github-actions + docker + pip). The
hashed transitive lock, full SBOM and base-image digest are measured in CI
(2.14b); the edge-bound factory cannot honestly bake real hashes/digests.
"""
import pathlib
GATE_ID = "ARTIFACT_SUPPLY_CHAIN_PINNED"; GATE_NAME = "Supply Chain Pinned (Actions on commit SHAs, no unpinned pip installs, Dependabot present)"; GATE_KIND = "hard"
GATE_CATEGORY = "artifact"

def applies(karta):
    return True

def _read(root, rel):
    p = root / rel
    return p.read_text(errors="ignore") if p.is_file() else ""

def _workflow_files(root):
    d = root / ".github" / "workflows"
    if not d.is_dir():
        return []
    return sorted(d.glob("*.yml")) + sorted(d.glob("*.yaml"))

def _is_sha(ref):
    at = ref.rfind("@")
    if at < 0:
        return False
    pin = ref[at + 1:]
    return len(pin) == 40 and all(c in "0123456789abcdef" for c in pin)

def _bare_pip(text):
    bad = []
    for line in text.splitlines():
        if line.strip().startswith("#"):
            continue
        marker = None
        for mk in ("pip install", "pip3 install"):
            if mk in line:
                marker = mk
                break
        if marker is None:
            continue
        rest = line.split(marker, 1)[1]
        for sep in ("&&", "||", ";"):
            rest = rest.split(sep)[0]
        rest = "".join(ch for ch in rest if ch != chr(92))
        toks = rest.split()
        j = 0
        while j < len(toks):
            t = toks[j]
            if t in ("-r", "--requirement", "-c", "--constraint"):
                j += 2
                continue
            if t.startswith("-") or t == ".":
                j += 1
                continue
            # Fas 3.4 (external DD) - the exemption that used to sit here let
            # an unpinned pip upgrade through while this gate's own NAME
            # claimed "no unpinned pip installs". A deliberately carved-out
            # counter-example to a stated absolute is the claims/reality class
            # this factory refuses to ship, so it is gone: pip pins like any
            # other package, and the claim is now true without qualification.
            if "==" in t and not any(x in t for x in (">", "<", "~", "!", "*")):
                j += 1
                continue
            bad.append(t)
            j += 1
    return bad

def evaluate(karta, root: pathlib.Path):
    violations = []
    checked = 0
    wfs = _workflow_files(root)
    if wfs:
        checked += 1
        for wf in wfs:
            for line in wf.read_text(errors="ignore").splitlines():
                s = line.strip()
                if s.startswith("#"):
                    continue
                if s.startswith("- "):
                    s = s[2:].strip()
                if not s.startswith("uses:"):
                    continue
                parts = s.split("uses:", 1)[1].split()
                if not parts:
                    continue
                ref = parts[0]
                if ref.startswith("./") or ref.startswith("docker://"):
                    continue
                if not _is_sha(ref):
                    violations.append({"file": ".github/workflows/" + wf.name, "fix_hint": "uses: %s runs on a floating tag/branch — pin to a 40-hex commit SHA." % ref})
        dep = _read(root, ".github/dependabot.yml") or _read(root, ".github/dependabot.yaml")
        if not dep:
            violations.append({"file": ".github/dependabot.yml", "fix_hint": "no Dependabot config — SHA/version pins would silently rot; cover github-actions + docker + pip."})
        else:
            for eco in ("github-actions", "docker", "pip"):
                if eco not in dep:
                    violations.append({"file": ".github/dependabot.yml", "fix_hint": "Dependabot config does not cover the '%s' ecosystem." % eco})
    targets = []
    df = _read(root, "deploy/Dockerfile")
    if df:
        checked += 1
        targets.append(("deploy/Dockerfile", df))
    for wf in wfs:
        targets.append((".github/workflows/" + wf.name, wf.read_text(errors="ignore")))
    for file, text in targets:
        bad = _bare_pip(text)
        if bad:
            violations.append({"file": file, "fix_hint": "unpinned pip install %s — install via -e . (pyproject) or a hashed -r requirements.lock (2.14b)." % " ".join(bad)})
    if checked == 0 and not violations:
        return {"status": "N_A", "violations": [], "details": "No GitHub workflow surface and no Dockerfile in this build target — nothing to pin."}
    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": "Build supply chain is pinned: every GitHub Action uses: is a 40-hex commit SHA, no unpinned pip installs ship in the Dockerfile/workflows, and Dependabot keeps the pins current (external DD #5, 2.14a). The hashed transitive lock, SBOM and base-image digest are measured in CI (2.14b)."}
