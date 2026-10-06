from pathlib import Path
from uuid import uuid4
from sqlalchemy import select
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from app.models.candidate_profile import CandidateProfile
from app.core.auth import require_role
from app.core.database import get_db
from app.models.user import User, UserRole
from app.schemas.resume import ResumeResponse
from fastapi import HTTPException
from app.models.resume import Resume
router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"],
)

@router.post("", response_model=ResumeResponse, status_code=201)
def upload_resume(file: UploadFile = File(...),current_user: User = Depends(require_role(UserRole.CANDIDATE)),db: Session = Depends(get_db)):
    extension = Path(file.filename).suffix.lower() # Path() created path object to represent filename and uniquefilename + filepath implementation
    storage_dir = Path("storage") / "resumes" # path() is used for separator instead of manually
    storage_dir.mkdir(parents=True, exist_ok=True) # check the directory already exists or not
    stored_filename = f"{uuid4()}{extension}" # generate unique file name using uuid 4 and commbine with extensiom
    file_path = storage_dir / stored_filename # file path where the file will be stored 
    with file_path.open("wb") as buffer: # pdf saved in stored actual path
        buffer.write(file.file.read())
    file_size = file_path.stat().st_size #get file size
     # 1. Find candidate profile
    candidate_profile = db.scalar(
        select(CandidateProfile).where(
            CandidateProfile.user_id == current_user.id
        )
    )

    # 2. Make sure it exists
    if candidate_profile is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found",
        )
    resume=Resume( # object created to store in database and as well as used that object to retrieve the info from db
        candidate_profile_id=candidate_profile.id,
        original_filename=file.filename,
        file_path=str(file_path),
        file_type=file.content_type or "",
        file_size=file_size,
        version=1,
        is_active=True,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return {
        "id": resume.id,
        "candidate_profile_id": resume.candidate_profile_id,
        "original_filename": resume.original_filename,
        "file_type": resume.file_type,
        "file_size": resume.file_size,
        "version": resume.version,
        "is_active": resume.is_active,
    }
    