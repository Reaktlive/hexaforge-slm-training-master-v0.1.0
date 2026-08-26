import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterIntakeOctaXiSchema, HexaforgeSlmTrainingMasterIntakeOctaXoSchema, HexaforgeSlmTrainingMasterIntakeOctaYiSchema, HexaforgeSlmTrainingMasterIntakeOctaYoSchema, HexaforgeSlmTrainingMasterIntakeOctaZiSchema, HexaforgeSlmTrainingMasterIntakeOctaZoSchema, HexaforgeSlmTrainingMasterIntakeOctaMiSchema, HexaforgeSlmTrainingMasterIntakeOctaMoSchema


def test_hexaforge_slm_training_master_intake_octa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterIntakeOctaXiSchema()


def test_hexaforge_slm_training_master_intake_octa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterIntakeOctaXoSchema()


def test_hexaforge_slm_training_master_intake_octa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterIntakeOctaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_intake_octa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterIntakeOctaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_intake_octa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterIntakeOctaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_intake_octa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterIntakeOctaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_intake_octa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterIntakeOctaZiSchema()


def test_hexaforge_slm_training_master_intake_octa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterIntakeOctaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_intake_octa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterIntakeOctaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_intake_octa_mi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterIntakeOctaMiSchema(cycle_id="smoke-cycle_id")


def test_hexaforge_slm_training_master_intake_octa_mi_requires_cycle_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterIntakeOctaMiSchema()


def test_hexaforge_slm_training_master_intake_octa_mo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterIntakeOctaMoSchema()

