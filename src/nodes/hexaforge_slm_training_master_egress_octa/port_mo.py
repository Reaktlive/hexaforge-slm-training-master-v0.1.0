"""hexaforge_slm_training_master_egress_octa.port_mo — macro / cohort signals out (governed by anonymization_contract)"""
from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterEgressOctaMoSchema
from src.shared.hexa_record import log_event
from src.shared.ceve_runtime import validate_contract
from src.shared.anonymization import enforce_contract
from .handler import handle_mo

router = APIRouter(prefix="/hexaforge_slm_training_master_egress_octa/port-mo")


@router.post("")
async def receive_mo(payload: dict):
    try:
        validated = HexaforgeSlmTrainingMasterEgressOctaMoSchema(**payload)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

    validate_contract(node_id="hexaforge_slm_training_master_egress_octa", port="mo", payload=validated.model_dump())
    enforce_contract(payload=validated.model_dump())
    log_event(node_id="hexaforge_slm_training_master_egress_octa", port="mo", payload=validated.model_dump())
    # DD P0 (Peter): pass a DICT to the handler, never the Pydantic model — a
    # handler does dict-style field access, and a model made every field read as
    # missing at the delivered HTTP boundary. Merge the raw payload under the
    # validated fields so signed extras (evidence/evidence_digest/sig) survive.
    return await handle_mo({**payload, **validated.model_dump(mode="json", exclude_none=True)})
