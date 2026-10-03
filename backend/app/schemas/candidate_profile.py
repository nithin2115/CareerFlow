from pydantic import BaseModel, ConfigDict, Field, HttpUrl

class CandidateProfileCreate(BaseModel):
    phone: str | None = Field(default=None, max_length=20)
    location: str | None = Field(default=None, max_length=150)
    professional_summary: str | None = None
    career_goal: str | None = None
    linkedin_url: HttpUrl | None = None
    github_url: HttpUrl | None = None
    portfolio_url: HttpUrl | None = None

class CandidateProfileUpdate(BaseModel):
    phone: str | None = Field(default=None, max_length=20)
    location: str | None = Field(default=None, max_length=150)
    professional_summary: str | None = None
    career_goal: str | None = None
    linkedin_url: HttpUrl | None = None
    github_url: HttpUrl | None = None
    portfolio_url: HttpUrl | None = None


class CandidateProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    phone: str | None
    location: str | None
    professional_summary: str | None
    career_goal: str | None
    linkedin_url: HttpUrl | None
    github_url: HttpUrl | None
    portfolio_url: HttpUrl | None