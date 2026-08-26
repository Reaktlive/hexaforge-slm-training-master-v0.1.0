import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterEgressOctaXiSchema, HexaforgeSlmTrainingMasterEgressOctaXoSchema, HexaforgeSlmTrainingMasterEgressOctaYiSchema, HexaforgeSlmTrainingMasterEgressOctaYoSchema, HexaforgeSlmTrainingMasterEgressOctaZiSchema, HexaforgeSlmTrainingMasterEgressOctaZoSchema, HexaforgeSlmTrainingMasterEgressOctaMiSchema, HexaforgeSlmTrainingMasterEgressOctaMoSchema


def test_hexaforge_slm_training_master_egress_octa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterEgressOctaXiSchema()


def test_hexaforge_slm_training_master_egress_octa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterEgressOctaXoSchema(action="smoke-action", target="smoke-target", governance_metadata={})


def test_hexaforge_slm_training_master_egress_octa_xo_requires_action():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterEgressOctaXoSchema(target="smoke-target", governance_metadata={})


def test_hexaforge_slm_training_master_egress_octa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterEgressOctaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_egress_octa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterEgressOctaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_egress_octa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterEgressOctaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_egress_octa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterEgressOctaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_egress_octa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterEgressOctaZiSchema()


def test_hexaforge_slm_training_master_egress_octa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterEgressOctaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_egress_octa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterEgressOctaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_egress_octa_mi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterEgressOctaMiSchema(cycle_id="smoke-cycle_id")


def test_hexaforge_slm_training_master_egress_octa_mi_requires_cycle_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterEgressOctaMiSchema()


def test_hexaforge_slm_training_master_egress_octa_mo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterEgressOctaMoSchema(schema_version="smoke-schema_version", event_type="smoke-event_type", vertical="smoke-vertical", aggregate_payload={}, k_count=5, cycle_id="smoke-cycle_id", window_start="2026-01-01T00:00:00Z", window_end="2026-01-01T00:00:00Z", member_agent_id="smoke-member_agent_id", karta_hash="smoke-karta_hash", doctrine_version="smoke-doctrine_version", evidence={}, evidence_digest="smoke-evidence_digest", sequence=0, nonce="smoke-nonce", emitted_at="smoke-emitted_at", sig="smoke-sig")


def test_hexaforge_slm_training_master_egress_octa_mo_requires_schema_version():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterEgressOctaMoSchema(event_type="smoke-event_type", vertical="smoke-vertical", aggregate_payload={}, k_count=5, cycle_id="smoke-cycle_id", window_start="2026-01-01T00:00:00Z", window_end="2026-01-01T00:00:00Z", member_agent_id="smoke-member_agent_id", karta_hash="smoke-karta_hash", doctrine_version="smoke-doctrine_version", evidence={}, evidence_digest="smoke-evidence_digest", sequence=0, nonce="smoke-nonce", emitted_at="smoke-emitted_at", sig="smoke-sig")


def test_hexaforge_slm_training_master_egress_octa_mo_rejects_k_count_below_declared_minimum():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterEgressOctaMoSchema(schema_version="smoke-schema_version", event_type="smoke-event_type", vertical="smoke-vertical", aggregate_payload={}, cycle_id="smoke-cycle_id", window_start="2026-01-01T00:00:00Z", window_end="2026-01-01T00:00:00Z", member_agent_id="smoke-member_agent_id", karta_hash="smoke-karta_hash", doctrine_version="smoke-doctrine_version", evidence={}, evidence_digest="smoke-evidence_digest", sequence=0, nonce="smoke-nonce", emitted_at="smoke-emitted_at", sig="smoke-sig", k_count=4)

