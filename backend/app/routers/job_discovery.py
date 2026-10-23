from datetime import date
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.jobs import (
    EmploymentType,
    Job,
    JobStatus,
    WorkArrangement,
)
from app.models.user import User
from app.schemas.job_discovery import JobDiscoveryResponse
router = APIRouter(
    prefix="/job-discovery",
    tags=["Job Discovery"],
)
#search and filter jobs
@router.get("", response_model=list[JobDiscoveryResponse])
def browse_published_jobs(
    offset: int = Query(ge=0), # offset for pagination
    limit: int = Query(ge=1, le=100), # limit for pagination
    q: str | None = Query(default=None, min_length=1, max_length=100), # search keyword
    location: str | None = Query(default=None, max_length=200),# location filter
    employment_type: EmploymentType | None = None,# employment type filter
    work_arrangement: WorkArrangement | None = None,# work arrangement filter
    experience_years: int | None = Query(default=None, ge=0),# experience filter
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()

    # Only return published jobs that have not passed their deadline.
    statement = select(Job).where(
        Job.status == JobStatus.PUBLISHED,
        or_(
            Job.application_deadline.is_(None), # job.applicationdeadline is null or
            Job.application_deadline >= today, # job.applicationdeadline is greater than today
        ),
    )

    # Search job title, description, and required skills.
    if q:
        search_term = f"%{q.strip()}%" # % is a wildcard for sql
        statement = statement.where(
            or_(
                Job.title.ilike(search_term), # job.title contains search_term handles case-insensitive search
                Job.description.ilike(search_term), # job.description contains search_term handles case-insensitive search
                Job.required_skills.ilike(search_term), # job.required_skills contains search_term handles case-insensitive search
            )
        )

    # Filter by location.
    if location:
        statement = statement.where(
            Job.location.ilike(f"%{location.strip()}%") # job.location contains location
        )

    # Filter by employment type.
    if employment_type is not None:
        statement = statement.where(
            Job.employment_type == employment_type # job.employment_type matches employment_type
        )

    # Filter by work arrangement.
    if work_arrangement is not None:
        statement = statement.where(
            Job.work_arrangement == work_arrangement # job.work_arrangement matches work_arrangement
        )

    # Match jobs whose experience range includes the requested experience.
    if experience_years is not None:
        statement = statement.where(
            or_(
                Job.experience_min_years.is_(None), # job.experience_min_years is null or
                Job.experience_min_years <= experience_years, # job.experience_min_years is less than or equal to experience_years
            ),
            or_(
                Job.experience_max_years.is_(None), # job.experience_max_years is null or
                Job.experience_max_years >= experience_years, # job.experience_max_years is greater than or equal to experience_years
            ),
        )

    # Return the newest published jobs first, with stable pagination.
    statement = (
        statement
        .order_by(Job.published_at.desc(), Job.id.desc()) # job.published_at is descending and job.id is descending
        .offset(offset) # offset for pagination
        .limit(limit) # limit for pagination
    ) # apply filters and order by published_at and id

    return list(db.scalars(statement).all()) # return list of jobs

# Get job details
@router.get("/{job_id}", response_model=JobDiscoveryResponse)
def get_published_job_details(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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
            status_code=404,
            detail="Job not found",
        )
    return job
