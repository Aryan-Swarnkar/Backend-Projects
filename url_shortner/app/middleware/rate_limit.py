from fastapi import Request
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.security import get_user_id_from_token
from app.services.rate_limiter import RedisTokenBucket

import math

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        redis: Redis,
    ):
        super().__init__(app)

        self.limiter = RedisTokenBucket(redis)

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        if (
            request.method != "POST"
            or request.url.path != "/api/v1/urls"
        ):
            return await call_next(request)

        authorization = request.headers.get(
            "Authorization"
        )

        if not authorization:
            return await call_next(request)

        scheme, _, token = authorization.partition(" ")

        if (
            scheme.lower() != "bearer"
            or not token
        ):
            return await call_next(request)

        user_id = get_user_id_from_token(token)

        if user_id is None:
            return await call_next(request)

        try:
            result = await self.limiter.consume(
                str(user_id)
            )

        except Exception:
            return JSONResponse(
                status_code=503,
                content={
                    "detail": (
                        "Rate limiting service unavailable"
                    ),
                },
            )

        if not result.allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                },
                headers={
                    "Retry-After": str(
                        result.retry_after
                    ),
                    "X-RateLimit-Limit": str(
                        int(self.limiter.capacity)
                    ),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)

        response.headers["X-RateLimit-Limit"] = str(
            int(self.limiter.capacity)
        )

        response.headers["X-RateLimit-Remaining"] = str(
            max(
                0,
                math.floor(result.remaining_tokens),
            )
        )

        return response