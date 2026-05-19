import pytest
from httpx import AsyncClient

SIGNUP_URL = "/api/v1/auth/signup"
SUBMIT_URL = "/api/v1/quiz/submit"
ESTIMATE_URL = "/api/v1/quiz/estimate-score"


async def _auth_headers(client: AsyncClient, email: str = "quiz@forge.app") -> dict:
    resp = await client.post(
        SIGNUP_URL,
        json={"email": email, "password": "securepass123", "name": "Quiz User"},
    )
    assert resp.status_code == 201
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


VALID_QUIZ = {
    "goals": ["skin", "hair", "posture"],
    "routine_level": "basic",
    "daily_time": "30min",
    "timeline": "90days",
    "main_concern": "skin",
    "age_range": "25-29",
    "has_photo": True,
}


@pytest.mark.asyncio
async def test_submit_quiz_success(client):
    headers = await _auth_headers(client)
    resp = await client.post(SUBMIT_URL, json=VALID_QUIZ, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["goals"] == ["skin", "hair", "posture"]
    assert data["routine_level"] == "basic"
    assert data["has_photo"] is True
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_submit_quiz_invalid_routine(client):
    headers = await _auth_headers(client)
    bad = {**VALID_QUIZ, "routine_level": "godlike"}
    resp = await client.post(SUBMIT_URL, json=bad, headers=headers)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_submit_quiz_empty_goals(client):
    headers = await _auth_headers(client)
    bad = {**VALID_QUIZ, "goals": []}
    resp = await client.post(SUBMIT_URL, json=bad, headers=headers)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_submit_quiz_requires_auth(client):
    resp = await client.post(SUBMIT_URL, json=VALID_QUIZ)
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_estimate_score_after_quiz(client):
    headers = await _auth_headers(client)
    await client.post(SUBMIT_URL, json=VALID_QUIZ, headers=headers)
    resp = await client.get(ESTIMATE_URL, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["pillar_scores"]) == 9
    assert 0 <= data["optimisation_score"] <= 100
    assert data["tier"] in ("beginner", "intermediate", "advanced")
    assert len(data["summary"]) > 0


@pytest.mark.asyncio
async def test_estimate_score_without_quiz(client):
    headers = await _auth_headers(client, email="noquiz@forge.app")
    resp = await client.get(ESTIMATE_URL, headers=headers)
    assert resp.status_code == 404
    assert "quiz" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_estimate_skin_concern_penalised(client):
    """Skin should score lower when it's the main concern."""
    headers = await _auth_headers(client)
    await client.post(SUBMIT_URL, json=VALID_QUIZ, headers=headers)
    resp = await client.get(ESTIMATE_URL, headers=headers)
    scores = {p["pillar"]: p["score"] for p in resp.json()["pillar_scores"]}
    assert scores["skin"] < scores["hair"]


@pytest.mark.asyncio
async def test_estimate_advanced_routine_higher(client):
    """Advanced routine should produce higher scores than none."""
    headers_adv = await _auth_headers(client, email="adv@forge.app")
    adv_quiz = {**VALID_QUIZ, "routine_level": "advanced"}
    await client.post(SUBMIT_URL, json=adv_quiz, headers=headers_adv)
    resp_adv = await client.get(ESTIMATE_URL, headers=headers_adv)
    adv_opt = resp_adv.json()["optimisation_score"]

    headers_none = await _auth_headers(client, email="none@forge.app")
    none_quiz = {**VALID_QUIZ, "routine_level": "none"}
    await client.post(SUBMIT_URL, json=none_quiz, headers=headers_none)
    resp_none = await client.get(ESTIMATE_URL, headers=headers_none)
    none_opt = resp_none.json()["optimisation_score"]

    assert adv_opt > none_opt
