import uuid
from contextvars import ContextVar
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

# Thread-safe ContextVar to store Request ID for log formatters
request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="")


def get_request_id() -> str:
    """
    Retrieves the current request ID from the context.
    """
    return request_id_ctx_var.get()


class RequestTracingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that generates/extracts an X-Request-ID correlation key
    for request tracking and assigns it to responses and logging contexts.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Set ContextVar value
        token = request_id_ctx_var.set(request_id)
        request.state.request_id = request_id

        try:
            response = await call_next(request)
        finally:
            # Always reset ContextVar to avoid context leaking across requests
            request_id_ctx_var.reset(token)

        # Set Response Header
        response.headers["X-Request-ID"] = request_id
        return response
