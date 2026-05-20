"""Pydantic schemas for subscription webhooks and status."""

from datetime import datetime

from pydantic import BaseModel


class SubscriptionStatusResponse(BaseModel):
    """Current subscription status for the user."""

    tier: str
    provider: str
    expires_at: datetime | None = None
    is_active: bool
    can_access_premium: bool


# ---------------------------------------------------------------------------
# RevenueCat Webhook Payload
# ---------------------------------------------------------------------------


class RevenueCatEvent(BaseModel):
    """Simplified RevenueCat webhook event."""

    type: str
    app_user_id: str
    product_id: str | None = None
    expiration_at_ms: int | None = None
    environment: str | None = None


class RevenueCatWebhook(BaseModel):
    """RevenueCat webhook envelope."""

    event: RevenueCatEvent


# ---------------------------------------------------------------------------
# Stripe Webhook (simplified — real validation uses raw body)
# ---------------------------------------------------------------------------


class StripeSubscriptionData(BaseModel):
    """Stripe subscription object (subset of fields)."""

    id: str
    customer: str
    status: str
    current_period_end: int | None = None
    metadata: dict | None = None


class StripeEventData(BaseModel):
    """Stripe event data.object wrapper."""

    object: dict


class StripeEvent(BaseModel):
    """Stripe webhook event."""

    id: str
    type: str
    data: StripeEventData
