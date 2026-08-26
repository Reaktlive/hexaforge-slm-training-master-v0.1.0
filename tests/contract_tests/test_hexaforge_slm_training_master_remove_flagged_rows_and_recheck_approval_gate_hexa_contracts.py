import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterRemoveFlaggedRowsAndRecheckApprovalGateHexaXiSchema, HexaforgeSlmTrainingMasterRemoveFlaggedRowsAndRecheckApprovalGateHexaXoSchema, HexaforgeSlmTrainingMasterRemoveFlaggedRowsAndRecheckApprovalGateHexaYiSchema, HexaforgeSlmTrainingMasterRemoveFlaggedRowsAndRecheckApprovalGateHexaYoSchema, HexaforgeSlmTrainingMasterRemoveFlaggedRowsAndRecheckApprovalGateHexaZiSchema, HexaforgeSlmTrainingMasterRemoveFlaggedRowsAndRecheckApprovalGateHexaZoSchema


def test_hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterRemoveFlaggedRowsAndRecheckApprovalGateHexaXiSchema(selected_action="smoke-selected_action", target_asset="smoke-target_asset", action_parameters={}, confidence=0, policy_requirements=[], idempotency_key="smoke-idempotency_key")


def test_hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa_xi_requires_selected_action():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterRemoveFlaggedRowsAndRecheckApprovalGateHexaXiSchema(target_asset="smoke-target_asset", action_parameters={}, confidence=0, policy_requirements=[], idempotency_key="smoke-idempotency_key")


def test_hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterRemoveFlaggedRowsAndRecheckApprovalGateHexaXoSchema()


def test_hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterRemoveFlaggedRowsAndRecheckApprovalGateHexaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterRemoveFlaggedRowsAndRecheckApprovalGateHexaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterRemoveFlaggedRowsAndRecheckApprovalGateHexaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterRemoveFlaggedRowsAndRecheckApprovalGateHexaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterRemoveFlaggedRowsAndRecheckApprovalGateHexaZiSchema()


def test_hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterRemoveFlaggedRowsAndRecheckApprovalGateHexaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterRemoveFlaggedRowsAndRecheckApprovalGateHexaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")

