from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
EmploymentType = Literal[
    "FULL_TIME",
    "PART_TIME",
    "INTERNSHIP",
    "CONTRACT",
    "FREELANCE",
]
WorkArrangement = Literal[
    "ON_SITE",
    "HYBRID",
    "REMOTE",
]
class CareerInterestBase(BaseModel):
    preferred_job_titles: list[str] = Field(
        default_factory=list,
        max_length=20,
    )
    preferred_locations: list[str] = Field(
        default_factory=list,
        max_length=20,
    )
    employment_types: list[EmploymentType] = Field(
        default_factory=list,
    )
    work_arrangements: list[WorkArrangement] = Field(
        default_factory=list,
    )
    min_expected_salary: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )
    max_expected_salary: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )
    currency: str = Field(default="INR", pattern=r"^[A-Z]{3}$")

    @field_validator("preferred_job_titles", "preferred_locations")
    @classmethod
    def clean_string_lists(cls, values: list[str]) -> list[str]:
        cleaned = [value.strip() for value in values]

        if any(not value for value in cleaned):
            raise ValueError("List entries cannot be empty.")

        if len(set(value.casefold() for value in cleaned)) != len(cleaned):
            raise ValueError("Duplicate entries are not allowed.")

        return cleaned

    @model_validator(mode="after")
    def validate_salary_range(self):
        if self.min_expected_salary is not None and self.max_expected_salary is not None and self.min_expected_salary > self.max_expected_salary:
            raise ValueError("Minimum salary cannot exceed maximum salary.")
        return self

class CareerInterestCreate(CareerInterestBase):
    pass

class CareerInterestUpdate(BaseModel):
    preferred_job_titles: list[str] | None = Field(
        default=None,
        max_length=20,
    )
    preferred_locations: list[str] | None = Field(
        default=None,
        max_length=20,
    )
    employment_types: list[EmploymentType] | None = None
    work_arrangements: list[WorkArrangement] | None = None
    min_expected_salary: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )
    max_expected_salary: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )
    currency: str | None = Field(
        default=None,
        pattern=r"^[A-Z]{3}$",
    )
    @field_validator("preferred_job_titles", "preferred_locations")
    @classmethod
    def clean_string_lists(cls, values: list[str] | None) -> list[str] | None:
        if values is None:
            return values
        cleaned = [value.strip() for value in values]

        if any(not value for value in cleaned):
            raise ValueError("List entries cannot be empty.")

        if len(set(value.casefold() for value in cleaned)) != len(cleaned):
            raise ValueError("Duplicate entries are not allowed.")

        return cleaned

class CareerInterestResponse(CareerInterestBase):
    id: int
    candidate_profile_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
