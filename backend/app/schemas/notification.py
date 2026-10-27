from datetime import datetime
from pydantic import BaseModel,Field,ConfigDict
from app.models.notification import NotificationType
class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    type: NotificationType
    title: str
    message: str
    application_id: int | None
    interview_id: int | None
    is_read: bool
    created_at: datetime
    read_at: datetime | None
