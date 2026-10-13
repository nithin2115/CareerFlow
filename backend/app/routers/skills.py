
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from app.core.auth import require_role
from app.core.database import get_db
from app.models import CandidateProfile, Skill, User
from app.models.user import UserRole
from app.schemas import SkillCreate, SkillResponse, SkillUpdate

router = APIRouter(prefix="/skills", tags=["Skills"])

@router.post("",response_model=SkillResponse,status_code=status.HTTP_201_CREATED)
def create_skill(skill_data: SkillCreate,current_user: User = Depends(require_role(UserRole.CANDIDATE)),db: Session = Depends(get_db),):
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

    existing_skill = db.scalar(
        select(Skill).where(
            Skill.candidate_profile_id == candidate_profile.id,
            func.lower(Skill.skill_name)
            == skill_data.skill_name.lower(),
        )
    )

    if existing_skill is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This skill already exists in your profile",
        )

    skill = Skill(
        **skill_data.model_dump(),
        candidate_profile_id=candidate_profile.id,
    )

    try:
        db.add(skill)
        db.commit()
        db.refresh(skill)
        return skill

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The skill conflicts with an existing record",
        )

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create skill",
        )


@router.get("",response_model=list[SkillResponse])
def list_skills(
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

    skills = db.scalars(
        select(Skill)
        .where(
            Skill.candidate_profile_id == candidate_profile.id
        )
        .order_by(Skill.skill_name.asc(), Skill.id.asc())
    ).all()

    return list(skills)

@router.get("/{skill_id}",response_model=SkillResponse)
def get_skill(
    skill_id: int,
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

    skill = db.scalar(
        select(Skill).where(
            Skill.id == skill_id,
            Skill.candidate_profile_id == candidate_profile.id,
        )
    )

    if skill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )

    return skill

@router.patch("/{skill_id}",response_model=SkillResponse)
def update_skill(
    skill_id: int,
    skill_data: SkillUpdate,
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

    skill = db.scalar(
        select(Skill).where(
            Skill.id == skill_id,
            Skill.candidate_profile_id == candidate_profile.id,
        )
    )

    if skill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )

    update_data = skill_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    if "skill_name" in update_data:
        if update_data["skill_name"] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Skill name cannot be null",
            )

        existing_skill = db.scalar(
            select(Skill).where(
                Skill.candidate_profile_id == candidate_profile.id,
                func.lower(Skill.skill_name)
                == update_data["skill_name"].lower(),
                Skill.id != skill.id,
            )
        )

        if existing_skill is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This skill already exists in your profile",
            )

    for field, value in update_data.items():
        setattr(skill, field, value)

    try:
        db.commit()
        db.refresh(skill)
        return skill

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The skill conflicts with an existing record",
        )

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update skill",
        )

@router.delete("/{skill_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(
    skill_id: int,
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

    skill = db.scalar(
        select(Skill).where(
            Skill.id == skill_id,
            Skill.candidate_profile_id == candidate_profile.id,
        )
    )

    if skill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )

    try:
        db.delete(skill)
        db.commit()
        return None

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete skill",
        )
    return {"message": "Skills deleted successfully."}
