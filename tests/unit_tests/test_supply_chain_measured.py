"""Measured supply chain — born in the bundle, signed, drift-bound (Fas 2.18).

External DD (Peter): measure the supply chain BEFORE export and sign it, not via
a CI bootstrap after delivery. The dependency set is bundle-invariant, so the
factory measures the transitive hash-locked requirements + CycloneDX SBOM once
and embeds them; every bundle is BORN with them, signed in the Ed25519 manifest.
These tests prove: the lock + SBOM are present, hash-locked, drift-bound to the
emitted pyproject and IN THE SIGNED MANIFEST; and the base-image digest is either
pinned (MEASURED_AND_LOCKED) or tag-based pending the factory-CI measurement
(MEASUREMENT_READY) — never a false claim.
"""
import hashlib
import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _pyproject_deps_sha():
    import tomllib
    deps = tomllib.load(open(ROOT / "pyproject.toml", "rb"))["project"]["dependencies"]
    return hashlib.sha256(chr(10).join(sorted(deps)).encode()).hexdigest()


def test_lock_and_sbom_are_born_in_and_hash_locked():
    lock = ROOT / "requirements.lock"
    sbom = ROOT / "sbom" / "cyclonedx.json"
    assert lock.is_file(), "requirements.lock not born in the bundle (measured before export)"
    assert sbom.is_file(), "sbom/cyclonedx.json not born in the bundle"
    body = lock.read_text(errors="ignore")
    assert body.count("--hash=sha256:") >= 300, "lock is not fully hash-pinned over the transitive closure"
    # drift marker binds the born-in lock to THIS bundle's emitted pyproject deps
    assert ("# pyproject-deps-sha256: " + _pyproject_deps_sha()) in body, "lock drift marker != emitted pyproject deps"
    doc = json.loads(sbom.read_text(errors="ignore"))
    assert doc.get("bomFormat") == "CycloneDX" and len(doc.get("components") or []) > 0, "SBOM not CycloneDX with components"


def test_measured_material_is_in_the_signed_manifest():
    mf = ROOT / "MANIFEST.json"
    if not mf.is_file():
        pytest.skip("no MANIFEST.json (unsigned/mock bundle)")
    paths = {e.get("path") for e in (json.loads(mf.read_text()).get("files") or [])}
    for p in ("requirements.lock", "sbom/cyclonedx.json"):
        assert p in paths, p + " is not in the SIGNED manifest — measured-before-export must be signed, not a post-delivery output"


def test_supply_chain_mechanism_is_shipped():
    if not (ROOT / ".github" / "workflows").is_dir():
        pytest.skip("no GitHub workflow surface in this build target")
    sc = (ROOT / ".github" / "workflows" / "supply-chain.yml").read_text(errors="ignore")
    for needle in ("--require-hashes", "pip check", "cyclonedx", "pyproject-deps-sha256"):
        assert needle in sc, "supply-chain re-verify workflow lacks: " + needle
    df = (ROOT / "deploy" / "Dockerfile").read_text(errors="ignore")
    assert df.count("FROM " + chr(36) + "{BASE_IMAGE}") >= 2, "both stages must use FROM with BASE_IMAGE"
    assert "--require-hashes" in df, "Dockerfile install is not hash-locked"


def test_base_image_digest_two_state():
    EXPECTED_REF = "python:3.11-slim@sha256:db3ff2e1800a8581e2c48a27c3995339d47bdf046da21c7627accd3d51053a93"
    base = ROOT / "deploy" / "base-image.lock"
    if not EXPECTED_REF:
        # MEASUREMENT_READY: no factory measurement embedded — a digest file
        # present anyway would be an INVENTED claim, so its absence is asserted.
        assert not base.is_file(), "deploy/base-image.lock present without a factory measurement (invented digest claim)"
        pytest.skip("MEASUREMENT_READY: base digest not measured by the factory CI yet (tag-based)")
    # MEASURED_AND_LOCKED: the digest is born-in, exact, and SIGNED.
    assert base.is_file(), "LOCKED bundle: born-in deploy/base-image.lock is missing"
    ref = base.read_text(errors="ignore").strip()
    assert ref == EXPECTED_REF, "base lock != the factory-measured ref"
    digest = ref.split("@sha256:", 1)[1]
    assert len(digest) == 64 and all(c in "0123456789abcdef" for c in digest), "base digest malformed"
    mf = ROOT / "MANIFEST.json"
    if mf.is_file():
        paths = {e.get("path") for e in (json.loads(mf.read_text()).get("files") or [])}
        assert "deploy/base-image.lock" in paths, "measured base digest is not in the SIGNED manifest"
    df = (ROOT / "deploy" / "Dockerfile").read_text(errors="ignore")
    assert ("ARG BASE_IMAGE=" + EXPECTED_REF) in df, "Dockerfile default is not the digest-pinned ref"
