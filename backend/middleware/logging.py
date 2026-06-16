"""
Request logging middleware with response timing.
Logs: [METHOD] path -> STATUS (X ms)
"""
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("onfido_api")

SKIP_LOG_PATHS = {"/api/health", "/favicon.ico"}

def _should_log(path: str) -> bool:
    if path in SKIP_LOG_PATHS:
        return False
    if path.startswith("/assets/"):
        return False
    return True

class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not _should_log(request.url.path):
            return await call_next(request)
        start = time.time()
        response = await call_next(request)
        duration = (time.time() - start) * 1000
        logger.info(
            f"{request.method} {request.url.path} -> {response.status_code} ({duration:.1f} ms)"
        )
        return response
