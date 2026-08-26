"""hexaforge_slm_training_master_intake_octa.port_xi — ingress for transport=https (profile request-response-v1)"""
import os
from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterIntakeOctaXiSchema
from src.shared.hexa_record import log_event
from src.shared.ceve_runtime import validate_contract
from .handler import handle_xi

router = APIRouter(prefix="/hexaforge_slm_training_master_intake_octa/port-xi")

# --- Transport config (loaded from env at startup) ---
endpoint = os.environ.get("ENDPOINT")
auth_header = os.environ.get("AUTH_HEADER")
timeout_seconds = os.environ.get("TIMEOUT_SECONDS")




@router.post("")
async def receive_xi(payload: dict):
    try:
        validated = HexaforgeSlmTrainingMasterIntakeOctaXiSchema(**payload)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    validate_contract(node_id="hexaforge_slm_training_master_intake_octa", port="xi", payload=validated.model_dump())
    log_event(node_id="hexaforge_slm_training_master_intake_octa", port="xi", payload=validated.model_dump())
    return await handle_xi(validated)
