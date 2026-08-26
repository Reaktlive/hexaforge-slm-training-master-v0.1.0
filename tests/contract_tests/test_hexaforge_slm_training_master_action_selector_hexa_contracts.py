import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterActionSelectorHexaXiSchema, HexaforgeSlmTrainingMasterActionSelectorHexaXoSchema, HexaforgeSlmTrainingMasterActionSelectorHexaYiSchema, HexaforgeSlmTrainingMasterActionSelectorHexaYoSchema, HexaforgeSlmTrainingMasterActionSelectorHexaZiSchema, HexaforgeSlmTrainingMasterActionSelectorHexaZoSchema


def test_hexaforge_slm_training_master_action_selector_hexa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterActionSelectorHexaXiSchema()


def test_hexaforge_slm_training_master_action_selector_hexa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterActionSelectorHexaXoSchema(selected_action="smoke-selected_action", target_asset="smoke-target_asset", action_parameters={}, confidence=0, policy_requirements=[], idempotency_key="smoke-idempotency_key", tenant_id="smoke-tenant_id")


def test_hexaforge_slm_training_master_action_selector_hexa_xo_requires_selected_action():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterActionSelectorHexaXoSchema(target_asset="smoke-target_asset", action_parameters={}, confidence=0, policy_requirements=[], idempotency_key="smoke-idempotency_key", tenant_id="smoke-tenant_id")


def test_hexaforge_slm_training_master_action_selector_hexa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterActionSelectorHexaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_action_selector_hexa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterActionSelectorHexaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_action_selector_hexa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterActionSelectorHexaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_action_selector_hexa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterActionSelectorHexaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_action_selector_hexa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterActionSelectorHexaZiSchema()


def test_hexaforge_slm_training_master_action_selector_hexa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterActionSelectorHexaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_action_selector_hexa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterActionSelectorHexaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")

