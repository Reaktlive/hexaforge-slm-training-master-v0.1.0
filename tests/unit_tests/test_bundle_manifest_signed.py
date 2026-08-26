"""Signed file manifest — every delivered file is hash-bound to the identity.

Fas 2.13e (external DD, Peter): identity.json signed karta + design +
conformance but not the bytes of the delivered code. A constant change in active
runtime code (DEFAULT_RETENTION_DAYS 365->366) that broke no test was invisible.
Now every delivered file is hashed in MANIFEST.json whose canonical hash is
Ed25519-signed in conformance.manifest, and verify_identity.py re-checks it
BEFORE any bundle code runs. These tests prove coverage, the signed link, and
that tampering a runtime file is caught.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _load(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return json.load(f)


# delivery_mode HANDOFF — a customer-owned, unsigned, editable build ships no
# signed file manifest (identity.json carries delivery_mode == "handoff" and
# signature == null). There is nothing to hash-bind, so the whole module skips
# honestly rather than hard-failing on the absent signed manifest.
if _load("identity.json").get("delivery_mode") == "handoff":
    pytest.skip("handoff build — no signed manifest", allow_module_level=True)


def test_every_delivered_file_is_in_the_signed_manifest():
    manifest = _load("MANIFEST.json")
    files = manifest.get("files")
    assert isinstance(files, list) and files, "MANIFEST.json has no files"
    listed = set()
    for ent in files:
        p = ent["path"]
        listed.add(p)
        fp = os.path.join(ROOT, p)
        assert os.path.isfile(fp), "manifest lists %s but it is missing" % p
        fb = open(fp, "rb").read()
        assert len(fb) == ent["size"], "%s: size mismatch" % p
        assert hashlib.sha256(fb).hexdigest() == ent["sha256"], "%s: sha256 mismatch" % p
    # core runtime + verifier files are covered (not just docs)
    for must in ("src/main.py", "runtime/api_server.py", "verify_identity.py", "verify_release.sh"):
        assert must in listed, "%s is not hash-bound in the manifest" % must


def test_manifest_hash_is_in_the_signed_conformance():
    manifest = _load("MANIFEST.json")
    identity = _load("identity.json")
    mconf = (identity.get("conformance") or {}).get("manifest")
    assert mconf, "conformance carries no manifest block — the manifest is not signed"
    assert mconf.get("manifest_sha256") == manifest.get("manifest_sha256"), "MANIFEST.json hash != signed conformance.manifest"
    assert mconf.get("file_count") == len(manifest.get("files") or []), "signed file_count != MANIFEST.json"
    excluded = set(mconf.get("excluded") or [])
    for x in ("identity.json", "MANIFEST.json", "generator.pub", "root.pub"):
        assert x in excluded, "%s must be in the SIGNED exclusion set" % x


def test_tampering_a_runtime_file_is_detected(tmp_path):
    identity = _load("identity.json")
    if identity.get("signature_pending"):
        pytest.skip("identity is unsigned (pending) — signature+manifest tamper check needs a signed bundle")
    dst = os.path.join(str(tmp_path), "bundle")
    # Copy the SHIPPABLE set: exclude caches AND the bundle's own runtime outputs
    # (the offline engine / pytest may already have written them into ROOT). ALL
    # supply-chain material (requirements.lock, sbom/cyclonedx.json and — once the
    # factory has measured the base digest — deploy/base-image.lock) is born-in
    # SIGNED manifest content (Fas 2.18/2.19), so it MUST stay in the pristine
    # copy or verify_identity correctly fails on a missing signed file. Nothing
    # is written post-signing (the shipped workflow is verify-only).
    shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns(
        "__pycache__", ".pytest_cache", ".git", "*.pyc", "*.egg-info",
        "hexa_record.jsonl", "hexa_record.jsonl.head", "hexa_source.jsonl",
        "cohort_store.jsonl*", "ccas_approvals.jsonl", "ccas_approvals.jsonl.hw",
        "artifact_conformance.json", "doctrine_reverification.json",
        "report.txt", "slm_eval.json"))
    base = subprocess.run([sys.executable, "verify_identity.py", "."], cwd=dst, capture_output=True, text=True)
    assert base.returncode == 0, "verify_identity failed on the pristine copy: %s %s" % (base.stdout, base.stderr)
    manifest = json.load(open(os.path.join(dst, "MANIFEST.json")))
    target = next(e["path"] for e in manifest["files"]
                  if e["path"].endswith(".py") and e["artifact_class"] in ("runtime", "handler"))
    with open(os.path.join(dst, target), "a") as f:
        f.write("# hexabox-tamper-probe 365 to 366")
    after = subprocess.run([sys.executable, "verify_identity.py", "."], cwd=dst, capture_output=True, text=True)
    assert after.returncode != 0, "verify_identity did NOT detect tampering of %s" % target
    assert "tamper" in (after.stdout + after.stderr).lower(), "failure was not attributed to tampering"
