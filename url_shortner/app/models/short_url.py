from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class ShortURL(Base):
    __tablename__ = "short_urls"

    id: Mapped[int] = mapped_column(primary_key=True)

    short_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )

    original_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    click_count: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
    )

    user: Mapped["User"] = relationship(
        back_populates="short_urls",
    )