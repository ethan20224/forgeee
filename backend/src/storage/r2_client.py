"""Cloudflare R2 storage client for photo uploads/downloads via presigned URLs."""

import uuid
from datetime import datetime, UTC

import boto3
from botocore.config import Config as BotoConfig

from src.config import get_settings

UPLOAD_EXPIRY_SECONDS = 300
DOWNLOAD_EXPIRY_SECONDS = 3600


def _get_s3_client():
    """Create an S3-compatible client configured for Cloudflare R2."""
    settings = get_settings()
    return boto3.client(
        "s3",
        endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        config=BotoConfig(
            signature_version="s3v4",
            region_name="auto",
        ),
    )


def build_photo_path(user_id: uuid.UUID, angle: str = "front") -> str:
    """Construct the R2 object key for a photo upload."""
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    return f"cycles/{user_id}/{timestamp}-{angle}.jpg"


def generate_upload_url(user_id: uuid.UUID, angle: str = "front") -> dict:
    """
    Generate a presigned PUT URL for photo upload.

    Returns dict with 'upload_url', 'object_key', and 'expires_in'.
    """
    settings = get_settings()
    client = _get_s3_client()
    object_key = build_photo_path(user_id, angle)

    url = client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.r2_bucket_name,
            "Key": object_key,
            "ContentType": "image/jpeg",
        },
        ExpiresIn=UPLOAD_EXPIRY_SECONDS,
    )

    return {
        "upload_url": url,
        "object_key": object_key,
        "expires_in": UPLOAD_EXPIRY_SECONDS,
    }


def generate_download_url(object_key: str) -> str:
    """Generate a presigned GET URL for photo download (1-hour expiry)."""
    settings = get_settings()
    client = _get_s3_client()

    return client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.r2_bucket_name,
            "Key": object_key,
        },
        ExpiresIn=DOWNLOAD_EXPIRY_SECONDS,
    )


def generate_download_urls(object_keys: list[str]) -> list[str]:
    """Generate presigned GET URLs for multiple photos."""
    return [generate_download_url(key) for key in object_keys]


def delete_object(object_key: str) -> None:
    """Delete a photo from R2."""
    settings = get_settings()
    client = _get_s3_client()
    client.delete_object(Bucket=settings.r2_bucket_name, Key=object_key)


"""
=== FILE FLOW DOCUMENTATION ===

Functionality: Cloudflare R2 storage client using S3-compatible presigned URLs.

Flow:
1. generate_upload_url() — creates presigned PUT URL (5 min expiry) for direct browser upload
2. generate_download_url() — creates presigned GET URL (1 hour expiry) for photo display
3. delete_object() — removes a photo from R2

Main Entry Point: generate_upload_url, generate_download_url, delete_object

Dependencies:
- boto3: S3-compatible client
- src.config: R2 credentials and bucket config
"""
