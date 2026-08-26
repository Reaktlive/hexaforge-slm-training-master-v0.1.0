import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterFleetBinderHexaXiSchema, HexaforgeSlmTrainingMasterFleetBinderHexaXoSchema, HexaforgeSlmTrainingMasterFleetBinderHexaYiSchema, HexaforgeSlmTrainingMasterFleetBinderHexaYoSchema, HexaforgeSlmTrainingMasterFleetBinderHexaZiSchema, HexaforgeSlmTrainingMasterFleetBinderHexaZoSchema


def test_hexaforge_slm_training_master_fleet_binder_hexa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterFleetBinderHexaXiSchema()


def test_hexaforge_slm_training_master_fleet_binder_hexa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterFleetBinderHexaXoSchema()


def test_hexaforge_slm_training_master_fleet_binder_hexa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterFleetBinderHexaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_fleet_binder_hexa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterFleetBinderHexaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_fleet_binder_hexa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterFleetBinderHexaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_fleet_binder_hexa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterFleetBinderHexaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_fleet_binder_hexa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterFleetBinderHexaZiSchema()


def test_hexaforge_slm_training_master_fleet_binder_hexa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterFleetBinderHexaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_fleet_binder_hexa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterFleetBinderHexaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")

