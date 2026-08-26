import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterProvenanceRecorderHexaXiSchema, HexaforgeSlmTrainingMasterProvenanceRecorderHexaXoSchema, HexaforgeSlmTrainingMasterProvenanceRecorderHexaYiSchema, HexaforgeSlmTrainingMasterProvenanceRecorderHexaYoSchema, HexaforgeSlmTrainingMasterProvenanceRecorderHexaZiSchema, HexaforgeSlmTrainingMasterProvenanceRecorderHexaZoSchema


def test_hexaforge_slm_training_master_provenance_recorder_hexa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterProvenanceRecorderHexaXiSchema()


def test_hexaforge_slm_training_master_provenance_recorder_hexa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterProvenanceRecorderHexaXoSchema()


def test_hexaforge_slm_training_master_provenance_recorder_hexa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterProvenanceRecorderHexaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_provenance_recorder_hexa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterProvenanceRecorderHexaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_provenance_recorder_hexa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterProvenanceRecorderHexaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_provenance_recorder_hexa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterProvenanceRecorderHexaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_provenance_recorder_hexa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterProvenanceRecorderHexaZiSchema()


def test_hexaforge_slm_training_master_provenance_recorder_hexa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterProvenanceRecorderHexaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_provenance_recorder_hexa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterProvenanceRecorderHexaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")

