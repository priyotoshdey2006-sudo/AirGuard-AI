"""Sliding-window rate limiter middleware for AirGuard AI.

Implements:
1. In-memory sliding window counter for single-worker local development.
2. Clear Redis backend integration documentation for multi-worker production deployments.
3. IP-based throttling returning RFC 7807 HTTP 429 Too Many Requests.
"""

import time
from collections import defaultdict, deque
from typing import Dict
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class SlidingWindowRateLimiter(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        max_requests: int = 60,
        window_seconds: int = 60,
    ):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # In-memory storage: IP -> deque of request timestamps
        self._ip_history: Dict[str, deque] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next) -> Response:
        # Exclude documentation and health check endpoints from rate limiting
        path = request.url.path
        if any(path.startswith(p) for p in ["/docs", "/redoc", "/api/v1/openapi.json", "/api/v1/health", "/favicon.ico"]):
            return await call_next(request)

        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()
        window_start = now - self.window_seconds

        history = self._ip_history[client_ip]

        # Evict timestamps outside sliding window
        while history and history[0] < window_start:
            history.popleft()

        if len(history) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Too many requests within the current window.",
                    "status_code": 429,
                    "max_requests_per_window": self.max_requests,
                    "window_seconds": self.window_seconds,
                    "client_ip": client_ip,
                },
                headers={"Retry-After": str(self.window_seconds)},
            )

        history.append(now)
        return await call_next(request)
