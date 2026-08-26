import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterExplainerHexaXiSchema, HexaforgeSlmTrainingMasterExplainerHexaXoSchema, HexaforgeSlmTrainingMasterExplainerHexaYiSchema, HexaforgeSlmTrainingMasterExplainerHexaYoSchema, HexaforgeSlmTrainingMasterExplainerHexaZiSchema, HexaforgeSlmTrainingMasterExplainerHexaZoSchema


def test_hexaforge_slm_training_master_explainer_hexa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterExplainerHexaXiSchema()


def test_hexaforge_slm_training_master_explainer_hexa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterExplainerHexaXoSchema()


def test_hexaforge_slm_training_master_explainer_hexa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterExplainerHexaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_explainer_hexa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterExplainerHexaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_explainer_hexa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterExplainerHexaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_explainer_hexa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterExplainerHexaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_explainer_hexa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterExplainerHexaZiSchema()


def test_hexaforge_slm_training_master_explainer_hexa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterExplainerHexaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_explainer_hexa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterExplainerHexaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")

