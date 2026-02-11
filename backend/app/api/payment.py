from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import json
import hmac
import hashlib
import httpx

from app.database import get_db
from app.models import PaymentTransaction
from app.schemas import CheckoutRequest, CheckoutResponse, TokenStatus
from app.services import token_service
from app.config import get_settings
from app.metrics import payment_success, payment_revenue_cents

router = APIRouter(prefix="/api/v1", tags=["payment"])

# Product configuration
PRODUCTS = {
    "starter": {"tokens": 10, "price_cents": 499},
    "popular": {"tokens": 30, "price_cents": 999},
    "pro": {"tokens": 100, "price_cents": 2499}
}


def get_device_id(x_device_id: Optional[str] = Header(None)) -> str:
    """Extract device ID from header."""
    if not x_device_id:
        raise HTTPException(status_code=400, detail="X-Device-Id header required")
    return x_device_id


@router.get("/tokens", response_model=TokenStatus)
def get_tokens(
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db)
):
    """Get current token status."""
    tokens_remaining, free_remaining = token_service.get_token_status(db, device_id)
    return TokenStatus(
        tokens_remaining=tokens_remaining,
        free_trial_remaining=free_remaining
    )


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    request: CheckoutRequest,
    db: Session = Depends(get_db)
):
    """Create a Creem checkout session."""
    settings = get_settings()
    
    if not settings.creem_api_key:
        raise HTTPException(status_code=500, detail="Payment not configured")
    
    if request.product_sku not in PRODUCTS:
        raise HTTPException(status_code=400, detail="Invalid product")
    
    # Parse product IDs from config
    try:
        product_ids = json.loads(settings.creem_product_ids)
    except json.JSONDecodeError:
        product_ids = {}
    
    creem_product_id = product_ids.get(request.product_sku)
    if not creem_product_id:
        raise HTTPException(status_code=500, detail="Product not configured in Creem")
    
    # Create Creem checkout
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.creem.io/v1/checkouts",
                headers={
                    "x-api-key": settings.creem_api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "product_id": creem_product_id,
                    "success_url": request.success_url,
                    "metadata": {
                        "device_id": request.device_id,
                        "product_sku": request.product_sku
                    }
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # Store pending transaction
            transaction = PaymentTransaction(
                device_id=request.device_id,
                creem_checkout_id=data.get("id"),
                product_sku=request.product_sku,
                tokens_granted=PRODUCTS[request.product_sku]["tokens"],
                amount_cents=PRODUCTS[request.product_sku]["price_cents"],
                status="pending"
            )
            db.add(transaction)
            db.commit()
            
            return CheckoutResponse(
                checkout_url=data.get("checkout_url"),
                checkout_id=data.get("id")
            )
            
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=500, detail=f"Payment provider error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Checkout failed: {str(e)}")


@router.post("/webhook/creem")
async def creem_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Creem payment webhooks."""
    settings = get_settings()
    
    # Verify webhook signature
    signature = request.headers.get("creem-signature")
    body = await request.body()
    
    if settings.creem_webhook_secret and signature:
        expected_sig = hmac.new(
            settings.creem_webhook_secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_sig):
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    event_type = payload.get("event_type")
    
    if event_type == "checkout.completed":
        checkout_data = payload.get("object", {})
        checkout_id = checkout_data.get("id")
        metadata = checkout_data.get("metadata", {})
        
        device_id = metadata.get("device_id")
        product_sku = metadata.get("product_sku")
        
        if not device_id or not product_sku:
            return {"status": "missing metadata"}
        
        # Find and update transaction
        transaction = db.query(PaymentTransaction).filter(
            PaymentTransaction.creem_checkout_id == checkout_id
        ).first()
        
        if transaction:
            transaction.status = "completed"
            transaction.completed_at = datetime.utcnow()
            
            # Grant tokens
            token_service.add_tokens(db, device_id, transaction.tokens_granted)
            
            # Record metrics
            payment_success.labels(tool="friend-keeper", product_sku=product_sku).inc()
            payment_revenue_cents.labels(tool="friend-keeper").inc(transaction.amount_cents)
            
            db.commit()
        
        return {"status": "ok"}
    
    return {"status": "ignored"}
