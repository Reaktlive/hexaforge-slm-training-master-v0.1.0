import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterDataProvenanceRecorderHexaXiSchema, HexaforgeSlmTrainingMasterDataProvenanceRecorderHexaXoSchema, HexaforgeSlmTrainingMasterDataProvenanceRecorderHexaYiSchema, HexaforgeSlmTrainingMasterDataProvenanceRecorderHexaYoSchema, HexaforgeSlmTrainingMasterDataProvenanceRecorderHexaZiSchema, HexaforgeSlmTrainingMasterDataProvenanceRecorderHexaZoSchema


def test_hexaforge_slm_training_master_data_provenance_recorder_hexa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDataProvenanceRecorderHexaXiSchema()


def test_hexaforge_slm_training_master_data_provenance_recorder_hexa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDataProvenanceRecorderHexaXoSchema()


def test_hexaforge_slm_training_master_data_provenance_recorder_hexa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDataProvenanceRecorderHexaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_data_provenance_recorder_hexa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterDataProvenanceRecorderHexaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_data_provenance_recorder_hexa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDataProvenanceRecorderHexaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_data_provenance_recorder_hexa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterDataProvenanceRecorderHexaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_data_provenance_recorder_hexa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDataProvenanceRecorderHexaZiSchema()


def test_hexaforge_slm_training_master_data_provenance_recorder_hexa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDataProvenanceRecorderHexaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_data_provenance_recorder_hexa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterDataProvenanceRecorderHexaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")

