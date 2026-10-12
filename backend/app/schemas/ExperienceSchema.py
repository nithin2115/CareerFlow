
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator
class ExperienceBase(BaseModel):
    company_name: str = Field(min_length=1, max_length=150)
    job_title: str = Field(min_length=1, max_length=150)
    employment_type: str = Field(min_length=1, max_length=50)
    location: str | None = Field(default=None, max_length=150)
    start_date: date
    end_date: date | None = None
    is_current: bool = False
    description: str | None = None
    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("End date cannot be earlier than start date")

        if self.is_current and self.end_date is not None:
            raise ValueError("Current employment cannot have an end date")

        return self
class ExperienceCreate(ExperienceBase): 
    pass
class ExperienceUpdate(BaseModel):
    company_name: str | None = Field(default=None, min_length=1, max_length=150)
    job_title: str | None = Field(default=None, min_length=1, max_length=150)
    employment_type: str | None = Field(default=None, min_length=1, max_length=50)
    location: str | None = Field(default=None, max_length=150)
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool | None = None
    description: str | None = None
    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date is not None and self.end_date is not None:
            if self.end_date < self.start_date:
                raise ValueError("End date cannot be earlier than start date")

        if self.is_current is True and self.end_date is not None:
            raise ValueError("Current employment cannot have an end date")

        return self

class ExperienceResponse(ExperienceBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    candidate_profile_id: int
    created_at: datetime
    updated_at: datetime
