import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterEnrichmentHexaXiSchema, HexaforgeSlmTrainingMasterEnrichmentHexaXoSchema, HexaforgeSlmTrainingMasterEnrichmentHexaYiSchema, HexaforgeSlmTrainingMasterEnrichmentHexaYoSchema, HexaforgeSlmTrainingMasterEnrichmentHexaZiSchema, HexaforgeSlmTrainingMasterEnrichmentHexaZoSchema


def test_hexaforge_slm_training_master_enrichment_hexa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterEnrichmentHexaXiSchema()


def test_hexaforge_slm_training_master_enrichment_hexa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterEnrichmentHexaXoSchema()


def test_hexaforge_slm_training_master_enrichment_hexa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterEnrichmentHexaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_enrichment_hexa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterEnrichmentHexaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_enrichment_hexa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterEnrichmentHexaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_enrichment_hexa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterEnrichmentHexaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_enrichment_hexa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterEnrichmentHexaZiSchema()


def test_hexaforge_slm_training_master_enrichment_hexa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterEnrichmentHexaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_enrichment_hexa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterEnrichmentHexaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")

