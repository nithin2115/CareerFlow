from app.core import database
from app.core import database
from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import RegisterRequest,RegisterResponse
from sqlalchemy import select
from app.models.user import User
from app.core.security import hash_password

router = APIRouter(prefix="/auth",tags=["Authentication"])
@router.post("/register",response_model=RegisterResponse)
def register(request: RegisterRequest,db: Session = Depends(get_db)):
  existing_username = db.scalar(select(User).where(User.username == request.username)) # checking username in db
  if existing_username:
    raise HTTPException(status_code = 409 , detail = "Username already registered") # send to client clear api response application check 
  existing_email = db.scalar(select(User).where(User.email == request.email)) # checking email in db
  if existing_email:
    raise HTTPException(status_code = 409 , detail = "Email already registered")# send to client
  user = User(  # user object created  to store in database
    username=request.username,
    name=request.name,
    email=request.email,
    password_hash=hash_password(request.password),
  )
  db.add(user)
  db.commit()
  return RegisterResponse(
    id=user.id,
    username=user.username,
    name=user.name,
    email=user.email,
    role=user.role.value,
    is_active=user.is_active,
)
