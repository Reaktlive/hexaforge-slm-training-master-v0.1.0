import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterGpuTelemetryNormalizerHexaXiSchema, HexaforgeSlmTrainingMasterGpuTelemetryNormalizerHexaXoSchema, HexaforgeSlmTrainingMasterGpuTelemetryNormalizerHexaYiSchema, HexaforgeSlmTrainingMasterGpuTelemetryNormalizerHexaYoSchema, HexaforgeSlmTrainingMasterGpuTelemetryNormalizerHexaZiSchema, HexaforgeSlmTrainingMasterGpuTelemetryNormalizerHexaZoSchema


def test_hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterGpuTelemetryNormalizerHexaXiSchema()


def test_hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterGpuTelemetryNormalizerHexaXoSchema()


def test_hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterGpuTelemetryNormalizerHexaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterGpuTelemetryNormalizerHexaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterGpuTelemetryNormalizerHexaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterGpuTelemetryNormalizerHexaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterGpuTelemetryNormalizerHexaZiSchema()


def test_hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterGpuTelemetryNormalizerHexaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterGpuTelemetryNormalizerHexaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")

