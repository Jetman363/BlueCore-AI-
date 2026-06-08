from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.assistant.router import router as assistant_router
from app.audit.logger import list_audit
from app.auth import ServicePrincipal, require_user_jwt
from app.settings import settings
from app.threat.router import router as threat_router


def _validate_secrets() -> None:
    if settings.jwt_secret == "change-me":
        import os

        if os.getenv("ENV", "development") == "production":
            raise RuntimeError("JWT_SECRET must be set in production")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    _validate_secrets()
    yield


app = FastAPI(
    title="BlueCore AI Add-On",
    version="1.0.0",
    description=(
        "Optional BlueCore add-on: Law Enforcement Assistant and Threat Assessment modules. "
        "Enable per-agency in BlueCore System Architect Portal."
    ),
    lifespan=lifespan,
)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(assistant_router)
app.include_router(threat_router)


@app.get("/healthz")
async def healthz() -> dict:
    return {
        "status": "ok",
        "service": "bluecore-ai-addon",
        "version": "1.0.0",
        "llm_provider": settings.llm_provider,
        "modules": ["law-enforcement-assistant", "threat-assessment"],
    }


@app.get("/v1/audit")
async def audit_log(
    agency_id: str | None = None,
    limit: int = 100,
    principal: ServicePrincipal = Depends(require_user_jwt),
) -> dict:
    if agency_id and principal.agency_id and principal.agency_id != agency_id:
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Agency mismatch")
    effective_agency = agency_id or principal.agency_id
    return {"entries": list_audit(agency_id=effective_agency, limit=min(limit, 500))}
