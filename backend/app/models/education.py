from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base
from app.models.candidate_profile import CandidateProfile


class Education(Base):
    __tablename__ = "educations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    candidate_profile_id: Mapped[int] = mapped_column(
        ForeignKey("candidate_profiles.id"),
        nullable=False,
        index=True,
    )

    institution_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    qualification: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    field_of_study: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    grade_type: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    grade_value: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
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

    candidate_profile: Mapped[CandidateProfile] = relationship(
        back_populates="educations",
    )
