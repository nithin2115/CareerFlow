from app.core import database
from app.core import database
from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import RegisterRequest,RegisterResponse,LoginRequest,LoginResponse
from sqlalchemy import select
from app.models.user import User
from app.core.security import hash_password,verify_password
from app.core.jwt import create_access_token
from app.core.auth import get_current_user
from app.schemas.auth import UserResponse
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
@router.post("/login",response_model=LoginResponse)
def login(request: LoginRequest,db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == request.username)) # finding the user in db using username
    if not user:
        raise HTTPException(status_code=401,detail="Invalid username or password")
    if not verify_password(request.password, user.password_hash): # checking the password using verify_password() function
        raise HTTPException(status_code=401,detail="Invalid username or password")
    access_token=create_access_token({ # create jwt after password verification using payload contain user id and role
      "sub":str(user.id),
      "role":user.role.value
    })
    return LoginResponse(access_token=access_token, token_type="bearer") # retuning jwt token
router = APIRouter(
    prefix="/users",
    tags=["Users"],
)
@router.get("/me",response_model=UserResponse)
def get_my_profile(current_user:User=Depends(get_current_user)):
    return current_user
    