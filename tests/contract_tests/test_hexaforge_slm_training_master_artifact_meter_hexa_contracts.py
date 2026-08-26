import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterArtifactMeterHexaXiSchema, HexaforgeSlmTrainingMasterArtifactMeterHexaXoSchema, HexaforgeSlmTrainingMasterArtifactMeterHexaYiSchema, HexaforgeSlmTrainingMasterArtifactMeterHexaYoSchema, HexaforgeSlmTrainingMasterArtifactMeterHexaZiSchema, HexaforgeSlmTrainingMasterArtifactMeterHexaZoSchema


def test_hexaforge_slm_training_master_artifact_meter_hexa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterArtifactMeterHexaXiSchema()


def test_hexaforge_slm_training_master_artifact_meter_hexa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterArtifactMeterHexaXoSchema()


def test_hexaforge_slm_training_master_artifact_meter_hexa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterArtifactMeterHexaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_artifact_meter_hexa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterArtifactMeterHexaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_artifact_meter_hexa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterArtifactMeterHexaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_artifact_meter_hexa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterArtifactMeterHexaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_artifact_meter_hexa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterArtifactMeterHexaZiSchema()


def test_hexaforge_slm_training_master_artifact_meter_hexa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterArtifactMeterHexaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_artifact_meter_hexa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterArtifactMeterHexaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")

