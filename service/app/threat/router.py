from fastapi import APIRouter, Depends, HTTPException

from app.audit.logger import log_audit
from app.auth import ServicePrincipal, require_user_jwt
from app.prompts import threat_assessment_system_prompt
from app.threat.engine import assess_threat
from app.threat.policy import get_policy, list_policies, upsert_policy
from app.threat.schemas import ThreatAssessmentRequest, ThreatAssessmentResponse, ThreatPolicyProfile

router = APIRouter(prefix="/v1/threat", tags=["threat-assessment"])


def _assert_agency(principal: ServicePrincipal, agency_id: str) -> None:
    if principal.agency_id and principal.agency_id != agency_id:
        raise HTTPException(status_code=403, detail="Agency mismatch")


@router.get("/prompt")
async def get_threat_prompt(_principal: ServicePrincipal = Depends(require_user_jwt)) -> dict:
    return {"prompt_id": "threat-assessment-module", "content": threat_assessment_system_prompt()}


@router.get("/policies", response_model=list[ThreatPolicyProfile])
async def get_policies(
    agency_id: str,
    principal: ServicePrincipal = Depends(require_user_jwt),
) -> list[ThreatPolicyProfile]:
    _assert_agency(principal, agency_id)
    return list_policies(agency_id)


@router.put("/policies/{policy_id}", response_model=ThreatPolicyProfile)
async def put_policy(
    policy_id: str,
    profile: ThreatPolicyProfile,
    principal: ServicePrincipal = Depends(require_user_jwt),
) -> ThreatPolicyProfile:
    _assert_agency(principal, profile.agency_id)
    if profile.policy_id != policy_id:
        raise HTTPException(status_code=400, detail="Policy ID mismatch")
    saved = upsert_policy(profile)
    log_audit(
        user_id=principal.subject,
        agency_id=profile.agency_id,
        action="threat.policy.update",
        resource_type="threat_policy",
        resource_id=policy_id,
    )
    return saved


@router.post("/assess", response_model=ThreatAssessmentResponse)
async def assess(
    payload: ThreatAssessmentRequest,
    principal: ServicePrincipal = Depends(require_user_jwt),
) -> ThreatAssessmentResponse:
    _assert_agency(principal, payload.agency_id)
    result = assess_threat(payload)
    log_audit(
        user_id=principal.subject,
        agency_id=payload.agency_id,
        action="threat.assess",
        resource_type="threat_assessment",
        resource_id=result.assessment_id,
        details={
            "risk_level": result.risk_level.value,
            "incident_id": payload.incident_id,
            "score": result.total_score,
        },
    )
    return result
