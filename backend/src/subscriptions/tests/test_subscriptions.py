"""Tests for subscription webhooks and status."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User

SIGNUP_URL = "/api/v1/auth/signup"
STATUS_URL = "/api/v1/subscriptions/status"
RC_WEBHOOK_URL = "/api/v1/subscriptions/webhooks/revenuecat"
STRIPE_WEBHOOK_URL = "/api/v1/subscriptions/webhooks/stripe"


async def _create_user(client: AsyncClient, db_session: AsyncSession) -> tuple[dict, User]:
    email = f"sub-test-{uuid.uuid4().hex[:8]}@forge.app"
    resp = await client.post(
        SIGNUP_URL,
        json={"email": email, "password": "securepass123", "name": "Sub Tester"},
    )
    assert resp.status_code == 201
    tokens = resp.json()

    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one()
    return tokens, user


def _auth(tokens: dict) -> dict:
    return {"Authorization": f"Bearer {tokens['access_token']}"}


class TestSubscriptionStatus:
    @pytest.mark.asyncio
    async def test_new_user_has_no_subscription(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        tokens, _ = await _create_user(client, db_session)
        resp = await client.get(STATUS_URL, headers=_auth(tokens))
        assert resp.status_code == 200
        data = resp.json()
        assert data["tier"] == "none"
        assert data["is_active"] is False
        assert data["can_access_premium"] is False

    @pytest.mark.asyncio
    async def test_active_subscription_shows_correctly(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        tokens, user = await _create_user(client, db_session)
        user.subscription_tier = "pro"
        user.subscription_expires_at = datetime.now(UTC) + timedelta(days=30)
        await db_session.flush()

        resp = await client.get(STATUS_URL, headers=_auth(tokens))
        data = resp.json()
        assert data["tier"] == "pro"
        assert data["is_active"] is True
        assert data["can_access_premium"] is True

    @pytest.mark.asyncio
    async def test_expired_subscription_is_inactive(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        tokens, user = await _create_user(client, db_session)
        user.subscription_tier = "pro"
        user.subscription_expires_at = datetime.now(UTC) - timedelta(days=1)
        await db_session.flush()

        resp = await client.get(STATUS_URL, headers=_auth(tokens))
        data = resp.json()
        assert data["is_active"] is False
        assert data["can_access_premium"] is False


class TestRevenueCatWebhook:
    @pytest.mark.asyncio
    async def test_initial_purchase_sets_tier(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        _, user = await _create_user(client, db_session)
        expiry_ms = int((datetime.now(UTC) + timedelta(days=30)).timestamp() * 1000)

        resp = await client.post(
            RC_WEBHOOK_URL,
            json={
                "event": {
                    "type": "INITIAL_PURCHASE",
                    "app_user_id": str(user.id),
                    "product_id": "forge_pro_monthly",
                    "expiration_at_ms": expiry_ms,
                }
            },
        )
        assert resp.status_code == 200
        assert resp.json()["processed"] is True

        await db_session.refresh(user)
        assert user.subscription_tier == "pro"

    @pytest.mark.asyncio
    async def test_cancellation_resets_tier(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        _, user = await _create_user(client, db_session)
        user.subscription_tier = "pro"
        user.subscription_expires_at = datetime.now(UTC) + timedelta(days=10)
        await db_session.flush()

        resp = await client.post(
            RC_WEBHOOK_URL,
            json={
                "event": {
                    "type": "CANCELLATION",
                    "app_user_id": str(user.id),
                    "product_id": "forge_pro_monthly",
                }
            },
        )
        assert resp.status_code == 200
        await db_session.refresh(user)
        assert user.subscription_tier == "none"

    @pytest.mark.asyncio
    async def test_unknown_user_returns_processed_false(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        resp = await client.post(
            RC_WEBHOOK_URL,
            json={
                "event": {
                    "type": "INITIAL_PURCHASE",
                    "app_user_id": str(uuid.uuid4()),
                    "product_id": "forge_pro_monthly",
                }
            },
        )
        assert resp.status_code == 200
        assert resp.json()["processed"] is False

    @pytest.mark.asyncio
    async def test_premium_product_sets_premium_tier(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        _, user = await _create_user(client, db_session)
        expiry_ms = int((datetime.now(UTC) + timedelta(days=365)).timestamp() * 1000)

        resp = await client.post(
            RC_WEBHOOK_URL,
            json={
                "event": {
                    "type": "INITIAL_PURCHASE",
                    "app_user_id": str(user.id),
                    "product_id": "forge_premium_annual",
                    "expiration_at_ms": expiry_ms,
                }
            },
        )
        assert resp.status_code == 200
        await db_session.refresh(user)
        assert user.subscription_tier == "premium"


class TestStripeWebhook:
    @pytest.mark.asyncio
    async def test_checkout_completed_sets_tier(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        _, user = await _create_user(client, db_session)
        period_end = int((datetime.now(UTC) + timedelta(days=30)).timestamp())

        resp = await client.post(
            STRIPE_WEBHOOK_URL,
            content=_stripe_payload(
                event_type="checkout.session.completed",
                user_id=str(user.id),
                period_end=period_end,
            ),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 200
        assert resp.json()["processed"] is True

        await db_session.refresh(user)
        assert user.subscription_tier == "pro"
        assert user.subscription_provider == "stripe"

    @pytest.mark.asyncio
    async def test_subscription_deleted_resets_tier(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        _, user = await _create_user(client, db_session)
        user.subscription_tier = "pro"
        user.subscription_provider = "stripe"
        await db_session.flush()

        resp = await client.post(
            STRIPE_WEBHOOK_URL,
            content=_stripe_payload(
                event_type="customer.subscription.deleted",
                user_id=str(user.id),
            ),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 200
        await db_session.refresh(user)
        assert user.subscription_tier == "none"


def _stripe_payload(
    event_type: str,
    user_id: str,
    period_end: int | None = None,
) -> bytes:
    import json

    payload = {
        "id": f"evt_{uuid.uuid4().hex[:16]}",
        "type": event_type,
        "data": {
            "object": {
                "id": f"sub_{uuid.uuid4().hex[:16]}",
                "customer": "cus_test",
                "status": "active",
                "metadata": {"user_id": user_id},
            }
        },
    }
    if period_end:
        payload["data"]["object"]["current_period_end"] = period_end
    return json.dumps(payload).encode()
