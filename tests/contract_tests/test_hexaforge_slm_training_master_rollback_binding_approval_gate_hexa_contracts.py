import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterRollbackBindingApprovalGateHexaXiSchema, HexaforgeSlmTrainingMasterRollbackBindingApprovalGateHexaXoSchema, HexaforgeSlmTrainingMasterRollbackBindingApprovalGateHexaYiSchema, HexaforgeSlmTrainingMasterRollbackBindingApprovalGateHexaYoSchema, HexaforgeSlmTrainingMasterRollbackBindingApprovalGateHexaZiSchema, HexaforgeSlmTrainingMasterRollbackBindingApprovalGateHexaZoSchema


def test_hexaforge_slm_training_master_rollback_binding_approval_gate_hexa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterRollbackBindingApprovalGateHexaXiSchema(selected_action="smoke-selected_action", target_asset="smoke-target_asset", action_parameters={}, confidence=0, policy_requirements=[], idempotency_key="smoke-idempotency_key")


def test_hexaforge_slm_training_master_rollback_binding_approval_gate_hexa_xi_requires_selected_action():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterRollbackBindingApprovalGateHexaXiSchema(target_asset="smoke-target_asset", action_parameters={}, confidence=0, policy_requirements=[], idempotency_key="smoke-idempotency_key")


def test_hexaforge_slm_training_master_rollback_binding_approval_gate_hexa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterRollbackBindingApprovalGateHexaXoSchema()


def test_hexaforge_slm_training_master_rollback_binding_approval_gate_hexa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterRollbackBindingApprovalGateHexaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_rollback_binding_approval_gate_hexa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterRollbackBindingApprovalGateHexaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_rollback_binding_approval_gate_hexa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterRollbackBindingApprovalGateHexaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_rollback_binding_approval_gate_hexa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterRollbackBindingApprovalGateHexaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_rollback_binding_approval_gate_hexa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterRollbackBindingApprovalGateHexaZiSchema()


def test_hexaforge_slm_training_master_rollback_binding_approval_gate_hexa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterRollbackBindingApprovalGateHexaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_rollback_binding_approval_gate_hexa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterRollbackBindingApprovalGateHexaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")

