import pytest
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterCampaignPlannerHexaXiSchema, HexaforgeSlmTrainingMasterCampaignPlannerHexaXoSchema, HexaforgeSlmTrainingMasterCampaignPlannerHexaYiSchema, HexaforgeSlmTrainingMasterCampaignPlannerHexaYoSchema, HexaforgeSlmTrainingMasterCampaignPlannerHexaZiSchema, HexaforgeSlmTrainingMasterCampaignPlannerHexaZoSchema


def test_hexaforge_slm_training_master_campaign_planner_hexa_xi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterCampaignPlannerHexaXiSchema()


def test_hexaforge_slm_training_master_campaign_planner_hexa_xo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterCampaignPlannerHexaXoSchema()


def test_hexaforge_slm_training_master_campaign_planner_hexa_yi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterCampaignPlannerHexaYiSchema(policy_id="smoke-policy_id", ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_campaign_planner_hexa_yi_requires_policy_id():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterCampaignPlannerHexaYiSchema(ccas_tier="smoke-ccas_tier")


def test_hexaforge_slm_training_master_campaign_planner_hexa_yo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterCampaignPlannerHexaYoSchema(action_kind="smoke-action_kind", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_campaign_planner_hexa_yo_requires_action_kind():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterCampaignPlannerHexaYoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_campaign_planner_hexa_zi_accepts_valid_contract():
    HexaforgeSlmTrainingMasterCampaignPlannerHexaZiSchema()


def test_hexaforge_slm_training_master_campaign_planner_hexa_zo_accepts_valid_contract():
    HexaforgeSlmTrainingMasterCampaignPlannerHexaZoSchema(event="smoke-event", session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")


def test_hexaforge_slm_training_master_campaign_planner_hexa_zo_requires_event():
    with pytest.raises(ValidationError):
        HexaforgeSlmTrainingMasterCampaignPlannerHexaZoSchema(session_id="smoke-session_id", vertical="smoke-vertical", ts="2026-01-01T00:00:00Z")

