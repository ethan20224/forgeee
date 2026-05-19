import pytest
from httpx import AsyncClient

SIGNUP_URL = "/api/v1/auth/signup"
QUIZ_URL = "/api/v1/quiz/submit"
GENERATE_URL = "/api/v1/plans/generate"
CURRENT_URL = "/api/v1/plans/current"

VALID_QUIZ = {
    "goals": ["skin", "hair", "posture"],
    "routine_level": "basic",
    "daily_time": "30min",
    "timeline": "90days",
    "main_concern": "skin",
    "age_range": "25-29",
    "has_photo": False,
}


async def _setup_user(client: AsyncClient, email: str = "plan@forge.app") -> dict:
    """Sign up and submit quiz, return auth headers."""
    resp = await client.post(
        SIGNUP_URL,
        json={"email": email, "password": "securepass123", "name": "Plan User"},
    )
    assert resp.status_code == 201
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post(QUIZ_URL, json=VALID_QUIZ, headers=headers)
    assert resp.status_code == 201
    return headers


@pytest.mark.asyncio
async def test_generate_plan_simulation(client):
    """AI_SIMULATION=true should return a mock plan."""
    headers = await _setup_user(client)
    resp = await client.post(GENERATE_URL, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert "plan" in data
    assert data["from_cache"] is False
    plan = data["plan"]
    assert plan["program_name"] == "Foundation Builder (Mock)"
    assert len(plan["daily_tasks"]) >= 90 * 3


@pytest.mark.asyncio
async def test_generate_plan_creates_tasks(client):
    """Generated plan should have daily tasks with correct fields."""
    headers = await _setup_user(client)
    resp = await client.post(GENERATE_URL, headers=headers)
    plan = resp.json()["plan"]
    task = plan["daily_tasks"][0]
    assert "title" in task
    assert "pillar" in task
    assert "tier" in task
    assert "day_number" in task
    assert "xp_value" in task
    assert task["is_completed"] is False


@pytest.mark.asyncio
async def test_plan_cache_hit(client):
    """Second generate with same quiz should hit cache."""
    headers = await _setup_user(client, email="cache@forge.app")
    resp1 = await client.post(GENERATE_URL, headers=headers)
    assert resp1.status_code == 201
    assert resp1.json()["from_cache"] is False

    resp2 = await client.post(GENERATE_URL, headers=headers)
    assert resp2.status_code == 201
    assert resp2.json()["from_cache"] is True


@pytest.mark.asyncio
async def test_get_current_plan(client):
    """After generating, GET /current should return the plan."""
    headers = await _setup_user(client, email="current@forge.app")
    await client.post(GENERATE_URL, headers=headers)
    resp = await client.get(CURRENT_URL, headers=headers)
    assert resp.status_code == 200
    assert "daily_tasks" in resp.json()


@pytest.mark.asyncio
async def test_get_current_plan_404_without_plan(client):
    """GET /current without generating should 404."""
    resp = await client.post(
        SIGNUP_URL,
        json={
            "email": "noplan@forge.app",
            "password": "securepass123",
            "name": "No Plan",
        },
    )
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.get(CURRENT_URL, headers=headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_plan_by_id(client):
    """GET /{plan_id} should return the specific plan."""
    headers = await _setup_user(client, email="byid@forge.app")
    resp = await client.post(GENERATE_URL, headers=headers)
    plan_id = resp.json()["plan"]["id"]
    resp = await client.get(f"/api/v1/plans/{plan_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == plan_id


@pytest.mark.asyncio
async def test_get_plan_wrong_user(client):
    """Cannot access another user's plan."""
    headers_a = await _setup_user(client, email="usera@forge.app")
    resp = await client.post(GENERATE_URL, headers=headers_a)
    plan_id = resp.json()["plan"]["id"]

    resp_b = await client.post(
        SIGNUP_URL,
        json={
            "email": "userb@forge.app",
            "password": "securepass123",
            "name": "B",
        },
    )
    headers_b = {"Authorization": f"Bearer {resp_b.json()['access_token']}"}
    resp = await client.get(f"/api/v1/plans/{plan_id}", headers=headers_b)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_generate_without_quiz(client):
    """Generate without quiz submission should 400."""
    resp = await client.post(
        SIGNUP_URL,
        json={
            "email": "noquiz-plan@forge.app",
            "password": "securepass123",
            "name": "No Quiz",
        },
    )
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.post(GENERATE_URL, headers=headers)
    assert resp.status_code == 400
