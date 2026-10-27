from fastapi import APIRouter, Depends, Query,HTTPException
from sqlalchemy import select,func
from sqlalchemy.orm import Session
from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse
from datetime import datetime, timezone

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/me", response_model=list[NotificationResponse])
def get_my_notifications(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = (
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc(), Notification.id.desc())
        .offset(skip)
        .limit(limit)
    )

    notifications = db.scalars(statement).all()

    return notifications

#unread count

@router.get("/unread-count")
def get_unread_notification_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = (
        select(func.count(Notification.id))
        .where(
            Notification.user_id == current_user.id,
            Notification.is_read.is_(False),
        )
    )

    unread_count = db.scalar(statement)

    return {"unread_count": unread_count}

#mark as read
@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notification = db.scalar(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
    )

    if notification is None:
        raise HTTPException(
            status_code=404,
            detail="Notification not found",
        )

    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(notification)

    return notification

#mark all as read

@router.patch("/read-all")
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = select(Notification).where(
        Notification.user_id == current_user.id,
        Notification.is_read.is_(False),
    )

    notifications = db.scalars(statement).all()

    read_time = datetime.now(timezone.utc)

    for notification in notifications:
        notification.is_read = True
        notification.read_at = read_time

    db.commit()

    return {
        "message": "All notifications marked as read",
        "updated_count": len(notifications),
    }
