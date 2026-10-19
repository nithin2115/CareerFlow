from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.recruiter_company import (
    RecruiterCompany,
    CompanyMembershipRole,
    MembershipStatus,
)
def authorize_company_access(db: Session,current_user: User,company_id: int,allowed_roles: set[CompanyMembershipRole]) -> RecruiterCompany:

    """Verify active membership and permission for a company."""
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=403,
            detail="Recruiter account required",
        )

    membership = db.scalar(
        select(RecruiterCompany).where(
            RecruiterCompany.user_id == current_user.id,
            RecruiterCompany.company_id == company_id,
        )
    )
    if membership is None or membership.status != MembershipStatus.ACTIVE:
        raise HTTPException(
            status_code=403,
            detail="Active company membership required",
        )

    if membership.role not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail="Insufficient company permissions",
        )
    return membership
