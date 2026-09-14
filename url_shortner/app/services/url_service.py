from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.short_url import ShortURL
from app.repositories.url_repository import (
    create_short_url,
    delete_short_url,
    get_url_by_id,
    get_user_urls,
)
from app.schemas.url import CreateURLRequest

import secrets
import string

from datetime import datetime, timezone

from app.repositories.url_repository import (
    get_url_by_short_code,
    increment_click_count,
)

from redis.asyncio import Redis

from app.services.cache_service import (
    cache_url,
    get_cached_url,
    delete_cached_url,
)


def generate_short_code(length: int = 6) -> str:
    characters = string.ascii_letters + string.digits

    return "".join(
        secrets.choice(characters)
        for _ in range(length)
    )

async def create_user_url(
    db: AsyncSession,
    user_id: int,
    data: CreateURLRequest
) -> ShortURL:
    short_code = generate_short_code()
    
    short_url = ShortURL(
        short_code=short_code,
        original_url=str(data.original_url),
        user_id=user_id,
        expires_at=data.expires_at
    )
    
    return await create_short_url(db, short_url)

async def get_user_url(
    db: AsyncSession,
    user_id: int,    
    url_id: int,
) -> ShortURL:
    short_url = await get_url_by_id(db, url_id)
    
    if short_url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found",
        )
    
    if short_url.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this URL."
        )
    
    return short_url

async def list_user_urls(
    db: AsyncSession,
    user_id: int,
) -> list[ShortURL]:
    return await get_user_urls(db, user_id)

async def delete_user_url(
    db: AsyncSession,
    redis: Redis,
    user_id: int,
    url_id: int,
) -> None:
    short_url = await get_user_url(
        db,
        user_id,
        url_id,
    )

    await delete_short_url(
        db,
        short_url,
    )

    await delete_cached_url(
        redis,
        short_url.short_code,
    )
    
async def resolve_short_url(
    db: AsyncSession,
    redis: Redis,
    short_code: str,
) -> dict:
    cached_url = await get_cached_url(
        redis,
        short_code,
    )

    if cached_url is not None:
        expires_at = cached_url["expires_at"]

        if expires_at is not None:
            expires_at = datetime.fromisoformat(expires_at)

            if expires_at <= datetime.now(timezone.utc):
                await redis.delete(
                    f"url:{short_code}"
                )

                raise HTTPException(
                    status_code=status.HTTP_410_GONE,
                    detail="Short URL has expired",
                )

        return {
            "id": cached_url["id"],
            "original_url": cached_url["original_url"],
        }

    short_url = await get_url_by_short_code(
        db,
        short_code,
    )

    if short_url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found",
        )

    if (
        short_url.expires_at is not None
        and short_url.expires_at <= datetime.now(timezone.utc)
    ):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Short URL has expired",
        )

    await cache_url(
        redis,
        short_code,
        short_url.id,
        short_url.original_url,
        short_url.expires_at,
    )

    return {
        "id": short_url.id,
        "original_url": short_url.original_url,
    }