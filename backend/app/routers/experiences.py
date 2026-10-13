from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.core.auth import require_role
from app.core.database import get_db
from app.models.candidate_profile import CandidateProfile
from app.models.experience import Experience
from app.models.user import User, UserRole
from app.schemas.ExperienceSchema import ExperienceCreate, ExperienceResponse,ExperienceUpdate

router = APIRouter(prefix="/experiences",tags=["Experiences"])

@router.post("",response_model=ExperienceResponse,status_code=status.HTTP_201_CREATED)
# Create Experience and Stored in Database
def create_experience(experience_data: ExperienceCreate,current_user: User = Depends(require_role(UserRole.CANDIDATE)),db: Session = Depends(get_db)):
    candidate_profile = db.scalar(select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)) # search in database if profile is exists or not for logged in user
    if candidate_profile is None:#if not exists error raised
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Candidate profile not found")

    experience = Experience(**experience_data.model_dump(),candidate_profile_id=candidate_profile.id) # object created to store in database and as well as used that object to retrieve the info from db

    try:
        db.add(experience) # add experience to the database
        db.commit()
        db.refresh(experience) # refresh the database to get the updated data
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Unable to save experience")

    return experience
@router.get("",response_model=list[ExperienceResponse])
def get_all_experience(current_user: User = Depends(require_role(UserRole.CANDIDATE)),db: Session = Depends(get_db)):
    candidate_profile = db.scalar(select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)) # search in database if profile is exists or not for logged in user
    if candidate_profile is None:#if not exists error raised
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Candidate profile not found")
    return db.scalars(select(Experience).where(Experience.candidate_profile_id == candidate_profile.id).order_by(Experience.start_date.desc(),Experience.id.desc())).all() # get all experience of the user in descending order of start date and id

@router.get("/{experience_id}",response_model=ExperienceResponse) # get experience by id
def get_experience(experience_id: int,current_user: User = Depends(require_role(UserRole.CANDIDATE)),db: Session = Depends(get_db),):
    candidate_profile = db.scalar(select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)) # search in database if profile is exists or not for logged in user

    if candidate_profile is None: #if not exists error raised
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Candidate profile not found")

    experience = db.scalar(select(Experience).where(Experience.id == experience_id,Experience.candidate_profile_id == candidate_profile.id)) # search in database i experience is exists or not for logged in user

    if experience is None: #if not exists error raised
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Experience not found")

    return experience

@router.patch("/{experience_id}",response_model=ExperienceResponse)
def update_experience(experience_id: int,experience_data:ExperienceUpdate,current_user: User = Depends(require_role(UserRole.CANDIDATE)),db:Session=Depends(get_db)):
    candidate_profile = db.scalar(select(CandidateProfile).where(CandidateProfile.user_id == current_user.id))
    if candidate_profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Candidate profile not found")
    experience = db.scalar(select(Experience).where(Experience.id == experience_id,Experience.candidate_profile_id == candidate_profile.id))
    if experience is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Experience not found")
    updated_data = experience_data.model_dump(exclude_unset=True)
    if not updated_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="No data provided to update")
    updated_start_date = updated_data.get("start_date",experience.start_date)
    updated_end_date = updated_data.get("end_date",experience.end_date)
    updated_is_current = updated_data.get("is_current",experience.is_current)
    if updated_is_current and updated_end_date is not  None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,detail="Current employment cannot have an end date")
    if updated_start_date and updated_end_date:
        if updated_start_date > updated_end_date:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Start date cannot be greater than end date")

    for key,value in updated_data.items():
        setattr(experience,key,value)
    try:
        db.add(experience)
        db.commit()
        db.refresh(experience)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Unable to update experience")
    return experience

@router.delete("/{experience_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_experience(experience_id: int,current_user: User = Depends(require_role(UserRole.CANDIDATE)),db: Session = Depends(get_db)):
    candidate_profile = db.scalar(
        select(CandidateProfile).where(
            CandidateProfile.user_id == current_user.id
        )
    )

    if candidate_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found",
        )

    experience = db.scalar(
        select(Experience).where(
            Experience.id == experience_id,
            Experience.candidate_profile_id == candidate_profile.id,
        )
    )

    if experience is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found",
        )

    try:
        db.delete(experience)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete experience",
        )

    return {"message": "Experience Details deleted successfully."}

    
