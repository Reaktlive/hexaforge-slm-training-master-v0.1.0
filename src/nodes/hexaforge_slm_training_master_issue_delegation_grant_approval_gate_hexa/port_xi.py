"""hexaforge_slm_training_master_issue_delegation_grant_approval_gate_hexa.port_xi — primary input"""
from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterIssueDelegationGrantApprovalGateHexaXiSchema
from src.shared.hexa_record import log_event
from src.shared.ceve_runtime import validate_contract
from .handler import handle_xi

router = APIRouter(prefix="/hexaforge_slm_training_master_issue_delegation_grant_approval_gate_hexa/port-xi")


@router.post("")
async def receive_xi(payload: dict):
    try:
        validated = HexaforgeSlmTrainingMasterIssueDelegationGrantApprovalGateHexaXiSchema(**payload)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

    validate_contract(node_id="hexaforge_slm_training_master_issue_delegation_grant_approval_gate_hexa", port="xi", payload=validated.model_dump())
    log_event(node_id="hexaforge_slm_training_master_issue_delegation_grant_approval_gate_hexa", port="xi", payload=validated.model_dump())
    # DD P0 (Peter): pass a DICT to the handler, never the Pydantic model — a
    # handler does dict-style field access, and a model made every field read as
    # missing at the delivered HTTP boundary. Merge the raw payload under the
    # validated fields so signed extras (evidence/evidence_digest/sig) survive.
    return await handle_xi({**payload, **validated.model_dump(mode="json", exclude_none=True)})
