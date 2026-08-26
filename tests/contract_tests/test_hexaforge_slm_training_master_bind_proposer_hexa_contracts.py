import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterBindProposerHexaXiSchema, HexaforgeSlmTrainingMasterBindProposerHexaXoSchema, HexaforgeSlmTrainingMasterBindProposerHexaYiSchema, HexaforgeSlmTrainingMasterBindProposerHexaYoSchema, HexaforgeSlmTrainingMasterBindProposerHexaZiSchema, HexaforgeSlmTrainingMasterBindProposerHexaZoSchema


def test_hexaforge_slm_training_master_bind_proposer_hexa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterBindProposerHexaXiSchema()


def test_hexaforge_slm_training_master_bind_proposer_hexa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterBindProposerHexaXoSchema()


def test_hexaforge_slm_training_master_bind_proposer_hexa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterBindProposerHexaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_bind_proposer_hexa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterBindProposerHexaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_bind_proposer_hexa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterBindProposerHexaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_bind_proposer_hexa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterBindProposerHexaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_bind_proposer_hexa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterBindProposerHexaZiSchema()


def test_hexaforge_slm_training_master_bind_proposer_hexa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterBindProposerHexaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_bind_proposer_hexa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterBindProposerHexaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")

