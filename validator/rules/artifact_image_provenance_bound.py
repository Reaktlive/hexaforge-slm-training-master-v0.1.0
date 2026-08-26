"""ARTIFACT_IMAGE_PROVENANCE_BOUND — the built image is bound to THIS signed bundle.

Fas 2.20 (external DD, Peter). The factory signs the SOURCE bundle; the container
image is built later in the customer CI. The emitted build chain therefore binds
the image to the bundle AT BUILD TIME: OCI labels resolved from the SIGNED files
(agent id, identity sha256, manifest sha256, karta sha256), the pushed digest is
captured and Sigstore-attested (actions/attest-build-provenance, SHA-pinned,
OIDC), and the binding record lands in the run summary. This twin re-derives at
receiver time that the WHOLE mechanism ships correctly wired — the attestation
executes at build time, never invented at generation (L8). Verification
commands: docs/verify_built_image.md.
"""
import pathlib
GATE_ID = "ARTIFACT_IMAGE_PROVENANCE_BOUND"; GATE_NAME = "Image Provenance Bound (built image carries the signed bundle identity as labels; pushed digest Sigstore-attested by the emitted build chain)"; GATE_KIND = "hard"
GATE_CATEGORY = "artifact"

ATTEST_PIN = "actions/attest-build-provenance@0f67c3f4856b2e3261c31976d6725780e5e4c373"

def applies(karta):
    return True

def _read(root, rel):
    p = root / rel
    return p.read_text(errors="ignore") if p.is_file() else ""

def evaluate(karta, root: pathlib.Path):
    violations = []
    checked = 0
    external_anchor = False
    if (root / ".github" / "workflows").is_dir():
        checked += 1
        bi = _read(root, ".github/workflows/build-image.yml")
        # Fas 3.42 (external DD, Peter) — the binding is only as trustworthy as WHO
        # runs the verifier. The build workflow runs the in-checkout verifier and
        # reads MANIFEST.json from the SAME mutable checkout, so whoever controls
        # the checkout can tamper the source, neutralise the verifier and update
        # its hash in the local manifest — the in-CI precheck still passes. It is
        # externally anchored only when the HexaBox root fingerprint is supplied
        # OUT-OF-BAND (secret HEXABOX_ROOT_FINGERPRINT), not read from the checkout.
        external_anchor = "HEXABOX_ROOT_FINGERPRINT" in bi
        if not bi:
            violations.append({"file": ".github/workflows/build-image.yml", "fix_hint": "image build workflow missing — nothing binds the built image to this bundle."})
        else:
            for needle in ("org.hexabox.agent-id", "org.hexabox.identity-sha256", "org.hexabox.manifest-sha256", "org.hexabox.karta-sha256",
                           "jq -r .manifest_sha256 MANIFEST.json", "sha256sum identity.json"):
                if needle not in bi:
                    violations.append({"file": ".github/workflows/build-image.yml", "fix_hint": "identity-label binding lacks '%s'." % needle})
            # Fas 3.1 (external DD, P0) — a LABEL is not a BINDING. Until 3.1 this
            # workflow read identity/MANIFEST to build labels but never verified
            # them, so a MODIFIED tree could be built and attested carrying labels
            # pointing at the ORIGINAL signed manifest: the attestation proved
            # repo/commit/workflow, never that the build context matched the
            # signature. The gate now requires the verifier to RUN in the same job
            # and the binding to be GATED on its verdict.
            for needle in ("verify_identity.py", "steps.verify.outputs.verified",
                           "org.hexabox.bundle-verified"):
                if needle not in bi:
                    violations.append({"file": ".github/workflows/build-image.yml",
                                       "fix_hint": "image build does not gate the identity binding on a real verification of the build context (missing '%s') — a modified tree could be attested as this signed bundle." % needle})
            _vpos, _bpos = bi.find("verify_identity.py"), bi.find("docker/build-push-action")
            if _vpos >= 0 and _bpos >= 0 and _vpos > _bpos:
                violations.append({"file": ".github/workflows/build-image.yml",
                                   "fix_hint": "the bundle verifier runs AFTER the build step — it must gate the build, not follow it."})
            for needle in ("org.hexabox.agent-id", "org.hexabox.identity-sha256",
                           "org.hexabox.manifest-sha256", "org.hexabox.karta-sha256"):
                if needle not in bi:
                    violations.append({"file": ".github/workflows/build-image.yml", "fix_hint": "identity-label binding lacks '%s'." % needle})
            for needle in ("steps.build.outputs.digest", ATTEST_PIN, "subject-digest:",
                           "id-token: write", "attestations: write", "GITHUB_STEP_SUMMARY"):
                if needle not in bi:
                    violations.append({"file": ".github/workflows/build-image.yml", "fix_hint": "attestation chain lacks '%s'." % needle})
        doc = _read(root, "docs/verify_built_image.md")
        if not doc:
            violations.append({"file": "docs/verify_built_image.md", "fix_hint": "verification doc missing — the image<->bundle binding cannot be re-verified by a receiver."})
        else:
            for needle in ("docker inspect", "gh attestation verify", "org.hexabox.manifest-sha256", "MANIFEST.json"):
                if needle not in doc:
                    violations.append({"file": "docs/verify_built_image.md", "fix_hint": "verification doc lacks '%s'." % needle})
    if checked == 0 and not violations:
        return {"status": "N_A", "violations": [], "details": "No GitHub workflow surface in this build target — no image build chain to bind."}
    if violations:
        return {"status": "FAIL", "violations": violations,
                "details": "The emitted image-provenance binding chain is not correctly wired. Fix the violations so the mechanism ships intact."}
    if not external_anchor:
        return {"status": "N_A", "violations": [],
                "details": "The emitted build chain WIRES the image<->bundle binding (labels from the SIGNED files, Sigstore-attested digest, verification doc) and that wiring is re-verifiable. But the trust BOOTSTRAP is NOT externally anchored: the build workflow runs the in-checkout verifier and reads MANIFEST.json from the same mutable checkout, so a party who controls the checkout can tamper the source, neutralise the verifier and update its hash in the local manifest and the in-CI precheck still passes. The binding is tamper-EVIDENT, not externally anchored; this control is N/A until an external trust anchor is configured (HexaBox root fingerprint supplied out-of-band as secret HEXABOX_ROOT_FINGERPRINT, not read from the checkout — docs/verify_root_fingerprint.md). It does NOT PASS on the presence of the wiring alone."}
    return {"status": "PASS", "violations": [],
            "details": "The emitted build chain binds the built image to THIS signed bundle AND the verification is externally anchored (out-of-band HexaBox root fingerprint): identity labels resolved at build time from the SIGNED files, the pushed digest is Sigstore-attested (pinned action, OIDC), the binding record is published in the run summary; docs/verify_built_image.md carries the re-verification commands."}
