"""Fas 2.6c — MO-kohortstandarden: rullande PII-golvad kohortstore.

Kontraktet (contracts/hexaforge_slm_training_master_egress_octa/mo.schema.json) är ENDA källan för
form (aggregated_fields), retention (retention_policy.duration_days) och
k_minimum. Bufferten fylls på varje OK-event; en senare påkopplad MacroHub
får den kvarhållna historiken från dag ett.
"""
import json
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from runtime.api_server import app
from src.shared import cohort_store


@pytest.fixture
def client():
    return TestClient(app)


def test_contract_is_the_single_source():
    ac = cohort_store.mo_contract("hexaforge_slm_training_master_egress_octa")
    raw = json.load(open("contracts/hexaforge_slm_training_master_egress_octa/mo.schema.json"))
    declared = raw.get("anonymization_contract") or (raw.get("schema") or {}).get("anonymization_contract") or {}
    rp = declared.get("retention_policy")
    if isinstance(rp, dict) and rp.get("duration_days"):
        assert ac["retention_days"] == rp["duration_days"]
    elif isinstance(rp, str):
        import re as _re
        m = _re.fullmatch(r"P(\d+)D", rp.strip(), _re.IGNORECASE)
        if m:
            assert ac["retention_days"] == int(m.group(1))
    assert ac["retention_days"] > 0
    assert ac["k_minimum"] > 0
    assert isinstance(ac["aggregated_fields"], list) and ac["aggregated_fields"]


def test_ok_event_lands_in_store(client, tmp_path, monkeypatch):
    monkeypatch.setenv("COHORT_STORE_PATH", str(tmp_path / "cohort.jsonl"))
    ev = dict({})
    ev.update({"event_id": "evt-cohort-1", "source": "cohort-suite", "payload": {"subject": "x"}})
    r = client.post("/api/events", json=ev)
    assert r.status_code == 200, r.text
    body = r.json()
    if body.get("status") != "ok":
        pytest.skip("pipeline degraderad före egress — kohortposten kräver ok-vägen")
    cohort = body.get("cohort") or {}
    assert cohort.get("size", 0) >= 1, body
    lines = [l for l in open(tmp_path / "cohort.jsonl").read().splitlines() if l.strip()]
    assert len(lines) == cohort["size"]
    rec = json.loads(lines[-1])
    assert rec.get("ts"), rec  # retention-klockan går alltid


def test_retention_purges_expired(tmp_path, monkeypatch):
    monkeypatch.setenv("COHORT_STORE_PATH", str(tmp_path / "cohort.jsonl"))
    ac = cohort_store.mo_contract("hexaforge_slm_training_master_egress_octa")
    old_ts = (datetime.now(timezone.utc) - timedelta(days=ac["retention_days"] + 1)).isoformat()
    cohort_store.append_event({"event_id": "evt-old", "ts": old_ts, "payload": {}}, contract=ac)
    stat = cohort_store.append_event(
        {"event_id": "evt-new", "ts": datetime.now(timezone.utc).isoformat(), "payload": {}}, contract=ac
    )
    # Den utgångna posten är BORTA ur filen (purge-on-write), inte bara dold.
    assert stat["purged"] == 1 and stat["cohort_size"] == 1
    lines = [l for l in open(tmp_path / "cohort.jsonl").read().splitlines() if l.strip()]
    assert len(lines) == 1 and "evt-old" not in lines[0]


def test_event_ts_survives_contract_projection():
    # Fas 2.6d (B9-kandidatens fällda fall): kontraktets aggregated_fields
    # utelämnar ts ("vertical"/"event_type"-formen) — händelsens ts får
    # ALDRIG omstämplas till skrivtid, då går retentionsklockan på fel tid
    # och purgen dör.
    old = "2020-01-01T00:00:00+00:00"
    rec = cohort_store.build_cohort_record(
        {"event_id": "e-ts", "ts": old, "payload": {}}, ["vertical", "event_type"]
    )
    assert rec.get("ts") == old, rec


def test_corrupt_ts_is_purged_fail_closed(tmp_path, monkeypatch):
    # Fas 2.6d: oparsbar ts ⇒ posten är UTGÅNGEN (lagringsminimering vinner)
    # — korrupta rader får aldrig evig retention.
    monkeypatch.setenv("COHORT_STORE_PATH", str(tmp_path / "cohort.jsonl"))
    ac = cohort_store.mo_contract("hexaforge_slm_training_master_egress_octa")
    (tmp_path / "cohort.jsonl").write_text('{"ts": "not-a-timestamp"}\n')
    stat = cohort_store.append_event(
        {"event_id": "evt-fresh", "ts": datetime.now(timezone.utc).isoformat(), "payload": {}}, contract=ac
    )
    assert stat["purged"] == 1 and stat["cohort_size"] == 1


def test_pii_floor_wins_over_contract():
    rec = cohort_store.build_cohort_record(
        {"event_id": "e1", "ts": "2026-01-01T00:00:00Z",
         "payload": {"email": "x@y.se", "verdict": "ok"}},
        ["event_id", "ts", "email", "verdict"],
    )
    assert "email" not in rec, rec
    assert rec.get("verdict") == "ok"


def test_release_is_k_gated(tmp_path, monkeypatch):
    monkeypatch.setenv("COHORT_STORE_PATH", str(tmp_path / "cohort.jsonl"))
    ac = cohort_store.mo_contract("hexaforge_slm_training_master_egress_octa")
    stat = cohort_store.append_event(
        {"event_id": "evt-k", "ts": datetime.now(timezone.utc).isoformat(),
         "tenant_id": "tenant-a", "payload": {}}, contract=ac
    )
    # Fas 2.9a (L7): released grindas på DISTINKTA TENANTS (k_count) —
    # aldrig på eventvolym (cohort_size). 2.6c:s eventräkning var en
    # felläsning av kontraktet som detta test tidigare cementerade.
    assert stat["released"] is (stat["k_count"] >= ac["k_minimum"])


def test_k_counts_distinct_tenants_not_events(tmp_path, monkeypatch):
    # Fas 2.9a (L7): kontraktet säger "distinct tenants observed" — N events
    # från SAMMA tenant får aldrig uppfylla k. Exakt DD-reprot som fällde
    # 2.6c-implementationen.
    monkeypatch.setenv("COHORT_STORE_PATH", str(tmp_path / "cohort.jsonl"))
    # DD k-policy (2026-08-15): the enforced floor is max(FLEET_K_FLOOR, contract k)
    # — a contract can never LOWER the fleet floor, so this test runs AT the floor.
    K = cohort_store.DEFAULT_K_MINIMUM
    ac = {"aggregated_fields": ["event_id", "ts"], "retention_days": 90, "k_minimum": K}
    now = datetime.now(timezone.utc).isoformat()
    # K events from the SAME tenant: cohort_size grows, k_count stays 1, never released.
    for i in range(K):
        stat = cohort_store.append_event({"event_id": f"e{i}", "ts": now, "tenant_id": "t-1", "payload": {}}, contract=ac)
    assert stat["cohort_size"] == K and stat["k_count"] == 1
    assert stat["released"] is False
    # Distinct tenants up to K-1: still held. The K-th distinct tenant releases.
    for j in range(2, K):
        stat = cohort_store.append_event({"event_id": f"d{j}", "ts": now, "tenant_id": f"t-{j}", "payload": {}}, contract=ac)
        assert stat["k_count"] == j and stat["released"] is False
    stat = cohort_store.append_event({"event_id": "dK", "ts": now, "tenant_id": f"t-{K}", "payload": {}}, contract=ac)
    assert stat["k_count"] == K and stat["released"] is True
    # Pseudonymen lagras — men rå tenant_id (FORBIDDEN_PII_KEY) ALDRIG.
    raw = open(tmp_path / "cohort.jsonl").read()
    assert "tenant_cohort_key" in raw and '"tenant_id"' not in raw
    assert "t-1" not in raw and f"t-{K}" not in raw


def test_contract_cannot_lower_the_fleet_k_floor(tmp_path, monkeypatch):
    # DD k-policy (external reviews 2026-08-15): the fleet floor is a FLOOR by
    # construction — effective_k = max(FLEET_K_FLOOR, contract_k). A member
    # contract declaring k=2 must NOT release at 2 distinct tenants; it releases
    # at the fleet floor. A stricter contract (floor+3) is honoured as-is.
    monkeypatch.setenv("COHORT_STORE_PATH", str(tmp_path / "cohort.jsonl"))
    F = cohort_store.DEFAULT_K_MINIMUM
    assert cohort_store._effective_k({"k_minimum": 2}) == F
    assert cohort_store._effective_k({"k_minimum": F + 3}) == F + 3
    assert cohort_store._effective_k({}) == F
    ac_low = {"aggregated_fields": ["event_id", "ts"], "retention_days": 90, "k_minimum": 2}
    now = datetime.now(timezone.utc).isoformat()
    stat = None
    for j in range(1, F):
        stat = cohort_store.append_event({"event_id": f"low-{j}", "ts": now, "tenant_id": f"t-{j}", "payload": {}}, contract=ac_low)
    assert stat["k_count"] == F - 1 and stat["released"] is False, "a k=2 contract released below the fleet floor"
    stat = cohort_store.append_event({"event_id": "low-F", "ts": now, "tenant_id": f"t-{F}", "payload": {}}, contract=ac_low)
    assert stat["k_count"] == F and stat["released"] is True


def test_missing_tenant_never_counts_toward_k(tmp_path, monkeypatch):
    # Fas 2.9a: händelse utan tenantidentitet buffras men räknas ALDRIG mot
    # k (fail-closed — obevisbar distinkthet får inte blåsa upp anonymiteten).
    monkeypatch.setenv("COHORT_STORE_PATH", str(tmp_path / "cohort.jsonl"))
    ac = {"aggregated_fields": ["event_id", "ts"], "retention_days": 90, "k_minimum": 1}
    now = datetime.now(timezone.utc).isoformat()
    for i in range(3):
        stat = cohort_store.append_event({"event_id": f"anon-{i}", "ts": now, "payload": {}}, contract=ac)
    assert stat["cohort_size"] == 3 and stat["k_count"] == 0
    assert stat["released"] is False


def test_mo_release_is_contract_shaped_and_validated(tmp_path, monkeypatch):
    # Fas 2.9b (L7): under k hålls släppet (release=None); när k nås
    # emitterar porten KONTRAKTSFORMEN {event_type, vertical,
    # aggregate_payload, k_count} — validerad mot portens egen genererade
    # modell, och utan poster/metadata/värdeuppräkningar.
    import asyncio
    monkeypatch.setenv("COHORT_STORE_PATH", str(tmp_path / "cohort.jsonl"))
    from src.nodes.hexaforge_slm_training_master_egress_octa import handler as egress
    ac = cohort_store.mo_contract("hexaforge_slm_training_master_egress_octa")
    now = datetime.now(timezone.utc).isoformat()
    r = asyncio.run(egress.handle_mo({"event_id": "seed-0", "ts": now, "tenant_id": "t-0", "payload": {}}))
    if not r["released"]:
        assert r["release"] is None  # hålls under k — inget kontraktsformat släpp claimas
    for i in range(1, ac["k_minimum"]):
        r = asyncio.run(egress.handle_mo({"event_id": f"seed-{i}", "ts": now, "tenant_id": f"t-{i}", "payload": {}}))
    assert r["released"] is True and isinstance(r["release"], dict), r
    rel = r["release"]
    assert set(("event_type", "vertical", "aggregate_payload", "k_count")) <= set(rel)
    assert rel["k_count"] >= ac["k_minimum"]
    blob = json.dumps(rel)
    assert "tenant_cohort_key" not in blob  # metadata lämnar aldrig gränsen


def test_pipeline_shaped_mo_event_fills_aggregates(tmp_path, monkeypatch):
    # Fas 2.10b (extern DD på B9, punkt 2): releasen var kontraktsgiltig men
    # INFORMATIONSTOM — pipelinen matade hela composite och aggregated_fields
    # fanns inte där projektionen läser. Detta test bygger MO-eventet med
    # PIPELINENS konstruktion: samma mall (moFeedEnvPy) OCH runtimens egen
    # _mo_event_type — kan inte glida isär från run_pipeline.
    monkeypatch.setenv("COHORT_STORE_PATH", str(tmp_path / "cohort.jsonl"))
    from runtime.api_server import _mo_event_type
    # DD k-policy (2026-08-15): run at the enforced fleet floor (a contract cannot lower it).
    K = cohort_store.DEFAULT_K_MINIMUM
    ac = {"aggregated_fields": ["vertical", "event_type"], "retention_days": 90, "k_minimum": K}
    now = datetime.now(timezone.utc).isoformat()
    stat = None
    for i in range(K):
        _composite = {"status": "ok", "disposition": "release", "verdict": "PASS"}
        event_id = f"pipe-{i}"
        env = {"event_id": event_id, "ts": now, "tenant_id": f"t-{i}", "payload": {"vertical": "ai-ml-ops", "event_type": _mo_event_type(_composite)}}
        stat = cohort_store.append_event(env, contract=ac)
    assert stat is not None and stat["k_count"] == K and stat["released"] is True
    rel = cohort_store.build_release(contract=ac)
    fields = rel["aggregate_payload"]["fields"]
    # Aggregatet är ALDRIG informationstomt när pipelinen matar rätt:
    assert fields["vertical"]["present"] == K and fields["vertical"]["distinct_values"] == 1
    assert fields["event_type"]["present"] == K and fields["event_type"]["distinct_values"] >= 1
    assert rel["k_count"] == K


def test_mo_probe_without_event_is_read_only(tmp_path, monkeypatch):
    # Fas 2.9b: anrop utan event_id är en läs-bara probe — porten buffrar
    # aldrig icke-händelser (kohorten kan inte förfalskas via porten).
    import asyncio
    monkeypatch.setenv("COHORT_STORE_PATH", str(tmp_path / "cohort.jsonl"))
    from src.nodes.hexaforge_slm_training_master_egress_octa import handler as egress
    r1 = asyncio.run(egress.handle_mo({}))
    r2 = asyncio.run(egress.handle_mo({"note": "still not an event"}))
    assert r1.get("probe") is True and r2.get("probe") is True
    assert r2["cohort_size"] == 0 and r2["release"] is None


def test_the_k_floor_belongs_to_build_release_not_to_its_caller(tmp_path, monkeypatch):
    """Fas 3.18 (adversarial) — the k floor is the entire point of this
    boundary, and it used to live in the CALLER: the MO handler checked
    stat["released"] before calling build_release. Calling build_release
    DIRECTLY at k=1 returned an aggregate with cohort_size 1 - a summary of
    exactly one event, under a name that says k-anonymous. Demonstrated on the
    real signed bundle.

    That is the shape Fas 3.7 already paid for: a property that must hold on
    every path, enforced by convention at one call site. The function that has
    the count is the only place the floor can be authoritative."""
    monkeypatch.setenv("COHORT_STORE_PATH", str(tmp_path / "cohort.jsonl"))
    ac = cohort_store.mo_contract("pharmacovigilance_signal_egress_octa")
    k_min = int(ac["k_minimum"])

    for i in range(1, k_min):
        cohort_store.append_event(
            {"event_id": "evt-%d" % i, "ts": datetime.now(timezone.utc).isoformat(),
             "tenant_id": "tenant-%d" % i, "payload": {}}, contract=ac)
        held = cohort_store.build_release(contract=ac)
        assert held["released"] is False, held
        assert held["aggregate_payload"] is None, (
            "an aggregate describing %d tenant(s) was built below k=%d" % (i, k_min))
        assert "below the contract" in held["held_reason"]

    # Exactly at the floor it opens - a guard that never releases is not a
    # guard, it is a broken boundary.
    cohort_store.append_event(
        {"event_id": "evt-k", "ts": datetime.now(timezone.utc).isoformat(),
         "tenant_id": "tenant-%d" % k_min, "payload": {}}, contract=ac)
    out = cohort_store.build_release(contract=ac)
    assert out["released"] is True and out["k_count"] == k_min
    assert out["aggregate_payload"]["cohort_size"] == k_min


def test_volume_from_one_tenant_never_opens_the_floor(tmp_path, monkeypatch):
    """k counts DISTINCT TENANTS, so no amount of traffic from a single tenant
    can release an aggregate about that tenant alone. Asserted against
    build_release itself rather than against the caller's flag, because the
    flag is what the previous test showed could be bypassed."""
    monkeypatch.setenv("COHORT_STORE_PATH", str(tmp_path / "cohort.jsonl"))
    ac = cohort_store.mo_contract("pharmacovigilance_signal_egress_octa")
    for i in range(int(ac["k_minimum"]) * 4):
        cohort_store.append_event(
            {"event_id": "evt-%d" % i, "ts": datetime.now(timezone.utc).isoformat(),
             "tenant_id": "the-only-tenant", "payload": {}}, contract=ac)
    out = cohort_store.build_release(contract=ac)
    assert out["k_count"] == 1
    assert out["released"] is False and out["aggregate_payload"] is None
