from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.auth import get_current_user
from app.core.company_auth import authorize_company_access
from app.core.database import get_db
from app.models.jobs import Job, JobStatus
from app.models.recruiter_company import (
    CompanyMembershipRole,
    MembershipStatus,
    RecruiterCompany,
)
from app.models.user import User, UserRole
from app.schemas.jobs import JobCreate, JobUpdate, JobResponse

router = APIRouter(prefix="/jobs", tags=["Jobs"])

# 1. Create a draft job
@router.post("", response_model=JobResponse, status_code=201)
def create_job(
    request: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    authorize_company_access(
        db=db,
        current_user=current_user,
        company_id=request.company_id,
        allowed_roles={
            CompanyMembershipRole.COMPANY_ADMIN,
            CompanyMembershipRole.RECRUITER,
        },
    )

    job = Job(
        **request.model_dump(),
        posted_by_user_id=current_user.id,
        status=JobStatus.DRAFT,
    )

    try:
        db.add(job)
        db.commit()
        db.refresh(job)
    except Exception:
        db.rollback()
        raise

    return job


# 2. Get a job by ID (authorized company members only)
@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.get(Job, job_id)

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    authorize_company_access(
        db=db,
        current_user=current_user,
        company_id=job.company_id,
        allowed_roles={
            CompanyMembershipRole.COMPANY_ADMIN,
            CompanyMembershipRole.RECRUITER,
            CompanyMembershipRole.VIEWER,
        },
    )

    return job


# 3. List jobs belonging to companies the recruiter can access
@router.get("", response_model=list[JobResponse])
def list_jobs(
    company_id: int | None = Query(default=None, gt=0),
    offset: int = Query(default=0, ge=0), # offset and limit for pagination
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if company_id is not None:
        authorize_company_access(
            db=db,
            current_user=current_user,
            company_id=company_id,
            allowed_roles={
                CompanyMembershipRole.COMPANY_ADMIN,
                CompanyMembershipRole.RECRUITER,
                CompanyMembershipRole.VIEWER,
            },
        )

        statement = select(Job).where(Job.company_id == company_id)
    else:
        if current_user.role != UserRole.RECRUITER:
            raise HTTPException(
                status_code=403,
                detail="Recruiter account required",
            )

        statement = (
            select(Job)
            .join(
                RecruiterCompany,
                RecruiterCompany.company_id == Job.company_id,
            )
            .where(
                RecruiterCompany.user_id == current_user.id,
                RecruiterCompany.status == MembershipStatus.ACTIVE,
            )
        )

    statement = (
        statement
        .order_by(Job.created_at.desc(), Job.id.desc())
        .offset(offset)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


# 4. Edit a job
@router.patch("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    request: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.get(Job, job_id)

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    authorize_company_access(
        db=db,
        current_user=current_user,
        company_id=job.company_id,
        allowed_roles={
            CompanyMembershipRole.COMPANY_ADMIN,
            CompanyMembershipRole.RECRUITER,
        },
    )

    if job.status != JobStatus.DRAFT:
        raise HTTPException(
            status_code=409,
            detail="Only draft jobs can be edited",
        )

    changes = request.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=422,
            detail="At least one field must be provided",
        )

    # Prevent null values for fields that must remain populated.
    required_fields = {
        "title",
        "description",
        "employment_type",
        "work_arrangement",
        "currency",
    }

    for field, value in changes.items():
        if field in required_fields and value is None:
            raise HTTPException(
                status_code=422,
                detail=f"{field} cannot be null",
            )

    # Validate partial updates against existing values too.
    experience_min = changes.get("experience_min", job.experience_min_years)
    experience_max = changes.get("experience_max", job.experience_max_years)
    salary_min = changes.get("salary_min", job.salary_min)
    salary_max = changes.get("salary_max", job.salary_max)

    if (
        experience_min is not None
        and experience_max is not None
        and experience_min > experience_max
    ):
        raise HTTPException(
            status_code=422,
            detail="Minimum experience cannot exceed maximum experience",
        )

    if (
        salary_min is not None
        and salary_max is not None
        and salary_min > salary_max
    ):
        raise HTTPException(
            status_code=422,
            detail="Minimum salary cannot exceed maximum salary",
        )

    if (
        changes.get("application_deadline", job.application_deadline)
        is not None
        and changes.get("application_deadline", job.application_deadline)
        < date.today()
    ):
        raise HTTPException(
            status_code=422,
            detail="Application deadline cannot be in the past",
        )

    for field, value in changes.items():
        setattr(job, field, value)

    try:
        db.commit()
        db.refresh(job)
    except Exception:
        db.rollback()
        raise

    return job


# 5. Publish a draft job
@router.post("/{job_id}/publish", response_model=JobResponse)
def publish_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.get(Job, job_id)

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    authorize_company_access(
        db=db,
        current_user=current_user,
        company_id=job.company_id,
        allowed_roles={
            CompanyMembershipRole.COMPANY_ADMIN,
            CompanyMembershipRole.RECRUITER,
        },
    )

    if job.status != JobStatus.DRAFT:
        raise HTTPException(
            status_code=409,
            detail="Only draft jobs can be published",
        )

    if not job.title or not job.description:
        raise HTTPException(
            status_code=422,
            detail="Job title and description are required for publishing",
        )

    if job.application_deadline is not None:
        if job.application_deadline < date.today():
            raise HTTPException(
                status_code=422,
                detail="Cannot publish a job with a past application deadline",
            )

    job.status = JobStatus.PUBLISHED
    job.published_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(job)
    except Exception:
        db.rollback()
        raise

    return job


# 6. Close a job
@router.post("/{job_id}/close", response_model=JobResponse)
def close_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.get(Job, job_id)

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    authorize_company_access(
        db=db,
        current_user=current_user,
        company_id=job.company_id,
        allowed_roles={
            CompanyMembershipRole.COMPANY_ADMIN,
            CompanyMembershipRole.RECRUITER,
        },
    )

    if job.status == JobStatus.CLOSED:
        raise HTTPException(
            status_code=409,
            detail="Job is already closed",
        )

    job.status = JobStatus.CLOSED

    try:
        db.commit()
        db.refresh(job)
    except Exception:
        db.rollback()
        raise

    return job
