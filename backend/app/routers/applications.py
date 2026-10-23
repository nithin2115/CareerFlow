from datetime import date
from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.auth import require_role
from app.core.database import get_db
from app.models.applications import Application, ApplicationStatus
from app.models.candidate_profile import CandidateProfile
from app.models.jobs import Job, JobStatus
from app.schemas.applications import RecruiterApplicantDetailsResponse
from app.models.resume import Resume
from app.schemas.applications import ApplicationStatusUpdate
from app.models.user import User, UserRole
from app.core.company_auth import authorize_company_access
from app.models.recruiter_company import CompanyMembershipRole
from app.models.candidate_profile import CandidateProfile
from app.schemas.applications import (
    ApplicationCreate,
    ApplicationResponse,
    MyApplicationResponse,
)

router = APIRouter(prefix="/applications", tags=["Applications"])

@router.post("/{job_id}",response_model=ApplicationResponse,status_code=201,)
def apply_for_job(job_id: int,request: ApplicationCreate,db: Session = Depends(get_db),current_user: User = Depends(require_role(UserRole.CANDIDATE)),):
    job = db.get(Job, job_id)

    if job is None or job.status != JobStatus.PUBLISHED:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    if (
        job.application_deadline is not None
        and job.application_deadline < date.today()
    ):
        raise HTTPException(
            status_code=409,
            detail="Job is no longer accepting applications",
        )

    resume = db.scalar(
        select(Resume)
        .join(
            CandidateProfile,
            Resume.candidate_profile_id == CandidateProfile.id,
        )
        .where(
            Resume.id == request.resume_id,
            CandidateProfile.user_id == current_user.id,
            Resume.is_active.is_(True),
        )
    )

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Active resume not found for this candidate",
        )

    existing_application = db.scalar(
        select(Application).where(
            Application.job_id == job_id,
            Application.candidate_id == current_user.id,
        )
    )

    if existing_application is not None:
        raise HTTPException(
            status_code=409,
            detail="You have already applied for this job",
        )

    application = Application(
        job_id=job_id,
        candidate_id=current_user.id,
        resume_id=resume.id,
        cover_letter=request.cover_letter,
        status=ApplicationStatus.APPLIED,
    )

    try:
        db.add(application)
        db.commit()
        db.refresh(application)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Application conflicts with an existing record",
        )
    return application

# 2. List applications belonging to the logged-in candidate
@router.get("/me", response_model=list[MyApplicationResponse])
def list_my_applications(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CANDIDATE)),
):
    statement = (
        select(Application, Job.title)
        .join(Job, Application.job_id == Job.id)
        .where(Application.candidate_id == current_user.id)
        .order_by(Application.applied_at.desc(), Application.id.desc())
        .offset(offset)
        .limit(limit)
    )

    results = db.execute(statement).all()

    applications = []

    for application, job_title in results:
        application_data = ApplicationResponse.model_validate(application).model_dump()

        application_data["job_title"] = job_title

        applications.append(MyApplicationResponse(**application_data))

    return applications

# 3. Get one application belonging to the logged-in candidate
@router.get(
    "/{application_id}",
    response_model=MyApplicationResponse,
)
def get_my_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CANDIDATE)),
):
    statement = (
        select(Application, Job.title)
        .join(Job, Application.job_id == Job.id)
        .where(
            Application.id == application_id,
            Application.candidate_id == current_user.id,
        )
    )

    result = db.execute(statement).first()

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    application, job_title = result

    application_data = ApplicationResponse.model_validate(application).model_dump()

    application_data["job_title"] = job_title

    return MyApplicationResponse(**application_data)


# 4. Withdraw an application
@router.patch("/{application_id}/withdraw", response_model=ApplicationResponse)
def withdraw_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CANDIDATE)),
):
    application = db.scalar(
        select(Application).where(
            Application.id == application_id,
            Application.candidate_id == current_user.id,
        )
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    if application.status not in [
        ApplicationStatus.APPLIED,
        ApplicationStatus.UNDER_REVIEW,
    ]:
        raise HTTPException(
            status_code=409,
            detail="This application can no longer be withdrawn",
        )

    application.status = ApplicationStatus.WITHDRAWN

    db.commit()
    db.refresh(application)

    return application


# 5. View applicants for a recruiter's job
@router.get("/jobs/{job_id}/applications")
def list_job_applicants(
    job_id: int,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.RECRUITER)),
):
    job = db.get(Job, job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    authorize_company_access(
        db=db,
        current_user=current_user,
        company_id=job.company_id,
        allowed_roles={
            CompanyMembershipRole.COMPANY_ADMIN,
            CompanyMembershipRole.RECRUITER,
        },
    )

    statement = (
        select(Application, User)
        .join(User, Application.candidate_id == User.id)
        .where(Application.job_id == job_id)
        .order_by(
            Application.applied_at.desc(),
            Application.id.desc(),
        )
        .offset(offset)
        .limit(limit)
    )

    results = db.execute(statement).all()

    applicants = []

    for application, candidate in results:
       applicants.append(
    {
        "application_id": application.id,
        "job_id": application.job_id,
        "candidate_id": candidate.id,
        "candidate_name": candidate.name,
        "candidate_email": candidate.email,
        "resume_id": application.resume_id,
        "status": application.status,
        "cover_letter": application.cover_letter,
        "applied_at": application.applied_at,
    }
)

    return applicants


# 6. View applicant details for a recruiter's job
@router.get(
    "/{application_id}/details",
    response_model=RecruiterApplicantDetailsResponse,
)
def get_recruiter_applicant_details(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.RECRUITER)),
):
    statement = (
        select(Application, Job, User, CandidateProfile, Resume)
        .join(Job, Application.job_id == Job.id)
        .join(User, Application.candidate_id == User.id)
        .outerjoin(
            CandidateProfile,
            CandidateProfile.user_id == User.id,
        )
        .join(Resume, Application.resume_id == Resume.id)
        .where(Application.id == application_id)
    )

    result = db.execute(statement).first()

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    application, job, candidate, profile, resume = result

    authorize_company_access(
        db=db,
        current_user=current_user,
        company_id=job.company_id,
        allowed_roles={
            CompanyMembershipRole.COMPANY_ADMIN,
            CompanyMembershipRole.RECRUITER,
        },
    )

    return {
        "application_id": application.id,
        "job_id": job.id,
        "job_title": job.title,
        "candidate_id": candidate.id,
        "candidate_name": candidate.name,
        "candidate_email": candidate.email,
        "professional_summary": (
            profile.professional_summary if profile else None
        ),
        "location": profile.location if profile else None,
        "linkedin_url": profile.linkedin_url if profile else None,
        "github_url": profile.github_url if profile else None,
        "portfolio_url": profile.portfolio_url if profile else None,
        "resume_id": resume.id,
        "resume_filename": resume.original_filename,
        "resume_file_type": resume.file_type,
        "resume_version": resume.version,
        "status": application.status,
        "cover_letter": application.cover_letter,
        "applied_at": application.applied_at,
    }


# 7. Shortlist or reject an applicant
@router.patch("/{application_id}/status", response_model=ApplicationResponse)
def update_application_status(
    application_id: int,
    request: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.RECRUITER)),
):
    application = db.get(Application, application_id) # get application from application id

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    job = db.get(Job, application.job_id) # get job from application 

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    authorize_company_access(
        db=db,
        current_user=current_user,
        company_id=job.company_id,
        allowed_roles={
            CompanyMembershipRole.COMPANY_ADMIN,
            CompanyMembershipRole.RECRUITER,
        },
    )

    allowed_transitions = {
        ApplicationStatus.APPLIED: {
            ApplicationStatus.UNDER_REVIEW,
            ApplicationStatus.SHORTLISTED,
            ApplicationStatus.REJECTED,
        },
        ApplicationStatus.UNDER_REVIEW: {
            ApplicationStatus.SHORTLISTED,
            ApplicationStatus.REJECTED,
        },
        ApplicationStatus.SHORTLISTED: {
            ApplicationStatus.REJECTED,
        },
    }

    allowed_statuses = allowed_transitions.get(application.status, set()) # get allowed statuses from application status

    if request.status not in allowed_statuses: # check if new status is allowed
        raise HTTPException(
            status_code=409,
            detail=(
                f"Cannot change application status from "
                f"'{application.status.value}' to '{request.status.value}'"
            ),
        )

    application.status = request.status # update application status

    db.commit()
    db.refresh(application)

    return application
