from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.core.auth import require_role
from app.models import User, CandidateProfile, Education
from app.schemas.EducationSchema import EducationCreate, EducationResponse, EducationUpdate
from app.models.user import UserRole
from sqlalchemy.exc import SQLAlchemyError
router = APIRouter(prefix="/educations", tags=["Education"])
@router.post("",response_model=EducationResponse,status_code=status.HTTP_201_CREATED)
def create_education(education_data: EducationCreate,current_user: User = Depends(require_role(UserRole.CANDIDATE)),db:Session=Depends(get_db)):
    candidate_profile = db.scalar(select(CandidateProfile).where(CandidateProfile.user_id == current_user.id))
    if candidate_profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Candidate profile not found")
    education = Education(**education_data.model_dump(),candidate_profile_id=candidate_profile.id)
    try:
        db.add(education)
        db.commit()
        db.refresh(education)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Unable to save education")
    return education

@router.get("",response_model=list[EducationResponse])
def list_educations(
    current_user: User = Depends(
        require_role(UserRole.CANDIDATE)
    ),
    db: Session = Depends(get_db),
):
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

    educations = db.scalars(
        select(Education)
        .where(
            Education.candidate_profile_id == candidate_profile.id
        )
        .order_by(
            Education.start_date.desc(),
            Education.id.desc(),
        )
    ).all()

    return educations

@router.get(
    "/{education_id}",
    response_model=EducationResponse,
)
def get_education(
    education_id: int,
    current_user: User = Depends(
        require_role(UserRole.CANDIDATE)
    ),
    db: Session = Depends(get_db),
):
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

    education = db.scalar(
        select(Education).where(
            Education.id == education_id,
            Education.candidate_profile_id == candidate_profile.id,
        )
    )

    if education is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Education not found",
        )

    return education

@router.patch( "/{education_id}",response_model=EducationResponse)
def update_education(education_id: int,education_data: EducationUpdate,current_user: User = Depends(require_role(UserRole.CANDIDATE)),db: Session = Depends(get_db)):
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

    education = db.scalar(
        select(Education).where(
            Education.id == education_id,
            Education.candidate_profile_id == candidate_profile.id,
        )
    )

    if education is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Education not found",
        )

    update_data = education_data.model_dump(
        exclude_unset=True,
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    updated_start_date = update_data.get(
        "start_date", education.start_date
    )
    updated_end_date = update_data.get(
        "end_date", education.end_date
    )

    if (
        updated_end_date is not None
        and updated_end_date < updated_start_date
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="End date cannot be earlier than start date",
        )

    for field, value in update_data.items():
        setattr(education, field, value)

    try:
        db.commit()
        db.refresh(education)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update education",
        )

    return education

@router.delete("/{education_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_education(
    education_id: int,
    current_user: User = Depends(
        require_role(UserRole.CANDIDATE)
    ),
    db: Session = Depends(get_db),
):
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

    education = db.scalar(
        select(Education).where(
            Education.id == education_id,
            Education.candidate_profile_id == candidate_profile.id,
        )
    )

    if education is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Education not found",
        )
    try:
        db.delete(education)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete education",
        )
    return {"message": "Education Details deleted successfully."}
