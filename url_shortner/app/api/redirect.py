from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.url_service import resolve_short_url

from redis.asyncio import Redis

from app.db.redis import get_redis

from app.repositories.url_repository import increment_click_count_by_id


router = APIRouter()

@router.get(
    "/{short_code}",
    include_in_schema=False,
)
async def redirect_to_original_url(
    short_code: str,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    short_url = await resolve_short_url(
        db,
        redis,
        short_code,
    )

    await increment_click_count_by_id(
        db,
        short_url["id"],
    )

    return RedirectResponse(
        url=short_url["original_url"],
        status_code=302,
    )