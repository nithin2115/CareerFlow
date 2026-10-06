from pydantic import BaseModel, ConfigDict

class ResumeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    candidate_profile_id: int
    original_filename: str
    file_type: str
    file_size: int
    version: int
    is_active: bool