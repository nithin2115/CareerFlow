from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime
from typing import Literal
from app.models.recruiter_company import CompanyMembershipRole,MembershipStatus
class RecruiterRegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(min_length=3, max_length=50)
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
class CompanyCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=2, max_length=200)
    website: str | None = Field(default=None, max_length=2048)
    industry: str | None = Field(default=None, max_length=150)
    description: str | None = None
class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    website: str | None
    industry: str | None
    description: str | None
    created_at: datetime
    updated_at: datetime
class MembershipRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    company_id: int
    role: CompanyMembershipRole
    status: MembershipStatus
#request to approve or reject membership request
class MembershipDecisionRequest(BaseModel):
    status: Literal["active", "rejected"]
