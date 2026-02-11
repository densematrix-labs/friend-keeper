from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas import (
    FriendCreate, FriendUpdate, FriendResponse, FriendDetailResponse,
    InteractionCreate, InteractionResponse, DashboardResponse
)
from app.services import friend_service, interaction_service

router = APIRouter(prefix="/api/v1/friends", tags=["friends"])


def get_device_id(x_device_id: Optional[str] = Header(None)) -> str:
    """Extract device ID from header."""
    if not x_device_id:
        raise HTTPException(status_code=400, detail="X-Device-Id header required")
    return x_device_id


@router.get("", response_model=List[FriendResponse])
def list_friends(
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db)
):
    """List all friends for the current device."""
    return friend_service.get_friends(db, device_id)


@router.post("", response_model=FriendResponse, status_code=201)
def create_friend(
    friend_data: FriendCreate,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db)
):
    """Create a new friend."""
    friend = friend_service.create_friend(db, device_id, friend_data)
    return friend_service.get_friends(db, device_id)[-1]  # Return with health status


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db)
):
    """Get friendship dashboard overview."""
    friends = friend_service.get_friends(db, device_id)
    
    need_today = [f for f in friends if f.health_status == "red"]
    need_week = [f for f in friends if f.health_status == "yellow"]
    healthy = len([f for f in friends if f.health_status == "green"])
    at_risk = len(need_today) + len(need_week)
    
    return DashboardResponse(
        total_friends=len(friends),
        need_contact_today=need_today[:5],
        need_contact_this_week=need_week[:5],
        healthy_friendships=healthy,
        at_risk_friendships=at_risk
    )


@router.get("/{friend_id}", response_model=FriendDetailResponse)
def get_friend(
    friend_id: int,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db)
):
    """Get a friend with interaction history."""
    friend = friend_service.get_friend(db, friend_id, device_id)
    if not friend:
        raise HTTPException(status_code=404, detail="Friend not found")
    
    # Get health status
    friends = friend_service.get_friends(db, device_id)
    friend_with_status = next((f for f in friends if f.id == friend_id), None)
    
    # Get interactions
    interactions = interaction_service.get_interactions(db, friend_id)
    interaction_responses = [
        interaction_service.interaction_to_response(i) for i in interactions
    ]
    
    return FriendDetailResponse(
        id=friend.id,
        name=friend.name,
        nickname=friend.nickname,
        relation_type=friend.relation_type,
        contact_frequency=friend.contact_frequency,
        notes=friend.notes,
        created_at=friend.created_at,
        updated_at=friend.updated_at,
        last_interaction=friend_with_status.last_interaction if friend_with_status else None,
        health_status=friend_with_status.health_status if friend_with_status else "unknown",
        days_since_contact=friend_with_status.days_since_contact if friend_with_status else None,
        interactions=interaction_responses
    )


@router.patch("/{friend_id}", response_model=FriendResponse)
def update_friend(
    friend_id: int,
    friend_data: FriendUpdate,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db)
):
    """Update a friend."""
    friend = friend_service.get_friend(db, friend_id, device_id)
    if not friend:
        raise HTTPException(status_code=404, detail="Friend not found")
    
    friend_service.update_friend(db, friend, friend_data)
    friends = friend_service.get_friends(db, device_id)
    return next((f for f in friends if f.id == friend_id), None)


@router.delete("/{friend_id}", status_code=204)
def delete_friend(
    friend_id: int,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db)
):
    """Delete a friend."""
    friend = friend_service.get_friend(db, friend_id, device_id)
    if not friend:
        raise HTTPException(status_code=404, detail="Friend not found")
    
    friend_service.delete_friend(db, friend)


@router.post("/{friend_id}/interactions", response_model=InteractionResponse, status_code=201)
def log_interaction(
    friend_id: int,
    interaction_data: InteractionCreate,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db)
):
    """Log a new interaction with a friend."""
    friend = friend_service.get_friend(db, friend_id, device_id)
    if not friend:
        raise HTTPException(status_code=404, detail="Friend not found")
    
    interaction = interaction_service.create_interaction(db, friend_id, interaction_data)
    return interaction_service.interaction_to_response(interaction)
