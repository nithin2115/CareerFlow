
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


ProficiencyLevel = Literal[
    "Beginner",
    "Intermediate",
    "Advanced",
    "Expert",
]


class SkillBase(BaseModel):
    skill_name: str = Field(min_length=1, max_length=100)
    proficiency_level: ProficiencyLevel | None = None
    years_of_experience: Decimal | None = Field(
        default=None,
        ge=0,
        le=999.9,
        max_digits=4,
        decimal_places=1,
    )

    @field_validator("skill_name")
    @classmethod
    def validate_skill_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Skill name cannot be empty")

        return value


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    skill_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    proficiency_level: ProficiencyLevel | None = None
    years_of_experience: Decimal | None = Field(
        default=None,
        ge=0,
        le=999.9,
        max_digits=4,
        decimal_places=1,
    )

    @field_validator("skill_name")
    @classmethod
    def validate_skill_name(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Skill name cannot be empty")

        return value


class SkillResponse(SkillBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    candidate_profile_id: int
    created_at: datetime
    updated_at: datetime
