from pydantic import BaseModel,Field,EmailStr
class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
class RegisterResponse(BaseModel): # what API is allowed to return 
    id: int
    username: str
    name: str
    email: EmailStr
    role: str
    is_active: bool
