"""Dedicated tests for the SlidingWindowRateLimiter middleware.

Verifies:
1. Permitted requests succeed up to max_requests.
2. The (max_requests + 1)-th request within the window returns HTTP 429 Too Many Requests.
3. The response includes the standard Retry-After header.
4. Response body includes RFC-aligned error metadata.
5. Exempt endpoints (/api/v1/health, /docs) are not rate-limited.
6. The sliding window evicts expired timestamps as time advances.
"""

import time
from unittest.mock import patch
import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient
from starlette.responses import JSONResponse
from app.core.rate_limiter import SlidingWindowRateLimiter


def create_test_app(max_requests: int = 5, window_seconds: int = 10) -> FastAPI:
    test_app = FastAPI()
    test_app.add_middleware(
        SlidingWindowRateLimiter,
        max_requests=max_requests,
        window_seconds=window_seconds,
    )

    @test_app.get("/api/v1/test")
    def test_endpoint():
        return {"status": "ok"}

    @test_app.get("/api/v1/health")
    def health_endpoint():
        return {"status": "healthy"}

    return test_app


def test_rate_limiter_allows_under_limit():
    """Verify that requests within max_requests return HTTP 200."""
    app = create_test_app(max_requests=3, window_seconds=10)
    client = TestClient(app)

    for i in range(3):
        response = client.get("/api/v1/test")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


def test_rate_limiter_blocks_and_returns_429_with_retry_after():
    """Verify that exceeding limit triggers HTTP 429 with Retry-After header."""
    app = create_test_app(max_requests=3, window_seconds=15)
    client = TestClient(app)

    for _ in range(3):
        res = client.get("/api/v1/test")
        assert res.status_code == 200

    # 4th request must be throttled
    blocked_res = client.get("/api/v1/test")
    assert blocked_res.status_code == 429
    assert blocked_res.headers.get("Retry-After") == "15"

    body = blocked_res.json()
    assert body["status_code"] == 429
    assert "Rate limit exceeded" in body["detail"]
    assert body["max_requests_per_window"] == 3
    assert body["window_seconds"] == 15
    assert "client_ip" in body


def test_rate_limiter_exempt_paths():
    """Verify that exempt paths such as /api/v1/health bypass the rate limiter."""
    app = create_test_app(max_requests=2, window_seconds=10)
    client = TestClient(app)

    # Exhaust limit on /api/v1/test
    client.get("/api/v1/test")
    client.get("/api/v1/test")
    assert client.get("/api/v1/test").status_code == 429

    # /api/v1/health must still succeed
    health_res = client.get("/api/v1/health")
    assert health_res.status_code == 200
    assert health_res.json() == {"status": "healthy"}


def test_rate_limiter_sliding_window_expiration():
    """Verify that when time moves past window_seconds, old timestamps are evicted."""
    app = create_test_app(max_requests=2, window_seconds=5)
    client = TestClient(app)

    start_time = 1000.0
    with patch("time.time", return_value=start_time):
        assert client.get("/api/v1/test").status_code == 200
        assert client.get("/api/v1/test").status_code == 200
        assert client.get("/api/v1/test").status_code == 429

    # Advance time by 6 seconds (beyond the 5s window)
    with patch("time.time", return_value=start_time + 6.0):
        # Window should have slid, permitting new requests
        res = client.get("/api/v1/test")
        assert res.status_code == 200
