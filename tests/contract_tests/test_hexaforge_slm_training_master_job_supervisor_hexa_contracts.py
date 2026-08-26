import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterJobSupervisorHexaXiSchema, HexaforgeSlmTrainingMasterJobSupervisorHexaXoSchema, HexaforgeSlmTrainingMasterJobSupervisorHexaYiSchema, HexaforgeSlmTrainingMasterJobSupervisorHexaYoSchema, HexaforgeSlmTrainingMasterJobSupervisorHexaZiSchema, HexaforgeSlmTrainingMasterJobSupervisorHexaZoSchema


def test_hexaforge_slm_training_master_job_supervisor_hexa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterJobSupervisorHexaXiSchema()


def test_hexaforge_slm_training_master_job_supervisor_hexa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterJobSupervisorHexaXoSchema()


def test_hexaforge_slm_training_master_job_supervisor_hexa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterJobSupervisorHexaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_job_supervisor_hexa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterJobSupervisorHexaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_job_supervisor_hexa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterJobSupervisorHexaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_job_supervisor_hexa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterJobSupervisorHexaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_job_supervisor_hexa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterJobSupervisorHexaZiSchema()


def test_hexaforge_slm_training_master_job_supervisor_hexa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterJobSupervisorHexaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_job_supervisor_hexa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterJobSupervisorHexaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")

