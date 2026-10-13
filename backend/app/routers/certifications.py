from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.core.auth import require_role
from app.models import User, CandidateProfile, Certification
from app.schemas.CertificationSchema import CertificationCreate, CertificationResponse, CertificationUpdate
from app.models.user import UserRole
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(prefix="/certifications", tags=["Certification"])

#  Create Certification
@router.post("",response_model=CertificationResponse,status_code=status.HTTP_201_CREATED)
def create_certification(certification_data: CertificationCreate,current_user: User = Depends(require_role(UserRole.CANDIDATE)),db:Session=Depends(get_db)):
    candidate_profile = db.scalar(select(CandidateProfile).where(CandidateProfile.user_id == current_user.id))
    if candidate_profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Candidate profile not found")
    certification_values=certification_data.model_dump() # model_dump() converts pydantic object to python dict
    if certification_values["credential_url"] is not None:
        certification_values["credential_url"]= str(certification_values["credential_url"])
    # Object created to store in database
    certification = Certification(**certification_values,candidate_profile_id=candidate_profile.id)
    try:
        db.add(certification)
        db.commit()
        db.refresh(certification)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Unable to save certification")
    return certification

# Get All Certifications

@router.get("",response_model=list[CertificationResponse])
def list_certifications(current_user: User = Depends(require_role(UserRole.CANDIDATE)),db: Session = Depends(get_db)):
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

    certifications = db.scalars(
        select(Certification)
        .where(
            Certification.candidate_profile_id == candidate_profile.id
        )
        .order_by(
            Certification.issue_date.desc(),
            Certification.id.desc(),
        )
    ).all()

    return certifications

# Get certification by ID
@router.get("/{certification_id}",response_model=CertificationResponse)
def get_certification(certification_id: int,current_user: User = Depends(require_role(UserRole.CANDIDATE)),db: Session = Depends(get_db)):
    candidate_profile = db.scalar(
        select(CandidateProfile).where(
            CandidateProfile.user_id == current_user.id
        )
    )

    if candidate_profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Candidate profile not found")
    
    certification = db.scalar(
        select(Certification).where(
            Certification.id == certification_id,
            Certification.candidate_profile_id == candidate_profile.id,
        )
    )

    if certification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Certification not found")

    return certification

# Update certification by ID
@router.patch("/{certification_id}",response_model=CertificationResponse)
def update_certification(certification_id: int,certification_data: CertificationUpdate,current_user: User = Depends(require_role(UserRole.CANDIDATE)),db: Session = Depends(get_db)):
    candidate_profile = db.scalar(
        select(CandidateProfile).where(
            CandidateProfile.user_id == current_user.id
        )
    )

    if candidate_profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Candidate profile not found")
    
    certification = db.scalar(
        select(Certification).where(
            Certification.id == certification_id,
            Certification.candidate_profile_id == candidate_profile.id,
        )
    )

    if certification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Certification not found")

    update_data = certification_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="No fields provided for update")

    if "credential_url" in update_data and update_data["credential_url"] is not None:
        update_data["credential_url"] = str(update_data["credential_url"])

    # These fields cannot explicitily null
    for fields in ("certification_name", "issuing_organization","issue_date","does_not_expire"):

        if fields in update_data and update_data[fields] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{fields} cannot be null",
            )
    
    updated_issue_date = update_data.get(
        "issue_date", certification.issue_date
    )
    updated_expiration_date = update_data.get(
        "expiration_date", certification.expiration_date
    )
    updated_does_not_expire = update_data.get(
        "does_not_expire", certification.does_not_expire
    )
    if updated_expiration_date and updated_does_not_expire is not None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Expiration date must be empty when certification does not expire"
        )
    if updated_expiration_date is not None and updated_expiration_date < updated_issue_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Expiration date cannot be earlier than issue date",
        ) 
    for field,value in update_data.items():
        setattr(certification,field,value)
    
    try:
        db.commit()
        db.refresh(certification)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Unable to update certification")
    return certification

# Delete certification by ID
@router.delete("/{certification_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_certification(certification_id: int,current_user: User = Depends(require_role(UserRole.CANDIDATE)),db: Session = Depends(get_db)):
    candidate_profile = db.scalar(
        select(CandidateProfile).where(
            CandidateProfile.user_id == current_user.id
        )
    )
    if candidate_profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Candidate profile not found")
    
    certification = db.scalar(
        select(Certification).where(
            Certification.id == certification_id,
            Certification.candidate_profile_id == candidate_profile.id,
        )
    )

    if certification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Certification not found")

    try:
        db.delete(certification)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Unable to delete certification")
    return None