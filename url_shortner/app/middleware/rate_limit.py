from fastapi import Request
from fastapi.responses import JSONResponse
from redis.asyncio import Redis

from app.core.security import get_user_id_from_token
from app.services.rate_limiter import RedisTokenBucket

class RateLimitMiddleware:
    def __init__(self, app, redis: Redis):
        self.app = app
        self.limiter = RedisTokenBucket(redis)
        
    async def __call__(self, scope, receive, send,):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive=receive)
        
        if (
            request.method != "POST"
            or request.url.path != "/api/v1/urls"
        ):
            await self.app(scope, receive, send)
            return
        
        authorization = request.headers.get("Authorization")
        
        if not authorization:
            await self.app(scope, receive, send)
            return
        
        scheme, _, token = authorization.partition(" ")
        
        if scheme.lower() != "bearer" or not token:
            await self.app(scope, receive, send)
            return 

        user_id = get_user_id_from_token(token)
        
        if user_id is None:
            await self.app(scope, receive, send)
            return
        
        try:
            allowed = await self.limiter.consume(
                str(user_id)
            )
            
        except Exception:
            return await JSONResponse(
                status_code=503,
                content={
                    "detail": "Rate limiting service unavailable",
                },
            )(scope, receive, send)
        
        if not allowed:
            response = JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded.",
                },
                headers={
                    "Retry-after": "1",
                },
            )
            
            await response(scope, receive, send)
            return 
        
        await self.app(scope, receive, send)
        
        
        