from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas import TalkStarterRequest, TalkStarterResponse
from app.services import friend_service, interaction_service, llm_service, token_service
from app.metrics import talk_starters_generated, tokens_consumed, free_trial_used

router = APIRouter(prefix="/api/v1/talk-starters", tags=["talk-starters"])


def get_device_id(x_device_id: Optional[str] = Header(None)) -> str:
    """Extract device ID from header."""
    if not x_device_id:
        raise HTTPException(status_code=400, detail="X-Device-Id header required")
    return x_device_id


@router.post("", response_model=TalkStarterResponse)
async def generate_talk_starters(
    request: TalkStarterRequest,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db)
):
    """Generate AI-powered conversation starters for a friend."""
    # Check tokens
    if not token_service.can_generate(db, device_id):
        raise HTTPException(
            status_code=402,
            detail={
                "error": "No generations remaining. Please purchase more.",
                "code": "payment_required"
            }
        )
    
    # Get friend
    friend = friend_service.get_friend(db, request.friend_id, device_id)
    if not friend:
        raise HTTPException(status_code=404, detail="Friend not found")
    
    # Get interaction context
    context = interaction_service.get_interaction_context(db, friend.id)
    
    # Generate starters
    starters = await llm_service.generate_talk_starters(
        friend_name=friend.name,
        relation_type=friend.relation_type.value,
        interaction_context=context,
        language=request.language
    )
    
    # Consume token
    tokens_remaining, free_remaining = token_service.get_token_status(db, device_id)
    if tokens_remaining > 0:
        tokens_consumed.labels(tool="friend-keeper").inc()
    else:
        free_trial_used.labels(tool="friend-keeper").inc()
    
    token_service.use_generation(db, device_id)
    talk_starters_generated.labels(tool="friend-keeper").inc()
    
    return TalkStarterResponse(
        starters=starters,
        context_used=context[:200] + "..." if len(context) > 200 else context
    )
