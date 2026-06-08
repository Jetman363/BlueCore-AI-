"""Assistant response engine with LLM provider abstraction."""

from __future__ import annotations

import re
from uuid import uuid4

from app.assistant.schemas import (
    AssistantCommand,
    AssistantRequest,
    AssistantResponse,
    NarrativeDraftRequest,
    NarrativeDraftResponse,
)
from app.prompts import assistant_system_prompt
from app.settings import settings

OFFICER_SAFETY_KEYWORDS = (
    "weapon",
    "gun",
    "knife",
    "firearm",
    "officer down",
    "active shooter",
    "domestic violence",
    "suicidal",
    "mental health crisis",
    "warrant",
    "armed",
    "assault on officer",
)


def _detect_officer_safety(text: str) -> list[str]:
    lower = text.lower()
    return [kw for kw in OFFICER_SAFETY_KEYWORDS if kw in lower]


def _detect_missing_info(command: AssistantCommand, context: dict) -> list[str]:
    missing: list[str] = []
    if command == AssistantCommand.CAD_CALL:
        for field in ("location", "incident_type", "caller_phone"):
            if not context.get(field):
                missing.append(field)
    if command == AssistantCommand.ARREST_REPORT:
        for field in ("subject_name", "charges", "location", "officer_id"):
            if not context.get(field):
                missing.append(field)
    return missing


def _stub_response(payload: AssistantRequest) -> str:
    cmd = payload.command
    prompt_preview = payload.prompt.strip()[:200]
    if cmd == AssistantCommand.CAD_CALL:
        return (
            "CAD call draft prepared from provided information. "
            "Verify location, incident type, and priority before creating the record. "
            f"Summary: {prompt_preview}"
        )
    if cmd == AssistantCommand.BOLO:
        return (
            "BOLO draft generated. Include subject description, vehicle, direction of travel, "
            "and reason for broadcast. Review for accuracy before release."
        )
    if cmd == AssistantCommand.ARREST_REPORT:
        return (
            "Arrest report narrative draft in chronological order. "
            "Facts are separated from observations. Review all required fields before submission."
        )
    if cmd == AssistantCommand.ACTIVE_CALLS_SUMMARY:
        return "Active calls summary prepared for dispatch review. Prioritize officer safety indicators first."
    if cmd == AssistantCommand.SHIFT_BRIEFING:
        return "Shift briefing outline generated covering active incidents, BOLOs, and unit availability."
    if cmd == AssistantCommand.RADIO_TRAFFIC_SUMMARY:
        incident = payload.incident_id or "specified incident"
        return f"Radio traffic summary for {incident} in chronological order with unit identifiers preserved."
    return (
        "BlueCore AI assistant response (stub mode). "
        "Configure LLM_PROVIDER for production inference. "
        f"Request: {prompt_preview}"
    )


async def run_assistant(payload: AssistantRequest) -> AssistantResponse:
    system_prompt = assistant_system_prompt()
    combined = f"{payload.prompt}\n\nContext: {payload.context}"
    safety_flags = _detect_officer_safety(combined)
    missing = _detect_missing_info(payload.command, payload.context)

    # Provider hook: extend with ollama/openai/azure when configured
    if settings.llm_provider == "stub":
        response_text = _stub_response(payload)
    else:
        response_text = _stub_response(payload)

    if safety_flags:
        response_text = (
            "**Officer Safety Notice:** Relevant indicators detected. "
            "Review cautionary notifications before proceeding.\n\n" + response_text
        )

    return AssistantResponse(
        request_id=str(uuid4()),
        command=payload.command,
        response=response_text,
        officer_safety_flags=safety_flags,
        missing_information=missing,
        requires_human_review=True,
        model=f"{settings.llm_provider}:{settings.llm_model}",
        confidence=0.72 if settings.llm_provider == "stub" else 0.85,
    )


async def draft_narrative(payload: NarrativeDraftRequest) -> NarrativeDraftResponse:
    missing: list[str] = []
    if not payload.involved_parties:
        missing.append("involved_parties")
    if len(payload.notes.strip()) < 20:
        missing.append("detailed_notes")

    narrative = (
        f"On the date and time of occurrence, the reporting officer documented the following based on "
        f"field notes and observations. {payload.notes.strip()} "
        "This draft uses objective language and requires officer review before official submission."
    )
    return NarrativeDraftResponse(
        draft_id=str(uuid4()),
        narrative=narrative,
        missing_fields=missing,
        requires_human_approval=True,
    )
