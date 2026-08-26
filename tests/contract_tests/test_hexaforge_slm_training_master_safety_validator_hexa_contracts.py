import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterSafetyValidatorHexaXiSchema, HexaforgeSlmTrainingMasterSafetyValidatorHexaXoSchema, HexaforgeSlmTrainingMasterSafetyValidatorHexaYiSchema, HexaforgeSlmTrainingMasterSafetyValidatorHexaYoSchema, HexaforgeSlmTrainingMasterSafetyValidatorHexaZiSchema, HexaforgeSlmTrainingMasterSafetyValidatorHexaZoSchema


def test_hexaforge_slm_training_master_safety_validator_hexa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterSafetyValidatorHexaXiSchema()


def test_hexaforge_slm_training_master_safety_validator_hexa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterSafetyValidatorHexaXoSchema()


def test_hexaforge_slm_training_master_safety_validator_hexa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterSafetyValidatorHexaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_safety_validator_hexa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterSafetyValidatorHexaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_safety_validator_hexa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterSafetyValidatorHexaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_safety_validator_hexa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterSafetyValidatorHexaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_safety_validator_hexa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterSafetyValidatorHexaZiSchema()


def test_hexaforge_slm_training_master_safety_validator_hexa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterSafetyValidatorHexaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_safety_validator_hexa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterSafetyValidatorHexaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")

