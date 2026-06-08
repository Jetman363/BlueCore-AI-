from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    INFORMATIONAL = "informational"
    OFFICER_SAFETY_ADVISORY = "officer_safety_advisory"
    ELEVATED_RISK = "elevated_risk"
    CRITICAL = "critical_officer_safety_alert"


class ThreatIndicatorCategory(str, Enum):
    PERSON = "person"
    LOCATION = "location"
    VEHICLE = "vehicle"
    INCIDENT = "incident"


class PolicyIndicator(BaseModel):
    id: str
    label: str
    category: ThreatIndicatorCategory
    weight: float = Field(ge=0.0, le=10.0)
    mandatory_supervisor_notify: bool = False


class ThreatPolicyProfile(BaseModel):
    policy_id: str
    agency_id: str
    name: str
    version: int = 1
    indicators: list[PolicyIndicator]
    advisory_threshold: float = 3.0
    elevated_threshold: float = 6.0
    critical_threshold: float = 9.0
    officer_warning_template: str = "Officer Safety Advisory: {factors}"


class SupportingRecord(BaseModel):
    record_type: str
    record_id: str
    summary: str
    occurred_at: str | None = None


class ContributingFactor(BaseModel):
    indicator_id: str
    label: str
    category: ThreatIndicatorCategory
    weight: float
    supporting_records: list[SupportingRecord] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.9)


class ThreatAssessmentRequest(BaseModel):
    agency_id: str
    policy_id: str | None = None
    person_records: list[dict[str, Any]] = Field(default_factory=list)
    location_records: list[dict[str, Any]] = Field(default_factory=list)
    vehicle_records: list[dict[str, Any]] = Field(default_factory=list)
    incident_context: dict[str, Any] = Field(default_factory=dict)
    subject_id: str | None = None
    location_id: str | None = None
    vehicle_id: str | None = None
    incident_id: str | None = None


class ThreatAssessmentResponse(BaseModel):
    assessment_id: str
    risk_level: RiskLevel
    total_score: float
    contributing_factors: list[ContributingFactor]
    officer_notification: str | None = None
    policy_reference: str
    confidence: float = Field(ge=0.0, le=1.0)
    requires_supervisor_notification: bool = False
    disclaimer: str = (
        "Informational decision-support only. Final tactical decisions remain the "
        "responsibility of sworn personnel, supervisors, dispatchers, and incident commanders."
    )
