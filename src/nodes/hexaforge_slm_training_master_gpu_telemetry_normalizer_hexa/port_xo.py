"""hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa.port_xo — primary output"""
from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterGpuTelemetryNormalizerHexaXoSchema
from src.shared.hexa_record import log_event
from src.shared.ceve_runtime import validate_contract
from .handler import handle_xo

router = APIRouter(prefix="/hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa/port-xo")


@router.post("")
async def receive_xo(payload: dict):
    try:
        validated = HexaforgeSlmTrainingMasterGpuTelemetryNormalizerHexaXoSchema(**payload)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

    validate_contract(node_id="hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa", port="xo", payload=validated.model_dump())
    log_event(node_id="hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa", port="xo", payload=validated.model_dump())
    # DD P0 (Peter): pass a DICT to the handler, never the Pydantic model — a
    # handler does dict-style field access, and a model made every field read as
    # missing at the delivered HTTP boundary. Merge the raw payload under the
    # validated fields so signed extras (evidence/evidence_digest/sig) survive.
    return await handle_xo({**payload, **validated.model_dump(mode="json", exclude_none=True)})
