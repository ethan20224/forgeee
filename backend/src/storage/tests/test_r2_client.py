"""Unit tests for R2 storage client — presigned URL generation (mocked boto3)."""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from src.storage.r2_client import (
    DOWNLOAD_EXPIRY_SECONDS,
    UPLOAD_EXPIRY_SECONDS,
    build_photo_path,
    delete_object,
    generate_download_url,
    generate_upload_url,
)


class TestBuildPhotoPath:
    def test_path_contains_user_id(self):
        user_id = uuid.uuid4()
        path = build_photo_path(user_id, "front")
        assert str(user_id) in path

    def test_path_contains_angle(self):
        user_id = uuid.uuid4()
        path = build_photo_path(user_id, "side")
        assert "side" in path

    def test_path_starts_with_cycles_prefix(self):
        user_id = uuid.uuid4()
        path = build_photo_path(user_id, "front")
        assert path.startswith("cycles/")

    def test_path_ends_with_jpg(self):
        user_id = uuid.uuid4()
        path = build_photo_path(user_id, "front")
        assert path.endswith(".jpg")


class TestGenerateUploadUrl:
    @patch("src.storage.r2_client._get_s3_client")
    def test_returns_upload_url_and_key(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.generate_presigned_url.return_value = "https://r2.example.com/upload?signed=1"
        mock_get_client.return_value = mock_client

        user_id = uuid.uuid4()
        result = generate_upload_url(user_id, "front")

        assert "upload_url" in result
        assert result["upload_url"] == "https://r2.example.com/upload?signed=1"
        assert "object_key" in result
        assert result["object_key"].startswith("cycles/")
        assert result["expires_in"] == UPLOAD_EXPIRY_SECONDS

    @patch("src.storage.r2_client._get_s3_client")
    def test_calls_put_object(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.generate_presigned_url.return_value = "https://r2.example.com/upload"
        mock_get_client.return_value = mock_client

        user_id = uuid.uuid4()
        generate_upload_url(user_id, "front")

        mock_client.generate_presigned_url.assert_called_once()
        args = mock_client.generate_presigned_url.call_args
        assert args[0][0] == "put_object"
        assert args[1]["Params"]["ContentType"] == "image/jpeg"
        assert args[1]["ExpiresIn"] == UPLOAD_EXPIRY_SECONDS


class TestGenerateDownloadUrl:
    @patch("src.storage.r2_client._get_s3_client")
    def test_returns_signed_url(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.generate_presigned_url.return_value = "https://r2.example.com/download?signed=1"
        mock_get_client.return_value = mock_client

        url = generate_download_url("cycles/user-123/photo.jpg")

        assert url == "https://r2.example.com/download?signed=1"
        mock_client.generate_presigned_url.assert_called_once()
        args = mock_client.generate_presigned_url.call_args
        assert args[0][0] == "get_object"
        assert args[1]["ExpiresIn"] == DOWNLOAD_EXPIRY_SECONDS


class TestDeleteObject:
    @patch("src.storage.r2_client._get_s3_client")
    def test_calls_delete(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        delete_object("cycles/user-123/photo.jpg")

        mock_client.delete_object.assert_called_once()
        args = mock_client.delete_object.call_args
        assert args[1]["Key"] == "cycles/user-123/photo.jpg"
