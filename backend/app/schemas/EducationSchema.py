from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator
class EducationBase(BaseModel):
    institution_name: str = Field(min_length=1, max_length=200)
    qualification: str = Field(min_length=1, max_length=100)
    field_of_study: str | None = Field(default=None, max_length=150)
    location: str | None = Field(default=None, max_length=150)
    start_date: date
    end_date: date | None = None
    grade_type: str | None = Field(default=None, max_length=30)
    grade_value: str | None = Field(default=None, max_length=30)
    description: str | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("End date cannot be earlier than start date")
        return self


class EducationCreate(EducationBase):
    pass


class EducationUpdate(BaseModel):
    institution_name: str | None = Field(default=None, min_length=1, max_length=200)
    qualification: str | None = Field(default=None, min_length=1, max_length=100)
    field_of_study: str | None = Field(default=None, max_length=150)
    location: str | None = Field(default=None, max_length=150)
    start_date: date | None = None
    end_date: date | None = None
    grade_type: str | None = Field(default=None, max_length=30)
    grade_value: str | None = Field(default=None, max_length=30)
    description: str | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if (self.start_date is not None and self.end_date is not None and self.end_date < self.start_date):
            raise ValueError("End date cannot be earlier than start date")
        return self
class EducationResponse(EducationBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    candidate_profile_id: int
    created_at: datetime
    updated_at: datetime
