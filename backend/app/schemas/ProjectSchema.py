
from datetime import date, datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)
class ProjectBase(BaseModel):
    project_name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    technologies_used: str | None = None
    repository_url: HttpUrl | None = None
    live_demo_url: HttpUrl | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_ongoing: bool = False

    @field_validator("project_name")
    @classmethod
    def validate_project_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Project name cannot be empty.")

        return value

    @field_validator("description", "technologies_used")
    @classmethod
    def clean_optional_text(cls, value: str | None) -> str | None:
        if value is not None:
            value = value.strip()
            return value or None

        return value

    @model_validator(mode="after")
    def validate_project_dates(self):
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise ValueError("End date cannot be earlier than start date.")

        if self.is_ongoing and self.end_date is not None:
            raise ValueError("Ongoing projects cannot have an end date.")

        return self


class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    project_name: str | None = Field(default=None, max_length=200)
    description: str | None = None
    technologies_used: str | None = None
    repository_url: HttpUrl | None = None
    live_demo_url: HttpUrl | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_ongoing: bool | None = None

    @field_validator("project_name")
    @classmethod
    def validate_project_name(cls, value: str | None) -> str | None:
        if value is not None:
            value = value.strip()

            if not value:
                raise ValueError("Project name cannot be empty.")

        return value

    @field_validator("description", "technologies_used")
    @classmethod
    def clean_optional_text(cls, value: str | None) -> str | None:
        if value is not None:
            value = value.strip()
            return value or None

        return value

class ProjectResponse(ProjectBase):
    id: int
    candidate_profile_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
