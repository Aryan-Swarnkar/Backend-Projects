from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.url import CreateURLRequest, URLResponse
from app.services.url_service import (
    create_user_url,
    delete_user_url,
    get_user_url,
    list_user_urls,
)

from redis.asyncio import Redis

from app.db.redis import get_redis

router = APIRouter(
    prefix="/urls",
    tags=["URLs"],
)

@router.post("", response_model=URLResponse, status_code=status.HTTP_201_CREATED,)
async def create_url(
    date: CreateURLRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await create_user_url(db, current_user.id, date,)

@router.get(
    "",
    response_model=list[URLResponse],
)
async def get_urls(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await list_user_urls(
        db,
        current_user.id,
    )

@router.get(
    "/{url_id}",
    response_model=URLResponse,
)
async def get_url(
    url_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_user_url(
        db,
        current_user.id,
        url_id,
    )

@router.delete(
    "/{url_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_url(
    url_id: int,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user),
):
    await delete_user_url(
        db,
        redis,
        current_user.id,
        url_id,
    )