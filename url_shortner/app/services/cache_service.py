import json
from datetime import datetime

from redis.asyncio import Redis


CACHE_TTL = 300


def build_url_cache_key(short_code: str) -> str:
    return f"url:{short_code}"


async def get_cached_url(
    redis: Redis,
    short_code: str,
) -> dict | None:
    key = build_url_cache_key(short_code)

    cached = await redis.get(key)

    if cached is None:
        return None

    return json.loads(cached)


async def cache_url(
    redis: Redis,
    short_code: str,
    url_id: int,
    original_url: str,
    expires_at: datetime | None,
) -> None:
    key = build_url_cache_key(short_code)

    data = {
        "id": url_id,
        "original_url": original_url,
        "expires_at": (
            expires_at.isoformat()
            if expires_at is not None
            else None
        ),
    }

    await redis.set(
        key,
        json.dumps(data),
        ex=CACHE_TTL,
    )

async def delete_cached_url(
    redis: Redis,
    short_code: str,
) -> None:
    key = build_url_cache_key(short_code)

    await redis.delete(key)