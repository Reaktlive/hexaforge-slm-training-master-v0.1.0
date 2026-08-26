"""ARTIFACT_SUPPLY_CHAIN_MEASURED — measured before export, signed born-in.

Fas 2.18 (external DD, Peter). The bundle-invariant dependency set is measured by
the FACTORY (uv --generate-hashes transitive lock + CycloneDX SBOM) and BORN IN
this bundle as SIGNED files (hashed into the Ed25519 manifest) — measured before
export, not by a post-delivery CI bootstrap. This twin re-derives at receiver
time: (1) requirements.lock + sbom/cyclonedx.json are present, hash-locked,
drift-bound to the emitted pyproject, and IN THE SIGNED MANIFEST; (2) the shipped
re-verify mechanism ships (supply-chain workflow + lock-aware Dockerfile);
(3) two-state — MEASURED_AND_LOCKED when the factory has embedded the measured
base-image digest (then deploy/base-image.lock is ALSO born-in + SIGNED and must
match the expected ref), else MEASUREMENT_READY (the base digest is the only
value the edge generator cannot reach; a digest file WITHOUT a factory
measurement would be an invented claim and is a violation). Nothing is written
post-signing (the shipped workflow is verify-only), so measured_outputs must not
tolerate supply-chain paths.
"""
import json
import pathlib
GATE_ID = "ARTIFACT_SUPPLY_CHAIN_MEASURED"; GATE_NAME = "Supply Chain Measured (transitive hash-locked lock + CycloneDX SBOM measured before export and signed; base-image digest two-state)"; GATE_KIND = "hard"
GATE_CATEGORY = "artifact"
EXPECTED_DEPS_SHA = "98ade96c788cbfff0cf10b6274c0330725e7ba3f3f07f3dba6b0c70f5f73dee8"
EXPECTED_BASE_IMAGE_REF = "python:3.11-slim@sha256:db3ff2e1800a8581e2c48a27c3995339d47bdf046da21c7627accd3d51053a93"

def applies(karta):
    return True

def _read(root, rel):
    p = root / rel
    return p.read_text(errors="ignore") if p.is_file() else ""

def evaluate(karta, root: pathlib.Path):
    violations = []
    checked = 0
    lock = _read(root, "requirements.lock")
    sbom = _read(root, "sbom/cyclonedx.json")
    df = _read(root, "deploy/Dockerfile")
    # (1) born-in measured material, present + consistent.
    if lock or sbom or df:
        checked += 1
    if df and "--require-hashes" not in df:
        violations.append({"file": "deploy/Dockerfile", "fix_hint": "install is not hash-locked (--require-hashes -r requirements.lock)."})
    if df and not lock:
        violations.append({"file": "requirements.lock", "fix_hint": "born-in hash-locked requirements.lock missing (measured before export)."})
    if lock:
        if "--hash=sha256:" not in lock:
            violations.append({"file": "requirements.lock", "fix_hint": "lock carries no sha256 hashes — not a --generate-hashes lock."})
        if ("# pyproject-deps-sha256: " + EXPECTED_DEPS_SHA) not in lock:
            violations.append({"file": "requirements.lock", "fix_hint": "lock drift marker != factory-measured pyproject deps — re-measure."})
        if not sbom:
            violations.append({"file": "sbom/cyclonedx.json", "fix_hint": "hashed lock ships without its SBOM."})
    if sbom:
        try:
            doc = json.loads(sbom)
            if doc.get("bomFormat") != "CycloneDX" or not (doc.get("components") or []):
                violations.append({"file": "sbom/cyclonedx.json", "fix_hint": "SBOM is not CycloneDX with components."})
        except Exception:
            violations.append({"file": "sbom/cyclonedx.json", "fix_hint": "SBOM is not parseable JSON."})
    # (2) SIGNED born-in: lock + SBOM (and the base lock, once measured) must be
    # in the signed MANIFEST.json; measured_outputs must not tolerate them.
    manifest = _read(root, "MANIFEST.json")
    mpaths = None
    if manifest:
        try:
            mpaths = {e.get("path") for e in (json.loads(manifest).get("files") or [])}
        except Exception:
            mpaths = None
    if mpaths is not None and lock:
        for p in ("requirements.lock", "sbom/cyclonedx.json"):
            if p not in mpaths:
                violations.append({"file": p, "fix_hint": "measured file is NOT in the signed manifest — measured-before-export requires it be signed, not a post-delivery output."})
    ident = _read(root, "identity.json")
    if ident:
        try:
            mconf = (json.loads(ident).get("conformance") or {}).get("manifest") or {}
        except Exception:
            mconf = {}
        if mconf:
            declared = list(mconf.get("measured_outputs") or [])
            for p in ("requirements.lock", "sbom/cyclonedx.json", "deploy/base-image.lock"):
                if p in declared or "sbom/*" in declared:
                    violations.append({"file": "identity.json", "fix_hint": "signed measured_outputs tolerates '%s' — nothing is written post-signing (verify-only workflow); supply-chain material must be born-in SIGNED, never a tolerated post-delivery write." % p})
                    break
    # (3) the shipped re-verify mechanism.
    if (root / ".github" / "workflows").is_dir():
        checked += 1
        sc = _read(root, ".github/workflows/supply-chain.yml")
        if not sc:
            violations.append({"file": ".github/workflows/supply-chain.yml", "fix_hint": "supply-chain re-verify workflow missing."})
        else:
            for needle in ("--require-hashes", "pip check", "cyclonedx", "pyproject-deps-sha256"):
                if needle not in sc:
                    violations.append({"file": ".github/workflows/supply-chain.yml", "fix_hint": "workflow lacks '%s' — re-verify chain incomplete." % needle})
    base = _read(root, "deploy/base-image.lock").strip()
    digest_locked = False
    if EXPECTED_BASE_IMAGE_REF:
        # Factory measured + embedded the digest: the lock file is born-in SIGNED
        # and must match the expected ref exactly; the Dockerfile default must be
        # the digest-pinned ref (no floating tag in a LOCKED bundle).
        if base != EXPECTED_BASE_IMAGE_REF:
            violations.append({"file": "deploy/base-image.lock", "fix_hint": "born-in base-image lock missing or != the factory-measured ref (%s)." % EXPECTED_BASE_IMAGE_REF})
        else:
            digest_locked = True
        if mpaths is not None and "deploy/base-image.lock" not in mpaths:
            violations.append({"file": "deploy/base-image.lock", "fix_hint": "base-image lock is NOT in the signed manifest — the measured digest must ship signed."})
        if df and ("ARG BASE_IMAGE=" + EXPECTED_BASE_IMAGE_REF) not in df:
            violations.append({"file": "deploy/Dockerfile", "fix_hint": "Dockerfile default is not the factory-measured digest ref (floating tag in a LOCKED bundle)."})
    elif base:
        # No factory measurement, yet a digest file exists: an INVENTED claim.
        violations.append({"file": "deploy/base-image.lock", "fix_hint": "digest file present without a factory measurement (BASE_IMAGE_REF unset) — an unmeasured digest is an invented claim."})
    if checked == 0 and not violations:
        return {"status": "N_A", "violations": [], "details": "No Dockerfile / workflow surface in this build target — nothing to measure."}
    state = ("SUPPLY_CHAIN_MEASURED_AND_LOCKED" if (lock and digest_locked and not violations)
             else ("SUPPLY_CHAIN_MEASUREMENT_READY" if (lock and not violations) else "SUPPLY_CHAIN_UNMEASURED"))
    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": "[%s] Transitive hash-locked requirements + CycloneDX SBOM measured by the factory (bundle-invariant deps) and born in this bundle as SIGNED files (in MANIFEST.json), drift-bound to the emitted pyproject; base image %s. Nothing is written post-signing (verify-only workflow). External DD, 2.18/2.19, L8." % (state, "digest-pinned, born-in SIGNED (MEASURED_AND_LOCKED)" if digest_locked else "tag-based until the factory CI measures its registry digest (MEASUREMENT_READY)")}
