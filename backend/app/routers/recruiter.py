from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.core.auth import require_role
from app.schemas.auth import RegisterResponse
from app.schemas.recruiter import RecruiterRegisterRequest,MembershipDecisionRequest,MembershipRequestResponse
from app.models.recruiter_company import RecruiterCompany,CompanyMembershipRole,MembershipStatus
from app.models.company import Company

router = APIRouter(prefix="/recruiters", tags=["Recruiters"])
@router.post("/register", response_model=RegisterResponse, status_code=201)
def register_recruiter(request: RecruiterRegisterRequest, db: Session = Depends(get_db)):
    existing_username = db.scalar(
        select(User).where(User.username == request.username)
    )
    if existing_username:
        raise HTTPException(
            status_code=409,
            detail="Username already registered",
        )

    existing_email = db.scalar(
        select(User).where(User.email == request.email)
    )
    if existing_email:
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    recruiter = User(
        username=request.username,
        name=request.name,
        email=request.email,
        password_hash=hash_password(request.password),
        role=UserRole.RECRUITER,
    )
    try:
        db.add(recruiter)
        db.commit()
        db.refresh(recruiter)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Username or email already registered",
        )

    return RegisterResponse(
        id=recruiter.id,
        username=recruiter.username,
        name=recruiter.name,
        email=recruiter.email,
        role=recruiter.role.value,
        is_active=recruiter.is_active,
    )
#request access for existing company
@router.post("/companies/{company_id}/membership-request",response_model=MembershipRequestResponse,status_code=201)
def request_company_membership(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.RECRUITER)
    ),
):
    company = db.get(Company, company_id) # check if company exists
    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Company not found",
        )

    existing = db.scalar(
        select(RecruiterCompany).where(
            RecruiterCompany.user_id == current_user.id,
            RecruiterCompany.company_id == company_id,
        )
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Membership or membership request already exists",
        )

    membership = RecruiterCompany(
        user_id=current_user.id,
        company_id=company_id,
        role=CompanyMembershipRole.RECRUITER,
        status=MembershipStatus.PENDING,
    )

    try:
        db.add(membership)
        db.commit()
        db.refresh(membership)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Membership request already exists",
        )
    return membership

#approve or reject membership request
@router.patch("/companies/{company_id}/memberships/{user_id}",response_model=MembershipRequestResponse)
def decide_company_membership(
    company_id: int,
    user_id: int,
    request: MembershipDecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.RECRUITER)
    ),
):
    admin_membership = db.scalar(
        select(RecruiterCompany).where(
            RecruiterCompany.user_id == current_user.id,
            RecruiterCompany.company_id == company_id,
            RecruiterCompany.role
            == CompanyMembershipRole.COMPANY_ADMIN,
            RecruiterCompany.status == MembershipStatus.ACTIVE,
        )
    )

    if admin_membership is None:
        raise HTTPException(
            status_code=403,
            detail="Active company administrator access required",
        )

    membership = db.scalar(
        select(RecruiterCompany).where(
            RecruiterCompany.user_id == user_id,
            RecruiterCompany.company_id == company_id,
        )
    )
    if membership is None:
        raise HTTPException(
            status_code=404,
            detail="Membership request not found",
        )

    if membership.status != MembershipStatus.PENDING:
        raise HTTPException(
            status_code=409,
            detail="Membership request has already been decided",
        )
    membership.status = MembershipStatus(request.status)
    try:
        db.commit()
        db.refresh(membership)
    except Exception:
        db.rollback()
        raise
    return membership
