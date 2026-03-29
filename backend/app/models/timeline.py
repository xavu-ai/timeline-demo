from datetime import datetime
from sqlalchemy import String, Text, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base


class Timeline(Base):
    __tablename__ = "timelines"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    entries: Mapped[list["TimelineEntry"]] = relationship(
        "TimelineEntry",
        back_populates="timeline",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_timelines_is_public", "is_public"),
        Index("ix_timelines_created_at", "created_at"),
    )


class TimelineEntry(Base):
    __tablename__ = "timeline_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    timeline_id: Mapped[str] = mapped_column(String(36), ForeignKey("timelines.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    timeline: Mapped["Timeline"] = relationship("Timeline", back_populates="entries")

    __table_args__ = (
        Index("ix_timeline_entries_timeline_id", "timeline_id"),
        Index("ix_timeline_entries_created_at", "created_at"),
    )
