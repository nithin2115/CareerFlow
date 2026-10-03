from sqlalchemy import Integer,String,Enum,Boolean,DateTime,func
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column,relationship
from app.core.base import Base
from enum import Enum as PyEnum
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.candidate_profile import CandidateProfile
class UserRole(str, PyEnum):
    CANDIDATE = "candidate"
    RECRUITER = "recruiter"
    ADMIN = "admin"
class User(Base):
    __tablename__ = "users"
    id:Mapped[int] = mapped_column(Integer ,primary_key=True)
    username:Mapped[str] = mapped_column(String(50) ,unique=True ,index=True ,nullable=False)
    name: Mapped[str] = mapped_column(String(100),nullable=False)
    email: Mapped[str] = mapped_column(String(255),unique=True,nullable=False,index=True)
    password_hash:Mapped[str] = mapped_column(String(255),nullable=False)
    role:Mapped[UserRole] = mapped_column(Enum(UserRole),nullable=False,default=UserRole.CANDIDATE)
    is_active:Mapped[bool] = mapped_column(Boolean,nullable=False,default=True)
    created_at:Mapped[datetime] = mapped_column(DateTime,nullable=False,server_default=func.now())
    updated_at:Mapped[datetime] = mapped_column(DateTime,nullable=False,server_default=func.now(),onupdate=func.now())
    candidate_profile: Mapped["CandidateProfile | None"] = relationship(back_populates="user",uselist=False)
    