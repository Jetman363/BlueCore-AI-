# BlueCore AI API Reference

Base URL: `http://localhost:8095` (standalone) or via BlueCore gateway `/v1/ai/*` when add-on is enabled.

Authentication: `Authorization: Bearer <BlueCore JWT>`

## Health

`GET /healthz`

## Law Enforcement Assistant

### Chat

`POST /v1/assistant/chat`

```json
{
  "agency_id": "agency-demo-001",
  "command": "cad_call",
  "prompt": "Create a CAD call for suspicious person at 100 Main St",
  "context": { "location": "100 Main St" },
  "incident_id": null
}
```

Commands: `cad_call`, `bolo`, `arrest_report`, `active_calls_summary`, `shift_briefing`, `case_summary`, `report_field_review`, `radio_traffic_summary`, `command_overview`, `general`

### Narrative Draft

`POST /v1/assistant/narrative`

```json
{
  "agency_id": "agency-demo-001",
  "report_type": "arrest",
  "notes": "Subject detained after traffic stop...",
  "involved_parties": ["John Doe"],
  "incident_id": "24-004125"
}
```

## Threat Assessment

### Assess

`POST /v1/threat/assess`

```json
{
  "agency_id": "agency-demo-001",
  "policy_id": "default-officer-safety",
  "person_records": [
    {
      "id": "p1",
      "indicators": ["assault_on_officer"],
      "summary": "Assault on officer 2024-05-18",
      "occurred_at": "2024-05-18T14:00:00Z"
    }
  ],
  "location_records": [],
  "vehicle_records": [],
  "incident_context": { "weapons_involved": true },
  "incident_id": "24-004125"
}
```

Risk levels: `informational`, `officer_safety_advisory`, `elevated_risk`, `critical_officer_safety_alert`

### Policy Management

- `GET /v1/threat/policies?agency_id=...`
- `PUT /v1/threat/policies/{policy_id}`

## Audit

`GET /v1/audit?agency_id=...&limit=100`

Supervisor/admin review of assistant and threat assessment activity.
