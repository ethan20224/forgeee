"""Subscription service — sync state from RevenueCat/Stripe webhooks."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.database.models import User
from src.subscriptions.schemas import SubscriptionStatusResponse

TIER_MAPPING = {
    "forge_pro_monthly": "pro",
    "forge_pro_annual": "pro",
    "forge_premium_monthly": "premium",
    "forge_premium_annual": "premium",
}


async def get_subscription_status(
    user_id: uuid.UUID, db: AsyncSession
) -> SubscriptionStatusResponse:
    """Get the current subscription status for a user."""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one()

    is_active = _is_subscription_active(user)

    return SubscriptionStatusResponse(
        tier=user.subscription_tier,
        provider=user.subscription_provider,
        expires_at=user.subscription_expires_at,
        is_active=is_active,
        can_access_premium=is_active and user.subscription_tier in ("pro", "premium"),
    )


async def sync_revenuecat_event(
    app_user_id: str,
    event_type: str,
    product_id: str | None,
    expiration_at_ms: int | None,
    db: AsyncSession,
) -> bool:
    """
    Process a RevenueCat webhook event.

    Returns True if the user was found and updated.
    """
    try:
        user_id = uuid.UUID(app_user_id)
    except ValueError:
        return False

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        return False

    if event_type in ("INITIAL_PURCHASE", "RENEWAL", "PRODUCT_CHANGE"):
        tier = TIER_MAPPING.get(product_id or "", "pro")
        user.subscription_tier = tier
        user.subscription_provider = "revenuecat"
        if expiration_at_ms:
            user.subscription_expires_at = datetime.fromtimestamp(
                expiration_at_ms / 1000, tz=UTC
            )

    elif event_type in ("CANCELLATION", "EXPIRATION"):
        user.subscription_tier = "none"
        user.subscription_expires_at = None

    await db.commit()
    return True


async def sync_stripe_event(
    event_type: str,
    data_object: dict,
    db: AsyncSession,
) -> bool:
    """
    Process a Stripe webhook event.

    Returns True if the user was found and updated.
    """
    metadata = data_object.get("metadata", {})
    user_id_str = metadata.get("user_id")
    if not user_id_str:
        customer_email = data_object.get("customer_email") or data_object.get(
            "customer_details", {}
        ).get("email")
        if customer_email:
            stmt = select(User).where(User.email == customer_email)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
        else:
            return False
    else:
        try:
            uid = uuid.UUID(user_id_str)
        except ValueError:
            return False
        stmt = select(User).where(User.id == uid)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

    if user is None:
        return False

    if event_type in ("checkout.session.completed", "invoice.paid"):
        user.subscription_tier = "pro"
        user.subscription_provider = "stripe"
        period_end = data_object.get("current_period_end")
        if period_end:
            user.subscription_expires_at = datetime.fromtimestamp(period_end, tz=UTC)

    elif event_type == "customer.subscription.deleted":
        user.subscription_tier = "none"
        user.subscription_expires_at = None

    await db.commit()
    return True


def validate_revenuecat_secret(authorization: str | None) -> bool:
    """Validate RevenueCat webhook authorization header."""
    settings = get_settings()
    if not settings.revenuecat_webhook_secret:
        return True
    expected = f"Bearer {settings.revenuecat_webhook_secret}"
    return authorization == expected


def _is_subscription_active(user: User) -> bool:
    """Check if subscription is currently active."""
    if user.subscription_tier == "none":
        return False
    if user.subscription_expires_at is None:
        return True
    return user.subscription_expires_at > datetime.now(UTC)


"""
=== FILE FLOW DOCUMENTATION ===

Functionality: Subscription state management via RevenueCat and Stripe webhooks.

Flow:
1. get_subscription_status() — reads user's current tier/expiry
2. sync_revenuecat_event() — processes RC webhook, updates tier on purchase/cancel
3. sync_stripe_event() — processes Stripe webhook, updates tier on checkout/cancel
4. validate_revenuecat_secret() — verifies webhook auth header

Main Entry Point: sync_revenuecat_event, sync_stripe_event, get_subscription_status

Dependencies:
- src.database.models: User model
- src.config: webhook secrets
"""
