"""API Gateway — ingress router, rate limiter, and request sanitizer."""

import time


class APIGateway:
    """Routes incoming HTTP requests to corresponding backend services."""

    def __init__(self, auth_service, rate_limiter):
        self.auth_service = auth_service
        self.rate_limiter = rate_limiter

    def route_request(self, path: str, method: str, headers: dict, body: dict) -> dict:
        """Route client request through authentication and rate limiting checks."""
        client_ip = headers.get("x-forwarded-for", "127.0.0.1")
        if not self.rate_limiter.apply_rate_limit(client_ip):
            return {"status": 429, "error": "Too Many Requests"}

        if path.startswith("/api/v1/protected/"):
            token = self.validate_auth(headers)
            if not token:
                return {"status": 401, "error": "Unauthorized"}

        return {"status": 200, "routed_to": path, "method": method}

    def validate_auth(self, headers: dict) -> str | None:
        """Extract and verify bearer token."""
        auth_header = headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            if self.auth_service.verify_token(token):
                return token
        return None


class RateLimiter:
    """Sliding-window rate limiter per client IP."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = {}

    def apply_rate_limit(self, client_ip: str) -> bool:
        """Return True if request is allowed, False if exceeded."""
        now = time.time()
        timestamps = self._requests.get(client_ip, [])
        timestamps = [t for t in timestamps if now - t < self.window_seconds]
        if len(timestamps) >= self.max_requests:
            return False
        timestamps.append(now)
        self._requests[client_ip] = timestamps
        return True

    def reset_window(self, client_ip: str) -> None:
        """Clear recorded requests for an IP."""
        if client_ip in self._requests:
            del self._requests[client_ip]
