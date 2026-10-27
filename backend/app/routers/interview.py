from app.core import database
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.applications import Application
from app.models.interviews import Interview, InterviewStatus
from app.models.jobs import Job
from app.models.recruiter_company import CompanyMembershipRole
from app.models.user import User, UserRole
from app.schemas.interview import InterviewCreate, InterviewResponse,InterviewReschedule,InterviewFeedback
from app.core.company_auth import authorize_company_access
from app.models.notification import Notification, NotificationType

router = APIRouter(prefix="/interviews", tags=["Interviews"])

@router.post("",response_model=InterviewResponse,status_code=status.HTTP_201_CREATED)

def create_interview(
    interview_data: InterviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can schedule interviews",
        )

    application = db.scalar(
        select(Application).where(
            Application.id == interview_data.application_id
        )
    )

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    job = db.scalar(
        select(Job).where(Job.id == application.job_id)
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    authorize_company_access(
        db=db,
        current_user=current_user,
        company_id=job.company_id,
        allowed_roles=[
            CompanyMembershipRole.COMPANY_ADMIN,
            CompanyMembershipRole.RECRUITER,
        ],
    )

    if application.status in {
        "REJECTED",
        "WITHDRAWN",
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot schedule an interview for this application",
        )

    interview = Interview(
        application_id=application.id,
        scheduled_at=interview_data.scheduled_at,
        duration_minutes=interview_data.duration_minutes,
        interview_type=interview_data.interview_type,
        meeting_link=interview_data.meeting_link,
        status=InterviewStatus.SCHEDULED,
    )

    try:
        db.add(interview)
        db.flush()

        notification = Notification(
            user_id=application.candidate_id,
            type=NotificationType.INTERVIEW_SCHEDULED,
            title="Interview scheduled",
            message=(
                f"An interview has been scheduled for your application "
                f"to '{job.title}' on "
            f"{interview.scheduled_at.isoformat()}."
        ),
        application_id=application.id,
        interview_id=interview.id,
    )

        db.add(notification)
        db.commit()
        db.refresh(interview)

    except Exception:
        db.rollback()
        raise

    return interview


#Get interviews

@router.get("/me", response_model=list[InterviewResponse])
def get_my_interviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    interviews = db.scalars(
        select(Interview)
        .join(Application, Interview.application_id == Application.id)
        .where(Application.candidate_id == current_user.id)
        .order_by(Interview.scheduled_at.asc())
    ).all()

    return interviews

# Get interviews for a specific job

@router.get("/jobs/{job_id}", response_model=list[InterviewResponse])
def get_job_interviews(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can view job interviews",
        )

    job = db.scalar(
        select(Job).where(Job.id == job_id)
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    authorize_company_access(
        db=db,
        current_user=current_user,
        company_id=job.company_id,
        allowed_roles=[
            CompanyMembershipRole.COMPANY_ADMIN,
            CompanyMembershipRole.RECRUITER,
        ],
    )

    interviews = db.scalars(
        select(Interview)
        .join(Application, Interview.application_id == Application.id)
        .where(Application.job_id == job_id)
        .order_by(Interview.scheduled_at.asc())
    ).all()

    return interviews

# update the interview schedule
@router.patch("/{interview_id}/reschedule", response_model=InterviewResponse)
def reschedule_interview(
    interview_id: int,
    interview_data: InterviewReschedule,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can reschedule interviews",
        )

    interview = db.scalar(
        select(Interview).where(Interview.id == interview_id)
    )

    if interview is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )

    application = db.get(Application, interview.application_id)
    job = db.get(Job, application.job_id) if application else None

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application or job not found",
        )

    authorize_company_access(
        db=db,
        current_user=current_user,
        company_id=job.company_id,
        allowed_roles=[
            CompanyMembershipRole.COMPANY_ADMIN,
            CompanyMembershipRole.RECRUITER,
        ],
    )

    if interview.status != InterviewStatus.SCHEDULED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only scheduled interviews can be rescheduled",
        )

    interview.scheduled_at = interview_data.scheduled_at
    interview.duration_minutes = interview_data.duration_minutes
    interview.meeting_link = interview_data.meeting_link

    try:
        notification = Notification(
            user_id=application.candidate_id,
            type=NotificationType.INTERVIEW_RESCHEDULED,
            title="Interview rescheduled",
            message=(
                f"Your interview for '{job.title}' has been rescheduled to "
                f"{interview.scheduled_at.isoformat()}."
            ),
            application_id=application.id,
            interview_id=interview.id,
        )

        db.add(notification)
        db.commit()
        db.refresh(interview)

    except Exception:
        db.rollback()
        raise

    return interview

# Cancel the interview
@router.patch("/{interview_id}/cancel", response_model=InterviewResponse)
def cancel_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can cancel interviews",
        )

    interview = db.scalar(
        select(Interview).where(Interview.id == interview_id)
    )

    if interview is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )

    application = db.get(Application, interview.application_id)
    job = db.get(Job, application.job_id) if application else None

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application or job not found",
        )

    authorize_company_access(
        db=db,
        current_user=current_user,
        company_id=job.company_id,
        allowed_roles=[
            CompanyMembershipRole.COMPANY_ADMIN,
            CompanyMembershipRole.RECRUITER,
        ],
    )

    if interview.status != InterviewStatus.SCHEDULED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only scheduled interviews can be cancelled",
        )

    interview.status = InterviewStatus.CANCELLED

    try:
        notification = Notification(
            user_id=application.candidate_id,
            type=NotificationType.INTERVIEW_CANCELLED,
            title="Interview cancelled",
            message=(
                f"Your interview for '{job.title}' scheduled for "
                f"{interview.scheduled_at.isoformat()} has been cancelled."
            ),
            application_id=application.id,
            interview_id=interview.id,
        )

        db.add(notification)
        db.commit()
        db.refresh(interview)

    except Exception:
        db.rollback()
        raise

    return interview

# completed interview

@router.patch("/{interview_id}/complete", response_model=InterviewResponse)
def complete_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can complete interviews",
        )

    interview = db.scalar(
        select(Interview).where(Interview.id == interview_id)
    )

    if interview is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )

    application = db.get(Application, interview.application_id)
    job = db.get(Job, application.job_id) if application else None

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application or job not found",
        )

    authorize_company_access(
        db=db,
        current_user=current_user,
        company_id=job.company_id,
        allowed_roles=[
            CompanyMembershipRole.COMPANY_ADMIN,
            CompanyMembershipRole.RECRUITER,
        ],
    )

    if interview.status != InterviewStatus.SCHEDULED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only scheduled interviews can be completed",
        )

    interview.status = InterviewStatus.COMPLETED

    db.commit()
    db.refresh(interview)

    return interview

#Feedback on the interview
@router.patch("/{interview_id}/feedback", response_model=InterviewResponse)
def add_interview_feedback(
    interview_id: int,
    feedback_data: InterviewFeedback,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can add interview feedback",
        )

    interview = db.scalar(
        select(Interview).where(Interview.id == interview_id)
    )

    if interview is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )

    application = db.get(Application, interview.application_id)
    job = db.get(Job, application.job_id) if application else None

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application or job not found",
        )

    authorize_company_access(
        db=db,
        current_user=current_user,
        company_id=job.company_id,
        allowed_roles=[
            CompanyMembershipRole.COMPANY_ADMIN,
            CompanyMembershipRole.RECRUITER,
        ],
    )

    if interview.status != InterviewStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Feedback can only be added to completed interviews",
        )

    interview.interviewer_notes = feedback_data.interviewer_notes

    db.commit()
    db.refresh(interview)

    return interview
