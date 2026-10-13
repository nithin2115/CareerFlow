from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.candidate_profile import CandidateProfile
from app.models.careerInterest import CareerInterest
from app.models.user import User
from app.schemas.career_interest import (
    CareerInterestCreate,
    CareerInterestResponse,CareerInterestUpdate
)
router = APIRouter(prefix="/career-interests",tags=["Career Interests"])

# Create Career Interest and stored in database
@router.post( "/",response_model=CareerInterestResponse,status_code=status.HTTP_201_CREATED)
def create_career_interests(interest_data: CareerInterestCreate,db: Session = Depends(get_db),current_user: User = Depends(get_current_user),):
    candidate_profile = db.scalar(
        select(CandidateProfile).where(
            CandidateProfile.user_id == current_user.id
        )
    )
    if candidate_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found.",
        )

    existing_interest = db.scalar(
        select(CareerInterest).where(
            CareerInterest.candidate_profile_id == candidate_profile.id
        )
    )
    if existing_interest is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Career interests already exist.",
        )
    interest = CareerInterest(**interest_data.model_dump(),candidate_profile_id=candidate_profile.id) # object creation 
    try:
        db.add(interest)
        db.commit()
        db.refresh(interest)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Career interests already exist.",
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create career interests.",
        )
    return interest

# Getting details of career interest
@router.get("/",response_model=CareerInterestResponse,status_code=status.HTTP_200_OK)
def get_career_interests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    candidate_profile = db.scalar(
        select(CandidateProfile).where(
            CandidateProfile.user_id == current_user.id
        )
    )

    if candidate_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found.",
        )

    interest = db.scalar(
        select(CareerInterest).where(
            CareerInterest.candidate_profile_id == candidate_profile.id
        )
    )
    if interest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career interests not found.",
        )
    return interest

# update career interest
@router.patch("/",response_model=CareerInterestResponse,status_code=status.HTTP_200_OK)
def update_career_interests(interest_data: CareerInterestUpdate,db: Session = Depends(get_db),current_user: User = Depends(get_current_user),):
    candidate_profile = db.scalar(
        select(CandidateProfile).where(
            CandidateProfile.user_id == current_user.id
        )
    )
    if candidate_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found.",
        )

    interest = db.scalar(
        select(CareerInterest).where(
            CareerInterest.candidate_profile_id == candidate_profile.id
        )
    )

    if interest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career interests not found.",
        )

    update_values = interest_data.model_dump(exclude_unset=True)

    if not update_values:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide at least one field to update.",
        )

    for field in (
        "preferred_job_titles",
        "preferred_locations",
        "employment_types",
        "work_arrangements",
        "currency",
    ):
        if field in update_values and update_values[field] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field} cannot be null.",
            )

    final_min_salary = update_values.get(
        "min_expected_salary", interest.min_expected_salary
    )
    final_max_salary = update_values.get(
        "max_expected_salary", interest.max_expected_salary
    )

    if (final_min_salary is not None and final_max_salary is not None and final_min_salary > final_max_salary):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Minimum salary cannot exceed maximum salary.",
        )
    try:
        for field, value in update_values.items():
            setattr(interest, field, value)

        db.commit()
        db.refresh(interest)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update career interests.",
        )
    return interest

# delete career interest
@router.delete("/",status_code=status.HTTP_204_NO_CONTENT)
def delete_career_interests(db: Session = Depends(get_db),current_user: User = Depends(get_current_user),
):
    candidate_profile = db.scalar(
        select(CandidateProfile).where(
            CandidateProfile.user_id == current_user.id
        )
    )

    if candidate_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found.",
        )

    interest = db.scalar(
        select(CareerInterest).where(
            CareerInterest.candidate_profile_id == candidate_profile.id
        )
    )

    if interest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career interests not found.",
        )

    try:
        db.delete(interest)
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete career interests.",
        )
    return {"message": "Career interests deleted successfully."}




