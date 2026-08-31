from .database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    
    email = Column(String, nullable=False, unique=True)
    
    hashed_password = Column(String, nullable=False)
    
    posts = relationship("Post", back_populates="owner", cascade="all, delete")
    
    
class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)

    title = Column(String, nullable=False)
    
    content = Column(String, nullable=False)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    owner = relationship("User", back_populates="posts")