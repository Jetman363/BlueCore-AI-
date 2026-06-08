"""Explainable threat assessment engine — policy-driven, no protected-class inputs."""

from __future__ import annotations

from uuid import uuid4

from app.settings import settings
from app.threat.policy import get_policy
from app.threat.schemas import (
    ContributingFactor,
    RiskLevel,
    SupportingRecord,
    ThreatAssessmentRequest,
    ThreatAssessmentResponse,
    ThreatIndicatorCategory,
)

PROTECTED_FIELDS = frozenset({
    "race",
    "ethnicity",
    "religion",
    "national_origin",
    "gender",
    "sexual_orientation",
    "political_affiliation",
})


def _strip_protected(data: dict) -> dict:
    return {k: v for k, v in data.items() if k.lower() not in PROTECTED_FIELDS}


def _match_indicator(indicator_id: str, records: list[dict], category: ThreatIndicatorCategory) -> list[SupportingRecord]:
    matches: list[SupportingRecord] = []
    for rec in records:
        clean = _strip_protected(rec)
        flags = clean.get("indicators") or clean.get("flags") or []
        if indicator_id in flags or clean.get("indicator_id") == indicator_id:
            matches.append(
                SupportingRecord(
                    record_type=clean.get("record_type", category.value),
                    record_id=str(clean.get("id", "unknown")),
                    summary=str(clean.get("summary", indicator_id)),
                    occurred_at=clean.get("occurred_at"),
                )
            )
    return matches


def _incident_flags(context: dict) -> list[str]:
    flags: list[str] = []
    if context.get("weapons_involved") or context.get("weapons_reported"):
        flags.append("weapons_on_incident")
    if int(context.get("involved_persons_count") or 0) > 2:
        flags.append("multiple_involved_persons")
    return flags


def assess_threat(payload: ThreatAssessmentRequest) -> ThreatAssessmentResponse:
    policy_id = payload.policy_id or settings.default_threat_policy_id
    policy = get_policy(policy_id, payload.agency_id)

    factors: list[ContributingFactor] = []
    incident_flags = _incident_flags(_strip_protected(payload.incident_context))

    for indicator in policy.indicators:
        records: list[dict] = []
        if indicator.category == ThreatIndicatorCategory.PERSON:
            records = payload.person_records
        elif indicator.category == ThreatIndicatorCategory.LOCATION:
            records = payload.location_records
        elif indicator.category == ThreatIndicatorCategory.VEHICLE:
            records = payload.vehicle_records
        elif indicator.category == ThreatIndicatorCategory.INCIDENT:
            if indicator.id in incident_flags:
                records = [{"id": payload.incident_id or "current", "indicators": [indicator.id], "summary": indicator.label}]

        supporting = _match_indicator(indicator.id, [_strip_protected(r) for r in records], indicator.category)
        if indicator.category == ThreatIndicatorCategory.INCIDENT and indicator.id in incident_flags and not supporting:
            supporting = [
                SupportingRecord(
                    record_type="incident",
                    record_id=payload.incident_id or "current",
                    summary=indicator.label,
                )
            ]

        if supporting:
            factors.append(
                ContributingFactor(
                    indicator_id=indicator.id,
                    label=indicator.label,
                    category=indicator.category,
                    weight=indicator.weight,
                    supporting_records=supporting,
                    confidence=0.92,
                )
            )

    total_score = sum(f.weight for f in factors)

    if total_score >= policy.critical_threshold:
        risk = RiskLevel.CRITICAL
    elif total_score >= policy.elevated_threshold:
        risk = RiskLevel.ELEVATED_RISK
    elif total_score >= policy.advisory_threshold:
        risk = RiskLevel.OFFICER_SAFETY_ADVISORY
    else:
        risk = RiskLevel.INFORMATIONAL

    factor_labels = "; ".join(f.label for f in factors) or "No verified risk indicators identified"
    notification: str | None = None
    if risk != RiskLevel.INFORMATIONAL:
        prefix = {
            RiskLevel.OFFICER_SAFETY_ADVISORY: "Officer Safety Advisory",
            RiskLevel.ELEVATED_RISK: "Elevated Risk Alert",
            RiskLevel.CRITICAL: "Critical Officer Safety Alert",
        }[risk]
        notification = f"{prefix}: {factor_labels}."

    requires_supervisor = any(
        ind.mandatory_supervisor_notify
        for ind in policy.indicators
        if any(f.indicator_id == ind.id for f in factors)
    ) or risk == RiskLevel.CRITICAL

    return ThreatAssessmentResponse(
        assessment_id=str(uuid4()),
        risk_level=risk,
        total_score=round(total_score, 2),
        contributing_factors=factors,
        officer_notification=notification,
        policy_reference=f"{policy.name} v{policy.version}",
        confidence=0.88 if factors else 0.95,
        requires_supervisor_notification=requires_supervisor,
    )
