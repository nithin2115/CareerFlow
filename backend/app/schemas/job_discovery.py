from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from app.models.jobs import EmploymentType, WorkArrangement

class JobDiscoveryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    company_id: int
    title: str
    description: str
    responsibilities: str | None
    required_skills: str | None
    location: str | None
    employment_type: EmploymentType
    work_arrangement: WorkArrangement
    experience_min_years: int | None
    experience_max_years: int | None
    salary_min: Decimal | None
    salary_max: Decimal | None
    salary_currency: str
    application_deadline: date | None
    published_at: datetime | None