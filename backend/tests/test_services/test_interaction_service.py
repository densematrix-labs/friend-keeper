import pytest

from app.services.interaction_service import (
    get_interactions,
    create_interaction,
    get_interaction_context,
    interaction_to_response
)
from app.services.friend_service import create_friend
from app.schemas import FriendCreate, InteractionCreate


class TestInteractionService:
    """Test interaction service."""
    
    def test_create_interaction(self, db):
        """Test creating an interaction."""
        friend = create_friend(db, "device-1", FriendCreate(name="Test"))
        
        interaction_data = InteractionCreate(
            summary="Had coffee",
            next_topics=["Work project", "Vacation plans"]
        )
        interaction = create_interaction(db, friend.id, interaction_data)
        
        assert interaction.id is not None
        assert interaction.summary == "Had coffee"
        assert "Work project" in interaction.next_topics
    
    def test_create_interaction_minimal(self, db):
        """Test creating interaction with minimal data."""
        friend = create_friend(db, "device-1", FriendCreate(name="Test"))
        
        interaction = create_interaction(db, friend.id, InteractionCreate())
        
        assert interaction.id is not None
        assert interaction.summary is None
    
    def test_get_interactions(self, db):
        """Test getting interactions."""
        friend = create_friend(db, "device-1", FriendCreate(name="Test"))
        
        create_interaction(db, friend.id, InteractionCreate(summary="First"))
        create_interaction(db, friend.id, InteractionCreate(summary="Second"))
        create_interaction(db, friend.id, InteractionCreate(summary="Third"))
        
        interactions = get_interactions(db, friend.id, limit=2)
        assert len(interactions) == 2
        # Should be most recent first
        assert interactions[0].summary == "Third"
    
    def test_get_interaction_context(self, db):
        """Test getting interaction context for LLM."""
        friend = create_friend(db, "device-1", FriendCreate(name="Test"))
        
        create_interaction(
            db, friend.id,
            InteractionCreate(summary="Talked about work")
        )
        
        context = get_interaction_context(db, friend.id)
        assert "Talked about work" in context
    
    def test_get_interaction_context_empty(self, db):
        """Test context when no interactions."""
        friend = create_friend(db, "device-1", FriendCreate(name="Test"))
        
        context = get_interaction_context(db, friend.id)
        assert "No previous interactions" in context
    
    def test_interaction_to_response(self, db):
        """Test converting interaction to response."""
        friend = create_friend(db, "device-1", FriendCreate(name="Test"))
        
        interaction = create_interaction(
            db, friend.id,
            InteractionCreate(
                summary="Test",
                next_topics=["Topic 1", "Topic 2"]
            )
        )
        
        response = interaction_to_response(interaction)
        
        assert response.id == interaction.id
        assert response.summary == "Test"
        assert response.next_topics == ["Topic 1", "Topic 2"]
