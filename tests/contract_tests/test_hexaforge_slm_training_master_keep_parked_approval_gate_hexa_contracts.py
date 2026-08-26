import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterKeepParkedApprovalGateHexaXiSchema, HexaforgeSlmTrainingMasterKeepParkedApprovalGateHexaXoSchema, HexaforgeSlmTrainingMasterKeepParkedApprovalGateHexaYiSchema, HexaforgeSlmTrainingMasterKeepParkedApprovalGateHexaYoSchema, HexaforgeSlmTrainingMasterKeepParkedApprovalGateHexaZiSchema, HexaforgeSlmTrainingMasterKeepParkedApprovalGateHexaZoSchema


def test_hexaforge_slm_training_master_keep_parked_approval_gate_hexa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterKeepParkedApprovalGateHexaXiSchema(selected_action="smoke-selected_action", target_asset="smoke-target_asset", action_parameters={}, confidence=0, policy_requirements=[], idempotency_key="smoke-idempotency_key")


def test_hexaforge_slm_training_master_keep_parked_approval_gate_hexa_xi_requires_selected_action():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterKeepParkedApprovalGateHexaXiSchema(target_asset="smoke-target_asset", action_parameters={}, confidence=0, policy_requirements=[], idempotency_key="smoke-idempotency_key")


def test_hexaforge_slm_training_master_keep_parked_approval_gate_hexa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterKeepParkedApprovalGateHexaXoSchema()


def test_hexaforge_slm_training_master_keep_parked_approval_gate_hexa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterKeepParkedApprovalGateHexaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_keep_parked_approval_gate_hexa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterKeepParkedApprovalGateHexaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_keep_parked_approval_gate_hexa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterKeepParkedApprovalGateHexaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_keep_parked_approval_gate_hexa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterKeepParkedApprovalGateHexaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_keep_parked_approval_gate_hexa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterKeepParkedApprovalGateHexaZiSchema()


def test_hexaforge_slm_training_master_keep_parked_approval_gate_hexa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterKeepParkedApprovalGateHexaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_keep_parked_approval_gate_hexa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterKeepParkedApprovalGateHexaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")

