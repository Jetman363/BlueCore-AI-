from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AssistantCommand(str, Enum):
    CAD_CALL = "cad_call"
    BOLO = "bolo"
    ARREST_REPORT = "arrest_report"
    ACTIVE_CALLS_SUMMARY = "active_calls_summary"
    SHIFT_BRIEFING = "shift_briefing"
    CASE_SUMMARY = "case_summary"
    REPORT_FIELD_REVIEW = "report_field_review"
    RADIO_TRAFFIC_SUMMARY = "radio_traffic_summary"
    COMMAND_OVERVIEW = "command_overview"
    GENERAL = "general"


class AssistantRequest(BaseModel):
    agency_id: str
    command: AssistantCommand = AssistantCommand.GENERAL
    prompt: str = Field(..., min_length=1, max_length=16000)
    context: dict[str, Any] = Field(default_factory=dict)
    incident_id: str | None = None
    report_id: str | None = None


class AssistantResponse(BaseModel):
    request_id: str
    command: AssistantCommand
    response: str
    officer_safety_flags: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    requires_human_review: bool = True
    model: str
    confidence: float = Field(ge=0.0, le=1.0)


class NarrativeDraftRequest(BaseModel):
    agency_id: str
    report_type: str
    notes: str = Field(..., min_length=1)
    involved_parties: list[str] = Field(default_factory=list)
    incident_id: str | None = None


class NarrativeDraftResponse(BaseModel):
    draft_id: str
    narrative: str
    missing_fields: list[str] = Field(default_factory=list)
    requires_human_approval: bool = True
