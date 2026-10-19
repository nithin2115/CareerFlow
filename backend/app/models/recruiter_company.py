from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.base import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.company import Company
class CompanyMembershipRole(str, PyEnum):
    COMPANY_ADMIN = "company_admin"
    RECRUITER = "recruiter"
    VIEWER = "viewer"

class MembershipStatus(str, PyEnum):
    PENDING = "pending"
    ACTIVE = "active"
    REJECTED = "rejected"

class RecruiterCompany(Base):
    __tablename__ = "recruiter_companies"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "company_id",
            name="uq_recruiter_company_user_company",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role: Mapped[CompanyMembershipRole] = mapped_column(
        Enum(CompanyMembershipRole),
        nullable=False,
        default=CompanyMembershipRole.RECRUITER,
    )
    status: Mapped[MembershipStatus] = mapped_column(
        Enum(MembershipStatus),
        nullable=False,
        default=MembershipStatus.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    user: Mapped["User"] = relationship(
        back_populates="recruiter_memberships",
    )

    company: Mapped["Company"] = relationship(
        back_populates="recruiter_membership",
    )
