import logging
import threading

import boto3
from botocore.exceptions import ClientError

from pcapi import settings


logger = logging.getLogger(__name__)

_thread_local_boto_session_container = threading.local()


def _get_boto_session() -> boto3.Session:
    if not hasattr(_thread_local_boto_session_container, "session"):
        _thread_local_boto_session_container.session = boto3.Session()
    return _thread_local_boto_session_container.session


def upload_file(user_id: str, file_path: str, file_name: str) -> bool:
    # Do not use `boto3.client()`, it is not thread safe. Instead, get
    # a session (and keep it for the whole duration of this thread,
    # since it's a bit costly to create).
    session = _get_boto_session()
    client = session.client(
        "s3",
        aws_access_key_id=settings.OUTSCALE_ACCESS_KEY,
        aws_secret_access_key=settings.OUTSCALE_SECRET_KEY,
        region_name=settings.OUTSCALE_REGION,
        endpoint_url=settings.OUTSCALE_ENDPOINT_URL,
    )
    key = f"{user_id}/{file_name}"

    try:
        client.upload_file(
            file_path, settings.OUTSCALE_SECNUM_BUCKET_NAME, key, ExtraArgs={"ACL": "bucket-owner-full-control"}
        )
        logger.info(
            "Outscale upload started",
            extra={"file_name": file_name},
        )

    except FileNotFoundError as e:
        logger.warning(e)
        return False
    except ClientError as e:
        logger.exception(
            "Could not upload file to Outscale bucket",
            extra={
                "original_error_msg": e.msg,
                "error_code": e.response["Error"]["Code"],
                "error_status_code": e.response["Error"]["HTTPStatusCode"],
                "error_message": e.response["Error"]["Message"],
                "error_type": e.response["Error"]["Type"],
            },
        )
        return False

    return True
