import pytest
from datetime import datetime, timedelta

from app.services.friend_service import (
    get_frequency_days,
    calculate_health_status,
    get_friends,
    create_friend,
    update_friend,
    delete_friend,
    get_friends_needing_contact
)
from app.schemas import FriendCreate, FriendUpdate, ContactFrequency, RelationType


class TestFrequencyDays:
    """Test frequency to days conversion."""
    
    def test_weekly(self):
        assert get_frequency_days(ContactFrequency.WEEKLY) == 7
    
    def test_biweekly(self):
        assert get_frequency_days(ContactFrequency.BIWEEKLY) == 14
    
    def test_monthly(self):
        assert get_frequency_days(ContactFrequency.MONTHLY) == 30
    
    def test_quarterly(self):
        assert get_frequency_days(ContactFrequency.QUARTERLY) == 90


class TestHealthStatus:
    """Test health status calculation."""
    
    def test_no_interaction(self):
        status, days = calculate_health_status(None, ContactFrequency.WEEKLY)
        assert status == "red"
        assert days is None
    
    def test_recent_interaction_green(self):
        last = datetime.utcnow() - timedelta(days=2)
        status, days = calculate_health_status(last, ContactFrequency.WEEKLY)
        assert status == "green"
        assert days == 2
    
    def test_approaching_deadline_yellow(self):
        last = datetime.utcnow() - timedelta(days=6)
        status, days = calculate_health_status(last, ContactFrequency.WEEKLY)
        assert status == "yellow"
        assert days == 6
    
    def test_overdue_red(self):
        last = datetime.utcnow() - timedelta(days=10)
        status, days = calculate_health_status(last, ContactFrequency.WEEKLY)
        assert status == "red"
        assert days == 10


class TestFriendCRUD:
    """Test friend CRUD operations."""
    
    def test_create_friend(self, db):
        friend_data = FriendCreate(
            name="Test Friend",
            nickname="Testy",
            relation_type=RelationType.FRIEND,
            contact_frequency=ContactFrequency.WEEKLY
        )
        friend = create_friend(db, "device-1", friend_data)
        
        assert friend.id is not None
        assert friend.name == "Test Friend"
        assert friend.device_id == "device-1"
    
    def test_get_friends(self, db):
        # Create friends
        create_friend(db, "device-1", FriendCreate(name="Friend 1"))
        create_friend(db, "device-1", FriendCreate(name="Friend 2"))
        create_friend(db, "device-2", FriendCreate(name="Friend 3"))
        
        friends = get_friends(db, "device-1")
        assert len(friends) == 2
        
        friends = get_friends(db, "device-2")
        assert len(friends) == 1
    
    def test_update_friend(self, db):
        friend = create_friend(db, "device-1", FriendCreate(name="Old Name"))
        
        update_data = FriendUpdate(name="New Name")
        updated = update_friend(db, friend, update_data)
        
        assert updated.name == "New Name"
    
    def test_delete_friend(self, db):
        friend = create_friend(db, "device-1", FriendCreate(name="To Delete"))
        friend_id = friend.id
        
        delete_friend(db, friend)
        
        friends = get_friends(db, "device-1")
        assert all(f.id != friend_id for f in friends)


class TestFriendsNeedingContact:
    """Test finding friends that need contact."""
    
    def test_no_interactions_needs_contact(self, db):
        create_friend(db, "device-1", FriendCreate(name="Lonely Friend"))
        
        needs_contact = get_friends_needing_contact(db, "device-1")
        assert len(needs_contact) == 1
        assert needs_contact[0].name == "Lonely Friend"
