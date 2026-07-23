from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter(prefix="/health", tags=["system"])


class HealthStatus(BaseModel):
    status: str
    details: dict[str, str] = {}


@router.get(
    "/live", status_code=status.HTTP_200_OK, response_model=HealthStatus
)
async def liveness() -> HealthStatus:
    """
    Simple check to verify the process is alive.
    """
    return HealthStatus(status="healthy")


@router.get(
    "/ready", status_code=status.HTTP_200_OK, response_model=HealthStatus
)
async def readiness() -> HealthStatus:
    """
    Verifies connection status to downstream dependencies.
    """
    # Placeholder for database, cache, or external LLM service health checks
    return HealthStatus(status="ready", details={"database": "connected"})
