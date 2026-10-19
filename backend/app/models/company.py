from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.base import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.recruiter_company import RecruiterCompany
    from app.models.jobs import Job

class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    website: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
    )

    industry: Mapped[str | None] = mapped_column(
        String(150),
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
    recruiter_membership: Mapped[list["RecruiterCompany"]] = relationship(
        back_populates="company",
    )
    jobs: Mapped[list["Job"]] = relationship(
        back_populates="company",
    )
