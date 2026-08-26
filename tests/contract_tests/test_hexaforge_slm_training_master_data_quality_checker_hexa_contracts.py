import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterDataQualityCheckerHexaXiSchema, HexaforgeSlmTrainingMasterDataQualityCheckerHexaXoSchema, HexaforgeSlmTrainingMasterDataQualityCheckerHexaYiSchema, HexaforgeSlmTrainingMasterDataQualityCheckerHexaYoSchema, HexaforgeSlmTrainingMasterDataQualityCheckerHexaZiSchema, HexaforgeSlmTrainingMasterDataQualityCheckerHexaZoSchema


def test_hexaforge_slm_training_master_data_quality_checker_hexa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDataQualityCheckerHexaXiSchema()


def test_hexaforge_slm_training_master_data_quality_checker_hexa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDataQualityCheckerHexaXoSchema()


def test_hexaforge_slm_training_master_data_quality_checker_hexa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDataQualityCheckerHexaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_data_quality_checker_hexa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterDataQualityCheckerHexaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_data_quality_checker_hexa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDataQualityCheckerHexaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_data_quality_checker_hexa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterDataQualityCheckerHexaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_data_quality_checker_hexa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDataQualityCheckerHexaZiSchema()


def test_hexaforge_slm_training_master_data_quality_checker_hexa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterDataQualityCheckerHexaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_data_quality_checker_hexa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterDataQualityCheckerHexaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")

