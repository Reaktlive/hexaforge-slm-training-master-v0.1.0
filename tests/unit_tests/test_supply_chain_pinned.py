"""Supply-chain pinning — Actions on commit SHAs, no unpinned installs, Dependabot present.

Fas 2.14a (external DD, Peter #5): GitHub Actions ran on floating major tags and
the Dockerfile installed unpinned packages. These tests prove every workflow
uses: is pinned to a 40-hex commit SHA, that no bare pip install of a named
package ships in the Dockerfile/workflows, and that Dependabot keeps the pins
current (skips cleanly on a non-GitHub build target).
"""
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _workflows():
    d = ROOT / ".github" / "workflows"
    if not d.is_dir():
        return []
    return sorted(d.glob("*.yml")) + sorted(d.glob("*.yaml"))


def _is_sha(ref):
    at = ref.rfind("@")
    if at < 0:
        return False
    pin = ref[at + 1:]
    return len(pin) == 40 and all(c in "0123456789abcdef" for c in pin)


def test_every_action_use_is_sha_pinned():
    wfs = _workflows()
    if not wfs:
        pytest.skip("no GitHub workflows in this build target")
    unpinned = []
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
                unpinned.append(wf.name + ": " + ref)
    assert not unpinned, "unpinned actions (must be 40-hex SHAs): " + "; ".join(unpinned)


def test_dependabot_covers_actions_docker_and_pip():
    if not _workflows():
        pytest.skip("no GitHub surface in this build target")
    dep = ROOT / ".github" / "dependabot.yml"
    if not dep.is_file():
        dep = ROOT / ".github" / "dependabot.yaml"
    assert dep.is_file(), "no .github/dependabot.yml — pins would silently rot"
    body = dep.read_text(errors="ignore")
    for eco in ("github-actions", "docker", "pip"):
        assert eco in body, "dependabot config missing ecosystem: " + eco


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
        toks = "".join(ch for ch in rest if ch != chr(92)).split()
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


def test_no_unpinned_pip_installs_in_dockerfile_or_workflows():
    targets = []
    df = ROOT / "deploy" / "Dockerfile"
    if df.is_file():
        targets.append(df)
    targets.extend(_workflows())
    if not targets:
        pytest.skip("no Dockerfile or workflows to scan")
    offenders = []
    for p in targets:
        bad = _bare_pip(p.read_text(errors="ignore"))
        if bad:
            offenders.append(p.name + ": " + " ".join(bad))
    assert not offenders, "unpinned pip installs (use -e . or -r requirements.lock): " + "; ".join(offenders)
