"""Rolling, PII-floored cohort store — the MO boundary standard (Fas 2.6c).

Doctrine: every event that completes the pipeline lands as a CONTRACT-SHAPED
cohort record in a local rolling store, so a later-connected MacroHub
receives the retained history (retention_policy.duration_days, default 90)
from day one. Three invariants, none hardcoded:

  * SHAPE      — the record carries ONLY the MO contract's aggregated_fields.
  * PII FLOOR  — FORBIDDEN_PII_KEYS are stripped recursively and the floor
                 WINS over the contract (a forbidden key in aggregated_fields
                 is still stripped).
  * RETENTION  — purge-on-write: every append atomically REWRITES the store
                 without expired records (atomic LOGICAL deletion — physical
                 or cryptographic erasure of underlying storage blocks is the
                 platform's responsibility: encrypted volumes / crypto-erase;
                 never claimed here); duration comes from the contract. The clock runs on
                 EVENT time: env ts is preserved even when the contract's
                 aggregated_fields omit ts; write time is stamped only when
                 the event carries no usable ts. A stored record whose ts
                 cannot be parsed is EXPIRED (fail-closed retention —
                 storage limitation wins over eternal buffering).

k_minimum gates RELEASE (export to an external MacroHub) — never local
buffering — and it counts DISTINCT TENANTS, exactly as the contract
declares ("distinct tenants observed"). Each record carries
tenant_cohort_key = HMAC-SHA256(local secret, tenant_id): a pseudonym
that never leaves the store (tenant_id itself is a FORBIDDEN_PII_KEY and
is never stored). k_count = distinct keys among live records; an event
without tenant identity buffers but NEVER counts toward k (fail-closed:
unprovable distinctness must not inflate anonymity). The store never
raises into the pipeline: cohort intelligence must not take down the
event path.

ts and tenant_cohort_key are store METADATA, kept so the clock and the
k-count can run. A future MacroHub export must re-project the release
through the contract's aggregated_fields — metadata never leaves the
boundary; ts only when the contract lists it.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.shared.anonymization import FORBIDDEN_PII_KEYS

_BUNDLE_ROOT = Path(__file__).resolve().parents[2]
_FORBIDDEN_LOWER = {k.lower() for k in FORBIDDEN_PII_KEYS}

DEFAULT_RETENTION_DAYS = 90
from src.shared.fleet_core import FLEET_K_FLOOR as _FLEET_K_FLOOR  # FTC-8 single authority
DEFAULT_K_MINIMUM = _FLEET_K_FLOOR
DEFAULT_AGGREGATED_FIELDS = ["event_id", "ts", "verdict", "confidence"]


def _effective_k(contract: dict) -> int:
    """The k-anonymity floor this cohort enforces (DD review 2026-08-15, k-policy):

        effective_k = max(FLEET_K_FLOOR, contract.k_minimum)

    FLEET_K_FLOOR is the single authority-bearing FLEET floor (5) — the value the
    coordinator's cohort aggregation also consumes. A member CONTRACT may declare a
    STRICTER floor (e.g. MacroHub / HexaIntel declare 10) and that stricter value
    is honoured; a contract can never LOWER the fleet floor — max() makes a
    contract below 5 impossible by construction rather than by convention. Before
    this guard the expression was "contract.k or DEFAULT" — a (malformed) contract
    k below the floor would have won."""
    raw = contract.get("k_minimum") if isinstance(contract, dict) else None
    try:
        contract_k = int(raw) if raw is not None else 0
    except (TypeError, ValueError):
        contract_k = 0
    # WS-1 (reviewer #4): the SIGNED manifest's k_policy.member_floor is a
    # runtime authority too — a fleet that raises the member floor changes this
    # store's behaviour on the next release; an unsigned edit is refused at
    # load (registry None -> policy {} -> the code floor still holds).
    try:
        from src.shared.fleet_trust import fleet_k_floor
        signed_floor = int(fleet_k_floor("member"))
    except Exception:
        signed_floor = int(_FLEET_K_FLOOR)
    return max(int(_FLEET_K_FLOOR), contract_k, signed_floor)


def _store_path(path: Optional[str] = None) -> Path:
    env = os.environ.get("COHORT_STORE_PATH")
    if path:
        return Path(path)
    return Path(env) if env else (_BUNDLE_ROOT / "cohort_store.jsonl")


# Fas 2.9a — tenantbaserad k-räkning. Lokal HMAC-hemlighet för
# tenant-pseudonymisering: env-override COHORT_HMAC_SECRET, annars en
# nyckelfil bredvid storen (skapas en gång, 0600). Hemligheten och de
# härledda nycklarna lämnar ALDRIG storen.
#
# Fas 2.9i — LIVSCYKEL (produktionskrav, se .env.example + docs/
# deployment-tls.md): hemligheten måste vara PERSISTENT och KONSISTENT
# över omstarter/replikor — en ny hemlighet byter pseudonymer och samma
# tenant räknas som ny mot äldre poster (k-kontinuiteten bryts). I drift:
# COHORT_HMAC_SECRET ur secret manager, eller nyckelfilen på SAMMA
# hållbara volym som storen (COHORT_STORE_PATH).
def _hmac_secret(store_path: Path) -> bytes:
    env = os.environ.get("COHORT_HMAC_SECRET")
    if env:
        return env.encode()
    keyfile = store_path.with_suffix(store_path.suffix + ".hmac.key")
    if not keyfile.exists():
        keyfile.parent.mkdir(parents=True, exist_ok=True)
        keyfile.write_text(os.urandom(32).hex())
        os.chmod(keyfile, 0o600)
    return keyfile.read_text().strip().encode()


def _tenant_key(env: Dict[str, Any], secret: bytes) -> Optional[str]:
    """Pseudonymised tenant key for k-counting, or None when the event
    carries no tenant identity (such events never count toward k).
    The raw tenant_id (a FORBIDDEN_PII_KEY) is read from the envelope,
    keyed, and discarded — it is never stored."""
    inner = env.get("payload") if isinstance(env.get("payload"), dict) else {}
    tenant = env.get("tenant_id") or inner.get("tenant_id")
    if not tenant:
        return None
    return hmac.new(secret, str(tenant).encode(), hashlib.sha256).hexdigest()


def _k_count(records: List[Dict[str, Any]]) -> int:
    """k_count = DISTINCT pseudonymised tenants among the given records —
    the contract's own semantics ("distinct tenants observed"), never
    event volume."""
    return len({r.get("tenant_cohort_key") for r in records if r.get("tenant_cohort_key")})


def mo_contract(node_id: str, root: Optional[Path] = None) -> Dict[str, Any]:
    """Read the MO anonymization_contract for node_id — the SINGLE SOURCE for
    shape/retention/k. Tolerant: a missing/unparseable contract falls back to
    the doctrine defaults (never crashes the boundary)."""
    base = Path(root) if root else _BUNDLE_ROOT
    ac: Dict[str, Any] = {}
    try:
        doc = json.loads((base / "contracts" / node_id / "mo.schema.json").read_text())
        ac = doc.get("anonymization_contract") or (doc.get("schema") or {}).get("anonymization_contract") or {}
    except (OSError, ValueError):
        ac = {}
    # retention_policy förekommer i TVÅ kontraktsformer: dict
    # ({"duration_days": 90, ...}) och ISO-8601-duration ("P30D").
    # Kontraktet är enda källan — båda formerna respekteras.
    rp = ac.get("retention_policy")
    if isinstance(rp, dict):
        retention = rp.get("duration_days")
    elif isinstance(rp, str):
        m = re.fullmatch(r"P(\d+)D", rp.strip(), re.IGNORECASE)
        retention = int(m.group(1)) if m else None
    else:
        retention = None
    fields = ac.get("aggregated_fields")
    k = ac.get("k_minimum")
    return {
        "aggregated_fields": list(fields) if isinstance(fields, list) and fields else list(DEFAULT_AGGREGATED_FIELDS),
        "retention_days": int(retention) if isinstance(retention, (int, float)) and retention > 0 else DEFAULT_RETENTION_DAYS,
        "k_minimum": int(k) if isinstance(k, (int, float)) and k > 0 else DEFAULT_K_MINIMUM,
    }


def _strip_pii(obj: Any) -> Any:
    """Recursive PII floor — the floor WINS over any contract field list."""
    if isinstance(obj, dict):
        return {k: _strip_pii(v) for k, v in obj.items()
                if not (isinstance(k, str) and k.lower() in _FORBIDDEN_LOWER)}
    if isinstance(obj, list):
        return [_strip_pii(x) for x in obj]
    return obj


def _parse_ts(value: Any) -> Optional[datetime]:
    if not isinstance(value, str) or not value.strip():
        return None
    raw = value.strip()
    if raw.endswith(("Z", "z")):
        raw = raw[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _is_live(rec: Dict[str, Any], cutoff: datetime) -> bool:
    """Fail-closed retention: a record whose ts is missing or unparseable is
    EXPIRED and purged on the next write — storage limitation wins; corrupt
    rows never gain eternal retention."""
    dt = _parse_ts(rec.get("ts"))
    return dt is not None and dt >= cutoff


def build_cohort_record(env: Dict[str, Any], aggregated_fields: List[str]) -> Dict[str, Any]:
    """Project the CONTRACT's aggregated_fields out of the envelope/payload,
    then apply the PII floor (floor wins). ts is retention METADATA: the
    EVENT's ts is preserved even when the contract omits it from
    aggregated_fields (projection must never restamp history); write time
    is stamped only when the event carries no usable ts — the retention
    clock always runs, on the truest time available."""
    inner = env.get("payload") if isinstance(env.get("payload"), dict) else {}
    source: Dict[str, Any] = {**inner, "event_id": env.get("event_id", inner.get("event_id")), "ts": env.get("ts", inner.get("ts"))}
    record = {k: source.get(k) for k in aggregated_fields if k in source and source.get(k) is not None}
    record = _strip_pii(record)
    if not record.get("ts"):
        source_ts = _parse_ts(source.get("ts"))
        record["ts"] = source_ts.isoformat() if source_ts else datetime.now(timezone.utc).isoformat()
    return record


def _load(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    out: List[Dict[str, Any]] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue  # skadad rad räknas aldrig in i kohorten
        if isinstance(rec, dict):
            out.append(rec)
    return out


def _rewrite(path: Path, records: List[Dict[str, Any]]) -> None:
    """Atomic purge-on-write: tmp + os.replace — the expired records are GONE
    from the live file, never appended-around. This is atomic LOGICAL
    deletion (L8): physical/cryptographic erasure of old storage blocks is
    the deployment platform's job (encrypted volume, crypto-erase) — this
    module never claims it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w") as f:
        for rec in records:
            f.write(json.dumps(rec, sort_keys=True, default=str) + "\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def append_event(env: Dict[str, Any], *, contract: Dict[str, Any], path: Optional[str] = None) -> Dict[str, Any]:
    """Append one contract-shaped record and purge expired ones (rolling
    retention from the CONTRACT). Returns the boundary status."""
    p = _store_path(path)
    retention_days = int(contract.get("retention_days") or DEFAULT_RETENTION_DAYS)
    k_minimum = _effective_k(contract)  # max(FLEET_K_FLOOR, contract k) — never below the fleet floor
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    records = _load(p)
    kept = [r for r in records if _is_live(r, cutoff)]
    purged = len(records) - len(kept)
    rec = build_cohort_record(env, contract.get("aggregated_fields") or DEFAULT_AGGREGATED_FIELDS)
    tk = _tenant_key(env, _hmac_secret(p))
    if tk:
        rec["tenant_cohort_key"] = tk  # store-METADATA (som ts) — släpps aldrig
    kept.append(rec)
    _rewrite(p, kept)
    k_count = _k_count(kept)
    return {
        "cohort_size": len(kept),
        "purged": purged,
        "k_count": k_count,
        "released": k_count >= k_minimum,
        "retention_days": retention_days,
        "k_minimum": k_minimum,
    }


def cohort_status(*, contract: Dict[str, Any], path: Optional[str] = None) -> Dict[str, Any]:
    """Read-only boundary status (size + k-gated release flag)."""
    p = _store_path(path)
    retention_days = int(contract.get("retention_days") or DEFAULT_RETENTION_DAYS)
    k_minimum = _effective_k(contract)  # max(FLEET_K_FLOOR, contract k) — never below the fleet floor
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    live = [r for r in _load(p) if _is_live(r, cutoff)]
    k_count = _k_count(live)
    return {"cohort_size": len(live), "k_count": k_count,
            "released": k_count >= k_minimum,
            "retention_days": retention_days, "k_minimum": k_minimum}


def _karta_vertical() -> str:
    """Agent vertical from the compiled karta (bundle root) — the release's
    top-level vertical field. Never crashes the boundary."""
    try:
        karta = json.loads((_BUNDLE_ROOT / "karta.compiled.json").read_text())
        v = (karta.get("metadata") or {}).get("vertical")
        return str(v) if v else "unspecified"
    except (OSError, ValueError):
        return "unspecified"


# Fas 2.9b (L7 Portkonformanslagen) — den kontraktsformade MO-releasen.
# Endast AGGREGATSTATISTIK lämnar gränsen: aldrig enskilda poster, aldrig
# store-metadata (ts/tenant_cohort_key), aldrig värdeuppräkningar (ett värde
# som setts en gång skulle exponera en enskild händelse). Anroparen
# validerar resultatet mot portens GENERERADE modell innan något lämnar.
def _fleet_stamp(env: Dict[str, Any]) -> Dict[str, Any]:
    """DD P0 — stamp + SIGN the FleetSignal envelope with this member's fleet
    identity (fleet_trust). Never raises: an unprovisioned member yields an
    explicitly UNSIGNED envelope (sig="unsigned") that a coordinator rejects —
    fail-closed at the consumer trust boundary, honest at the producer."""
    try:
        from src.shared.fleet_trust import stamp_and_sign
        return stamp_and_sign(env)
    except Exception:
        env.setdefault("member_agent_id", "unprovisioned")
        env.setdefault("karta_hash", "unprovisioned")
        env.setdefault("doctrine_version", "unprovisioned")
        env.setdefault("sequence", 0)
        env.setdefault("nonce", "unprovisioned")
        env.setdefault("emitted_at", datetime.now(timezone.utc).isoformat())
        env["sig"] = "unsigned"
        return env


def build_release(*, contract: Dict[str, Any], path: Optional[str] = None) -> Dict[str, Any]:
    """The k-anonymous MO release, or a HELD envelope when k is not met.

    Fas 3.18 (adversarial finding). The k floor is the entire point of this
    boundary, and it used to live in the CALLER: the MO handler checked
    stat["released"] before calling this. Calling build_release directly at
    k=1 produced an aggregate with cohort_size 1 - a summary of exactly one
    event, released under a name that says k-anonymous. Demonstrated on the
    real signed bundle.

    That is the shape Fas 3.7 already paid for once: a property that must hold
    on every path, enforced by convention at one call site. A refactor, a second
    caller, or a node that composes this seam differently gets a sub-k release
    and nothing says no. The function that HAS the count is the only place the
    floor can be authoritative, so the floor now lives here. The handler keeps
    its check - two guards, not one moved.
    """
    p = _store_path(path)
    retention_days = int(contract.get("retention_days") or DEFAULT_RETENTION_DAYS)
    k_minimum = _effective_k(contract)  # max(FLEET_K_FLOOR, contract k) — never below the fleet floor
    _now = datetime.now(timezone.utc)
    cutoff = _now - timedelta(days=retention_days)
    # Fas 3.50 — FleetSignal/v1 envelope fields: the cohort-cycle correlation id +
    # aggregation window every MO must carry so a MacroHub intake (coordinator XI,
    # required cycle_id/window_start/window_end) can consume ANY specialist's MO.
    _window_start = cutoff.isoformat()
    _window_end = _now.isoformat()
    _cycle_id = "cycle-" + _now.strftime("%Y%m%dT%H%M%SZ")
    live = [r for r in _load(p) if _is_live(r, cutoff)]
    k_count = _k_count(live)
    if k_count < k_minimum:
        return _fleet_stamp({
            "schema_version": "fleet_signal/v1",
            "event_type": "k_anonymous_cohort_summary",
            "vertical": _karta_vertical(),
            "aggregate_payload": None,
            "k_count": k_count,
            "cycle_id": _cycle_id,
            "window_start": _window_start,
            "window_end": _window_end,
            "released": False,
            "held_reason": ("k_count %d is below the contract's k_minimum %d; no aggregate is "
                            "built, not even an empty one" % (k_count, k_minimum)),
        })
    fields = [f for f in (contract.get("aggregated_fields") or []) if f not in ("ts", "tenant_cohort_key")]
    aggregate: Dict[str, Any] = {
        "cohort_size": len(live),
        "window_days": retention_days,
        "fields": {
            f: {
                "present": sum(1 for r in live if f in r),
                "distinct_values": len({json.dumps(r.get(f), sort_keys=True, default=str) for r in live if f in r}),
            }
            for f in fields
        },
    }
    return _fleet_stamp({
        "schema_version": "fleet_signal/v1",
        "event_type": "k_anonymous_cohort_summary",
        "vertical": _karta_vertical(),
        "aggregate_payload": aggregate,
        "k_count": k_count,
        "cycle_id": _cycle_id,
        "window_start": _window_start,
        "window_end": _window_end,
        "released": True,
    })
