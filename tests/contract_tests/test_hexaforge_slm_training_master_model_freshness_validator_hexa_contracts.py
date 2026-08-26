import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterModelFreshnessValidatorHexaXiSchema, HexaforgeSlmTrainingMasterModelFreshnessValidatorHexaXoSchema, HexaforgeSlmTrainingMasterModelFreshnessValidatorHexaYiSchema, HexaforgeSlmTrainingMasterModelFreshnessValidatorHexaYoSchema, HexaforgeSlmTrainingMasterModelFreshnessValidatorHexaZiSchema, HexaforgeSlmTrainingMasterModelFreshnessValidatorHexaZoSchema


def test_hexaforge_slm_training_master_model_freshness_validator_hexa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterModelFreshnessValidatorHexaXiSchema()


def test_hexaforge_slm_training_master_model_freshness_validator_hexa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterModelFreshnessValidatorHexaXoSchema()


def test_hexaforge_slm_training_master_model_freshness_validator_hexa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterModelFreshnessValidatorHexaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_model_freshness_validator_hexa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterModelFreshnessValidatorHexaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_model_freshness_validator_hexa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterModelFreshnessValidatorHexaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_model_freshness_validator_hexa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterModelFreshnessValidatorHexaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_model_freshness_validator_hexa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterModelFreshnessValidatorHexaZiSchema()


def test_hexaforge_slm_training_master_model_freshness_validator_hexa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterModelFreshnessValidatorHexaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_model_freshness_validator_hexa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterModelFreshnessValidatorHexaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")

