import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterDecisionLedgerHexaXiSchema, HexaforgeSlmTrainingMasterDecisionLedgerHexaXoSchema, HexaforgeSlmTrainingMasterDecisionLedgerHexaYiSchema, HexaforgeSlmTrainingMasterDecisionLedgerHexaYoSchema, HexaforgeSlmTrainingMasterDecisionLedgerHexaZiSchema, HexaforgeSlmTrainingMasterDecisionLedgerHexaZoSchema


def test_hexaforge_slm_training_master_decision_ledger_hexa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDecisionLedgerHexaXiSchema()


def test_hexaforge_slm_training_master_decision_ledger_hexa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDecisionLedgerHexaXoSchema()


def test_hexaforge_slm_training_master_decision_ledger_hexa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDecisionLedgerHexaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_decision_ledger_hexa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterDecisionLedgerHexaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_decision_ledger_hexa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDecisionLedgerHexaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_decision_ledger_hexa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterDecisionLedgerHexaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_decision_ledger_hexa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDecisionLedgerHexaZiSchema()


def test_hexaforge_slm_training_master_decision_ledger_hexa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDecisionLedgerHexaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_decision_ledger_hexa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterDecisionLedgerHexaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")

