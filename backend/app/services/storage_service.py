import os
import uuid
from abc import ABC, abstractmethod
from pathlib import Path

import boto3
from botocore.config import Config

from app.core.config import settings


class StorageService(ABC):
    @abstractmethod
    async def upload(self, file_bytes: bytes, path: str, content_type: str) -> str:
        """Upload file and return its public URL."""

    @abstractmethod
    async def delete(self, path: str) -> None:
        """Delete a file by path."""

    @abstractmethod
    async def get_url(self, path: str) -> str:
        """Get the public URL for a file path."""


class LocalStorageService(StorageService):
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    async def upload(self, file_bytes: bytes, path: str, content_type: str) -> str:
        full_path = self.storage_path / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(file_bytes)
        return f"/static/{path}"

    async def delete(self, path: str) -> None:
        full_path = self.storage_path / path
        if full_path.exists():
            full_path.unlink()

    async def get_url(self, path: str) -> str:
        return f"/static/{path}"


class S3StorageService(StorageService):
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL or None,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
            config=Config(signature_version="s3v4"),
        )
        self.bucket = settings.S3_BUCKET_NAME
        self.public_url = settings.S3_PUBLIC_URL

    async def upload(self, file_bytes: bytes, path: str, content_type: str) -> str:
        import asyncio

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.s3.put_object(
                Bucket=self.bucket,
                Key=path,
                Body=file_bytes,
                ContentType=content_type,
                ACL="public-read",
            ),
        )
        return await self.get_url(path)

    async def delete(self, path: str) -> None:
        import asyncio

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.s3.delete_object(Bucket=self.bucket, Key=path),
        )

    async def get_url(self, path: str) -> str:
        if self.public_url:
            return f"{self.public_url.rstrip('/')}/{path}"
        return f"https://{self.bucket}.s3.{settings.S3_REGION}.amazonaws.com/{path}"


def get_storage_service() -> StorageService:
    """Factory function returning the configured storage service."""
    if settings.STORAGE_BACKEND == "s3":
        return S3StorageService()
    return LocalStorageService(settings.STORAGE_PATH)
