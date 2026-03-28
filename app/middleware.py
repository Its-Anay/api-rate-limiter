from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from app.database import get_valkey


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, strategy, limit: int, window: int):
        super().__init__(app)
        self.strategy = strategy
        self.limit = limit
        self.window = window

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host
        key = f"rate_limit:{ip}"
        
        async with get_valkey() as redis:
            allowed = await self.strategy.should_allow(redis, key, self.limit, self.window)
        
        if allowed:
            return await call_next(request)
        else:
            return Response(content="Too Many Requests", status_code=429)