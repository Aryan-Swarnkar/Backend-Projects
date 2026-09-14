from typing import TYPE_CHECKING

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.short_url import ShortURL

class User(Base):
    __tablename__="users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )
    
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )
    
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
    
    short_urls: Mapped[list["ShortURL"]] = relationship(
        back_populates="user",
    )
    