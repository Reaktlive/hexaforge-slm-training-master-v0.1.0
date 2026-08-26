"""HexaRecord v2 — the hashed core binds WHO / WHAT-IN / WHAT-OUT.

Fas 2.11a: principal, input_sha256 and output_sha256 live INSIDE the hashed
core (_CORE_KEYS), so attribution and data binding are tamper-evident facts,
not annotations. These tests prove it against a throwaway chain file.
"""
import json
import os

from src.shared import hexa_record as hr
from src.shared import state_paths


def _isolated_chain(tmp_path, monkeypatch):
    chain = tmp_path / "chain.jsonl"
    monkeypatch.setenv("HEXA_RECORD_PATH", str(chain))
    return chain


def test_audit_core_binds_principal_input_output(tmp_path, monkeypatch):
    """One entry binds the caller identity and the EXACT input/output hashes,
    and verify_chain accepts the intact chain."""
    _isolated_chain(tmp_path, monkeypatch)
    token = hr.set_principal("auditor@unit-test")
    try:
        rec = hr.log_event(
            "node_a", "xi", {"receipt": True}, event_id="evt-bind-1",
            input_payload={"in": 1}, output_payload={"out": 2},
        )
    finally:
        hr.reset_principal(token)
    assert rec["principal"] == "auditor@unit-test"
    assert rec["input_sha256"] == hr.canonical_sha256({"in": 1})
    assert rec["output_sha256"] == hr.canonical_sha256({"out": 2})
    assert hr.verify_chain() is True


def test_tampered_principal_breaks_the_chain(tmp_path, monkeypatch):
    """THE claim: attribution sits INSIDE the hash. Rewriting the principal
    (or a bound data hash) after the fact must break verify_chain."""
    chain = _isolated_chain(tmp_path, monkeypatch)
    token = hr.set_principal("auditor@unit-test")
    try:
        hr.log_event("node_a", "xi", {"r": 1}, event_id="evt-tamper-1",
                     input_payload={"in": 1}, output_payload={"out": 2})
    finally:
        hr.reset_principal(token)
    assert hr.verify_chain() is True

    lines = chain.read_text().splitlines()
    forged = json.loads(lines[-1])
    forged["principal"] = "someone-else"
    chain.write_text("\n".join(lines[:-1] + [json.dumps(forged)]) + "\n")
    assert hr.verify_chain() is False, "principal tamper must break the chain"

    # Same for a bound data hash: swapping input_sha256 is detected.
    chain.write_text("\n".join(lines) + "\n")
    assert hr.verify_chain() is True
    forged = json.loads(lines[-1])
    forged["input_sha256"] = hr.canonical_sha256({"in": "forged"})
    chain.write_text("\n".join(lines[:-1] + [json.dumps(forged)]) + "\n")
    assert hr.verify_chain() is False, "input-hash tamper must break the chain"


def test_absent_binding_is_visible_never_fabricated(tmp_path, monkeypatch):
    """A site that provides no input/output gets NO hash keys (absence is
    honest), and outside a request context the principal is an EXPLICIT None
    in the hashed core — visible, never silently missing."""
    _isolated_chain(tmp_path, monkeypatch)
    rec = hr.log_event("node_b", "xo", {"r": 2}, event_id="evt-absent-1")
    assert "input_sha256" not in rec
    assert "output_sha256" not in rec
    assert "principal" in rec and rec["principal"] is None
    assert hr.verify_chain() is True


def test_canonical_sha256_is_the_single_source():
    """One canonicalisation for writers, verifiers and tests: sorted-key JSON.
    Key order must not change the hash; value changes must."""
    a = hr.canonical_sha256({"x": 1, "y": 2})
    b = hr.canonical_sha256({"y": 2, "x": 1})
    assert a == b
    assert hr.canonical_sha256({"x": 1, "y": 3}) != a


def test_request_id_is_bound_in_the_hashed_core(tmp_path, monkeypatch):
    """Fas 2.11b — the caller's request_id sits INSIDE the hash when provided:
    rewriting it afterwards breaks verify_chain. Absent = key omitted, honest."""
    chain = _isolated_chain(tmp_path, monkeypatch)
    hr.log_event("node_a", "xi", {"r": 1}, event_id="evt-req-1", request_id="req-77")
    rec_no = hr.log_event("node_a", "xi", {"r": 2}, event_id="evt-req-2")
    assert "request_id" not in rec_no
    assert hr.verify_chain() is True
    lines = chain.read_text().splitlines()
    forged = json.loads(lines[0])
    forged["request_id"] = "req-FORGED"
    chain.write_text("\n".join([json.dumps(forged)] + lines[1:]) + "\n")
    assert hr.verify_chain() is False, "request_id tamper must break the chain"


def test_dropping_the_tail_is_detected_not_merely_shorter(tmp_path, monkeypatch):
    """Fas 3.9 (adversarial) — a hash chain proves links were not MODIFIED. It
    says nothing about links that were REMOVED: delete the last entries and what
    is left is a perfectly valid shorter chain. That is the tamper an attacker
    with file access actually performs — drop exactly the entries covering their
    own actions. The head sidecar records the high-water mark under the same
    lock as the append, so a dropped tail no longer verifies."""
    chain = _isolated_chain(tmp_path, monkeypatch)
    for i in range(4):
        hr.log_event("node_a", "xi", {"i": i}, event_id="evt-trunc-" + str(i))
    assert hr.verify_chain() is True
    status = hr.chain_status()
    assert status["ok"] is True and status["count"] == 4
    assert status["truncation_detectable"] is True, "the head must be recorded"

    lines = chain.read_text().splitlines()
    chain.write_text(chr(10).join(lines[:2]) + chr(10))

    # every remaining LINK is still intact - that is exactly why this is the hole
    kept = [json.loads(x) for x in chain.read_text().splitlines()]
    assert kept[0]["entry_hash"] == kept[1]["prev_hash"]

    assert hr.verify_chain() is False, "a dropped tail must not verify"
    after = hr.chain_status()
    assert after["ok"] is False
    assert after["reason"] == "truncated"
    assert after["count"] == 2 and after["expected_count"] == 4


def test_absent_head_is_disclosed_never_assumed_intact(tmp_path, monkeypatch):
    """A chain written before the head existed (or on a filesystem where the
    sidecar could not be written) must still verify its links - and must SAY
    that truncation is undetectable rather than implying a guarantee it cannot
    give. An artifact may ship a weaker posture; it may not overstate one."""
    _isolated_chain(tmp_path, monkeypatch)
    hr.log_event("node_a", "xi", {"i": 0}, event_id="evt-nohead-0")
    hr.log_event("node_a", "xi", {"i": 1}, event_id="evt-nohead-1")
    os.remove(hr._head_path())

    status = hr.chain_status()
    assert status["ok"] is True, "intact links must still verify"
    assert status["truncation_detectable"] is False
    assert status["reason"] == "no_head_recorded"


def test_head_follows_the_configured_chain_not_the_import_time_default(tmp_path, monkeypatch):
    """The head must resolve through the same path function as the chain. Pairing
    the head of one chain with the entries of another is not a hypothetical: it
    is what happens whenever HEXA_RECORD_PATH is set after import, which is every
    isolated run and every re-pointed deployment. It would report a healthy chain
    as truncated (false alarm) or, worse, accept a truncated one."""
    first = _isolated_chain(tmp_path, monkeypatch)
    for i in range(3):
        hr.log_event("node_a", "xi", {"i": i}, event_id="evt-path-a-" + str(i))
    assert os.path.exists(str(first) + ".head")

    second = tmp_path / "other_chain.jsonl"
    monkeypatch.setenv("HEXA_RECORD_PATH", str(second))
    hr.log_event("node_a", "xi", {"i": 9}, event_id="evt-path-b")

    assert os.path.exists(str(second) + ".head"), "each chain owns its own head"
    assert hr.verify_chain() is True, "a shorter NEW chain is not a truncated old one"
    assert hr.chain_status()["count"] == 1


def _bytes_read_during_one_append(node="node_a", event_id="probe"):
    """How much of the chain file a single append actually reads.

    Measured in BYTES, not milliseconds: a timing assertion in a test suite is a
    flake generator, and the property here is structural anyway - append must
    read a bounded tail, not the file.

    Restores os.pread by hand rather than through monkeypatch, because
    monkeypatch.undo() rolls back EVERY patch the test has applied - including
    the fixture's HEXA_RECORD_PATH, which would quietly send the rest of the
    test's events to a different chain and make it pass on nothing.
    """
    total = {"n": 0}
    real_pread = os.pread

    def counting_pread(fd, length, offset):
        data = real_pread(fd, length, offset)
        total["n"] += len(data)
        return data

    hr.os.pread = counting_pread
    try:
        hr.log_event(node, "xi", {"probe": True}, event_id=event_id)
    finally:
        hr.os.pread = real_pread
    return total["n"]


def test_append_reads_a_bounded_tail_not_the_whole_chain(tmp_path, monkeypatch):
    """Fas 3.14 (adversarial) — the audit write sits on the critical path of
    every node execution and is fail-closed, so it cannot be skipped or
    deferred. It used to re-read and json-parse the ENTIRE chain to find
    prev_hash: O(n) per event, O(n^2) over a run. Measured on the real signed
    bundle at 0.25 ms/event over 200 events and 1.46 ms/event over 2000, still
    climbing. No exploit and no credential is needed to trigger that - only
    traffic. Append must therefore read a BOUNDED tail whatever the chain
    weighs."""
    chain = _isolated_chain(tmp_path, monkeypatch)
    for i in range(1000):
        hr.log_event("node_a", "xi", {"i": i}, event_id="a-%d" % i)
    file_a = chain.stat().st_size
    read_a = _bytes_read_during_one_append(event_id="probe-a")

    for i in range(4000):
        hr.log_event("node_a", "xi", {"i": i}, event_id="b-%d" % i)
    file_b = chain.stat().st_size
    read_b = _bytes_read_during_one_append(event_id="probe-b")

    assert file_b > file_a * 4, "the fixture must actually grow the chain"
    assert read_a == read_b, (
        "the chain grew %dx and an append read %d bytes instead of %d: the cost "
        "still scales with history" % (file_b // file_a, read_b, read_a))
    assert read_b <= hr._TAIL_READ_BLOCK, (
        "an append read %d bytes; the bound must be a constant, not the file" % read_b)

    # Bounded reading must not have cost correctness: the whole chain still
    # verifies, and the count is exact rather than inferred.
    assert hr.verify_chain() is True
    assert hr.chain_status()["count"] == 5002


def test_a_torn_tail_still_refuses_to_re_root_the_chain(tmp_path, monkeypatch):
    """Reading only the tail must not weaken the one thing the old full scan was
    actually protecting: a half-written last line must never be read as "empty
    chain" and silently re-root the chain at GENESIS, which would orphan every
    prior entry while leaving a structurally valid file behind."""
    chain = _isolated_chain(tmp_path, monkeypatch)
    for i in range(3):
        hr.log_event("node_a", "xi", {"i": i}, event_id="torn-%d" % i)
    with open(str(chain), "a", encoding="utf-8") as f:
        f.write('{"entry_hash": "deadbe')  # a torn append: no closing brace, no newline

    try:
        hr.log_event("node_a", "xi", {"i": 99}, event_id="after-torn")
    except RuntimeError as e:
        assert "corrupt chain tail" in str(e)
    else:
        raise AssertionError("appending onto a torn tail must refuse, not re-root the chain")


def test_state_is_never_written_through_a_symlink(tmp_path, monkeypatch):
    """Fas 3.15 (adversarial) — the audit chain is located by an environment
    variable and opened by name, so a symlink planted at that path redirects the
    agent's own accountability record into any file the process can write. The
    attacker does not need to set the variable: creating one link inside a
    shared state volume is enough, which a sidecar, a restore or an earlier
    foothold can do. Demonstrated on the real signed bundle - the write went
    through. O_NOFOLLOW makes it fail closed."""
    victim = tmp_path / "outside" / "arbitrary.txt"
    victim.parent.mkdir()
    link = tmp_path / "chain.jsonl"
    os.symlink(str(victim), str(link))
    monkeypatch.setenv("HEXA_RECORD_PATH", str(link))

    try:
        hr.log_event("node_a", "xi", {"a": 1}, event_id="symlink-probe")
    except state_paths.StatePathRefused as e:
        assert "symlink" in str(e)
    else:
        raise AssertionError("the audit chain was written THROUGH a symlink")
    assert not victim.exists(), "the redirected target must never be created"


def test_state_cannot_escape_a_bound_root(tmp_path, monkeypatch):
    """The image and the k8s manifest assert that all state stays in the state
    volume. Until the root is ENFORCED that is prose: '..' in the variable walks
    straight out, which was demonstrated on the real signed bundle. O_NOFOLLOW
    cannot see this one - it only covers the final component - so containment is
    a second, independent guard rather than a restatement of the first."""
    root = tmp_path / "state"
    root.mkdir()
    monkeypatch.setenv("DOER_STATE_ROOT", str(root))
    monkeypatch.setenv("HEXA_RECORD_PATH", str(root / ".." / "escaped.jsonl"))

    try:
        hr.log_event("node_a", "xi", {"a": 2}, event_id="escape-probe")
    except state_paths.StatePathRefused as e:
        assert "outside the bound state root" in str(e)
    else:
        raise AssertionError("state escaped the bound root via '..'")
    assert not (tmp_path / "escaped.jsonl").exists()

    # The guard must not break the normal case it exists to protect.
    monkeypatch.setenv("HEXA_RECORD_PATH", str(root / "chain.jsonl"))
    hr.log_event("node_a", "xi", {"a": 3}, event_id="inside-root")
    assert hr.verify_chain() is True
    assert state_paths.state_confinement() == "confined:" + os.path.realpath(str(root))


def test_an_unbound_state_root_is_disclosed_not_assumed_safe(tmp_path, monkeypatch):
    """With no root bound, containment is simply not in force. That is a
    legitimate posture for a local run - and it must be visible as such, the
    same way clock_trust and approval_trust are, rather than read as a
    guarantee the deployment never actually asked for."""
    monkeypatch.delenv("DOER_STATE_ROOT", raising=False)
    assert state_paths.state_confinement() == "unconfined"
    # O_NOFOLLOW does NOT depend on the root: the symlink guard still holds.
    victim = tmp_path / "v.txt"
    link = tmp_path / "c.jsonl"
    os.symlink(str(victim), str(link))
    monkeypatch.setenv("HEXA_RECORD_PATH", str(link))
    try:
        hr.log_event("node_a", "xi", {"a": 4}, event_id="unconfined-symlink")
    except state_paths.StatePathRefused:
        pass
    else:
        raise AssertionError("the symlink guard must not depend on a bound root")
