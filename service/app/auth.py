"""JWT authentication compatible with BlueCore gateway tokens."""

from __future__ import annotations

import hmac
import os
from dataclasses import dataclass

import jwt
from fastapi import Header, HTTPException

from app.settings import settings


@dataclass(frozen=True)
class ServicePrincipal:
    subject: str
    roles: tuple[str, ...]
    agency_id: str | None
    token_type: str
    email: str | None = None


AI_READ_ROLES = frozenset({
    "admin",
    "dispatcher",
    "supervisor",
    "officer",
    "calltaker",
    "analyst",
    "detective",
    "records",
    "investigator",
    "emergency_management",
})


def verify_service_token(provided: str) -> bool:
    expected = settings.service_auth_token
    if not provided or not expected:
        return False
    return hmac.compare_digest(provided.strip(), expected.strip())


def decode_user_jwt(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "exp"]},
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc


def require_user_jwt(authorization: str | None = Header(default=None)) -> ServicePrincipal:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    payload = decode_user_jwt(authorization[7:].strip())
    roles = tuple(payload.get("roles") or [])
    if roles and not AI_READ_ROLES.intersection(roles):
        raise HTTPException(status_code=403, detail="Insufficient role for AI assistant")
    return ServicePrincipal(
        subject=str(payload["sub"]),
        roles=roles,
        agency_id=payload.get("agency_id"),
        token_type="user",
        email=payload.get("email"),
    )


def require_service_or_user(
    authorization: str | None = Header(default=None),
    x_service_token: str | None = Header(default=None, alias="X-Service-Token"),
) -> ServicePrincipal:
    if x_service_token and verify_service_token(x_service_token):
        return ServicePrincipal(
            subject="service",
            roles=("service",),
            agency_id=None,
            token_type="service",
        )
    return require_user_jwt(authorization)
