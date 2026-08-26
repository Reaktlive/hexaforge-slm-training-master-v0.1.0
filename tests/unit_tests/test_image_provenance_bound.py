"""Image provenance bound — the built container is traceable to this signed bundle.

Fas 2.20 (external DD, Peter): the factory signs the SOURCE bundle; the image is
built in the customer CI. These tests prove the emitted build chain binds them:
identity labels resolved AT BUILD TIME from the signed files, the pushed digest
captured + Sigstore-attested (pinned action, OIDC, non-PR only), the binding
record published, and the re-verification procedure shipped. The attestation
itself runs at build time — nothing here pretends an image already exists.
"""
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]

ATTEST_PIN = "actions/attest-build-provenance@0f67c3f4856b2e3261c31976d6725780e5e4c373"


def _workflow():
    wf = ROOT / ".github" / "workflows" / "build-image.yml"
    if not (ROOT / ".github" / "workflows").is_dir():
        pytest.skip("no GitHub workflow surface in this build target")
    assert wf.is_file(), "build-image.yml missing"
    return wf.read_text(errors="ignore")


def test_build_workflow_binds_identity_labels():
    bi = _workflow()
    for needle in ("org.hexabox.agent-id", "org.hexabox.identity-sha256",
                   "org.hexabox.manifest-sha256", "org.hexabox.karta-sha256",
                   "jq -r .manifest_sha256 MANIFEST.json", "sha256sum identity.json"):
        assert needle in bi, "identity-label binding lacks: " + needle


def test_attestation_step_is_pinned_and_wired():
    bi = _workflow()
    assert ATTEST_PIN in bi, "attestation action missing or not SHA-pinned"
    for needle in ("subject-digest:", "steps.build.outputs.digest",
                   "id-token: write", "attestations: write", "GITHUB_STEP_SUMMARY"):
        assert needle in bi, "attestation chain lacks: " + needle
    # the attestation runs only when an image was actually pushed (never on PRs).
    assert bi.count("if: github.event_name != 'pull_request'") >= 2, "attestation/binding-record must be gated to pushed builds"


def test_verification_doc_ships():
    doc = ROOT / "docs" / "verify_built_image.md"
    assert doc.is_file(), "docs/verify_built_image.md missing"
    body = doc.read_text(errors="ignore")
    for needle in ("docker inspect", "gh attestation verify",
                   "org.hexabox.manifest-sha256", "MANIFEST.json", "verify_identity.py"):
        assert needle in body, "verification doc lacks: " + needle
