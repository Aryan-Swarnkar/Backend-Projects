from app.database import get_db
from app.schemas import (
    UserCreate,
    UserResponse,
    UserLogin,
)

from app.models import User
from app.auth import hash_password, verify_password, create_access_token
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user

# from typing import List

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/")
def home():
    return {
        "message": "This is the users route."
    }

@router.post("/register", response_model=UserResponse)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    
    existing_user = db.query(User).filter(User.email == user.email).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists."
        )
    
    db_user = User(
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    
    db.add(db_user)
    
    db.commit()
    
    db.refresh(db_user)
    
    return db_user

@router.post("/login")
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.email == user.email).first()
    
    # check if user actuually exists 
    
    if existing_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found."
        )
    
    # check if passwords match
    
    if verify_password(user.password, existing_user.hashed_password) is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Credentials don't match."
        )
    
    existing_user_data = {
        "sub": str(existing_user.id)
    }
    
    access_token = create_access_token(existing_user_data)
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_me_route(
    current_user: User = Depends(get_current_user)
):
    return current_user
