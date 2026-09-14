from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

async def get_user_by_username(
    db: AsyncSession,
    username: str,    
) -> User | None:
    result = await db.execute(
        select(User).where(User.username == username)
    )
    
    return result.scalar_one_or_none()

async def get_user_by_email(
    db: AsyncSession,
    email: str,
) -> User | None:
    result = await db.execute(
        select(User).where(User.email == email)
    )

    users = result.scalars().all()

    print("SEARCH EMAIL:", repr(email))
    print("USERS FOUND:", users)

    return users[0] if users else None

async def get_user_by_id(
    db: AsyncSession,
    id: int,    
) -> User | None:
    result = await db.execute(
        select(User).where(User.id == id)
    )
    
    return result.scalar_one_or_none()

async def create_user(
    db: AsyncSession,
    user: User,    
) -> User:
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user
