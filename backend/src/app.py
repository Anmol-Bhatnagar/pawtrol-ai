import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.api.middlewares.tracing import RequestTracingMiddleware
from src.api.routers import dogs, health, v1_chat
from src.config.logging_cfg import setup_logging
from src.config.settings import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    App lifecycle manager. Handles server boot and cleanup.
    """
    setup_logging(settings.ENVIRONMENT)
    logger.info(f"Booting project: {settings.PROJECT_NAME}")
    logger.info(f"Target Environment: {settings.ENVIRONMENT}")

    # Load and warmup the dog breed classifier session
    from src.services.dog_classifier import dog_classifier

    try:
        dog_classifier.load_model()
    except Exception as e:
        logger.error(
            f"Failed to load dog breed classification model on startup: {e}"
        )

    yield
    logger.info("Shutting down agent services backend...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise API microservice orchestrating LangGraph cognitive agents.",
    version="0.1.0",
    lifespan=lifespan,
)

# Setup CORS Origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Correlation middleware (X-Request-ID)
app.add_middleware(RequestTracingMiddleware)

# API Routers integration
app.include_router(health.router, prefix=settings.API_V1_STR)
app.include_router(v1_chat.router, prefix=settings.API_V1_STR)
app.include_router(dogs.router, prefix=settings.API_V1_STR)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all crash handler ensuring errors are cleanly serialized and logged.
    """
    logger.error(
        f"Unhandled application exception on {request.url.path}: {exc}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred while processing your request."
        },
    )
