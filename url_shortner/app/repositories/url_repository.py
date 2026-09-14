from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.short_url import ShortURL


async def create_short_url(
    db: AsyncSession,
    short_url: ShortURL,
) -> ShortURL:
    db.add(short_url)

    await db.commit()
    await db.refresh(short_url)

    return short_url


async def get_url_by_id(
    db: AsyncSession,
    url_id: int,
) -> ShortURL | None:
    result = await db.execute(
        select(ShortURL).where(ShortURL.id == url_id)
    )

    return result.scalar_one_or_none()


async def get_user_urls(
    db: AsyncSession,
    user_id: int,
) -> list[ShortURL]:
    result = await db.execute(
        select(ShortURL)
        .where(ShortURL.user_id == user_id)
        .order_by(ShortURL.created_at.desc())
    )

    return list(result.scalars().all())


async def delete_short_url(
    db: AsyncSession,
    short_url: ShortURL,
) -> None:
    await db.delete(short_url)
    await db.commit()
    
    
async def get_url_by_short_code(
    db: AsyncSession,
    short_code: str,
) -> ShortURL | None:
    result = await db.execute(
        select(ShortURL).where(
            ShortURL.short_code == short_code
        )
    )

    return result.scalar_one_or_none()

async def increment_click_count(
    db: AsyncSession,
    short_url: ShortURL,
) -> None:
    short_url.click_count += 1

    await db.commit()
    
async def increment_click_count_by_id(
    db: AsyncSession,
    url_id: int,
) -> None:
    await db.execute(
        update(ShortURL)
        .where(ShortURL.id == url_id)
        .values(click_count=ShortURL.click_count + 1)
    )

    await db.commit()