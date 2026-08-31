from app.database import get_db
from app.schemas import (
    PostCreate,
    PostResponse,
    PostUpdate,
)

from app.models import User, Post
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user

from typing import List

post_router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

@post_router.get("/")
def home():
    return {
        "message": "This is the posts route."
    }
    

@post_router.post("/create", response_model=PostResponse)
def create_post(
    post: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    new_post = Post(
        title = post.title,
        content=post.content,
        user_id=current_user.id
    )
    
    db.add(new_post)
    
    db.commit()
    
    db.refresh(new_post)
    
    return new_post

@post_router.put("/update/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    updated_data: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
      
    existing_post = db.query(Post).filter(Post.id == post_id).first()
    
    if existing_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post doesn't exist."
        )
    
    if  existing_post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post."
        )
    
    existing_post.title, existing_post.content = updated_data.title, updated_data.content
    
    db.commit()
    db.refresh(existing_post)
    
    return existing_post

@post_router.delete("/delete/{post_id}")
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing_post = db.query(Post).filter(Post.id == post_id).first()
    
    if existing_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found."
        )
    
    if existing_post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only allowed to delete your own post."
        )
    
    db.delete(existing_post)
    
    db.commit()
    
    return {
        "message": "Post deleted successfully."
    }


@post_router.patch("/update", response_model=PostResponse)
def partial_update(
    post_id: int,
    title: str | None = None,
    content: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)    
):
      
    existing_post = db.query(Post).filter(Post.id == post_id).first()
    
    if existing_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found."
        )
    
    if existing_post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only allowed to update your own post."
        )
    
    if title is not None:
        existing_post.title = title
    
    if content is not None:
        existing_post.content = content
    
    db.commit()
    
    db.refresh(existing_post)

    return existing_post

@post_router.get("/posts", response_model=List[PostResponse])
def get_posts(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    posts = (
        db.query(Post)
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return posts
