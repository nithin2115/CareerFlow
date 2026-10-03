from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.auth import get_current_user, require_role
from app.core.database import get_db
from app.models.candidate_profile import CandidateProfile
from app.models.user import User, UserRole
from app.schemas.candidate_profile import (CandidateProfileCreate,CandidateProfileResponse)

router = APIRouter(prefix="/candidate-profile",tags=["Candidate Profile"])

@router.post("", response_model=CandidateProfileResponse, status_code=201)
def create_candidate_profile(request: CandidateProfileCreate,current_user: User = Depends(require_role(UserRole.CANDIDATE)),db: Session = Depends(get_db)):
    existing_profile = (db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()) # retreive data from candidate profile table with user id
    if existing_profile:
        raise HTTPException(status_code=409,detail="Candidate profile already exists")

    profile = CandidateProfile( # object created to store in database
        user_id=current_user.id,
        phone=request.phone,
        location=request.location,
        professional_summary=request.professional_summary,
        career_goal=request.career_goal,
        linkedin_url=str(request.linkedin_url)
        if request.linkedin_url
        else None,
        github_url=str(request.github_url)
        if request.github_url
        else None,
        portfolio_url=str(request.portfolio_url)
        if request.portfolio_url
        else None,
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile
# get userprofile 
@router.get("/me", response_model=CandidateProfileResponse)
def get_my_candidate_profile(current_user: User = Depends(require_role(UserRole.CANDIDATE)),db: Session = Depends(get_db)):
    profile = (db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first())

    if profile is None:
        raise HTTPException(status_code=404,detail="Candidate profile not found")

    return profile
#Update profile
@router.patch("/me", response_model=CandidateProfileResponse)
def update_my_candidate_profile(request:CandidateProfileCreate,current_user: User = Depends(require_role(UserRole.CANDIDATE)),db: Session = Depends(get_db)):
    profile = (db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first())

    if profile is None:
        raise HTTPException(status_code=404,detail="Candidate profile not found")
    update_data=request.model_dump(exclude_unset=True)
    for key,value in update_data.items():
        if value is not None:
            setattr(profile,key,value) # setattr dynamically update the fields which need to be updated 
    db.commit()
    db.refresh(profile) # update 
    return profile
#delete profile
@router.delete("/me", status_code=204)
def delete_my_candidate_profile(
    current_user: User = Depends(
        require_role(UserRole.CANDIDATE)
    ),
    db: Session = Depends(get_db),
):
    profile = (
        db.query(CandidateProfile)
        .filter(CandidateProfile.user_id == current_user.id)
        .first()
    )

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found",
        )
    db.delete(profile)
    db.commit()
