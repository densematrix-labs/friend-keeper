from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class ContactFrequency(str, enum.Enum):
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class RelationType(str, enum.Enum):
    FRIEND = "friend"
    FAMILY = "family"
    COLLEAGUE = "colleague"
    ACQUAINTANCE = "acquaintance"


class Friend(Base):
    __tablename__ = "friends"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(255), index=True, nullable=False)
    name = Column(String(255), nullable=False)
    nickname = Column(String(255), nullable=True)
    relation_type = Column(SQLEnum(RelationType), default=RelationType.FRIEND)
    contact_frequency = Column(SQLEnum(ContactFrequency), default=ContactFrequency.MONTHLY)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    interactions = relationship("Interaction", back_populates="friend", cascade="all, delete-orphan")


class Interaction(Base):
    __tablename__ = "interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    friend_id = Column(Integer, ForeignKey("friends.id"), nullable=False)
    contacted_at = Column(DateTime, default=datetime.utcnow)
    summary = Column(Text, nullable=True)
    next_topics = Column(Text, nullable=True)  # JSON array of topics
    created_at = Column(DateTime, default=datetime.utcnow)
    
    friend = relationship("Friend", back_populates="interactions")


class GenerationToken(Base):
    __tablename__ = "generation_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(255), unique=True, index=True, nullable=False)
    tokens_remaining = Column(Integer, default=0)
    free_trial_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(255), index=True, nullable=False)
    creem_checkout_id = Column(String(255), unique=True, nullable=True)
    product_sku = Column(String(100), nullable=False)
    tokens_granted = Column(Integer, nullable=False)
    amount_cents = Column(Integer, nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
