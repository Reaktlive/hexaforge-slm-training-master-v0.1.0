"""ARTIFACT_BUNDLE_MANIFEST_SIGNED — every delivered file is hash-bound.

Fas 2.13e (external DD, Peter). identity.json signed karta + design +
conformance but NOT the bytes of the delivered code files: a constant change in
active runtime code (DEFAULT_RETENTION_DAYS 365->366) that broke no test still
verified as genuine. Now every delivered file (except the structurally-post-
signature exclusions, listed SIGNED in conformance.manifest.excluded) is hashed
in MANIFEST.json, whose canonical hash is Ed25519-signed in conformance.manifest.
This offline twin RE-DERIVES the manifest independently and checks it against the
signed conformance + the files on disk; the Ed25519 signature itself is checked
by verify_identity.py.
"""
import hashlib, json, os, pathlib
GATE_ID = "ARTIFACT_BUNDLE_MANIFEST_SIGNED"; GATE_NAME = "Bundle Manifest Signed (every delivered file hash-bound to the signed identity)"; GATE_KIND = "hard"
GATE_CATEGORY = "artifact"

def applies(karta):
    return True

def _canonical(v):
    if v is None or isinstance(v, bool) or isinstance(v, (int, float)) or isinstance(v, str):
        return json.dumps(v, separators=(",", ":"), ensure_ascii=False, sort_keys=False)
    if isinstance(v, list):
        return "[" + ",".join(_canonical(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{" + ",".join(json.dumps(k) + ":" + _canonical(v[k]) for k in sorted(v.keys())) + "}"
    raise TypeError("uncanonicalisable")

def evaluate(karta, root: pathlib.Path):
    violations = []
    try:
        identity = json.loads((root / "identity.json").read_text(errors="ignore"))
    except Exception as e:
        return {"status": "FAIL", "violations": [{"file": "identity.json", "fix_hint": "identity.json unreadable: %s" % e}], "details": "no identity"}
    # delivery_mode HANDOFF — a customer-owned, unsigned, editable build makes no
    # attestation claim (signature == null), so the signed file manifest is void by
    # construction. Do NOT hard-fail on the absent/void manifest: PASS with a clear
    # handoff (unsigned) note. A sealed build never carries delivery_mode == "handoff".
    if identity.get("delivery_mode") == "handoff" and identity.get("signature") is None:
        return {"status": "PASS", "violations": [],
                "details": "handoff (unsigned) build — customer-owned editable bundle makes no attestation claim; the signed file manifest is void by construction, so this gate is a PASS (not a hard-fail on the absent signature). A sealed build is still strictly enforced."}
    mconf = (identity.get("conformance") or {}).get("manifest")
    if not mconf:
        return {"status": "FAIL", "violations": [{"file": "identity.json", "fix_hint": "conformance.manifest missing — delivered files are not hash-bound to the signed identity."}], "details": "no signed manifest"}
    signed_mhash = mconf.get("manifest_sha256")
    excluded = set(mconf.get("excluded") or [])
    try:
        mdoc = json.loads((root / "MANIFEST.json").read_text(errors="ignore"))
    except Exception as e:
        return {"status": "FAIL", "violations": [{"file": "MANIFEST.json", "fix_hint": "signed manifest declared but MANIFEST.json unreadable: %s" % e}], "details": "manifest missing"}
    files = mdoc.get("files")
    if not isinstance(files, list):
        return {"status": "FAIL", "violations": [{"file": "MANIFEST.json", "fix_hint": "no files array"}], "details": "bad manifest"}
    if hashlib.sha256(_canonical(files).encode("utf-8")).hexdigest() != signed_mhash:
        violations.append({"file": "MANIFEST.json", "fix_hint": "files array hash != SIGNED manifest_sha256 — manifest tampered."})
    if mdoc.get("manifest_sha256") != signed_mhash:
        violations.append({"file": "MANIFEST.json", "fix_hint": "manifest_sha256 disagrees with SIGNED conformance.manifest."})
    manifest_paths = set()
    for ent in files:
        p = ent.get("path"); manifest_paths.add(p)
        fp = root / p
        if not fp.is_file():
            violations.append({"file": p, "fix_hint": "listed in manifest but missing on disk."}); continue
        fb = fp.read_bytes()
        if len(fb) != ent.get("size"):
            violations.append({"file": p, "fix_hint": "size != manifest — file tampered."})
        if hashlib.sha256(fb).hexdigest() != ent.get("sha256"):
            violations.append({"file": p, "fix_hint": "sha256 != manifest — file tampered."})
    import fnmatch
    # Fas 2.14b — SIGNED measured_outputs (post-release supply-chain material
    # measured by the shipped CI) are tolerated in the sweep exactly like the
    # runtime outputs; their CONTENT is validated by the supply-chain verify job.
    runtime = list(mconf.get("runtime_outputs") or []) + list(mconf.get("measured_outputs") or [])
    IGNORE = ("__pycache__", ".pytest_cache", ".git")
    on_disk = set()
    for r, dirs, fnames in os.walk(root):
        # *.egg-info: in-tree debris of the shipped package's own editable
        # install (metadata only, never imported) — same category as __pycache__.
        dirs[:] = [d for d in dirs if d not in IGNORE and not d.endswith(".egg-info")]
        for fn in fnames:
            rel = os.path.relpath(os.path.join(r, fn), root).replace(os.sep, "/")
            if rel.endswith(".pyc") or rel in excluded or any(fnmatch.fnmatch(rel, p) for p in runtime):
                continue
            on_disk.add(rel)
    extra = sorted(on_disk - manifest_paths)
    missing = sorted(manifest_paths - on_disk)
    if extra:
        violations.append({"file": extra[0], "fix_hint": "%d delivered file(s) NOT in the signed manifest (added/unlisted)." % len(extra)})
    if missing:
        violations.append({"file": missing[0], "fix_hint": "%d manifest file(s) missing on disk." % len(missing)})
    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": "Every delivered file (minus the SIGNED exclusions) is hash-bound: MANIFEST.json canonical hash == signed conformance.manifest, every file sha256+size matches, disk set == manifest path set. Ed25519 signature checked by verify_identity.py (supply-chain integrity, L7/L8)."}
