import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterEventParserHexaXiSchema, HexaforgeSlmTrainingMasterEventParserHexaXoSchema, HexaforgeSlmTrainingMasterEventParserHexaYiSchema, HexaforgeSlmTrainingMasterEventParserHexaYoSchema, HexaforgeSlmTrainingMasterEventParserHexaZiSchema, HexaforgeSlmTrainingMasterEventParserHexaZoSchema


def test_hexaforge_slm_training_master_event_parser_hexa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterEventParserHexaXiSchema()


def test_hexaforge_slm_training_master_event_parser_hexa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterEventParserHexaXoSchema()


def test_hexaforge_slm_training_master_event_parser_hexa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterEventParserHexaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_event_parser_hexa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterEventParserHexaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_event_parser_hexa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterEventParserHexaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_event_parser_hexa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterEventParserHexaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_event_parser_hexa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterEventParserHexaZiSchema()


def test_hexaforge_slm_training_master_event_parser_hexa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterEventParserHexaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_event_parser_hexa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterEventParserHexaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")

