from datetime import date, datetime
from decimal import Decimal
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.base import Base
if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.user import User


class EmploymentType(str, PyEnum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    INTERNSHIP = "internship"
    CONTRACT = "contract"
    FREELANCE = "freelance"


class WorkArrangement(str, PyEnum):
    ON_SITE = "on_site"
    HYBRID = "hybrid"
    REMOTE = "remote"


class JobStatus(str, PyEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CLOSED = "closed"


class Job(Base):
    __tablename__ = "jobs"

    __table_args__ = (
        CheckConstraint(
            "salary_min IS NULL OR salary_min >= 0",
            name="ck_jobs_salary_min_nonnegative",
        ),
        CheckConstraint(
            "salary_max IS NULL OR salary_max >= 0",
            name="ck_jobs_salary_max_nonnegative",
        ),
        CheckConstraint(
            "salary_min IS NULL OR salary_max IS NULL "
            "OR salary_min <= salary_max",
            name="ck_jobs_salary_range",
        ),
        CheckConstraint(
            "experience_min_years IS NULL OR experience_min_years >= 0",
            name="ck_jobs_experience_min_nonnegative",
        ),
        CheckConstraint(
            "experience_max_years IS NULL OR experience_max_years >= 0",
            name="ck_jobs_experience_max_nonnegative",
        ),
        CheckConstraint(
            "experience_min_years IS NULL OR experience_max_years IS NULL "
            "OR experience_min_years <= experience_max_years",
            name="ck_jobs_experience_range",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    posted_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    responsibilities: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    required_skills: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        index=True,
    )

    employment_type: Mapped[EmploymentType] = mapped_column(
        Enum(EmploymentType),
        nullable=False,
        index=True,
    )

    work_arrangement: Mapped[WorkArrangement] = mapped_column(
        Enum(WorkArrangement),
        nullable=False,
        index=True,
    )

    experience_min_years: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    experience_max_years: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    salary_min: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    salary_max: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    salary_currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="INR",
    )

    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus),
        nullable=False,
        default=JobStatus.DRAFT,
        index=True,
    )

    application_deadline: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
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

    company: Mapped["Company"] = relationship(
        back_populates="jobs",
    )

    posted_by: Mapped["User"] = relationship(
        back_populates="posted_jobs",
    )
