from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import (
    authenticate_user,
    generate_user_token,
    register_user,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authenticate"],
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    return await register_user(db, data)

@router.post("/login", response_model=TokenResponse,)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(
        db,
        data.username,
        data.password
    )
    
    if user is None:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = generate_user_token(user)
    
    return TokenResponse(
        access_token=token
    )
    
@router.get("/me", response_model=UserResponse)
async def me(
    current_user: User = Depends(get_current_user),
):
    return current_user
