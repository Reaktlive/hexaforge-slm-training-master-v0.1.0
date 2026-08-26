import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterFailureDiagnoserHexaXiSchema, HexaforgeSlmTrainingMasterFailureDiagnoserHexaXoSchema, HexaforgeSlmTrainingMasterFailureDiagnoserHexaYiSchema, HexaforgeSlmTrainingMasterFailureDiagnoserHexaYoSchema, HexaforgeSlmTrainingMasterFailureDiagnoserHexaZiSchema, HexaforgeSlmTrainingMasterFailureDiagnoserHexaZoSchema


def test_hexaforge_slm_training_master_failure_diagnoser_hexa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterFailureDiagnoserHexaXiSchema()


def test_hexaforge_slm_training_master_failure_diagnoser_hexa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterFailureDiagnoserHexaXoSchema()


def test_hexaforge_slm_training_master_failure_diagnoser_hexa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterFailureDiagnoserHexaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_failure_diagnoser_hexa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterFailureDiagnoserHexaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_failure_diagnoser_hexa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterFailureDiagnoserHexaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_failure_diagnoser_hexa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterFailureDiagnoserHexaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_failure_diagnoser_hexa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterFailureDiagnoserHexaZiSchema()


def test_hexaforge_slm_training_master_failure_diagnoser_hexa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterFailureDiagnoserHexaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_failure_diagnoser_hexa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterFailureDiagnoserHexaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")

