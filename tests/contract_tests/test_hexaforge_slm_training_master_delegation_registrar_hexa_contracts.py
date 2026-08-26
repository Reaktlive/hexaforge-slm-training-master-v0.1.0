import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterDelegationRegistrarHexaXiSchema, HexaforgeSlmTrainingMasterDelegationRegistrarHexaXoSchema, HexaforgeSlmTrainingMasterDelegationRegistrarHexaYiSchema, HexaforgeSlmTrainingMasterDelegationRegistrarHexaYoSchema, HexaforgeSlmTrainingMasterDelegationRegistrarHexaZiSchema, HexaforgeSlmTrainingMasterDelegationRegistrarHexaZoSchema


def test_hexaforge_slm_training_master_delegation_registrar_hexa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDelegationRegistrarHexaXiSchema()


def test_hexaforge_slm_training_master_delegation_registrar_hexa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDelegationRegistrarHexaXoSchema()


def test_hexaforge_slm_training_master_delegation_registrar_hexa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDelegationRegistrarHexaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_delegation_registrar_hexa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterDelegationRegistrarHexaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_delegation_registrar_hexa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDelegationRegistrarHexaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_delegation_registrar_hexa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterDelegationRegistrarHexaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_delegation_registrar_hexa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDelegationRegistrarHexaZiSchema()


def test_hexaforge_slm_training_master_delegation_registrar_hexa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDelegationRegistrarHexaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_delegation_registrar_hexa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterDelegationRegistrarHexaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")

