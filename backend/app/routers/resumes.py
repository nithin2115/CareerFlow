from app.models import resume
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
    candidate_profile = db.scalar(select(CandidateProfile).where(CandidateProfile.user_id == current_user.id))

    # 2. Make sure it exists
    if candidate_profile is None:
        raise HTTPException(status_code=404,detail="Candidate profile not found")
    
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
    
@router.get("", response_model=list[ResumeResponse])
def list_resumes(
    current_user: User = Depends(require_role(UserRole.CANDIDATE)),
    db: Session = Depends(get_db),
):
    # Find candidate profile id
    candidate_profile = db.scalar(
        select(CandidateProfile).where(
            CandidateProfile.user_id == current_user.id
        )
    )

    if candidate_profile is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found",
        )
    # get all resumes based on candidate profile id
    resumes = db.scalars(
        select(Resume).where(
            Resume.candidate_profile_id == candidate_profile.id
        )
    ).all()

    return resumes
@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(resume_id: int,current_user: User = Depends(require_role(UserRole.CANDIDATE)),db: Session = Depends(get_db)):
    candidate_profile = db.scalar( # search in database if profile is exists or not for logged in user
        select(CandidateProfile).where(
            CandidateProfile.user_id == current_user.id
        )
    )

    if candidate_profile is None: #if not exists error raised
        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found",
        )

    resume = db.scalar( # search in database if RESUME ID AND CANDIDATE ID IS EQUAL
        select(Resume).where(
            Resume.id == resume_id,
            Resume.candidate_profile_id == candidate_profile.id,
        )
    )

    if resume is None:#if not exists error raised
        raise HTTPException(
            status_code=404,
            detail="Resume not found",
        )
    return resume
@router.delete("/{resume_id}", status_code=204)
def delete_resume(resume_id: int,current_user: User = Depends(require_role(UserRole.CANDIDATE)),db: Session = Depends(get_db)):
    candidate_profile = db.scalar( # search in database if profile is exists or not for logged in user
        select(CandidateProfile).where(
            CandidateProfile.user_id == current_user.id
        )
    )
    if candidate_profile is None: #if not exists error raised
        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found",
        )
    resume = db.scalar( # search in database if RESUME ID AND CANDIDATE ID IS EQUAL
        select(Resume).where(
            Resume.id == resume_id,
            Resume.candidate_profile_id == candidate_profile.id,
        )
    )
    if resume is None:#if not exists error raised
        raise HTTPException(
            status_code=404,
            detail="Resume not found",
        )

    file_path = Path(resume.file_path)
    try:
        if file_path.exists():
            file_path.unlink()
    except OSError:
        raise HTTPException(
            status_code=500,
        detail="Unable to delete resume file",
    )
    db.delete(resume)
    db.commit()
    return

  
    