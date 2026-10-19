from app.schemas.recruiter import CompanyCreateRequest
from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from app.models.user import User, UserRole
from app.schemas.recruiter import CompanyResponse
from app.models.recruiter_company import RecruiterCompany,CompanyMembershipRole,MembershipStatus
from sqlalchemy.orm import Session
from app.core.auth import require_role
from app.models.company import Company
router = APIRouter(prefix="/company", tags=["Company"])

@router.post("/companies",response_model=CompanyResponse,status_code=201,)
def create_company(request: CompanyCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.RECRUITER)
    ),
):
    company = Company(
        name=request.name,
        website=request.website,
        industry=request.industry,
        description=request.description,
    )

    try:
        db.add(company)
        db.flush()  # Generates company.id without committing yet.

        membership = RecruiterCompany(
            user_id=current_user.id,
            company_id=company.id,
            role=CompanyMembershipRole.COMPANY_ADMIN,
            status=MembershipStatus.ACTIVE,
        )
        db.add(membership)
        db.commit()
        db.refresh(company)
    except Exception:
        db.rollback()
        raise
    return company
