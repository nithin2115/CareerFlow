from fastapi import FastAPI, Depends
from app.core.database import get_db
from app.routers.auth import router as auth_router
from app.routers.auth import router as users_router
from app.core.auth import get_current_user
#from sqlalchemy import func, select
#from app.models.user import User
app=FastAPI()
app.include_router(auth_router)
app.include_router(users_router)

@app.get("/")
def root():
    return {"message": "Welcome to CareerFlow Backend!"}
@app.get("/test-auth")
def test_auth(current_user=Depends(get_current_user)):
    return current_user
'''@app.get("/db-test")    
def db_test(db=Depends(get_db)):
    user_count = db.scalar(
        select(func.count(User.id))
    )

    return {
        "message": "Database session is working",
        "user_count": user_count,
    }''' # seession communicate with postgresql testing donne