import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterRetrainProposerHexaXiSchema, HexaforgeSlmTrainingMasterRetrainProposerHexaXoSchema, HexaforgeSlmTrainingMasterRetrainProposerHexaYiSchema, HexaforgeSlmTrainingMasterRetrainProposerHexaYoSchema, HexaforgeSlmTrainingMasterRetrainProposerHexaZiSchema, HexaforgeSlmTrainingMasterRetrainProposerHexaZoSchema


def test_hexaforge_slm_training_master_retrain_proposer_hexa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterRetrainProposerHexaXiSchema()


def test_hexaforge_slm_training_master_retrain_proposer_hexa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterRetrainProposerHexaXoSchema()


def test_hexaforge_slm_training_master_retrain_proposer_hexa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterRetrainProposerHexaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_retrain_proposer_hexa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterRetrainProposerHexaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_retrain_proposer_hexa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterRetrainProposerHexaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_retrain_proposer_hexa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterRetrainProposerHexaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_retrain_proposer_hexa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterRetrainProposerHexaZiSchema()


def test_hexaforge_slm_training_master_retrain_proposer_hexa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterRetrainProposerHexaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_retrain_proposer_hexa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterRetrainProposerHexaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")

