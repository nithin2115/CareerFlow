from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.interviews import InterviewStatus, InterviewType

class InterviewCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    application_id: int = Field(gt=0)
    scheduled_at: datetime
    duration_minutes: int = Field(default=60, gt=0, le=480)
    interview_type: InterviewType = InterviewType.TECHNICAL
    meeting_link: str | None = Field(default=None, max_length=500)

class InterviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    application_id: int
    scheduled_at: datetime
    duration_minutes: int
    interview_type: InterviewType
    meeting_link: str | None
    status: InterviewStatus
    created_at: datetime
    updated_at: datetime

class InterviewReschedule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scheduled_at: datetime
    duration_minutes: int = Field(default=60, gt=0, le=480)
    meeting_link: str | None = Field(default=None, max_length=500)

class InterviewFeedback(BaseModel):
    model_config = ConfigDict(extra="forbid")

    interviewer_notes: str = Field(min_length=1, max_length=5000)

