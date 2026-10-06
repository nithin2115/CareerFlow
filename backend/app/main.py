from fastapi import FastAPI, Depends
from app.core.database import get_db
from app.routers.auth import router as auth_router
from app.routers.auth import router as users_router
from app.routers.candidate_profile import router as candidate_profile_router
from app.routers.resumes import router as resumes_router
from app.core.auth import get_current_user
from app.core.auth import  require_role
from app.models.user import UserRole
#from sqlalchemy import func, select
#from app.models.user import User
from app.models import User, CandidateProfile, Resume
app=FastAPI()
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(candidate_profile_router)
app.include_router(resumes_router)
@app.get("/")
def root():
    return {"message": "Welcome to CareerFlow Backend!"}
'''@app.get("/test-auth")
def test_auth(current_user=Depends(get_current_user)):
    return current_use'''

'''@app.get("/test-recruiter")
def test_recruiter(
    current_user=Depends(require_role(UserRole.RECRUITER)),
):
    return {
        "message": "Recruiter access granted",
        "username": current_user.username,
        "role": current_user.role.value,
    }'''