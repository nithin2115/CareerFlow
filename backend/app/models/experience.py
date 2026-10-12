from datetime import datetime, date
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import func, Boolean,Integer,String,Text,ForeignKey,Date,DateTime
from app.core.base import Base
from app.models.candidate_profile import CandidateProfile
class Experience(Base):
    __tablename__ = "experiences"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    candidate_profile_id: Mapped[int] = mapped_column(ForeignKey("candidate_profiles.id"),nullable=False,index=True)
    company_name: Mapped[str] = mapped_column(String(150),nullable=False)
    job_title: Mapped[str] = mapped_column(String(150),nullable=False)
    employment_type: Mapped[str] = mapped_column(String(50),nullable=False)
    location: Mapped[str | None] = mapped_column(String(150),nullable=True)
    start_date: Mapped[date] = mapped_column(Date,nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date,nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean,nullable=False,default=False)
    description: Mapped[str | None] = mapped_column(Text,nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False,server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False,server_default=func.now(),onupdate=func.now())
    candidate_profile: Mapped[CandidateProfile] = relationship(back_populates="experience")
    