from fastapi import Header, HTTPException, status
from src.config.settings import settings


async def verify_api_key(
    x_api_key: str | None = Header(None, alias="X-API-Key", description="API Access Token")
) -> str:
    """
    Dependency to verify incoming requests contain a valid X-API-Key header.
    """
    if not x_api_key or x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )
    return x_api_key
