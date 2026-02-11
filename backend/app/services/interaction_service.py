from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
import json

from app.models import Interaction, Friend
from app.schemas import InteractionCreate, InteractionResponse


def get_interactions(db: Session, friend_id: int, limit: int = 20) -> List[Interaction]:
    """Get interactions for a friend."""
    return db.query(Interaction).filter(
        Interaction.friend_id == friend_id
    ).order_by(Interaction.contacted_at.desc()).limit(limit).all()


def create_interaction(db: Session, friend_id: int, interaction_data: InteractionCreate) -> Interaction:
    """Create a new interaction."""
    # Convert next_topics list to JSON string if present
    next_topics_json = None
    if interaction_data.next_topics:
        next_topics_json = json.dumps(interaction_data.next_topics)
    
    interaction = Interaction(
        friend_id=friend_id,
        summary=interaction_data.summary,
        next_topics=next_topics_json,
        contacted_at=datetime.utcnow()
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


def get_interaction_context(db: Session, friend_id: int, limit: int = 5) -> str:
    """Get recent interaction context for AI talk starter generation."""
    interactions = get_interactions(db, friend_id, limit)
    
    if not interactions:
        return "No previous interactions recorded."
    
    context_parts = []
    for i, interaction in enumerate(interactions):
        date_str = interaction.contacted_at.strftime("%Y-%m-%d")
        summary = interaction.summary or "No summary"
        context_parts.append(f"- {date_str}: {summary}")
        
        if interaction.next_topics:
            try:
                topics = json.loads(interaction.next_topics)
                context_parts.append(f"  Topics to follow up: {', '.join(topics)}")
            except json.JSONDecodeError:
                pass
    
    return "\n".join(context_parts)


def interaction_to_response(interaction: Interaction) -> InteractionResponse:
    """Convert interaction model to response schema."""
    next_topics = None
    if interaction.next_topics:
        try:
            next_topics = json.loads(interaction.next_topics)
        except json.JSONDecodeError:
            next_topics = []
    
    return InteractionResponse(
        id=interaction.id,
        friend_id=interaction.friend_id,
        contacted_at=interaction.contacted_at,
        summary=interaction.summary,
        next_topics=next_topics,
        created_at=interaction.created_at
    )
