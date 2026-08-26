import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterDecisionHexaXiSchema, HexaforgeSlmTrainingMasterDecisionHexaXoSchema, HexaforgeSlmTrainingMasterDecisionHexaYiSchema, HexaforgeSlmTrainingMasterDecisionHexaYoSchema, HexaforgeSlmTrainingMasterDecisionHexaZiSchema, HexaforgeSlmTrainingMasterDecisionHexaZoSchema


def test_hexaforge_slm_training_master_decision_hexa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDecisionHexaXiSchema()


def test_hexaforge_slm_training_master_decision_hexa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDecisionHexaXoSchema()


def test_hexaforge_slm_training_master_decision_hexa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDecisionHexaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_decision_hexa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterDecisionHexaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_decision_hexa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDecisionHexaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_decision_hexa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterDecisionHexaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_decision_hexa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDecisionHexaZiSchema()


def test_hexaforge_slm_training_master_decision_hexa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDecisionHexaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_decision_hexa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterDecisionHexaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")

