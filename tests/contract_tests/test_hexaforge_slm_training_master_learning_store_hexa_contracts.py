import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterLearningStoreHexaXiSchema, HexaforgeSlmTrainingMasterLearningStoreHexaXoSchema, HexaforgeSlmTrainingMasterLearningStoreHexaYiSchema, HexaforgeSlmTrainingMasterLearningStoreHexaYoSchema, HexaforgeSlmTrainingMasterLearningStoreHexaZiSchema, HexaforgeSlmTrainingMasterLearningStoreHexaZoSchema


def test_hexaforge_slm_training_master_learning_store_hexa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterLearningStoreHexaXiSchema()


def test_hexaforge_slm_training_master_learning_store_hexa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterLearningStoreHexaXoSchema()


def test_hexaforge_slm_training_master_learning_store_hexa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterLearningStoreHexaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_learning_store_hexa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterLearningStoreHexaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_learning_store_hexa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterLearningStoreHexaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_learning_store_hexa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterLearningStoreHexaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_learning_store_hexa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterLearningStoreHexaZiSchema()


def test_hexaforge_slm_training_master_learning_store_hexa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterLearningStoreHexaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_learning_store_hexa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterLearningStoreHexaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")

