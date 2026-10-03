
from app.models.user import UserRole
from fastapi import Depends,HTTPException
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
import jwt
from app.core.jwt import JWT_SECRET_KEY , JWT_ALGORITHM
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
security=HTTPBearer()
def get_token(token:HTTPAuthorizationCredentials = Depends(security)):
    return token.credentials # this is what i return after decoding jwt token extracted from header
def get_current_user(token: str = Depends(get_token),db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401,detail="Invalid authentication token")

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(status_code=401,detail="Invalid token")
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=401,detail="Invalid user identity in token")
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=404,detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=403,detail="User account is inactive")

    return user
def require_role(required_role:UserRole):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(status_code=403,detail="Insufficient permissions")

        return current_user

    return role_checker



