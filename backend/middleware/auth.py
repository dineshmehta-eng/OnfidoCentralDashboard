"""
Optional API key middleware. Enable by setting API_KEY in .env.
If API_KEY is empty, no auth is enforced. The dashboard remains fully open.
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# Delay import to avoid config-loading race during early imports
_api_key = None

def _get_api_key():
    global _api_key
    if _api_key is None:
        from config import settings
        _api_key = settings.API_KEY
    return _api_key


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        key = _get_api_key()
        # Skip auth if not configured
        if not key:
            return await call_next(request)

        # Allow health and static assets without key
        path = request.url.path
        if path in ("/api/health", "/") or path.startswith("/assets/"):
            return await call_next(request)

        # Require header
        header_key = request.headers.get("X-API-Key", "")
        if header_key != key:
            return JSONResponse(
                status_code=401,
                content={"success": False, "error": "Invalid or missing API key"}
            )

        return await call_next(request)
