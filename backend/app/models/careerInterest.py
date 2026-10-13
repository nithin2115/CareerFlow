from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.base import Base
from app.models.candidate_profile import CandidateProfile

class CareerInterest(Base):
    __tablename__ = "career_interests"
    __table_args__ = (
        UniqueConstraint(
            "candidate_profile_id",
            name="uq_career_interests_candidate_profile_id",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    candidate_profile_id: Mapped[int] = mapped_column(
        ForeignKey("candidate_profiles.id"),
        nullable=False,
    )

    preferred_job_titles: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    preferred_locations: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    employment_types: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    work_arrangements: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    min_expected_salary: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    max_expected_salary: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="INR",
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
        back_populates="career_interests",
    )
