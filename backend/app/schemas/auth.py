from pydantic import BaseModel,Field,EmailStr,ConfigDict
class RegisterRequest(BaseModel): # Register
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
class LoginRequest(BaseModel): # Login
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)
class LoginResponse(BaseModel):
      access_token: str
      token_type: str
class UserResponse(BaseModel):# API Response from get_current_user for authenticated object
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    name: str
    email: EmailStr
    role: str
    is_active: bool