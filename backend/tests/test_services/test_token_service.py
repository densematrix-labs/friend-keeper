import pytest

from app.services.token_service import (
    get_or_create_token,
    get_token_status,
    can_generate,
    use_generation,
    add_tokens
)


class TestTokenService:
    """Test token service."""
    
    def test_get_or_create_new(self, db):
        """Test creating a new token record."""
        token = get_or_create_token(db, "new-device")
        assert token.device_id == "new-device"
        assert token.tokens_remaining == 0
        assert token.free_trial_used == 0
    
    def test_get_or_create_existing(self, db):
        """Test getting existing token record."""
        token1 = get_or_create_token(db, "device-1")
        token1.tokens_remaining = 5
        db.commit()
        
        token2 = get_or_create_token(db, "device-1")
        assert token2.tokens_remaining == 5
        assert token1.id == token2.id
    
    def test_token_status_new_device(self, db):
        """Test token status for new device."""
        tokens, free = get_token_status(db, "new-device")
        assert tokens == 0
        assert free == 3  # Default free trial count
    
    def test_can_generate_with_free_trial(self, db):
        """Test can generate with free trial available."""
        assert can_generate(db, "new-device") is True
    
    def test_can_generate_with_tokens(self, db):
        """Test can generate with paid tokens."""
        add_tokens(db, "device-1", 10)
        assert can_generate(db, "device-1") is True
    
    def test_cannot_generate_exhausted(self, db):
        """Test cannot generate when exhausted."""
        # Use all free trials
        for _ in range(3):
            use_generation(db, "device-1")
        
        assert can_generate(db, "device-1") is False
    
    def test_use_generation_free_trial(self, db):
        """Test using free trial."""
        result = use_generation(db, "device-1")
        assert result is True
        
        token = get_or_create_token(db, "device-1")
        assert token.free_trial_used == 1
    
    def test_use_generation_paid_tokens(self, db):
        """Test using paid tokens (priority over free trial)."""
        add_tokens(db, "device-1", 5)
        
        result = use_generation(db, "device-1")
        assert result is True
        
        token = get_or_create_token(db, "device-1")
        assert token.tokens_remaining == 4
        assert token.free_trial_used == 0  # Paid tokens used first
    
    def test_use_generation_fails_exhausted(self, db):
        """Test use generation fails when exhausted."""
        for _ in range(3):
            use_generation(db, "device-1")
        
        result = use_generation(db, "device-1")
        assert result is False
    
    def test_add_tokens(self, db):
        """Test adding tokens."""
        new_total = add_tokens(db, "device-1", 10)
        assert new_total == 10
        
        new_total = add_tokens(db, "device-1", 5)
        assert new_total == 15
