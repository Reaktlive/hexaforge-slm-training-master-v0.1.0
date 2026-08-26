import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterEvalGatekeeperHexaXiSchema, HexaforgeSlmTrainingMasterEvalGatekeeperHexaXoSchema, HexaforgeSlmTrainingMasterEvalGatekeeperHexaYiSchema, HexaforgeSlmTrainingMasterEvalGatekeeperHexaYoSchema, HexaforgeSlmTrainingMasterEvalGatekeeperHexaZiSchema, HexaforgeSlmTrainingMasterEvalGatekeeperHexaZoSchema


def test_hexaforge_slm_training_master_eval_gatekeeper_hexa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterEvalGatekeeperHexaXiSchema()


def test_hexaforge_slm_training_master_eval_gatekeeper_hexa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterEvalGatekeeperHexaXoSchema()


def test_hexaforge_slm_training_master_eval_gatekeeper_hexa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterEvalGatekeeperHexaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_eval_gatekeeper_hexa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterEvalGatekeeperHexaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_eval_gatekeeper_hexa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterEvalGatekeeperHexaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_eval_gatekeeper_hexa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterEvalGatekeeperHexaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_eval_gatekeeper_hexa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterEvalGatekeeperHexaZiSchema()


def test_hexaforge_slm_training_master_eval_gatekeeper_hexa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterEvalGatekeeperHexaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_eval_gatekeeper_hexa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterEvalGatekeeperHexaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")

