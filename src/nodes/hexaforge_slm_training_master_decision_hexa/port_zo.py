"""hexaforge_slm_training_master_decision_hexa.port_zo — telemetry out"""
from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterDecisionHexaZoSchema
from src.shared.hexa_record import log_event
from src.shared.ceve_runtime import validate_contract
from .handler import handle_zo

router = APIRouter(prefix="/hexaforge_slm_training_master_decision_hexa/port-zo")


@router.post("")
async def receive_zo(payload: dict):
    try:
        validated = HexaforgeSlmTrainingMasterDecisionHexaZoSchema(**payload)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

    validate_contract(node_id="hexaforge_slm_training_master_decision_hexa", port="zo", payload=validated.model_dump())
    log_event(node_id="hexaforge_slm_training_master_decision_hexa", port="zo", payload=validated.model_dump())
    # DD P0 (Peter): pass a DICT to the handler, never the Pydantic model — a
    # handler does dict-style field access, and a model made every field read as
    # missing at the delivered HTTP boundary. Merge the raw payload under the
    # validated fields so signed extras (evidence/evidence_digest/sig) survive.
    return await handle_zo({**payload, **validated.model_dump(mode="json", exclude_none=True)})
