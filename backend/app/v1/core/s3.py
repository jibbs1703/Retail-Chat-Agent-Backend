"""Retail Chat Agent — S3 Presigned URL Utilities."""

import urllib.parse

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from .configuration import get_settings


def _parse_s3_url(url: str) -> tuple[str, str]:
    """Parse a virtual-hosted S3 URL into (bucket, key).

    Expects the format:
    ``https://{bucket}.s3.{region}.amazonaws.com/{key}``
    """
    parsed = urllib.parse.urlparse(url)
    bucket = parsed.hostname.split(".")[0]
    key = parsed.path.lstrip("/")
    return bucket, key


def generate_presigned_url(s3_url: str) -> str | None:
    """Generate a time-limited presigned GET URL for an S3 object.

    Args:
        s3_url: Public or internal S3 object URL in virtual-hosted style,
                e.g. ``https://my-bucket.s3.us-east-2.amazonaws.com/product/img.jpg``.

    Returns:
        A presigned URL string, or ``None`` if generation fails.
    """
    settings = get_settings()
    try:
        bucket, key = _parse_s3_url(s3_url)
        client = boto3.client(
            "s3",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )
        return client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=settings.aws_s3_presigned_url_expiry,
        )
    except (ClientError, NoCredentialsError, Exception):
        return None
