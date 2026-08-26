"""hexaforge_slm_training_master_rollback_binding_approval_gate_hexa.port_yo — side effects out (privileged actions, gated by CCAS)"""
from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from src.shared.contracts import HexaforgeSlmTrainingMasterRollbackBindingApprovalGateHexaYoSchema
from src.shared.hexa_record import log_event
from src.shared.ceve_runtime import validate_contract
from src.shared.ccas_gate import ccas_decide
from .handler import handle_yo

router = APIRouter(prefix="/hexaforge_slm_training_master_rollback_binding_approval_gate_hexa/port-yo")


@router.post("")
async def receive_yo(payload: dict):
    try:
        validated = HexaforgeSlmTrainingMasterRollbackBindingApprovalGateHexaYoSchema(**payload)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

    validate_contract(node_id="hexaforge_slm_training_master_rollback_binding_approval_gate_hexa", port="yo", payload=validated.model_dump())
    decision = ccas_decide(action=validated.model_dump(), tier="human")
    log_event(node_id="hexaforge_slm_training_master_rollback_binding_approval_gate_hexa", port="yo", payload=validated.model_dump(), ccas_decision=decision)
    if decision["status"] != "approved":
        return {"status": "pending", "decision": decision}
    # DD P0 (Peter): pass a DICT to the handler, never the Pydantic model — a
    # handler does dict-style field access, and a model made every field read as
    # missing at the delivered HTTP boundary. Merge the raw payload under the
    # validated fields so signed extras (evidence/evidence_digest/sig) survive.
    return await handle_yo({**payload, **validated.model_dump(mode="json", exclude_none=True)})
