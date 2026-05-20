"""Integration and unit tests for cycle check-in endpoints."""

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.cycles.photo_analyser import MOCK_ANALYSIS, validate_analysis
from src.cycles.service import CYCLE_COOLDOWN_DAYS
from src.database.models import Cycle, Progress, User

SIGNUP_URL = "/api/v1/auth/signup"
UPLOAD_URL_ENDPOINT = "/api/v1/cycles/upload-url"
ELIGIBILITY_URL = "/api/v1/cycles/eligibility"
ANALYSE_URL = "/api/v1/cycles/analyse"
HISTORY_URL = "/api/v1/cycles/history"


async def _create_user(client: AsyncClient, db_session: AsyncSession) -> tuple[dict, User]:
    """Helper: sign up a user and return tokens + user model."""
    email = f"cycle-test-{uuid.uuid4().hex[:8]}@forge.app"
    resp = await client.post(
        SIGNUP_URL,
        json={"email": email, "password": "securepass123", "name": "Cycle Tester"},
    )
    assert resp.status_code == 201
    tokens = resp.json()

    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one()
    return tokens, user


def _auth_headers(tokens: dict) -> dict:
    return {"Authorization": f"Bearer {tokens['access_token']}"}


# ---------------------------------------------------------------------------
# Unit Tests — Photo Analyser
# ---------------------------------------------------------------------------


class TestValidateAnalysis:
    def test_clamps_scores_to_0_100(self):
        data = dict(MOCK_ANALYSIS)
        data["skin_score"] = 150
        data["grooming_score"] = -20
        result = validate_analysis(data, "full")
        assert result["skin_score"] == 100
        assert result["grooming_score"] == 0

    def test_face_scan_nullifies_body_pillars(self):
        data = dict(MOCK_ANALYSIS)
        data["sleep_score"] = 70
        data["nutrition_score"] = 65
        result = validate_analysis(data, "face")
        assert result["sleep_score"] is None
        assert result["nutrition_score"] is None

    def test_voice_always_null(self):
        data = dict(MOCK_ANALYSIS)
        data["voice_score"] = 80
        result = validate_analysis(data, "full")
        assert result["voice_score"] is None

    def test_invalid_face_shape_becomes_none(self):
        data = dict(MOCK_ANALYSIS)
        data["face_shape"] = "unknown_shape"
        result = validate_analysis(data, "face")
        assert result["face_shape"] is None

    def test_valid_face_shapes_accepted(self):
        for shape in ["oval", "square", "round", "long", "heart", "diamond", "triangle", "oblong"]:
            data = dict(MOCK_ANALYSIS)
            data["face_shape"] = shape
            result = validate_analysis(data, "face")
            assert result["face_shape"] == shape


# ---------------------------------------------------------------------------
# Integration Tests — Eligibility
# ---------------------------------------------------------------------------


class TestEligibility:
    @pytest.mark.asyncio
    async def test_first_time_user_is_eligible(self, client: AsyncClient, db_session: AsyncSession):
        tokens, user = await _create_user(client, db_session)
        resp = await client.get(ELIGIBILITY_URL, headers=_auth_headers(tokens))
        assert resp.status_code == 200
        data = resp.json()
        assert data["eligible"] is True
        assert data["current_cycle_number"] == 1

    @pytest.mark.asyncio
    async def test_user_ineligible_during_cooldown(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        tokens, user = await _create_user(client, db_session)

        cycle = Cycle(
            user_id=user.id,
            cycle_number=1,
            cycle_type="face",
            checked_in_at=datetime.now(UTC) - timedelta(days=2),
        )
        db_session.add(cycle)
        await db_session.flush()

        resp = await client.get(ELIGIBILITY_URL, headers=_auth_headers(tokens))
        assert resp.status_code == 200
        data = resp.json()
        assert data["eligible"] is False
        assert data["current_cycle_number"] == 1

    @pytest.mark.asyncio
    async def test_user_eligible_after_cooldown(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        tokens, user = await _create_user(client, db_session)

        cycle = Cycle(
            user_id=user.id,
            cycle_number=1,
            cycle_type="face",
            checked_in_at=datetime.now(UTC) - timedelta(days=CYCLE_COOLDOWN_DAYS + 1),
        )
        db_session.add(cycle)
        await db_session.flush()

        resp = await client.get(ELIGIBILITY_URL, headers=_auth_headers(tokens))
        assert resp.status_code == 200
        data = resp.json()
        assert data["eligible"] is True
        assert data["current_cycle_number"] == 2


# ---------------------------------------------------------------------------
# Integration Tests — Upload URL
# ---------------------------------------------------------------------------


class TestUploadUrl:
    @pytest.mark.asyncio
    @patch("src.cycles.service.generate_upload_url")
    async def test_returns_presigned_url(
        self, mock_upload, client: AsyncClient, db_session: AsyncSession
    ):
        mock_upload.return_value = {
            "upload_url": "https://r2.example.com/upload?signed=1",
            "object_key": "cycles/user/photo.jpg",
            "expires_in": 300,
        }
        tokens, _ = await _create_user(client, db_session)

        resp = await client.post(
            UPLOAD_URL_ENDPOINT,
            json={"angle": "front", "scan_mode": "face"},
            headers=_auth_headers(tokens),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "upload_url" in data
        assert data["expires_in"] == 300

    @pytest.mark.asyncio
    async def test_requires_auth(self, client: AsyncClient):
        resp = await client.post(UPLOAD_URL_ENDPOINT, json={"angle": "front"})
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# Integration Tests — Analyse
# ---------------------------------------------------------------------------


class TestAnalyse:
    @pytest.mark.asyncio
    @patch("src.cycles.service.generate_download_url")
    async def test_creates_cycle_record(
        self, mock_download_url, client: AsyncClient, db_session: AsyncSession
    ):
        mock_download_url.return_value = "https://r2.example.com/photo.jpg"
        tokens, user = await _create_user(client, db_session)

        resp = await client.post(
            ANALYSE_URL,
            json={"object_key": "cycles/test/photo.jpg", "scan_mode": "face"},
            headers=_auth_headers(tokens),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["cycle_number"] == 1
        assert data["scan_mode"] == "face"
        assert data["scores"]["facial_composition_score"] is not None
        assert data["face_shape"] is not None

    @pytest.mark.asyncio
    @patch("src.cycles.service.generate_download_url")
    async def test_updates_progress_scores(
        self, mock_download_url, client: AsyncClient, db_session: AsyncSession
    ):
        mock_download_url.return_value = "https://r2.example.com/photo.jpg"
        tokens, user = await _create_user(client, db_session)

        resp = await client.post(
            ANALYSE_URL,
            json={"object_key": "cycles/test/photo.jpg", "scan_mode": "face"},
            headers=_auth_headers(tokens),
        )
        assert resp.status_code == 200

        result = await db_session.execute(select(Progress).where(Progress.user_id == user.id))
        progress = result.scalar_one()
        assert progress.facial_composition_score != 50

    @pytest.mark.asyncio
    @patch("src.cycles.service.generate_download_url")
    async def test_rejects_during_cooldown(
        self, mock_download_url, client: AsyncClient, db_session: AsyncSession
    ):
        mock_download_url.return_value = "https://r2.example.com/photo.jpg"
        tokens, user = await _create_user(client, db_session)

        cycle = Cycle(
            user_id=user.id,
            cycle_number=1,
            cycle_type="face",
            checked_in_at=datetime.now(UTC),
        )
        db_session.add(cycle)
        await db_session.flush()

        resp = await client.post(
            ANALYSE_URL,
            json={"object_key": "cycles/test/photo.jpg", "scan_mode": "face"},
            headers=_auth_headers(tokens),
        )
        assert resp.status_code == 429


# ---------------------------------------------------------------------------
# Integration Tests — History
# ---------------------------------------------------------------------------


class TestHistory:
    @pytest.mark.asyncio
    async def test_returns_empty_for_new_user(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        tokens, _ = await _create_user(client, db_session)
        resp = await client.get(HISTORY_URL, headers=_auth_headers(tokens))
        assert resp.status_code == 200
        data = resp.json()
        assert data["cycles"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_returns_cycle_history(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        tokens, user = await _create_user(client, db_session)

        for i in range(3):
            cycle = Cycle(
                user_id=user.id,
                cycle_number=i + 1,
                cycle_type="face",
                facial_composition_score=60 + i,
                skin_score=55 + i,
                checked_in_at=datetime.now(UTC) - timedelta(days=(3 - i) * 7),
            )
            db_session.add(cycle)
        await db_session.flush()

        resp = await client.get(HISTORY_URL, headers=_auth_headers(tokens))
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 3
        assert len(data["cycles"]) == 3
        assert data["cycles"][0]["cycle_number"] == 3


# ---------------------------------------------------------------------------
# Integration Tests — Compare
# ---------------------------------------------------------------------------


class TestCompare:
    @pytest.mark.asyncio
    async def test_compare_returns_deltas(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        tokens, user = await _create_user(client, db_session)

        c1 = Cycle(
            user_id=user.id,
            cycle_number=1,
            cycle_type="face",
            facial_composition_score=50,
            skin_score=50,
            grooming_score=50,
            hair_score=50,
            checked_in_at=datetime.now(UTC) - timedelta(days=14),
        )
        c2 = Cycle(
            user_id=user.id,
            cycle_number=2,
            cycle_type="face",
            facial_composition_score=60,
            skin_score=55,
            grooming_score=48,
            hair_score=65,
            checked_in_at=datetime.now(UTC) - timedelta(days=7),
        )
        db_session.add_all([c1, c2])
        await db_session.flush()

        url = f"/api/v1/cycles/compare/{c2.id}/{c1.id}"
        resp = await client.get(url, headers=_auth_headers(tokens))
        assert resp.status_code == 200
        data = resp.json()
        assert data["deltas"]["facial_composition"] == 10
        assert data["deltas"]["skin"] == 5
        assert data["deltas"]["grooming"] == -2
        assert data["deltas"]["hair"] == 15
        assert data["days_between"] == 7
