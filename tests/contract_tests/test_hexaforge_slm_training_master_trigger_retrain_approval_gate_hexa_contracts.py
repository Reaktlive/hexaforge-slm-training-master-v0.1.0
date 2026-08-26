import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterTriggerRetrainApprovalGateHexaXiSchema, HexaforgeSlmTrainingMasterTriggerRetrainApprovalGateHexaXoSchema, HexaforgeSlmTrainingMasterTriggerRetrainApprovalGateHexaYiSchema, HexaforgeSlmTrainingMasterTriggerRetrainApprovalGateHexaYoSchema, HexaforgeSlmTrainingMasterTriggerRetrainApprovalGateHexaZiSchema, HexaforgeSlmTrainingMasterTriggerRetrainApprovalGateHexaZoSchema


def test_hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterTriggerRetrainApprovalGateHexaXiSchema(selected_action="smoke-selected_action", target_asset="smoke-target_asset", action_parameters={}, confidence=0, policy_requirements=[], idempotency_key="smoke-idempotency_key")


def test_hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa_xi_requires_selected_action():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterTriggerRetrainApprovalGateHexaXiSchema(target_asset="smoke-target_asset", action_parameters={}, confidence=0, policy_requirements=[], idempotency_key="smoke-idempotency_key")


def test_hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterTriggerRetrainApprovalGateHexaXoSchema()


def test_hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterTriggerRetrainApprovalGateHexaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterTriggerRetrainApprovalGateHexaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterTriggerRetrainApprovalGateHexaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterTriggerRetrainApprovalGateHexaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterTriggerRetrainApprovalGateHexaZiSchema()


def test_hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterTriggerRetrainApprovalGateHexaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterTriggerRetrainApprovalGateHexaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")

