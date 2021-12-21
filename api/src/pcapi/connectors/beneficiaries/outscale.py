import logging

import boto3
from botocore.exceptions import ClientError

from pcapi import settings


logger = logging.getLogger(__name__)


def upload_file(user_id: str, file_path: str, file_name: str) -> bool:

    client = boto3.client(
        "s3",
        aws_access_key_id=settings.OUTSCALE_ACCESS_KEY,
        aws_secret_access_key=settings.OUTSCALE_SECRET_KEY,
        region_name=settings.OUTSCALE_REGION,
        endpoint_url=settings.OUTSCALE_ENDPOINT_URL,
    )
    key = f"{user_id}/{file_name}"

    try:
        client.upload_file(file_path, settings.OUTSCALE_SECNUM_BUCKET_NAME, key)
        logger.info(
            "Outscale upload started",
            extra={"file_name": file_name},
        )

    except FileNotFoundError as e:
        logging.warning(e)
        return False
    except ClientError as e:
        logging.exception(
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
