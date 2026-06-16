"""
Adds Cache-Control headers for static files so browsers cache JS, CSS, and HTML.
Helps reduce server load when serving ~200 concurrent users.
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class CacheControlMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        path = request.url.path

        # Keep the local FastAPI bridge fresh; stale bridge code can break page startup.
        if path == "/fastapi_bridge.js":
            response.headers["Cache-Control"] = "no-store"
        # Cache static assets (JS, CSS, images) aggressively
        elif path.startswith("/assets/"):
            response.headers["Cache-Control"] = "public, max-age=3600"
        # Do not cache HTML; deployments and bridge fixes must be visible immediately.
        elif path == "/" or path.endswith(".html"):
            response.headers["Cache-Control"] = "no-store"
        # API responses should NOT be cached by the browser (our app-level TTLCache handles server-side)
        elif path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"

        return response
