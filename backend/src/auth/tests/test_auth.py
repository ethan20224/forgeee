import pytest
from httpx import AsyncClient

SIGNUP_URL = "/api/v1/auth/signup"
LOGIN_URL = "/api/v1/auth/login"
REFRESH_URL = "/api/v1/auth/refresh"
ME_URL = "/api/v1/auth/me"
DELETE_URL = "/api/v1/auth/account"
ONBOARD_URL = "/api/v1/auth/complete-onboarding"


@pytest.fixture
def user_payload():
    return {
        "email": "test@forge.app",
        "password": "securepass123",
        "name": "Test User",
    }


async def _signup(client: AsyncClient, payload: dict) -> dict:
    resp = await client.post(SIGNUP_URL, json=payload)
    assert resp.status_code == 201
    return resp.json()


@pytest.mark.asyncio
async def test_signup_returns_tokens(client, user_payload):
    tokens = await _signup(client, user_payload)
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_signup_duplicate_email(client, user_payload):
    await _signup(client, user_payload)
    resp = await client.post(SIGNUP_URL, json=user_payload)
    assert resp.status_code == 409
    assert "already registered" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_signup_short_password(client):
    resp = await client.post(SIGNUP_URL, json={"email": "short@forge.app", "password": "abc"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_signup_invalid_email(client):
    resp = await client.post(
        SIGNUP_URL, json={"email": "not-an-email", "password": "securepass123"}
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client, user_payload):
    await _signup(client, user_payload)
    resp = await client.post(
        LOGIN_URL,
        json={"email": user_payload["email"], "password": user_payload["password"]},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client, user_payload):
    await _signup(client, user_payload)
    resp = await client.post(
        LOGIN_URL,
        json={"email": user_payload["email"], "password": "wrongpassword"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_email(client):
    resp = await client.post(
        LOGIN_URL,
        json={"email": "nobody@forge.app", "password": "securepass123"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client, user_payload):
    tokens = await _signup(client, user_payload)
    resp = await client.post(REFRESH_URL, json={"refresh_token": tokens["refresh_token"]})
    assert resp.status_code == 200
    new_tokens = resp.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens


@pytest.mark.asyncio
async def test_refresh_with_access_token_fails(client, user_payload):
    tokens = await _signup(client, user_payload)
    resp = await client.post(REFRESH_URL, json={"refresh_token": tokens["access_token"]})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_returns_user(client, user_payload):
    tokens = await _signup(client, user_payload)
    resp = await client.get(ME_URL, headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == user_payload["email"]
    assert data["name"] == user_payload["name"]
    assert data["program_day"] == 1
    assert data["season"] == 1
    assert data["onboarded"] is False
    assert data["subscription_tier"] == "none"


@pytest.mark.asyncio
async def test_me_without_token(client):
    resp = await client.get(ME_URL)
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_me_with_invalid_token(client):
    resp = await client.get(ME_URL, headers={"Authorization": "Bearer invalid.token.here"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_complete_onboarding(client, user_payload):
    tokens = await _signup(client, user_payload)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    resp = await client.post(ONBOARD_URL, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["onboarded"] is True
    assert data["program_day"] == 1

    resp_again = await client.post(ONBOARD_URL, headers=headers)
    assert resp_again.status_code == 200
    assert resp_again.json()["onboarded"] is True


@pytest.mark.asyncio
async def test_delete_account(client, user_payload):
    tokens = await _signup(client, user_payload)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    resp = await client.get(ME_URL, headers=headers)
    assert resp.status_code == 200

    resp = await client.delete(DELETE_URL, headers=headers)
    assert resp.status_code == 204

    resp = await client.get(ME_URL, headers=headers)
    assert resp.status_code == 401
