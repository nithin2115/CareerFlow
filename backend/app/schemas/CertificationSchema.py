
from datetime import date, datetime
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)

class CertificationBase(BaseModel):
    certification_name: str = Field(min_length=1, max_length=200)
    issuing_organization: str = Field(min_length=1, max_length=150)
    issue_date: date
    expiration_date: date | None = None
    does_not_expire: bool = False
    credential_id: str | None = Field(default=None, max_length=150)
    credential_url: HttpUrl | None = None
    description: str | None = None

    @field_validator("certification_name", "issuing_organization")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty")
        return value

    @field_validator("credential_id")
    @classmethod
    def normalize_credential_id(cls,value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @model_validator(mode="after")
    def validate_expiration(self):
        if self.does_not_expire and self.expiration_date is not None:
            raise ValueError("Expiration date must be empty when certification does not expire")

        if (self.expiration_date is not None and self.expiration_date < self.issue_date):
            raise ValueError("Expiration date cannot be earlier than issue date")

        return self


class CertificationCreate(CertificationBase):
    pass


class CertificationUpdate(BaseModel):
    certification_name: str | None = Field(default=None, min_length=1, max_length=200)
    issuing_organization: str | None = Field(default=None, min_length=1, max_length=150)
    issue_date: date | None = None
    expiration_date: date | None = None
    does_not_expire: bool | None = None
    credential_id: str | None = Field(default=None, max_length=150)
    credential_url: HttpUrl | None = None
    description: str | None = None

    @field_validator("certification_name", "issuing_organization")
    @classmethod
    def validate_required_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty")
        return value

    @field_validator("credential_id")
    @classmethod
    def normalize_credential_id(cls,value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class CertificationResponse(CertificationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    candidate_profile_id: int
    created_at: datetime
    updated_at: datetime
