from fastapi import APIRouter, Depends, HTTPException

from app.assistant.engine import draft_narrative, run_assistant
from app.assistant.schemas import (
    AssistantRequest,
    AssistantResponse,
    NarrativeDraftRequest,
    NarrativeDraftResponse,
)
from app.audit.logger import log_audit
from app.auth import ServicePrincipal, require_user_jwt
from app.prompts import assistant_system_prompt

router = APIRouter(prefix="/v1/assistant", tags=["assistant"])


def _assert_agency(principal: ServicePrincipal, agency_id: str) -> None:
    if principal.agency_id and principal.agency_id != agency_id:
        raise HTTPException(status_code=403, detail="Agency mismatch")


@router.get("/prompt")
async def get_system_prompt(_principal: ServicePrincipal = Depends(require_user_jwt)) -> dict:
    return {"prompt_id": "law-enforcement-assistant", "content": assistant_system_prompt()}


@router.post("/chat", response_model=AssistantResponse)
async def assistant_chat(
    payload: AssistantRequest,
    principal: ServicePrincipal = Depends(require_user_jwt),
) -> AssistantResponse:
    _assert_agency(principal, payload.agency_id)
    result = await run_assistant(payload)
    log_audit(
        user_id=principal.subject,
        agency_id=payload.agency_id,
        action="assistant.chat",
        resource_type="assistant_request",
        resource_id=result.request_id,
        details={"command": payload.command.value, "incident_id": payload.incident_id},
    )
    return result


@router.post("/narrative", response_model=NarrativeDraftResponse)
async def narrative_draft(
    payload: NarrativeDraftRequest,
    principal: ServicePrincipal = Depends(require_user_jwt),
) -> NarrativeDraftResponse:
    _assert_agency(principal, payload.agency_id)
    result = await draft_narrative(payload)
    log_audit(
        user_id=principal.subject,
        agency_id=payload.agency_id,
        action="assistant.narrative_draft",
        resource_type="narrative_draft",
        resource_id=result.draft_id,
        details={"report_type": payload.report_type, "incident_id": payload.incident_id},
    )
    return result
