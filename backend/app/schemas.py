from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ContactFrequency(str, Enum):
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class RelationType(str, Enum):
    FRIEND = "friend"
    FAMILY = "family"
    COLLEAGUE = "colleague"
    ACQUAINTANCE = "acquaintance"


# Friend schemas
class FriendCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    nickname: Optional[str] = Field(None, max_length=255)
    relation_type: RelationType = RelationType.FRIEND
    contact_frequency: ContactFrequency = ContactFrequency.MONTHLY
    notes: Optional[str] = None


class FriendUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    nickname: Optional[str] = Field(None, max_length=255)
    relation_type: Optional[RelationType] = None
    contact_frequency: Optional[ContactFrequency] = None
    notes: Optional[str] = None


class InteractionBase(BaseModel):
    summary: Optional[str] = None
    next_topics: Optional[List[str]] = None


class InteractionCreate(InteractionBase):
    pass


class InteractionResponse(InteractionBase):
    id: int
    friend_id: int
    contacted_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class FriendResponse(BaseModel):
    id: int
    name: str
    nickname: Optional[str]
    relation_type: RelationType
    contact_frequency: ContactFrequency
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_interaction: Optional[datetime] = None
    health_status: str = "unknown"  # green, yellow, red
    days_since_contact: Optional[int] = None
    
    class Config:
        from_attributes = True


class FriendDetailResponse(FriendResponse):
    interactions: List[InteractionResponse] = []


# Talk starter schemas
class TalkStarterRequest(BaseModel):
    friend_id: int
    language: str = "en"


class TalkStarterResponse(BaseModel):
    starters: List[str]
    context_used: str


# Token schemas
class TokenStatus(BaseModel):
    tokens_remaining: int
    free_trial_remaining: int


class CheckoutRequest(BaseModel):
    product_sku: str
    success_url: str
    device_id: str


class CheckoutResponse(BaseModel):
    checkout_url: str
    checkout_id: str


# Dashboard
class DashboardResponse(BaseModel):
    total_friends: int
    need_contact_today: List[FriendResponse]
    need_contact_this_week: List[FriendResponse]
    healthy_friendships: int
    at_risk_friendships: int
