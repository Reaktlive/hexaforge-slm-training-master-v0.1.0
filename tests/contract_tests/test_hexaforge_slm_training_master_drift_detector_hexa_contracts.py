import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterDriftDetectorHexaXiSchema, HexaforgeSlmTrainingMasterDriftDetectorHexaXoSchema, HexaforgeSlmTrainingMasterDriftDetectorHexaYiSchema, HexaforgeSlmTrainingMasterDriftDetectorHexaYoSchema, HexaforgeSlmTrainingMasterDriftDetectorHexaZiSchema, HexaforgeSlmTrainingMasterDriftDetectorHexaZoSchema


def test_hexaforge_slm_training_master_drift_detector_hexa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDriftDetectorHexaXiSchema()


def test_hexaforge_slm_training_master_drift_detector_hexa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDriftDetectorHexaXoSchema()


def test_hexaforge_slm_training_master_drift_detector_hexa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDriftDetectorHexaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_drift_detector_hexa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterDriftDetectorHexaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_drift_detector_hexa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDriftDetectorHexaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_drift_detector_hexa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterDriftDetectorHexaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_drift_detector_hexa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDriftDetectorHexaZiSchema()


def test_hexaforge_slm_training_master_drift_detector_hexa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDriftDetectorHexaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_drift_detector_hexa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterDriftDetectorHexaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")

