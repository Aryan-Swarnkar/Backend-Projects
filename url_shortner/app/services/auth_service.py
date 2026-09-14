from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import (
    create_user,
    get_user_by_email,
    get_user_by_username,
)
from app.schemas.auth import RegisterRequest

async def register_user(
    db: AsyncSession,
    data: RegisterRequest    
) -> User:
    existing_username = await get_user_by_username(
        db, data.username
    )
    
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )
    
    existing_email = await get_user_by_email(
        db, data.email
    )
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists",
        )
    
    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password)
    )
    
    return await create_user(db, user)

async def authenticate_user(
    db: AsyncSession,
    username: str,
    password: str,    
) -> User | None:
    user = await get_user_by_username(
        db,
        username,
    )
    
    if user is None:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    return user

def generate_user_token(user: User) -> str:
    return create_access_token(user.id)