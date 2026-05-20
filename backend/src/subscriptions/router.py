"""API routes for subscription status and webhooks."""

import hashlib
import hmac

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.config import get_settings
from src.database.connection import get_db
from src.database.models import User
from src.subscriptions.schemas import (
    RevenueCatWebhook,
    SubscriptionStatusResponse,
)
from src.subscriptions.service import (
    get_subscription_status,
    sync_revenuecat_event,
    sync_stripe_event,
    validate_revenuecat_secret,
)

router = APIRouter(prefix="/api/v1/subscriptions", tags=["subscriptions"])


@router.get("/status", response_model=SubscriptionStatusResponse)
async def subscription_status(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current subscription status."""
    return await get_subscription_status(user.id, db)


@router.post("/webhooks/revenuecat")
async def revenuecat_webhook(
    payload: RevenueCatWebhook,
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Handle RevenueCat subscription webhook."""
    if not validate_revenuecat_secret(authorization):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook secret",
        )

    event = payload.event
    success = await sync_revenuecat_event(
        app_user_id=event.app_user_id,
        event_type=event.type,
        product_id=event.product_id,
        expiration_at_ms=event.expiration_at_ms,
        db=db,
    )

    return {"processed": success}


@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Handle Stripe subscription webhook."""
    settings = get_settings()

    body = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    if settings.stripe_webhook_secret and not _verify_stripe_signature(
        body, sig_header, settings.stripe_webhook_secret
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature",
        )

    import json

    payload = json.loads(body)
    event_type = payload.get("type", "")
    data_object = payload.get("data", {}).get("object", {})

    success = await sync_stripe_event(event_type, data_object, db)
    return {"processed": success}


def _verify_stripe_signature(payload: bytes, sig_header: str, secret: str) -> bool:
    """Simplified Stripe signature verification (v1 scheme)."""
    if not sig_header:
        return False

    parts = {}
    for item in sig_header.split(","):
        if "=" in item:
            k, v = item.split("=", 1)
            parts[k.strip()] = v.strip()

    timestamp = parts.get("t", "")
    signature = parts.get("v1", "")

    if not timestamp or not signature:
        return False

    signed_payload = f"{timestamp}.".encode() + payload
    expected = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()

    return hmac.compare_digest(expected, signature)
