from sqlalchemy.orm import Session
from typing import Tuple

from app.models import GenerationToken
from app.config import get_settings


def get_or_create_token(db: Session, device_id: str) -> GenerationToken:
    """Get or create token record for a device."""
    token = db.query(GenerationToken).filter(
        GenerationToken.device_id == device_id
    ).first()
    
    if not token:
        token = GenerationToken(device_id=device_id)
        db.add(token)
        db.commit()
        db.refresh(token)
    
    return token


def get_token_status(db: Session, device_id: str) -> Tuple[int, int]:
    """Get token status: (tokens_remaining, free_trial_remaining)."""
    settings = get_settings()
    token = get_or_create_token(db, device_id)
    free_remaining = max(0, settings.free_trial_count - token.free_trial_used)
    return token.tokens_remaining, free_remaining


def can_generate(db: Session, device_id: str) -> bool:
    """Check if device can generate (has tokens or free trial)."""
    tokens_remaining, free_remaining = get_token_status(db, device_id)
    return tokens_remaining > 0 or free_remaining > 0


def use_generation(db: Session, device_id: str) -> bool:
    """Use one generation. Returns True if successful."""
    settings = get_settings()
    token = get_or_create_token(db, device_id)
    
    # Try paid tokens first
    if token.tokens_remaining > 0:
        token.tokens_remaining -= 1
        db.commit()
        return True
    
    # Try free trial
    if token.free_trial_used < settings.free_trial_count:
        token.free_trial_used += 1
        db.commit()
        return True
    
    return False


def add_tokens(db: Session, device_id: str, amount: int) -> int:
    """Add tokens to a device. Returns new total."""
    token = get_or_create_token(db, device_id)
    token.tokens_remaining += amount
    db.commit()
    return token.tokens_remaining
