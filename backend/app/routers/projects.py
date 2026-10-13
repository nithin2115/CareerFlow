from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.candidate_profile import CandidateProfile
from app.models.project import Project
from app.models.user import User
from app.schemas.ProjectSchema import ProjectCreate, ProjectResponse , ProjectUpdate

router = APIRouter(prefix="/projects", tags=["Projects"])

#Create Project
@router.post("/",response_model=ProjectResponse,status_code=status.HTTP_201_CREATED)
def create_project(project_data: ProjectCreate,current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):
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

    project_values = project_data.model_dump()

    if project_values["repository_url"] is not None:
        project_values["repository_url"] = str(
            project_values["repository_url"]
        )

    if project_values["live_demo_url"] is not None:
        project_values["live_demo_url"] = str(
            project_values["live_demo_url"]
        )

    project = Project(
        **project_values,
        candidate_profile_id=candidate_profile.id,
    )

    try:
        db.add(project)
        db.commit()
        db.refresh(project)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create project.",
        )
    return project

#Get All Projects for the logged in user (candidate)
@router.get("/",response_model=list[ProjectResponse],status_code=status.HTTP_200_OK)
def list_projects(db: Session = Depends(get_db),current_user: User = Depends(get_current_user),):
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

    projects = db.scalars(
        select(Project)
        .where(Project.candidate_profile_id == candidate_profile.id)
        .order_by(Project.created_at.desc(), Project.id.desc())
    ).all()

    return projects

# Get specific project by id for the logged in user (candidate)
@router.get("/{project_id}", response_model=ProjectResponse,status_code=status.HTTP_200_OK)
def get_project(project_id: int,db: Session = Depends(get_db),current_user: User = Depends(get_current_user),):
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

    project = db.scalar(
        select(Project).where(
            Project.id == project_id,
            Project.candidate_profile_id == candidate_profile.id,
        )
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )
    return project

# Update specific project by id for the logged in user (candidate)
@router.patch("/{project_id}",response_model=ProjectResponse,status_code=status.HTTP_200_OK)
def update_project(project_id: int,project_data: ProjectUpdate,db: Session = Depends(get_db),current_user: User = Depends(get_current_user),):
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
    project = db.scalar(
        select(Project).where(
            Project.id == project_id,
            Project.candidate_profile_id == candidate_profile.id,
        )
    )
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    update_values = project_data.model_dump(exclude_unset=True) # if value is not provided exlude it 

    if not update_values: # if no value is provided error is raised
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide at least one field to update.",
        )
    if "project_name" in update_values and update_values["project_name"] is None: # if project name is null error raised
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Project name cannot be null.",
        )

    for field in ("repository_url", "live_demo_url"): # convert url to string
        if field in update_values and update_values[field] is not None:
            update_values[field] = str(update_values[field])

    final_start_date = update_values.get( # if start date is not provided take it from database
        "start_date", project.start_date
    )
    final_end_date = update_values.get( # if end date is not provided take it from database
        "end_date", project.end_date
    )
    final_is_ongoing = update_values.get( # if is_ongoing is not provided take it from database
        "is_ongoing", project.is_ongoing
    )
    if (final_start_date is not None and final_end_date is not None and final_end_date < final_start_date): # if end date is before start date error is raised
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, # bad request
            detail="End date cannot be earlier than start date.",
        )
    if final_is_ongoing and final_end_date is not None: # if ongoing is true and end date is not null error is raised
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Ongoing projects cannot have an end date.",
        )

    try:
        for field, value in update_values.items():
            setattr(project, field, value)

        db.commit()
        db.refresh(project)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update project.",
        )
    return project

#Delete specific project by id for the logged in user (candidate)
@router.delete("/{project_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int,db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    candidate_profile = db.scalar(
        select(CandidateProfile).where(
            CandidateProfile.user_id == current_user.id
        )
    )
    if candidate_profile is None: # if candidate profile is not found error is raised
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found.",
        )
    project = db.scalar(
        select(Project).where(
            Project.id == project_id,
            Project.candidate_profile_id == candidate_profile.id,
        )
    )
    if project is None: # if project is not found error is raised
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )
    try:
        db.delete(project)
        db.commit()
    except SQLAlchemyError: # if error occurs during deletion error is raised
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project.",
        )
    return {"message": "Project deleted successfully."}


