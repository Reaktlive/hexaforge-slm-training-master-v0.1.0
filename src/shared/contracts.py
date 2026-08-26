"""Pydantic contract models — generated from the canonical port contracts.

Single source of truth: contracts/<node_id>/<port>.schema.json (Purity Gate
Plan P2). Required fields and types are emitted from the exact same canonical
schemas as contracts/ and src/nodes/<node_id>/schemas.json — do not edit by
hand; regenerate via Forseti bundleBuilder.
"""
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field

class HexaforgeSlmTrainingMasterIntakeOctaXiSchema(BaseModel):
    """hexaforge_slm_training_master_intake_octa.xi — generated from contracts/hexaforge_slm_training_master_intake_octa/xi.schema.json (v1.0.0)."""
    source: Optional[str] = None
    request_id: Optional[str] = None
    ts: Optional[str] = None
    payload: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterIntakeOctaXoSchema(BaseModel):
    """hexaforge_slm_training_master_intake_octa.xo — generated from contracts/hexaforge_slm_training_master_intake_octa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterIntakeOctaYiSchema(BaseModel):
    """hexaforge_slm_training_master_intake_octa.yi — generated from contracts/hexaforge_slm_training_master_intake_octa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_intake_octa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterIntakeOctaYoSchema(BaseModel):
    """hexaforge_slm_training_master_intake_octa.yo — generated from contracts/hexaforge_slm_training_master_intake_octa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_intake_octa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_intake_octa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_intake_octa.yo action_kind")

class HexaforgeSlmTrainingMasterIntakeOctaZiSchema(BaseModel):
    """hexaforge_slm_training_master_intake_octa.zi — generated from contracts/hexaforge_slm_training_master_intake_octa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterIntakeOctaZoSchema(BaseModel):
    """hexaforge_slm_training_master_intake_octa.zo — generated from contracts/hexaforge_slm_training_master_intake_octa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_intake_octa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_intake_octa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_intake_octa.zo session_id")

class HexaforgeSlmTrainingMasterIntakeOctaMiSchema(BaseModel):
    """hexaforge_slm_training_master_intake_octa.mi — generated from contracts/hexaforge_slm_training_master_intake_octa/mi.schema.json (v1.0.0)."""
    cycle_id: str = Field(..., description="N6 cohort-cycle correlation id")
    session_id: Optional[str] = None
    attempt_count: Optional[int] = None
    aggregated_count: Optional[int] = None
    side_feed_writes: Optional[dict[str, Any]] = None
    escalation_reason: Optional[str] = Field(None, description="legacy escalation payload (optional)")

class HexaforgeSlmTrainingMasterIntakeOctaMoSchema(BaseModel):
    """hexaforge_slm_training_master_intake_octa.mo — generated from contracts/hexaforge_slm_training_master_intake_octa/mo.schema.json (v1.0.0)."""
    ok: Optional[bool] = Field(None, description="relay ack")
    node: Optional[str] = Field(None, description="relay ack — platform node id")
    port: Optional[str] = Field(None, description="relay ack — port id (mo)")

class HexaforgeSlmTrainingMasterEnrichmentHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_enrichment_hexa.xi — generated from contracts/hexaforge_slm_training_master_enrichment_hexa/xi.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterEnrichmentHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_enrichment_hexa.xo — generated from contracts/hexaforge_slm_training_master_enrichment_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterEnrichmentHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_enrichment_hexa.yi — generated from contracts/hexaforge_slm_training_master_enrichment_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_enrichment_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterEnrichmentHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_enrichment_hexa.yo — generated from contracts/hexaforge_slm_training_master_enrichment_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_enrichment_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_enrichment_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_enrichment_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterEnrichmentHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_enrichment_hexa.zi — generated from contracts/hexaforge_slm_training_master_enrichment_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterEnrichmentHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_enrichment_hexa.zo — generated from contracts/hexaforge_slm_training_master_enrichment_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_enrichment_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_enrichment_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_enrichment_hexa.zo session_id")

class HexaforgeSlmTrainingMasterEventParserHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_event_parser_hexa.xi — generated from contracts/hexaforge_slm_training_master_event_parser_hexa/xi.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterEventParserHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_event_parser_hexa.xo — generated from contracts/hexaforge_slm_training_master_event_parser_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterEventParserHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_event_parser_hexa.yi — generated from contracts/hexaforge_slm_training_master_event_parser_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_event_parser_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterEventParserHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_event_parser_hexa.yo — generated from contracts/hexaforge_slm_training_master_event_parser_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_event_parser_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_event_parser_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_event_parser_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterEventParserHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_event_parser_hexa.zi — generated from contracts/hexaforge_slm_training_master_event_parser_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterEventParserHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_event_parser_hexa.zo — generated from contracts/hexaforge_slm_training_master_event_parser_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_event_parser_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_event_parser_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_event_parser_hexa.zo session_id")

class HexaforgeSlmTrainingMasterCampaignPlannerHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_campaign_planner_hexa.xi — generated from contracts/hexaforge_slm_training_master_campaign_planner_hexa/xi.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterCampaignPlannerHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_campaign_planner_hexa.xo — generated from contracts/hexaforge_slm_training_master_campaign_planner_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterCampaignPlannerHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_campaign_planner_hexa.yi — generated from contracts/hexaforge_slm_training_master_campaign_planner_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_campaign_planner_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterCampaignPlannerHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_campaign_planner_hexa.yo — generated from contracts/hexaforge_slm_training_master_campaign_planner_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_campaign_planner_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_campaign_planner_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_campaign_planner_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterCampaignPlannerHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_campaign_planner_hexa.zi — generated from contracts/hexaforge_slm_training_master_campaign_planner_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterCampaignPlannerHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_campaign_planner_hexa.zo — generated from contracts/hexaforge_slm_training_master_campaign_planner_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_campaign_planner_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_campaign_planner_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_campaign_planner_hexa.zo session_id")

class HexaforgeSlmTrainingMasterJobSupervisorHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_job_supervisor_hexa.xi — generated from contracts/hexaforge_slm_training_master_job_supervisor_hexa/xi.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterJobSupervisorHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_job_supervisor_hexa.xo — generated from contracts/hexaforge_slm_training_master_job_supervisor_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterJobSupervisorHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_job_supervisor_hexa.yi — generated from contracts/hexaforge_slm_training_master_job_supervisor_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_job_supervisor_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterJobSupervisorHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_job_supervisor_hexa.yo — generated from contracts/hexaforge_slm_training_master_job_supervisor_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_job_supervisor_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_job_supervisor_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_job_supervisor_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterJobSupervisorHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_job_supervisor_hexa.zi — generated from contracts/hexaforge_slm_training_master_job_supervisor_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterJobSupervisorHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_job_supervisor_hexa.zo — generated from contracts/hexaforge_slm_training_master_job_supervisor_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_job_supervisor_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_job_supervisor_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_job_supervisor_hexa.zo session_id")

class HexaforgeSlmTrainingMasterGpuTelemetryNormalizerHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa.xi — generated from contracts/hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa/xi.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterGpuTelemetryNormalizerHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa.xo — generated from contracts/hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterGpuTelemetryNormalizerHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa.yi — generated from contracts/hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterGpuTelemetryNormalizerHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa.yo — generated from contracts/hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterGpuTelemetryNormalizerHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa.zi — generated from contracts/hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterGpuTelemetryNormalizerHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa.zo — generated from contracts/hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa.zo session_id")

class HexaforgeSlmTrainingMasterFailureDiagnoserHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_failure_diagnoser_hexa.xi — generated from contracts/hexaforge_slm_training_master_failure_diagnoser_hexa/xi.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterFailureDiagnoserHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_failure_diagnoser_hexa.xo — generated from contracts/hexaforge_slm_training_master_failure_diagnoser_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterFailureDiagnoserHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_failure_diagnoser_hexa.yi — generated from contracts/hexaforge_slm_training_master_failure_diagnoser_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_failure_diagnoser_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterFailureDiagnoserHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_failure_diagnoser_hexa.yo — generated from contracts/hexaforge_slm_training_master_failure_diagnoser_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_failure_diagnoser_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_failure_diagnoser_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_failure_diagnoser_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterFailureDiagnoserHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_failure_diagnoser_hexa.zi — generated from contracts/hexaforge_slm_training_master_failure_diagnoser_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterFailureDiagnoserHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_failure_diagnoser_hexa.zo — generated from contracts/hexaforge_slm_training_master_failure_diagnoser_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_failure_diagnoser_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_failure_diagnoser_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_failure_diagnoser_hexa.zo session_id")

class HexaforgeSlmTrainingMasterEvalGatekeeperHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_eval_gatekeeper_hexa.xi — generated from contracts/hexaforge_slm_training_master_eval_gatekeeper_hexa/xi.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterEvalGatekeeperHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_eval_gatekeeper_hexa.xo — generated from contracts/hexaforge_slm_training_master_eval_gatekeeper_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterEvalGatekeeperHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_eval_gatekeeper_hexa.yi — generated from contracts/hexaforge_slm_training_master_eval_gatekeeper_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_eval_gatekeeper_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterEvalGatekeeperHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_eval_gatekeeper_hexa.yo — generated from contracts/hexaforge_slm_training_master_eval_gatekeeper_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_eval_gatekeeper_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_eval_gatekeeper_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_eval_gatekeeper_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterEvalGatekeeperHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_eval_gatekeeper_hexa.zi — generated from contracts/hexaforge_slm_training_master_eval_gatekeeper_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterEvalGatekeeperHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_eval_gatekeeper_hexa.zo — generated from contracts/hexaforge_slm_training_master_eval_gatekeeper_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_eval_gatekeeper_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_eval_gatekeeper_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_eval_gatekeeper_hexa.zo session_id")

class HexaforgeSlmTrainingMasterProvenanceRecorderHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_provenance_recorder_hexa.xi — generated from contracts/hexaforge_slm_training_master_provenance_recorder_hexa/xi.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterProvenanceRecorderHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_provenance_recorder_hexa.xo — generated from contracts/hexaforge_slm_training_master_provenance_recorder_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterProvenanceRecorderHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_provenance_recorder_hexa.yi — generated from contracts/hexaforge_slm_training_master_provenance_recorder_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_provenance_recorder_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterProvenanceRecorderHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_provenance_recorder_hexa.yo — generated from contracts/hexaforge_slm_training_master_provenance_recorder_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_provenance_recorder_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_provenance_recorder_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_provenance_recorder_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterProvenanceRecorderHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_provenance_recorder_hexa.zi — generated from contracts/hexaforge_slm_training_master_provenance_recorder_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterProvenanceRecorderHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_provenance_recorder_hexa.zo — generated from contracts/hexaforge_slm_training_master_provenance_recorder_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_provenance_recorder_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_provenance_recorder_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_provenance_recorder_hexa.zo session_id")

class HexaforgeSlmTrainingMasterBindProposerHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_bind_proposer_hexa.xi — generated from contracts/hexaforge_slm_training_master_bind_proposer_hexa/xi.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterBindProposerHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_bind_proposer_hexa.xo — generated from contracts/hexaforge_slm_training_master_bind_proposer_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterBindProposerHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_bind_proposer_hexa.yi — generated from contracts/hexaforge_slm_training_master_bind_proposer_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_bind_proposer_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterBindProposerHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_bind_proposer_hexa.yo — generated from contracts/hexaforge_slm_training_master_bind_proposer_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_bind_proposer_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_bind_proposer_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_bind_proposer_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterBindProposerHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_bind_proposer_hexa.zi — generated from contracts/hexaforge_slm_training_master_bind_proposer_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterBindProposerHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_bind_proposer_hexa.zo — generated from contracts/hexaforge_slm_training_master_bind_proposer_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_bind_proposer_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_bind_proposer_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_bind_proposer_hexa.zo session_id")

class HexaforgeSlmTrainingMasterExplainerHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_explainer_hexa.xi — generated from contracts/hexaforge_slm_training_master_explainer_hexa/xi.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterExplainerHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_explainer_hexa.xo — generated from contracts/hexaforge_slm_training_master_explainer_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterExplainerHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_explainer_hexa.yi — generated from contracts/hexaforge_slm_training_master_explainer_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_explainer_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterExplainerHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_explainer_hexa.yo — generated from contracts/hexaforge_slm_training_master_explainer_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_explainer_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_explainer_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_explainer_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterExplainerHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_explainer_hexa.zi — generated from contracts/hexaforge_slm_training_master_explainer_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterExplainerHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_explainer_hexa.zo — generated from contracts/hexaforge_slm_training_master_explainer_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_explainer_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_explainer_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_explainer_hexa.zo session_id")

class HexaforgeSlmTrainingMasterDataQualityCheckerHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_data_quality_checker_hexa.xi — generated from contracts/hexaforge_slm_training_master_data_quality_checker_hexa/xi.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterDataQualityCheckerHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_data_quality_checker_hexa.xo — generated from contracts/hexaforge_slm_training_master_data_quality_checker_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterDataQualityCheckerHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_data_quality_checker_hexa.yi — generated from contracts/hexaforge_slm_training_master_data_quality_checker_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_data_quality_checker_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterDataQualityCheckerHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_data_quality_checker_hexa.yo — generated from contracts/hexaforge_slm_training_master_data_quality_checker_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_data_quality_checker_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_data_quality_checker_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_data_quality_checker_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterDataQualityCheckerHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_data_quality_checker_hexa.zi — generated from contracts/hexaforge_slm_training_master_data_quality_checker_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterDataQualityCheckerHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_data_quality_checker_hexa.zo — generated from contracts/hexaforge_slm_training_master_data_quality_checker_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_data_quality_checker_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_data_quality_checker_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_data_quality_checker_hexa.zo session_id")

class HexaforgeSlmTrainingMasterDecisionLedgerHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_decision_ledger_hexa.xi — generated from contracts/hexaforge_slm_training_master_decision_ledger_hexa/xi.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterDecisionLedgerHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_decision_ledger_hexa.xo — generated from contracts/hexaforge_slm_training_master_decision_ledger_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterDecisionLedgerHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_decision_ledger_hexa.yi — generated from contracts/hexaforge_slm_training_master_decision_ledger_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_decision_ledger_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterDecisionLedgerHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_decision_ledger_hexa.yo — generated from contracts/hexaforge_slm_training_master_decision_ledger_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_decision_ledger_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_decision_ledger_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_decision_ledger_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterDecisionLedgerHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_decision_ledger_hexa.zi — generated from contracts/hexaforge_slm_training_master_decision_ledger_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterDecisionLedgerHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_decision_ledger_hexa.zo — generated from contracts/hexaforge_slm_training_master_decision_ledger_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_decision_ledger_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_decision_ledger_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_decision_ledger_hexa.zo session_id")

class HexaforgeSlmTrainingMasterArtifactMeterHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_artifact_meter_hexa.xi — generated from contracts/hexaforge_slm_training_master_artifact_meter_hexa/xi.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterArtifactMeterHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_artifact_meter_hexa.xo — generated from contracts/hexaforge_slm_training_master_artifact_meter_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterArtifactMeterHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_artifact_meter_hexa.yi — generated from contracts/hexaforge_slm_training_master_artifact_meter_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_artifact_meter_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterArtifactMeterHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_artifact_meter_hexa.yo — generated from contracts/hexaforge_slm_training_master_artifact_meter_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_artifact_meter_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_artifact_meter_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_artifact_meter_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterArtifactMeterHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_artifact_meter_hexa.zi — generated from contracts/hexaforge_slm_training_master_artifact_meter_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterArtifactMeterHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_artifact_meter_hexa.zo — generated from contracts/hexaforge_slm_training_master_artifact_meter_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_artifact_meter_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_artifact_meter_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_artifact_meter_hexa.zo session_id")

class HexaforgeSlmTrainingMasterDataProvenanceRecorderHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_data_provenance_recorder_hexa.xi — generated from contracts/hexaforge_slm_training_master_data_provenance_recorder_hexa/xi.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterDataProvenanceRecorderHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_data_provenance_recorder_hexa.xo — generated from contracts/hexaforge_slm_training_master_data_provenance_recorder_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterDataProvenanceRecorderHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_data_provenance_recorder_hexa.yi — generated from contracts/hexaforge_slm_training_master_data_provenance_recorder_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_data_provenance_recorder_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterDataProvenanceRecorderHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_data_provenance_recorder_hexa.yo — generated from contracts/hexaforge_slm_training_master_data_provenance_recorder_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_data_provenance_recorder_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_data_provenance_recorder_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_data_provenance_recorder_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterDataProvenanceRecorderHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_data_provenance_recorder_hexa.zi — generated from contracts/hexaforge_slm_training_master_data_provenance_recorder_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterDataProvenanceRecorderHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_data_provenance_recorder_hexa.zo — generated from contracts/hexaforge_slm_training_master_data_provenance_recorder_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_data_provenance_recorder_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_data_provenance_recorder_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_data_provenance_recorder_hexa.zo session_id")

class HexaforgeSlmTrainingMasterDriftDetectorHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_drift_detector_hexa.xi — generated from contracts/hexaforge_slm_training_master_drift_detector_hexa/xi.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterDriftDetectorHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_drift_detector_hexa.xo — generated from contracts/hexaforge_slm_training_master_drift_detector_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterDriftDetectorHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_drift_detector_hexa.yi — generated from contracts/hexaforge_slm_training_master_drift_detector_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_drift_detector_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterDriftDetectorHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_drift_detector_hexa.yo — generated from contracts/hexaforge_slm_training_master_drift_detector_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_drift_detector_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_drift_detector_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_drift_detector_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterDriftDetectorHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_drift_detector_hexa.zi — generated from contracts/hexaforge_slm_training_master_drift_detector_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterDriftDetectorHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_drift_detector_hexa.zo — generated from contracts/hexaforge_slm_training_master_drift_detector_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_drift_detector_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_drift_detector_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_drift_detector_hexa.zo session_id")

class HexaforgeSlmTrainingMasterRetrainProposerHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_retrain_proposer_hexa.xi — generated from contracts/hexaforge_slm_training_master_retrain_proposer_hexa/xi.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterRetrainProposerHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_retrain_proposer_hexa.xo — generated from contracts/hexaforge_slm_training_master_retrain_proposer_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterRetrainProposerHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_retrain_proposer_hexa.yi — generated from contracts/hexaforge_slm_training_master_retrain_proposer_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_retrain_proposer_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterRetrainProposerHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_retrain_proposer_hexa.yo — generated from contracts/hexaforge_slm_training_master_retrain_proposer_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_retrain_proposer_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_retrain_proposer_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_retrain_proposer_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterRetrainProposerHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_retrain_proposer_hexa.zi — generated from contracts/hexaforge_slm_training_master_retrain_proposer_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterRetrainProposerHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_retrain_proposer_hexa.zo — generated from contracts/hexaforge_slm_training_master_retrain_proposer_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_retrain_proposer_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_retrain_proposer_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_retrain_proposer_hexa.zo session_id")

class HexaforgeSlmTrainingMasterFleetBinderHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_fleet_binder_hexa.xi — generated from contracts/hexaforge_slm_training_master_fleet_binder_hexa/xi.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterFleetBinderHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_fleet_binder_hexa.xo — generated from contracts/hexaforge_slm_training_master_fleet_binder_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterFleetBinderHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_fleet_binder_hexa.yi — generated from contracts/hexaforge_slm_training_master_fleet_binder_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_fleet_binder_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterFleetBinderHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_fleet_binder_hexa.yo — generated from contracts/hexaforge_slm_training_master_fleet_binder_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_fleet_binder_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_fleet_binder_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_fleet_binder_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterFleetBinderHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_fleet_binder_hexa.zi — generated from contracts/hexaforge_slm_training_master_fleet_binder_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterFleetBinderHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_fleet_binder_hexa.zo — generated from contracts/hexaforge_slm_training_master_fleet_binder_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_fleet_binder_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_fleet_binder_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_fleet_binder_hexa.zo session_id")

class HexaforgeSlmTrainingMasterDelegationRegistrarHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_delegation_registrar_hexa.xi — generated from contracts/hexaforge_slm_training_master_delegation_registrar_hexa/xi.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterDelegationRegistrarHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_delegation_registrar_hexa.xo — generated from contracts/hexaforge_slm_training_master_delegation_registrar_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterDelegationRegistrarHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_delegation_registrar_hexa.yi — generated from contracts/hexaforge_slm_training_master_delegation_registrar_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_delegation_registrar_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterDelegationRegistrarHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_delegation_registrar_hexa.yo — generated from contracts/hexaforge_slm_training_master_delegation_registrar_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_delegation_registrar_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_delegation_registrar_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_delegation_registrar_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterDelegationRegistrarHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_delegation_registrar_hexa.zi — generated from contracts/hexaforge_slm_training_master_delegation_registrar_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterDelegationRegistrarHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_delegation_registrar_hexa.zo — generated from contracts/hexaforge_slm_training_master_delegation_registrar_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_delegation_registrar_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_delegation_registrar_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_delegation_registrar_hexa.zo session_id")

class HexaforgeSlmTrainingMasterDecisionHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_decision_hexa.xi — generated from contracts/hexaforge_slm_training_master_decision_hexa/xi.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterDecisionHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_decision_hexa.xo — generated from contracts/hexaforge_slm_training_master_decision_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterDecisionHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_decision_hexa.yi — generated from contracts/hexaforge_slm_training_master_decision_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_decision_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterDecisionHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_decision_hexa.yo — generated from contracts/hexaforge_slm_training_master_decision_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_decision_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_decision_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_decision_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterDecisionHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_decision_hexa.zi — generated from contracts/hexaforge_slm_training_master_decision_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterDecisionHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_decision_hexa.zo — generated from contracts/hexaforge_slm_training_master_decision_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_decision_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_decision_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_decision_hexa.zo session_id")

class HexaforgeSlmTrainingMasterModelFreshnessValidatorHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_model_freshness_validator_hexa.xi — generated from contracts/hexaforge_slm_training_master_model_freshness_validator_hexa/xi.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterModelFreshnessValidatorHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_model_freshness_validator_hexa.xo — generated from contracts/hexaforge_slm_training_master_model_freshness_validator_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterModelFreshnessValidatorHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_model_freshness_validator_hexa.yi — generated from contracts/hexaforge_slm_training_master_model_freshness_validator_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_model_freshness_validator_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterModelFreshnessValidatorHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_model_freshness_validator_hexa.yo — generated from contracts/hexaforge_slm_training_master_model_freshness_validator_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_model_freshness_validator_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_model_freshness_validator_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_model_freshness_validator_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterModelFreshnessValidatorHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_model_freshness_validator_hexa.zi — generated from contracts/hexaforge_slm_training_master_model_freshness_validator_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterModelFreshnessValidatorHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_model_freshness_validator_hexa.zo — generated from contracts/hexaforge_slm_training_master_model_freshness_validator_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_model_freshness_validator_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_model_freshness_validator_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_model_freshness_validator_hexa.zo session_id")

class HexaforgeSlmTrainingMasterSafetyValidatorHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_safety_validator_hexa.xi — generated from contracts/hexaforge_slm_training_master_safety_validator_hexa/xi.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterSafetyValidatorHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_safety_validator_hexa.xo — generated from contracts/hexaforge_slm_training_master_safety_validator_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterSafetyValidatorHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_safety_validator_hexa.yi — generated from contracts/hexaforge_slm_training_master_safety_validator_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_safety_validator_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterSafetyValidatorHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_safety_validator_hexa.yo — generated from contracts/hexaforge_slm_training_master_safety_validator_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_safety_validator_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_safety_validator_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_safety_validator_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterSafetyValidatorHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_safety_validator_hexa.zi — generated from contracts/hexaforge_slm_training_master_safety_validator_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterSafetyValidatorHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_safety_validator_hexa.zo — generated from contracts/hexaforge_slm_training_master_safety_validator_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_safety_validator_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_safety_validator_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_safety_validator_hexa.zo session_id")

class HexaforgeSlmTrainingMasterPackagerHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_packager_hexa.xi — generated from contracts/hexaforge_slm_training_master_packager_hexa/xi.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterPackagerHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_packager_hexa.xo — generated from contracts/hexaforge_slm_training_master_packager_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterPackagerHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_packager_hexa.yi — generated from contracts/hexaforge_slm_training_master_packager_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_packager_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterPackagerHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_packager_hexa.yo — generated from contracts/hexaforge_slm_training_master_packager_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_packager_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_packager_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_packager_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterPackagerHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_packager_hexa.zi — generated from contracts/hexaforge_slm_training_master_packager_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterPackagerHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_packager_hexa.zo — generated from contracts/hexaforge_slm_training_master_packager_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_packager_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_packager_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_packager_hexa.zo session_id")

class HexaforgeSlmTrainingMasterEgressOctaXiSchema(BaseModel):
    """hexaforge_slm_training_master_egress_octa.xi — generated from contracts/hexaforge_slm_training_master_egress_octa/xi.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterEgressOctaXoSchema(BaseModel):
    """hexaforge_slm_training_master_egress_octa.xo — generated from contracts/hexaforge_slm_training_master_egress_octa/xo.schema.json (v1.0.0)."""
    action: str = Field(..., description="hexaforge_slm_training_master_egress_octa.xo action")
    target: str = Field(..., description="hexaforge_slm_training_master_egress_octa.xo target")
    classification: Optional[str] = None
    governance_metadata: dict[str, Any] = Field(..., description="expects sub-fields: doctrine_score, audit_chain_hash")

class HexaforgeSlmTrainingMasterEgressOctaYiSchema(BaseModel):
    """hexaforge_slm_training_master_egress_octa.yi — generated from contracts/hexaforge_slm_training_master_egress_octa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_egress_octa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterEgressOctaYoSchema(BaseModel):
    """hexaforge_slm_training_master_egress_octa.yo — generated from contracts/hexaforge_slm_training_master_egress_octa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_egress_octa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_egress_octa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_egress_octa.yo action_kind")

class HexaforgeSlmTrainingMasterEgressOctaZiSchema(BaseModel):
    """hexaforge_slm_training_master_egress_octa.zi — generated from contracts/hexaforge_slm_training_master_egress_octa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterEgressOctaZoSchema(BaseModel):
    """hexaforge_slm_training_master_egress_octa.zo — generated from contracts/hexaforge_slm_training_master_egress_octa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_egress_octa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_egress_octa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_egress_octa.zo session_id")

class HexaforgeSlmTrainingMasterEgressOctaMiSchema(BaseModel):
    """hexaforge_slm_training_master_egress_octa.mi — generated from contracts/hexaforge_slm_training_master_egress_octa/mi.schema.json (v1.0.0)."""
    cycle_id: str = Field(..., description="N6 cohort-cycle correlation id")
    session_id: Optional[str] = None
    attempt_count: Optional[int] = None
    aggregated_count: Optional[int] = None
    side_feed_writes: Optional[dict[str, Any]] = None
    escalation_reason: Optional[str] = Field(None, description="legacy escalation payload (optional)")

class HexaforgeSlmTrainingMasterEgressOctaMoSchema(BaseModel):
    """hexaforge_slm_training_master_egress_octa.mo — generated from contracts/hexaforge_slm_training_master_egress_octa/mo.schema.json (v1.0.0)."""
    schema_version: str = Field(..., description="FleetSignal envelope version")
    event_type: str = Field(..., description="classification of the signal")
    vertical: str = Field(..., description="hexaforge_slm_training_master_egress_octa.mo vertical")
    aggregate_payload: dict[str, Any] = Field(..., description="k-anonymized aggregate")
    k_count: int = Field(..., ge=5, description="distinct tenants observed; must be >= 5")
    cycle_id: str = Field(..., description="N6 cohort-cycle correlation id")
    window_start: str = Field(..., description="aggregation window start (ISO 8601)")
    window_end: str = Field(..., description="aggregation window end (ISO 8601)")
    member_agent_id: str = Field(..., description="sending member agent id — must exist in the signed fleet member registry")
    karta_hash: str = Field(..., description="sha256 of the member compiled karta — must match the registry binding")
    doctrine_version: str = Field(..., description="member doctrine/ruleset version — must match the fleet doctrine")
    evidence: dict[str, Any] = Field(..., description="FleetEvidence/v1 — the authority-bearing conformance the coordinator attests (CEVE verdict/score, degraded, action rate, approval provenance), bound to the signature via evidence_digest.")
    evidence_digest: str = Field(..., description="sha256 of the canonical FleetEvidence/v1 object; a SIGNED field, so tampering the evidence breaks the signature.")
    sequence: int = Field(..., ge=0, description="per-member monotonic counter (replay protection)")
    nonce: str = Field(..., description="unique per envelope (replay protection inside the freshness window)")
    emitted_at: str = Field(..., description="ISO 8601 emission timestamp (freshness window)")
    sig: str = Field(..., description="Ed25519 signature (hex) over the canonical signed fields; verified against the member pubkey in the fleet registry")

class HexaforgeSlmTrainingMasterLearningStoreHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_learning_store_hexa.xi — generated from contracts/hexaforge_slm_training_master_learning_store_hexa/xi.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterLearningStoreHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_learning_store_hexa.xo — generated from contracts/hexaforge_slm_training_master_learning_store_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterLearningStoreHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_learning_store_hexa.yi — generated from contracts/hexaforge_slm_training_master_learning_store_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_learning_store_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterLearningStoreHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_learning_store_hexa.yo — generated from contracts/hexaforge_slm_training_master_learning_store_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_learning_store_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_learning_store_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_learning_store_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterLearningStoreHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_learning_store_hexa.zi — generated from contracts/hexaforge_slm_training_master_learning_store_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterLearningStoreHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_learning_store_hexa.zo — generated from contracts/hexaforge_slm_training_master_learning_store_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_learning_store_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_learning_store_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_learning_store_hexa.zo session_id")

class HexaforgeSlmTrainingMasterStartTrainingJobApprovalGateHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_start_training_job_approval_gate_hexa.xi — generated from contracts/hexaforge_slm_training_master_start_training_job_approval_gate_hexa/xi.schema.json (v1.0.0)."""
    confidence: float = Field(..., description="Selection confidence 0..1.")
    target_asset: str = Field(..., description="Subject the action applies to.")
    idempotency_key: str = Field(..., description="Stable key so a replayed proposal cannot double-execute.")
    selected_action: str = Field(..., description="Declared privileged-action name the router selected; empty string = no action.")
    action_parameters: dict[str, Any] = Field(..., description="Action-specific parameters.")
    policy_requirements: list[Any] = Field(..., description="Policy/CCAS requirements the selected gate must satisfy.")

class HexaforgeSlmTrainingMasterStartTrainingJobApprovalGateHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_start_training_job_approval_gate_hexa.xo — generated from contracts/hexaforge_slm_training_master_start_training_job_approval_gate_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterStartTrainingJobApprovalGateHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_start_training_job_approval_gate_hexa.yi — generated from contracts/hexaforge_slm_training_master_start_training_job_approval_gate_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_start_training_job_approval_gate_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterStartTrainingJobApprovalGateHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_start_training_job_approval_gate_hexa.yo — generated from contracts/hexaforge_slm_training_master_start_training_job_approval_gate_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_start_training_job_approval_gate_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_start_training_job_approval_gate_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_start_training_job_approval_gate_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterStartTrainingJobApprovalGateHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_start_training_job_approval_gate_hexa.zi — generated from contracts/hexaforge_slm_training_master_start_training_job_approval_gate_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterStartTrainingJobApprovalGateHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_start_training_job_approval_gate_hexa.zo — generated from contracts/hexaforge_slm_training_master_start_training_job_approval_gate_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_start_training_job_approval_gate_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_start_training_job_approval_gate_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_start_training_job_approval_gate_hexa.zo session_id")

class HexaforgeSlmTrainingMasterRequeueJobApprovalGateHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_requeue_job_approval_gate_hexa.xi — generated from contracts/hexaforge_slm_training_master_requeue_job_approval_gate_hexa/xi.schema.json (v1.0.0)."""
    confidence: float = Field(..., description="Selection confidence 0..1.")
    target_asset: str = Field(..., description="Subject the action applies to.")
    idempotency_key: str = Field(..., description="Stable key so a replayed proposal cannot double-execute.")
    selected_action: str = Field(..., description="Declared privileged-action name the router selected; empty string = no action.")
    action_parameters: dict[str, Any] = Field(..., description="Action-specific parameters.")
    policy_requirements: list[Any] = Field(..., description="Policy/CCAS requirements the selected gate must satisfy.")

class HexaforgeSlmTrainingMasterRequeueJobApprovalGateHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_requeue_job_approval_gate_hexa.xo — generated from contracts/hexaforge_slm_training_master_requeue_job_approval_gate_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterRequeueJobApprovalGateHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_requeue_job_approval_gate_hexa.yi — generated from contracts/hexaforge_slm_training_master_requeue_job_approval_gate_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_requeue_job_approval_gate_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterRequeueJobApprovalGateHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_requeue_job_approval_gate_hexa.yo — generated from contracts/hexaforge_slm_training_master_requeue_job_approval_gate_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_requeue_job_approval_gate_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_requeue_job_approval_gate_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_requeue_job_approval_gate_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterRequeueJobApprovalGateHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_requeue_job_approval_gate_hexa.zi — generated from contracts/hexaforge_slm_training_master_requeue_job_approval_gate_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterRequeueJobApprovalGateHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_requeue_job_approval_gate_hexa.zo — generated from contracts/hexaforge_slm_training_master_requeue_job_approval_gate_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_requeue_job_approval_gate_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_requeue_job_approval_gate_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_requeue_job_approval_gate_hexa.zo session_id")

class HexaforgeSlmTrainingMasterRetryWithAdjustmentApprovalGateHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_retry_with_adjustment_approval_gate_hexa.xi — generated from contracts/hexaforge_slm_training_master_retry_with_adjustment_approval_gate_hexa/xi.schema.json (v1.0.0)."""
    confidence: float = Field(..., description="Selection confidence 0..1.")
    target_asset: str = Field(..., description="Subject the action applies to.")
    idempotency_key: str = Field(..., description="Stable key so a replayed proposal cannot double-execute.")
    selected_action: str = Field(..., description="Declared privileged-action name the router selected; empty string = no action.")
    action_parameters: dict[str, Any] = Field(..., description="Action-specific parameters.")
    policy_requirements: list[Any] = Field(..., description="Policy/CCAS requirements the selected gate must satisfy.")

class HexaforgeSlmTrainingMasterRetryWithAdjustmentApprovalGateHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_retry_with_adjustment_approval_gate_hexa.xo — generated from contracts/hexaforge_slm_training_master_retry_with_adjustment_approval_gate_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterRetryWithAdjustmentApprovalGateHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_retry_with_adjustment_approval_gate_hexa.yi — generated from contracts/hexaforge_slm_training_master_retry_with_adjustment_approval_gate_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_retry_with_adjustment_approval_gate_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterRetryWithAdjustmentApprovalGateHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_retry_with_adjustment_approval_gate_hexa.yo — generated from contracts/hexaforge_slm_training_master_retry_with_adjustment_approval_gate_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_retry_with_adjustment_approval_gate_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_retry_with_adjustment_approval_gate_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_retry_with_adjustment_approval_gate_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterRetryWithAdjustmentApprovalGateHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_retry_with_adjustment_approval_gate_hexa.zi — generated from contracts/hexaforge_slm_training_master_retry_with_adjustment_approval_gate_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterRetryWithAdjustmentApprovalGateHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_retry_with_adjustment_approval_gate_hexa.zo — generated from contracts/hexaforge_slm_training_master_retry_with_adjustment_approval_gate_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_retry_with_adjustment_approval_gate_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_retry_with_adjustment_approval_gate_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_retry_with_adjustment_approval_gate_hexa.zo session_id")

class HexaforgeSlmTrainingMasterKillJobApprovalGateHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_kill_job_approval_gate_hexa.xi — generated from contracts/hexaforge_slm_training_master_kill_job_approval_gate_hexa/xi.schema.json (v1.0.0)."""
    confidence: float = Field(..., description="Selection confidence 0..1.")
    target_asset: str = Field(..., description="Subject the action applies to.")
    idempotency_key: str = Field(..., description="Stable key so a replayed proposal cannot double-execute.")
    selected_action: str = Field(..., description="Declared privileged-action name the router selected; empty string = no action.")
    action_parameters: dict[str, Any] = Field(..., description="Action-specific parameters.")
    policy_requirements: list[Any] = Field(..., description="Policy/CCAS requirements the selected gate must satisfy.")

class HexaforgeSlmTrainingMasterKillJobApprovalGateHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_kill_job_approval_gate_hexa.xo — generated from contracts/hexaforge_slm_training_master_kill_job_approval_gate_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterKillJobApprovalGateHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_kill_job_approval_gate_hexa.yi — generated from contracts/hexaforge_slm_training_master_kill_job_approval_gate_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_kill_job_approval_gate_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterKillJobApprovalGateHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_kill_job_approval_gate_hexa.yo — generated from contracts/hexaforge_slm_training_master_kill_job_approval_gate_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_kill_job_approval_gate_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_kill_job_approval_gate_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_kill_job_approval_gate_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterKillJobApprovalGateHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_kill_job_approval_gate_hexa.zi — generated from contracts/hexaforge_slm_training_master_kill_job_approval_gate_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterKillJobApprovalGateHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_kill_job_approval_gate_hexa.zo — generated from contracts/hexaforge_slm_training_master_kill_job_approval_gate_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_kill_job_approval_gate_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_kill_job_approval_gate_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_kill_job_approval_gate_hexa.zo session_id")

class HexaforgeSlmTrainingMasterPauseCampaignApprovalGateHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_pause_campaign_approval_gate_hexa.xi — generated from contracts/hexaforge_slm_training_master_pause_campaign_approval_gate_hexa/xi.schema.json (v1.0.0)."""
    confidence: float = Field(..., description="Selection confidence 0..1.")
    target_asset: str = Field(..., description="Subject the action applies to.")
    idempotency_key: str = Field(..., description="Stable key so a replayed proposal cannot double-execute.")
    selected_action: str = Field(..., description="Declared privileged-action name the router selected; empty string = no action.")
    action_parameters: dict[str, Any] = Field(..., description="Action-specific parameters.")
    policy_requirements: list[Any] = Field(..., description="Policy/CCAS requirements the selected gate must satisfy.")

class HexaforgeSlmTrainingMasterPauseCampaignApprovalGateHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_pause_campaign_approval_gate_hexa.xo — generated from contracts/hexaforge_slm_training_master_pause_campaign_approval_gate_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterPauseCampaignApprovalGateHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_pause_campaign_approval_gate_hexa.yi — generated from contracts/hexaforge_slm_training_master_pause_campaign_approval_gate_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_pause_campaign_approval_gate_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterPauseCampaignApprovalGateHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_pause_campaign_approval_gate_hexa.yo — generated from contracts/hexaforge_slm_training_master_pause_campaign_approval_gate_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_pause_campaign_approval_gate_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_pause_campaign_approval_gate_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_pause_campaign_approval_gate_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterPauseCampaignApprovalGateHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_pause_campaign_approval_gate_hexa.zi — generated from contracts/hexaforge_slm_training_master_pause_campaign_approval_gate_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterPauseCampaignApprovalGateHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_pause_campaign_approval_gate_hexa.zo — generated from contracts/hexaforge_slm_training_master_pause_campaign_approval_gate_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_pause_campaign_approval_gate_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_pause_campaign_approval_gate_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_pause_campaign_approval_gate_hexa.zo session_id")

class HexaforgeSlmTrainingMasterResumeCampaignApprovalGateHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_resume_campaign_approval_gate_hexa.xi — generated from contracts/hexaforge_slm_training_master_resume_campaign_approval_gate_hexa/xi.schema.json (v1.0.0)."""
    confidence: float = Field(..., description="Selection confidence 0..1.")
    target_asset: str = Field(..., description="Subject the action applies to.")
    idempotency_key: str = Field(..., description="Stable key so a replayed proposal cannot double-execute.")
    selected_action: str = Field(..., description="Declared privileged-action name the router selected; empty string = no action.")
    action_parameters: dict[str, Any] = Field(..., description="Action-specific parameters.")
    policy_requirements: list[Any] = Field(..., description="Policy/CCAS requirements the selected gate must satisfy.")

class HexaforgeSlmTrainingMasterResumeCampaignApprovalGateHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_resume_campaign_approval_gate_hexa.xo — generated from contracts/hexaforge_slm_training_master_resume_campaign_approval_gate_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterResumeCampaignApprovalGateHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_resume_campaign_approval_gate_hexa.yi — generated from contracts/hexaforge_slm_training_master_resume_campaign_approval_gate_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_resume_campaign_approval_gate_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterResumeCampaignApprovalGateHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_resume_campaign_approval_gate_hexa.yo — generated from contracts/hexaforge_slm_training_master_resume_campaign_approval_gate_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_resume_campaign_approval_gate_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_resume_campaign_approval_gate_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_resume_campaign_approval_gate_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterResumeCampaignApprovalGateHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_resume_campaign_approval_gate_hexa.zi — generated from contracts/hexaforge_slm_training_master_resume_campaign_approval_gate_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterResumeCampaignApprovalGateHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_resume_campaign_approval_gate_hexa.zo — generated from contracts/hexaforge_slm_training_master_resume_campaign_approval_gate_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_resume_campaign_approval_gate_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_resume_campaign_approval_gate_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_resume_campaign_approval_gate_hexa.zo session_id")

class HexaforgeSlmTrainingMasterParkJobApprovalGateHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_park_job_approval_gate_hexa.xi — generated from contracts/hexaforge_slm_training_master_park_job_approval_gate_hexa/xi.schema.json (v1.0.0)."""
    confidence: float = Field(..., description="Selection confidence 0..1.")
    target_asset: str = Field(..., description="Subject the action applies to.")
    idempotency_key: str = Field(..., description="Stable key so a replayed proposal cannot double-execute.")
    selected_action: str = Field(..., description="Declared privileged-action name the router selected; empty string = no action.")
    action_parameters: dict[str, Any] = Field(..., description="Action-specific parameters.")
    policy_requirements: list[Any] = Field(..., description="Policy/CCAS requirements the selected gate must satisfy.")

class HexaforgeSlmTrainingMasterParkJobApprovalGateHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_park_job_approval_gate_hexa.xo — generated from contracts/hexaforge_slm_training_master_park_job_approval_gate_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterParkJobApprovalGateHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_park_job_approval_gate_hexa.yi — generated from contracts/hexaforge_slm_training_master_park_job_approval_gate_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_park_job_approval_gate_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterParkJobApprovalGateHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_park_job_approval_gate_hexa.yo — generated from contracts/hexaforge_slm_training_master_park_job_approval_gate_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_park_job_approval_gate_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_park_job_approval_gate_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_park_job_approval_gate_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterParkJobApprovalGateHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_park_job_approval_gate_hexa.zi — generated from contracts/hexaforge_slm_training_master_park_job_approval_gate_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterParkJobApprovalGateHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_park_job_approval_gate_hexa.zo — generated from contracts/hexaforge_slm_training_master_park_job_approval_gate_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_park_job_approval_gate_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_park_job_approval_gate_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_park_job_approval_gate_hexa.zo session_id")

class HexaforgeSlmTrainingMasterKeepParkedApprovalGateHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_keep_parked_approval_gate_hexa.xi — generated from contracts/hexaforge_slm_training_master_keep_parked_approval_gate_hexa/xi.schema.json (v1.0.0)."""
    confidence: float = Field(..., description="Selection confidence 0..1.")
    target_asset: str = Field(..., description="Subject the action applies to.")
    idempotency_key: str = Field(..., description="Stable key so a replayed proposal cannot double-execute.")
    selected_action: str = Field(..., description="Declared privileged-action name the router selected; empty string = no action.")
    action_parameters: dict[str, Any] = Field(..., description="Action-specific parameters.")
    policy_requirements: list[Any] = Field(..., description="Policy/CCAS requirements the selected gate must satisfy.")

class HexaforgeSlmTrainingMasterKeepParkedApprovalGateHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_keep_parked_approval_gate_hexa.xo — generated from contracts/hexaforge_slm_training_master_keep_parked_approval_gate_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterKeepParkedApprovalGateHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_keep_parked_approval_gate_hexa.yi — generated from contracts/hexaforge_slm_training_master_keep_parked_approval_gate_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_keep_parked_approval_gate_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterKeepParkedApprovalGateHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_keep_parked_approval_gate_hexa.yo — generated from contracts/hexaforge_slm_training_master_keep_parked_approval_gate_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_keep_parked_approval_gate_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_keep_parked_approval_gate_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_keep_parked_approval_gate_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterKeepParkedApprovalGateHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_keep_parked_approval_gate_hexa.zi — generated from contracts/hexaforge_slm_training_master_keep_parked_approval_gate_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterKeepParkedApprovalGateHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_keep_parked_approval_gate_hexa.zo — generated from contracts/hexaforge_slm_training_master_keep_parked_approval_gate_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_keep_parked_approval_gate_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_keep_parked_approval_gate_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_keep_parked_approval_gate_hexa.zo session_id")

class HexaforgeSlmTrainingMasterRemoveFlaggedRowsAndRecheckApprovalGateHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa.xi — generated from contracts/hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa/xi.schema.json (v1.0.0)."""
    confidence: float = Field(..., description="Selection confidence 0..1.")
    target_asset: str = Field(..., description="Subject the action applies to.")
    idempotency_key: str = Field(..., description="Stable key so a replayed proposal cannot double-execute.")
    selected_action: str = Field(..., description="Declared privileged-action name the router selected; empty string = no action.")
    action_parameters: dict[str, Any] = Field(..., description="Action-specific parameters.")
    policy_requirements: list[Any] = Field(..., description="Policy/CCAS requirements the selected gate must satisfy.")

class HexaforgeSlmTrainingMasterRemoveFlaggedRowsAndRecheckApprovalGateHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa.xo — generated from contracts/hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterRemoveFlaggedRowsAndRecheckApprovalGateHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa.yi — generated from contracts/hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterRemoveFlaggedRowsAndRecheckApprovalGateHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa.yo — generated from contracts/hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterRemoveFlaggedRowsAndRecheckApprovalGateHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa.zi — generated from contracts/hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterRemoveFlaggedRowsAndRecheckApprovalGateHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa.zo — generated from contracts/hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa.zo session_id")

class HexaforgeSlmTrainingMasterPromoteAndBindAdapterApprovalGateHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_promote_and_bind_adapter_approval_gate_hexa.xi — generated from contracts/hexaforge_slm_training_master_promote_and_bind_adapter_approval_gate_hexa/xi.schema.json (v1.0.0)."""
    confidence: float = Field(..., description="Selection confidence 0..1.")
    target_asset: str = Field(..., description="Subject the action applies to.")
    idempotency_key: str = Field(..., description="Stable key so a replayed proposal cannot double-execute.")
    selected_action: str = Field(..., description="Declared privileged-action name the router selected; empty string = no action.")
    action_parameters: dict[str, Any] = Field(..., description="Action-specific parameters.")
    policy_requirements: list[Any] = Field(..., description="Policy/CCAS requirements the selected gate must satisfy.")

class HexaforgeSlmTrainingMasterPromoteAndBindAdapterApprovalGateHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_promote_and_bind_adapter_approval_gate_hexa.xo — generated from contracts/hexaforge_slm_training_master_promote_and_bind_adapter_approval_gate_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterPromoteAndBindAdapterApprovalGateHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_promote_and_bind_adapter_approval_gate_hexa.yi — generated from contracts/hexaforge_slm_training_master_promote_and_bind_adapter_approval_gate_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_promote_and_bind_adapter_approval_gate_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterPromoteAndBindAdapterApprovalGateHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_promote_and_bind_adapter_approval_gate_hexa.yo — generated from contracts/hexaforge_slm_training_master_promote_and_bind_adapter_approval_gate_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_promote_and_bind_adapter_approval_gate_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_promote_and_bind_adapter_approval_gate_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_promote_and_bind_adapter_approval_gate_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterPromoteAndBindAdapterApprovalGateHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_promote_and_bind_adapter_approval_gate_hexa.zi — generated from contracts/hexaforge_slm_training_master_promote_and_bind_adapter_approval_gate_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterPromoteAndBindAdapterApprovalGateHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_promote_and_bind_adapter_approval_gate_hexa.zo — generated from contracts/hexaforge_slm_training_master_promote_and_bind_adapter_approval_gate_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_promote_and_bind_adapter_approval_gate_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_promote_and_bind_adapter_approval_gate_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_promote_and_bind_adapter_approval_gate_hexa.zo session_id")

class HexaforgeSlmTrainingMasterDenyBindApprovalGateHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_deny_bind_approval_gate_hexa.xi — generated from contracts/hexaforge_slm_training_master_deny_bind_approval_gate_hexa/xi.schema.json (v1.0.0)."""
    confidence: float = Field(..., description="Selection confidence 0..1.")
    target_asset: str = Field(..., description="Subject the action applies to.")
    idempotency_key: str = Field(..., description="Stable key so a replayed proposal cannot double-execute.")
    selected_action: str = Field(..., description="Declared privileged-action name the router selected; empty string = no action.")
    action_parameters: dict[str, Any] = Field(..., description="Action-specific parameters.")
    policy_requirements: list[Any] = Field(..., description="Policy/CCAS requirements the selected gate must satisfy.")

class HexaforgeSlmTrainingMasterDenyBindApprovalGateHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_deny_bind_approval_gate_hexa.xo — generated from contracts/hexaforge_slm_training_master_deny_bind_approval_gate_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterDenyBindApprovalGateHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_deny_bind_approval_gate_hexa.yi — generated from contracts/hexaforge_slm_training_master_deny_bind_approval_gate_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_deny_bind_approval_gate_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterDenyBindApprovalGateHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_deny_bind_approval_gate_hexa.yo — generated from contracts/hexaforge_slm_training_master_deny_bind_approval_gate_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_deny_bind_approval_gate_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_deny_bind_approval_gate_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_deny_bind_approval_gate_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterDenyBindApprovalGateHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_deny_bind_approval_gate_hexa.zi — generated from contracts/hexaforge_slm_training_master_deny_bind_approval_gate_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterDenyBindApprovalGateHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_deny_bind_approval_gate_hexa.zo — generated from contracts/hexaforge_slm_training_master_deny_bind_approval_gate_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_deny_bind_approval_gate_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_deny_bind_approval_gate_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_deny_bind_approval_gate_hexa.zo session_id")

class HexaforgeSlmTrainingMasterRollbackBindingApprovalGateHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_rollback_binding_approval_gate_hexa.xi — generated from contracts/hexaforge_slm_training_master_rollback_binding_approval_gate_hexa/xi.schema.json (v1.0.0)."""
    confidence: float = Field(..., description="Selection confidence 0..1.")
    target_asset: str = Field(..., description="Subject the action applies to.")
    idempotency_key: str = Field(..., description="Stable key so a replayed proposal cannot double-execute.")
    selected_action: str = Field(..., description="Declared privileged-action name the router selected; empty string = no action.")
    action_parameters: dict[str, Any] = Field(..., description="Action-specific parameters.")
    policy_requirements: list[Any] = Field(..., description="Policy/CCAS requirements the selected gate must satisfy.")

class HexaforgeSlmTrainingMasterRollbackBindingApprovalGateHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_rollback_binding_approval_gate_hexa.xo — generated from contracts/hexaforge_slm_training_master_rollback_binding_approval_gate_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterRollbackBindingApprovalGateHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_rollback_binding_approval_gate_hexa.yi — generated from contracts/hexaforge_slm_training_master_rollback_binding_approval_gate_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_rollback_binding_approval_gate_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterRollbackBindingApprovalGateHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_rollback_binding_approval_gate_hexa.yo — generated from contracts/hexaforge_slm_training_master_rollback_binding_approval_gate_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_rollback_binding_approval_gate_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_rollback_binding_approval_gate_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_rollback_binding_approval_gate_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterRollbackBindingApprovalGateHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_rollback_binding_approval_gate_hexa.zi — generated from contracts/hexaforge_slm_training_master_rollback_binding_approval_gate_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterRollbackBindingApprovalGateHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_rollback_binding_approval_gate_hexa.zo — generated from contracts/hexaforge_slm_training_master_rollback_binding_approval_gate_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_rollback_binding_approval_gate_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_rollback_binding_approval_gate_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_rollback_binding_approval_gate_hexa.zo session_id")

class HexaforgeSlmTrainingMasterDeleteArtifactApprovalGateHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_delete_artifact_approval_gate_hexa.xi — generated from contracts/hexaforge_slm_training_master_delete_artifact_approval_gate_hexa/xi.schema.json (v1.0.0)."""
    confidence: float = Field(..., description="Selection confidence 0..1.")
    target_asset: str = Field(..., description="Subject the action applies to.")
    idempotency_key: str = Field(..., description="Stable key so a replayed proposal cannot double-execute.")
    selected_action: str = Field(..., description="Declared privileged-action name the router selected; empty string = no action.")
    action_parameters: dict[str, Any] = Field(..., description="Action-specific parameters.")
    policy_requirements: list[Any] = Field(..., description="Policy/CCAS requirements the selected gate must satisfy.")

class HexaforgeSlmTrainingMasterDeleteArtifactApprovalGateHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_delete_artifact_approval_gate_hexa.xo — generated from contracts/hexaforge_slm_training_master_delete_artifact_approval_gate_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterDeleteArtifactApprovalGateHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_delete_artifact_approval_gate_hexa.yi — generated from contracts/hexaforge_slm_training_master_delete_artifact_approval_gate_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_delete_artifact_approval_gate_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterDeleteArtifactApprovalGateHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_delete_artifact_approval_gate_hexa.yo — generated from contracts/hexaforge_slm_training_master_delete_artifact_approval_gate_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_delete_artifact_approval_gate_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_delete_artifact_approval_gate_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_delete_artifact_approval_gate_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterDeleteArtifactApprovalGateHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_delete_artifact_approval_gate_hexa.zi — generated from contracts/hexaforge_slm_training_master_delete_artifact_approval_gate_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterDeleteArtifactApprovalGateHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_delete_artifact_approval_gate_hexa.zo — generated from contracts/hexaforge_slm_training_master_delete_artifact_approval_gate_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_delete_artifact_approval_gate_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_delete_artifact_approval_gate_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_delete_artifact_approval_gate_hexa.zo session_id")

class HexaforgeSlmTrainingMasterTriggerRetrainApprovalGateHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa.xi — generated from contracts/hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa/xi.schema.json (v1.0.0)."""
    confidence: float = Field(..., description="Selection confidence 0..1.")
    target_asset: str = Field(..., description="Subject the action applies to.")
    idempotency_key: str = Field(..., description="Stable key so a replayed proposal cannot double-execute.")
    selected_action: str = Field(..., description="Declared privileged-action name the router selected; empty string = no action.")
    action_parameters: dict[str, Any] = Field(..., description="Action-specific parameters.")
    policy_requirements: list[Any] = Field(..., description="Policy/CCAS requirements the selected gate must satisfy.")

class HexaforgeSlmTrainingMasterTriggerRetrainApprovalGateHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa.xo — generated from contracts/hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterTriggerRetrainApprovalGateHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa.yi — generated from contracts/hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterTriggerRetrainApprovalGateHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa.yo — generated from contracts/hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterTriggerRetrainApprovalGateHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa.zi — generated from contracts/hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterTriggerRetrainApprovalGateHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa.zo — generated from contracts/hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa.zo session_id")

class HexaforgeSlmTrainingMasterBindAdapterToFleetAgentApprovalGateHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_bind_adapter_to_fleet_agent_approval_gate_hexa.xi — generated from contracts/hexaforge_slm_training_master_bind_adapter_to_fleet_agent_approval_gate_hexa/xi.schema.json (v1.0.0)."""
    confidence: float = Field(..., description="Selection confidence 0..1.")
    target_asset: str = Field(..., description="Subject the action applies to.")
    idempotency_key: str = Field(..., description="Stable key so a replayed proposal cannot double-execute.")
    selected_action: str = Field(..., description="Declared privileged-action name the router selected; empty string = no action.")
    action_parameters: dict[str, Any] = Field(..., description="Action-specific parameters.")
    policy_requirements: list[Any] = Field(..., description="Policy/CCAS requirements the selected gate must satisfy.")

class HexaforgeSlmTrainingMasterBindAdapterToFleetAgentApprovalGateHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_bind_adapter_to_fleet_agent_approval_gate_hexa.xo — generated from contracts/hexaforge_slm_training_master_bind_adapter_to_fleet_agent_approval_gate_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterBindAdapterToFleetAgentApprovalGateHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_bind_adapter_to_fleet_agent_approval_gate_hexa.yi — generated from contracts/hexaforge_slm_training_master_bind_adapter_to_fleet_agent_approval_gate_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_bind_adapter_to_fleet_agent_approval_gate_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterBindAdapterToFleetAgentApprovalGateHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_bind_adapter_to_fleet_agent_approval_gate_hexa.yo — generated from contracts/hexaforge_slm_training_master_bind_adapter_to_fleet_agent_approval_gate_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_bind_adapter_to_fleet_agent_approval_gate_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_bind_adapter_to_fleet_agent_approval_gate_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_bind_adapter_to_fleet_agent_approval_gate_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterBindAdapterToFleetAgentApprovalGateHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_bind_adapter_to_fleet_agent_approval_gate_hexa.zi — generated from contracts/hexaforge_slm_training_master_bind_adapter_to_fleet_agent_approval_gate_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterBindAdapterToFleetAgentApprovalGateHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_bind_adapter_to_fleet_agent_approval_gate_hexa.zo — generated from contracts/hexaforge_slm_training_master_bind_adapter_to_fleet_agent_approval_gate_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_bind_adapter_to_fleet_agent_approval_gate_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_bind_adapter_to_fleet_agent_approval_gate_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_bind_adapter_to_fleet_agent_approval_gate_hexa.zo session_id")

class HexaforgeSlmTrainingMasterRollbackFleetBindingApprovalGateHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_rollback_fleet_binding_approval_gate_hexa.xi — generated from contracts/hexaforge_slm_training_master_rollback_fleet_binding_approval_gate_hexa/xi.schema.json (v1.0.0)."""
    confidence: float = Field(..., description="Selection confidence 0..1.")
    target_asset: str = Field(..., description="Subject the action applies to.")
    idempotency_key: str = Field(..., description="Stable key so a replayed proposal cannot double-execute.")
    selected_action: str = Field(..., description="Declared privileged-action name the router selected; empty string = no action.")
    action_parameters: dict[str, Any] = Field(..., description="Action-specific parameters.")
    policy_requirements: list[Any] = Field(..., description="Policy/CCAS requirements the selected gate must satisfy.")

class HexaforgeSlmTrainingMasterRollbackFleetBindingApprovalGateHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_rollback_fleet_binding_approval_gate_hexa.xo — generated from contracts/hexaforge_slm_training_master_rollback_fleet_binding_approval_gate_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterRollbackFleetBindingApprovalGateHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_rollback_fleet_binding_approval_gate_hexa.yi — generated from contracts/hexaforge_slm_training_master_rollback_fleet_binding_approval_gate_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_rollback_fleet_binding_approval_gate_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterRollbackFleetBindingApprovalGateHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_rollback_fleet_binding_approval_gate_hexa.yo — generated from contracts/hexaforge_slm_training_master_rollback_fleet_binding_approval_gate_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_rollback_fleet_binding_approval_gate_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_rollback_fleet_binding_approval_gate_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_rollback_fleet_binding_approval_gate_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterRollbackFleetBindingApprovalGateHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_rollback_fleet_binding_approval_gate_hexa.zi — generated from contracts/hexaforge_slm_training_master_rollback_fleet_binding_approval_gate_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterRollbackFleetBindingApprovalGateHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_rollback_fleet_binding_approval_gate_hexa.zo — generated from contracts/hexaforge_slm_training_master_rollback_fleet_binding_approval_gate_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_rollback_fleet_binding_approval_gate_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_rollback_fleet_binding_approval_gate_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_rollback_fleet_binding_approval_gate_hexa.zo session_id")

class HexaforgeSlmTrainingMasterGrantSharedAdapterTrainingApprovalGateHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_grant_shared_adapter_training_approval_gate_hexa.xi — generated from contracts/hexaforge_slm_training_master_grant_shared_adapter_training_approval_gate_hexa/xi.schema.json (v1.0.0)."""
    confidence: float = Field(..., description="Selection confidence 0..1.")
    target_asset: str = Field(..., description="Subject the action applies to.")
    idempotency_key: str = Field(..., description="Stable key so a replayed proposal cannot double-execute.")
    selected_action: str = Field(..., description="Declared privileged-action name the router selected; empty string = no action.")
    action_parameters: dict[str, Any] = Field(..., description="Action-specific parameters.")
    policy_requirements: list[Any] = Field(..., description="Policy/CCAS requirements the selected gate must satisfy.")

class HexaforgeSlmTrainingMasterGrantSharedAdapterTrainingApprovalGateHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_grant_shared_adapter_training_approval_gate_hexa.xo — generated from contracts/hexaforge_slm_training_master_grant_shared_adapter_training_approval_gate_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterGrantSharedAdapterTrainingApprovalGateHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_grant_shared_adapter_training_approval_gate_hexa.yi — generated from contracts/hexaforge_slm_training_master_grant_shared_adapter_training_approval_gate_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_grant_shared_adapter_training_approval_gate_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterGrantSharedAdapterTrainingApprovalGateHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_grant_shared_adapter_training_approval_gate_hexa.yo — generated from contracts/hexaforge_slm_training_master_grant_shared_adapter_training_approval_gate_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_grant_shared_adapter_training_approval_gate_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_grant_shared_adapter_training_approval_gate_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_grant_shared_adapter_training_approval_gate_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterGrantSharedAdapterTrainingApprovalGateHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_grant_shared_adapter_training_approval_gate_hexa.zi — generated from contracts/hexaforge_slm_training_master_grant_shared_adapter_training_approval_gate_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterGrantSharedAdapterTrainingApprovalGateHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_grant_shared_adapter_training_approval_gate_hexa.zo — generated from contracts/hexaforge_slm_training_master_grant_shared_adapter_training_approval_gate_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_grant_shared_adapter_training_approval_gate_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_grant_shared_adapter_training_approval_gate_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_grant_shared_adapter_training_approval_gate_hexa.zo session_id")

class HexaforgeSlmTrainingMasterIssueDelegationGrantApprovalGateHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_issue_delegation_grant_approval_gate_hexa.xi — generated from contracts/hexaforge_slm_training_master_issue_delegation_grant_approval_gate_hexa/xi.schema.json (v1.0.0)."""
    confidence: float = Field(..., description="Selection confidence 0..1.")
    target_asset: str = Field(..., description="Subject the action applies to.")
    idempotency_key: str = Field(..., description="Stable key so a replayed proposal cannot double-execute.")
    selected_action: str = Field(..., description="Declared privileged-action name the router selected; empty string = no action.")
    action_parameters: dict[str, Any] = Field(..., description="Action-specific parameters.")
    policy_requirements: list[Any] = Field(..., description="Policy/CCAS requirements the selected gate must satisfy.")

class HexaforgeSlmTrainingMasterIssueDelegationGrantApprovalGateHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_issue_delegation_grant_approval_gate_hexa.xo — generated from contracts/hexaforge_slm_training_master_issue_delegation_grant_approval_gate_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterIssueDelegationGrantApprovalGateHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_issue_delegation_grant_approval_gate_hexa.yi — generated from contracts/hexaforge_slm_training_master_issue_delegation_grant_approval_gate_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_issue_delegation_grant_approval_gate_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterIssueDelegationGrantApprovalGateHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_issue_delegation_grant_approval_gate_hexa.yo — generated from contracts/hexaforge_slm_training_master_issue_delegation_grant_approval_gate_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_issue_delegation_grant_approval_gate_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_issue_delegation_grant_approval_gate_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_issue_delegation_grant_approval_gate_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterIssueDelegationGrantApprovalGateHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_issue_delegation_grant_approval_gate_hexa.zi — generated from contracts/hexaforge_slm_training_master_issue_delegation_grant_approval_gate_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterIssueDelegationGrantApprovalGateHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_issue_delegation_grant_approval_gate_hexa.zo — generated from contracts/hexaforge_slm_training_master_issue_delegation_grant_approval_gate_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_issue_delegation_grant_approval_gate_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_issue_delegation_grant_approval_gate_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_issue_delegation_grant_approval_gate_hexa.zo session_id")

class HexaforgeSlmTrainingMasterRevokeDelegationGrantApprovalGateHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_revoke_delegation_grant_approval_gate_hexa.xi — generated from contracts/hexaforge_slm_training_master_revoke_delegation_grant_approval_gate_hexa/xi.schema.json (v1.0.0)."""
    confidence: float = Field(..., description="Selection confidence 0..1.")
    target_asset: str = Field(..., description="Subject the action applies to.")
    idempotency_key: str = Field(..., description="Stable key so a replayed proposal cannot double-execute.")
    selected_action: str = Field(..., description="Declared privileged-action name the router selected; empty string = no action.")
    action_parameters: dict[str, Any] = Field(..., description="Action-specific parameters.")
    policy_requirements: list[Any] = Field(..., description="Policy/CCAS requirements the selected gate must satisfy.")

class HexaforgeSlmTrainingMasterRevokeDelegationGrantApprovalGateHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_revoke_delegation_grant_approval_gate_hexa.xo — generated from contracts/hexaforge_slm_training_master_revoke_delegation_grant_approval_gate_hexa/xo.schema.json (v1.0.0)."""

class HexaforgeSlmTrainingMasterRevokeDelegationGrantApprovalGateHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_revoke_delegation_grant_approval_gate_hexa.yi — generated from contracts/hexaforge_slm_training_master_revoke_delegation_grant_approval_gate_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_revoke_delegation_grant_approval_gate_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterRevokeDelegationGrantApprovalGateHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_revoke_delegation_grant_approval_gate_hexa.yo — generated from contracts/hexaforge_slm_training_master_revoke_delegation_grant_approval_gate_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_revoke_delegation_grant_approval_gate_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_revoke_delegation_grant_approval_gate_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_revoke_delegation_grant_approval_gate_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterRevokeDelegationGrantApprovalGateHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_revoke_delegation_grant_approval_gate_hexa.zi — generated from contracts/hexaforge_slm_training_master_revoke_delegation_grant_approval_gate_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterRevokeDelegationGrantApprovalGateHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_revoke_delegation_grant_approval_gate_hexa.zo — generated from contracts/hexaforge_slm_training_master_revoke_delegation_grant_approval_gate_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_revoke_delegation_grant_approval_gate_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_revoke_delegation_grant_approval_gate_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_revoke_delegation_grant_approval_gate_hexa.zo session_id")

class HexaforgeSlmTrainingMasterActionSelectorHexaXiSchema(BaseModel):
    """hexaforge_slm_training_master_action_selector_hexa.xi — generated from contracts/hexaforge_slm_training_master_action_selector_hexa/xi.schema.json (v1.0.0)."""
    confidence: Optional[float] = Field(None, description="Selection confidence 0..1.")
    target_asset: Optional[str] = Field(None, description="Subject the action applies to.")
    idempotency_key: Optional[str] = Field(None, description="Stable key so a replayed proposal cannot double-execute.")
    selected_action: Optional[str] = Field(None, description="Declared privileged-action name the router selected; empty string = no action.")
    action_parameters: Optional[dict[str, Any]] = Field(None, description="Action-specific parameters.")
    policy_requirements: Optional[list[Any]] = Field(None, description="Policy/CCAS requirements the selected gate must satisfy.")

class HexaforgeSlmTrainingMasterActionSelectorHexaXoSchema(BaseModel):
    """hexaforge_slm_training_master_action_selector_hexa.xo — generated from contracts/hexaforge_slm_training_master_action_selector_hexa/xo.schema.json (v1.0.0)."""
    # schema declares additionalProperties:false — an undeclared field is a
    # contract violation, not something to silently drop.
    model_config = ConfigDict(extra="forbid")
    ts: Optional[str] = None
    payload: Optional[dict[str, Any]] = Field(None, description="final payload ready for external emission")
    confidence: float = Field(..., description="Selection confidence 0..1.")
    target_asset: str = Field(..., description="Subject the action applies to.")
    idempotency_key: str = Field(..., description="Stable key so a replayed proposal cannot double-execute.")
    selected_action: str = Field(..., description="Declared privileged-action name the router selected; empty string = no action.")
    action_parameters: dict[str, Any] = Field(..., description="Action-specific parameters.")
    policy_requirements: list[Any] = Field(..., description="Policy/CCAS requirements the selected gate must satisfy.")
    tenant_id: str = Field(..., description="Tenant the action is scoped to. Bound into the signed action hash and into the execution reservation; a gated action without it fails closed.")

class HexaforgeSlmTrainingMasterActionSelectorHexaYiSchema(BaseModel):
    """hexaforge_slm_training_master_action_selector_hexa.yi — generated from contracts/hexaforge_slm_training_master_action_selector_hexa/yi.schema.json (v1.0.0)."""
    ccas_tier: str = Field(..., description="auto | manual | human | dual_approval")
    policy_id: str = Field(..., description="hexaforge_slm_training_master_action_selector_hexa.yi policy_id")
    tenant_id: Optional[str] = None
    effective_k_minimum: Optional[dict[str, Any]] = None

class HexaforgeSlmTrainingMasterActionSelectorHexaYoSchema(BaseModel):
    """hexaforge_slm_training_master_action_selector_hexa.yo — generated from contracts/hexaforge_slm_training_master_action_selector_hexa/yo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    reason: Optional[str] = None
    user_id: Optional[str] = None
    vertical: str = Field(..., description="hexaforge_slm_training_master_action_selector_hexa.yo vertical")
    ccas_tier: Optional[str] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_action_selector_hexa.yo session_id")
    action_kind: str = Field(..., description="hexaforge_slm_training_master_action_selector_hexa.yo action_kind")

class HexaforgeSlmTrainingMasterActionSelectorHexaZiSchema(BaseModel):
    """hexaforge_slm_training_master_action_selector_hexa.zi — generated from contracts/hexaforge_slm_training_master_action_selector_hexa/zi.schema.json (v1.0.0)."""
    cohort_examples: Optional[list[Any]] = Field(None, description="cohort-aggregated few-shot or template data")

class HexaforgeSlmTrainingMasterActionSelectorHexaZoSchema(BaseModel):
    """hexaforge_slm_training_master_action_selector_hexa.zo — generated from contracts/hexaforge_slm_training_master_action_selector_hexa/zo.schema.json (v1.0.0)."""
    ts: str = Field(..., description="ISO 8601 timestamp")
    event: str = Field(..., description="hexaforge_slm_training_master_action_selector_hexa.zo event")
    vertical: str = Field(..., description="hexaforge_slm_training_master_action_selector_hexa.zo vertical")
    latency_ms: Optional[int] = None
    session_id: str = Field(..., description="hexaforge_slm_training_master_action_selector_hexa.zo session_id")
