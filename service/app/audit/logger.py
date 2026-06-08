"""In-memory audit log for development; replace with persistent store in production."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class AuditEntry:
    id: str
    timestamp: str
    user_id: str
    agency_id: str | None
    action: str
    resource_type: str
    resource_id: str | None
    details: dict[str, Any] = field(default_factory=dict)


_AUDIT_LOG: list[AuditEntry] = []


def log_audit(
    *,
    user_id: str,
    agency_id: str | None,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> AuditEntry:
    entry = AuditEntry(
        id=str(uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        user_id=user_id,
        agency_id=agency_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {},
    )
    _AUDIT_LOG.append(entry)
    return entry


def list_audit(*, agency_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
    entries = _AUDIT_LOG
    if agency_id:
        entries = [e for e in entries if e.agency_id == agency_id]
    return [asdict(e) for e in entries[-limit:]]
