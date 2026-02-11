from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from app.models import Friend, Interaction, ContactFrequency
from app.schemas import FriendCreate, FriendUpdate, FriendResponse


def get_frequency_days(frequency: ContactFrequency) -> int:
    """Get the number of days for a contact frequency."""
    mapping = {
        ContactFrequency.WEEKLY: 7,
        ContactFrequency.BIWEEKLY: 14,
        ContactFrequency.MONTHLY: 30,
        ContactFrequency.QUARTERLY: 90,
    }
    return mapping.get(frequency, 30)


def calculate_health_status(last_interaction: Optional[datetime], frequency: ContactFrequency) -> Tuple[str, Optional[int]]:
    """Calculate friendship health status based on last interaction and target frequency."""
    if last_interaction is None:
        return "red", None
    
    days_since = (datetime.utcnow() - last_interaction).days
    target_days = get_frequency_days(frequency)
    
    if days_since <= target_days * 0.7:
        return "green", days_since
    elif days_since <= target_days:
        return "yellow", days_since
    else:
        return "red", days_since


def get_friends(db: Session, device_id: str) -> List[FriendResponse]:
    """Get all friends for a device with health status."""
    friends = db.query(Friend).filter(Friend.device_id == device_id).all()
    result = []
    
    for friend in friends:
        # Get last interaction
        last_interaction = db.query(func.max(Interaction.contacted_at)).filter(
            Interaction.friend_id == friend.id
        ).scalar()
        
        health_status, days_since = calculate_health_status(last_interaction, friend.contact_frequency)
        
        friend_response = FriendResponse(
            id=friend.id,
            name=friend.name,
            nickname=friend.nickname,
            relation_type=friend.relation_type,
            contact_frequency=friend.contact_frequency,
            notes=friend.notes,
            created_at=friend.created_at,
            updated_at=friend.updated_at,
            last_interaction=last_interaction,
            health_status=health_status,
            days_since_contact=days_since
        )
        result.append(friend_response)
    
    return result


def get_friend(db: Session, friend_id: int, device_id: str) -> Optional[Friend]:
    """Get a single friend by ID."""
    return db.query(Friend).filter(
        Friend.id == friend_id,
        Friend.device_id == device_id
    ).first()


def create_friend(db: Session, device_id: str, friend_data: FriendCreate) -> Friend:
    """Create a new friend."""
    friend = Friend(
        device_id=device_id,
        name=friend_data.name,
        nickname=friend_data.nickname,
        relation_type=friend_data.relation_type,
        contact_frequency=friend_data.contact_frequency,
        notes=friend_data.notes
    )
    db.add(friend)
    db.commit()
    db.refresh(friend)
    return friend


def update_friend(db: Session, friend: Friend, friend_data: FriendUpdate) -> Friend:
    """Update a friend."""
    update_data = friend_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(friend, key, value)
    db.commit()
    db.refresh(friend)
    return friend


def delete_friend(db: Session, friend: Friend) -> None:
    """Delete a friend."""
    db.delete(friend)
    db.commit()


def get_friends_needing_contact(db: Session, device_id: str, days_threshold: int = 0) -> List[FriendResponse]:
    """Get friends that need to be contacted (past their frequency threshold)."""
    friends = get_friends(db, device_id)
    result = []
    
    for friend in friends:
        target_days = get_frequency_days(friend.contact_frequency)
        if friend.days_since_contact is None or friend.days_since_contact >= target_days - days_threshold:
            result.append(friend)
    
    return sorted(result, key=lambda x: x.days_since_contact or 999, reverse=True)
