from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.base import Base
from app.models.applications import Application
class InterviewType(str, PyEnum):
    TECHNICAL = "technical"
    HR = "hr"
    MANAGERIAL = "managerial"
    OTHER = "other"


class InterviewStatus(str, PyEnum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    duration_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=60,
    )

    interview_type: Mapped[InterviewType] = mapped_column(
        Enum(InterviewType),
        nullable=False,
        default=InterviewType.TECHNICAL,
    )

    meeting_link: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    status: Mapped[InterviewStatus] = mapped_column(
        Enum(InterviewStatus),
        nullable=False,
        default=InterviewStatus.SCHEDULED,
        index=True,
    )

    interviewer_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    application: Mapped["Application"] = relationship(
    back_populates="interviews"
)
