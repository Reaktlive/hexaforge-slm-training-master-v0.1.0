import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterPackagerHexaXiSchema, HexaforgeSlmTrainingMasterPackagerHexaXoSchema, HexaforgeSlmTrainingMasterPackagerHexaYiSchema, HexaforgeSlmTrainingMasterPackagerHexaYoSchema, HexaforgeSlmTrainingMasterPackagerHexaZiSchema, HexaforgeSlmTrainingMasterPackagerHexaZoSchema


def test_hexaforge_slm_training_master_packager_hexa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterPackagerHexaXiSchema()


def test_hexaforge_slm_training_master_packager_hexa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterPackagerHexaXoSchema()


def test_hexaforge_slm_training_master_packager_hexa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterPackagerHexaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_packager_hexa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterPackagerHexaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_packager_hexa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterPackagerHexaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_packager_hexa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterPackagerHexaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_packager_hexa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterPackagerHexaZiSchema()


def test_hexaforge_slm_training_master_packager_hexa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterPackagerHexaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_packager_hexa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterPackagerHexaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")

