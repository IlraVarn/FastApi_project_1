#AWS SDK access
import boto3
from functools import lru_cache

#S3 client configuration
from botocore.config import Config

# The S3ObjectStore should know:
# which bucket to use
# which AWS region to use
# the boto3 S3 client

# It should not know:
# TenantContext
# organization_id
# Evidence
# EvidenceVersion
# Gate
# FastAPI Depends
# SQLModel Session
# HTTPException




#create one reusable Python object whose job is to talk to your S3 bucket:

#isolate S3 operations:
# class S3ObjectStore:
#     def __init__(
#         self,
#         *,
#         bucket_name: str, #server infrastructure config
#         region_name: str, #AWS infrastructure config
#     ) -> None:

#         #prevent invalid infrastructure configuration:
#         if not bucket_name:
#             raise ValueError("bucket_name is required")

#         if not region_name:
#             raise ValueError("region_name is required")

#         self._bucket_name = bucket_name

#         #construct S3 client:
#         self._client = boto3.client(
#             "s3",
#             region_name=region_name,
#             config=Config(
#                 signature_version="s3v4",#control AWS request signing
#                 s3={"addressing_style": "virtual"},
#             ),
#         )


import base64
import binascii
from dataclasses import dataclass
import os

import boto3
from botocore.config import Config
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
)

from dataclasses import dataclass


@dataclass(frozen=True)



class S3ObjectStoreError(Exception):
    pass


class S3ObjectNotFoundError(
    S3ObjectStoreError
):
    pass


@dataclass(frozen=True)
class PresignedUpload:
    url: str
    headers: dict[str, str]
    expires_in_seconds: int



    """object_store
    = S3ObjectStore object
    = the thing that talks to AWS

    metadata
    = S3ObjectMetadata object
    = the information returned from AWS"""

@dataclass(frozen=True)
class S3ObjectMetadata:
    size_bytes: int
    checksum_sha256: str | None


class S3ObjectStore:

    def __init__(
        self,
        *,
        bucket_name: str,
        region_name: str,
    ) -> None:

        self._bucket_name = bucket_name

        self._client = boto3.client(
            "s3",
            region_name=region_name,
            config=Config(
                signature_version="s3v4",
                s3={
                    "addressing_style": "virtual",
                },
            ),
        )

    def create_presigned_upload(
        self,
        *,
        storage_key: str,
        content_type: str,
        checksum_sha256: str,
        expires_in_seconds: int,
    ) -> PresignedUpload:

        checksum_base64 = (
            self._sha256_hex_to_base64(
                checksum_sha256
            )
        )

    #If-None-Match: *
# → tells S3 not to overwrite an object 
# if that exact key somehow already exists
        try:
            url = (
                self._client.generate_presigned_url(
                    ClientMethod="put_object",
                    Params={
                        "Bucket": self._bucket_name,
                        "Key": storage_key,
                        "ContentType": content_type,
                        "ChecksumSHA256": (
                            checksum_base64
                        ),
                        "IfNoneMatch": "*",
                    },
                    ExpiresIn=expires_in_seconds,
                    HttpMethod="PUT",
                )
            )

        except (
            BotoCoreError,
            ClientError,
        ) as error:
            raise S3ObjectStoreError() from error

        return PresignedUpload(
            url=url,
            headers={
                "Content-Type": content_type,
                "x-amz-checksum-sha256": (
                    checksum_base64
                ),
                "If-None-Match": "*",
            },
            expires_in_seconds=(
                expires_in_seconds
            ),
        )

    def get_object_metadata(
        self,
        *,
        storage_key: str,
    ) -> S3ObjectMetadata:

        try:
            response = self._client.head_object(
                Bucket=self._bucket_name,
                Key=storage_key,
                ChecksumMode="ENABLED",
            )

        except ClientError as error:
            status_code = (
                error.response
                .get("ResponseMetadata", {})
                .get("HTTPStatusCode")
            )

            # Only 404 can safely mean
            # "object is not present".
            #
            # AWS may return 403 instead of 404
            # when ListBucket is not permitted,
            # so 403 must NOT be treated as
            # object-not-found.
            if status_code == 404:
                raise (
                    S3ObjectNotFoundError()
                ) from error

            raise S3ObjectStoreError() from error

        except BotoCoreError as error:
            raise S3ObjectStoreError() from error

        checksum_base64 = response.get(
            "ChecksumSHA256"
        )

        checksum_sha256 = None

        if checksum_base64 is not None:
            checksum_sha256 = (
                self._sha256_base64_to_hex(
                    checksum_base64
                )
            )

        return S3ObjectMetadata(
            size_bytes=response["ContentLength"],
            checksum_sha256=checksum_sha256,
        )

    @staticmethod
    def _sha256_hex_to_base64(
        checksum_sha256: str,
    ) -> str:

        try:
            checksum_bytes = bytes.fromhex(
                checksum_sha256
            )

        except ValueError as error:
            raise ValueError(
                "Invalid SHA-256 checksum"
            ) from error

        if len(checksum_bytes) != 32:
            raise ValueError(
                "Invalid SHA-256 checksum"
            )

        return base64.b64encode(
            checksum_bytes
        ).decode("ascii")

    @staticmethod
    def _sha256_base64_to_hex(
        checksum_base64: str,
    ) -> str:

        try:
            checksum_bytes = base64.b64decode(
                checksum_base64,
                validate=True,
            )

        except (
            ValueError,
            binascii.Error,
        ) as error:
            raise S3ObjectStoreError() from error

        if len(checksum_bytes) != 32:
            raise S3ObjectStoreError()

        return checksum_bytes.hex()


@lru_cache
def get_s3_object_store() -> S3ObjectStore:

    bucket_name = os.environ.get(
        "S3_BUCKET_NAME"
    )

    if bucket_name is None:
        raise RuntimeError(
            "S3_BUCKET_NAME is not configured"
        )

    return S3ObjectStore(
        bucket_name=bucket_name,
        region_name="us-west-2",
    )


# S3ObjectStore = the backend object that knows how to talk to S3.

# get_s3_object_store()
# ↓
# creates S3ObjectStore
# ↓
# router receives it as object_store
# ↓
# service uses it
# ↓
# S3

# It mainly does two jobs:

# create_presigned_upload()
# = get temporary upload URL

# get_object_metadata()
# = ask S3 what file actually arrived

# The checksum helper methods just convert checksum format for AWS.