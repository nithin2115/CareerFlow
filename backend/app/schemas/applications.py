from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.applications import ApplicationStatus

class ApplicationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    resume_id: int = Field(gt=0)
    cover_letter: str | None = Field(
        default=None,
        max_length=5000,
    )

class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    candidate_id: int
    resume_id: int
    status: ApplicationStatus
    cover_letter: str | None
    applied_at: datetime
    updated_at: datetime

class MyApplicationResponse(ApplicationResponse):
    job_title: str


class RecruiterApplicantDetailsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    application_id: int
    job_id: int
    job_title: str
    candidate_id: int
    candidate_name: str
    candidate_email: str
    professional_summary: str | None
    location: str | None
    linkedin_url: str | None
    github_url: str | None
    portfolio_url: str | None
    resume_id: int
    resume_filename: str
    resume_file_type: str
    resume_version: int
    status: ApplicationStatus
    cover_letter: str | None
    applied_at: datetime

class ApplicationStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: ApplicationStatus
