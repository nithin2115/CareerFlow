from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.models.jobs import (
    EmploymentType,
    WorkArrangement,
    JobStatus,
)

#for admin create job
class JobCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    company_id: int = Field(gt=0)
    title: str = Field(min_length=2, max_length=200)
    description: str = Field(min_length=20)
    responsibilities: Optional[str] = None
    required_skills: Optional[str] = None
    location: Optional[str] = Field(default=None, max_length=200)
    employment_type: EmploymentType
    work_arrangement: WorkArrangement
    experience_min_years: Optional[int] = Field(default=None, ge=0)
    experience_max_years: Optional[int] = Field(default=None, ge=0)
    salary_min: Optional[Decimal] = Field(default=None, ge=0)
    salary_max: Optional[Decimal] = Field(default=None, ge=0)
    salary_currency: str = Field(default="INR", min_length=3, max_length=3)
    application_deadline: Optional[date] = None

    @model_validator(mode="after")
    def validate_ranges(self):
        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_min > self.salary_max
        ):
            raise ValueError("Minimum salary cannot exceed maximum salary")

        if (
            self.experience_min_years is not None
            and self.experience_max_years is not None
            and self.experience_min_years > self.experience_max_years
        ):
            raise ValueError(
                "Minimum experience cannot exceed maximum experience"
            )
        return self

#for admin update job
class JobUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: Optional[str] = Field(default=None, min_length=2, max_length=200)
    description: Optional[str] = Field(default=None, min_length=20)
    responsibilities: Optional[str] = None
    required_skills: Optional[str] = None
    location: Optional[str] = Field(default=None, max_length=200)
    employment_type: Optional[EmploymentType] = None
    work_arrangement: Optional[WorkArrangement] = None
    experience_min_years: Optional[int] = Field(default=None, ge=0)
    experience_max_years: Optional[int] = Field(default=None, ge=0)
    salary_min: Optional[Decimal] = Field(default=None, ge=0)
    salary_max: Optional[Decimal] = Field(default=None, ge=0)
    salary_currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    application_deadline: Optional[date] = None

    @model_validator(mode="after")
    def validate_ranges(self):
        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_min > self.salary_max
        ):
            raise ValueError("Minimum salary cannot exceed maximum salary")

        if (
            self.experience_min_years is not None
            and self.experience_max_years is not None
            and self.experience_min_years > self.experience_max_years
        ):
            raise ValueError(
                "Minimum experience cannot exceed maximum experience"
            )
        return self

# response 

class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    company_id: int
    posted_by_user_id: int
    title: str
    description: str
    responsibilities: Optional[str] = None
    required_skills: Optional[str] = None
    location: Optional[str] = None
    employment_type: EmploymentType
    work_arrangement: WorkArrangement
    experience_min_years: Optional[int] = None
    experience_max_years: Optional[int] = None
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None
    salary_currency: str
    status: JobStatus
    application_deadline: Optional[date] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime



