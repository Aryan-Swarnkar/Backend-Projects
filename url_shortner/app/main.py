from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.db.database import get_db
from app.db.redis import get_redis

from app.db.redis import redis_client
from app.middleware.rate_limit import RateLimitMiddleware

from app.api.v1.auth import router as auth_router
from app.api.v1.urls import router as urls_router
from app.api.redirect import router as redirect_router

app = FastAPI(title="ShortLink API")

app.add_middleware(
    RateLimitMiddleware,
    redis=redis_client,
)

app.include_router(
    auth_router,
    prefix="/api/v1",
)

app.include_router(
    urls_router,
    prefix="/api/v1",
)

app.include_router(redirect_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/health/db")
async def database_health_check(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "database": result.scalar(),
    }

@app.get("/health/redis")
async def redis_health_check(
    redis: Redis = Depends(get_redis),
):
    result = await redis.ping()
    
    return {
        "status": "ok",
        "redis": result,
    }


@app.get("/health/db-info")
async def database_info(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        text(
            """
            SELECT
                current_database(),
                current_user,
                inet_server_addr(),
                inet_server_port(),
                current_schema()
            """
        )
    )

    row = result.one()

    return {
        "database": row[0],
        "user": row[1],
        "host": str(row[2]),
        "port": row[3],
        "schema": row[4],
    }
