import logging

from google.cloud.exceptions import NotFound
from google.cloud.storage.bucket import Bucket
from google.cloud.storage.client import Client
import google.cloud.storage.retry
from google.oauth2.service_account import Credentials

from pcapi import settings

from .base import BaseBackend


logger = logging.getLogger(__name__)

# `google.cloud.storage.constants._DEFAULT_TIMEOUT` is 60 seconds.
# Our files are not big, no operation should take that long.
TIMEOUT = 20
# The default retry strategy for the methods used in this module is
# DEFAULT_RETRY_IF_GENERATION_SPECIFIED. Since we don't specify the
# generation, there is no retry by default. We need to specify it.
# This strategy is safe because the "generation" feature is disabled
# on our buckets. We set the deadline to TIMEOUT so that the operation
# does not exceed this TIMEOUT even with multiple retries.
RETRY_STRATEGY = google.cloud.storage.retry.DEFAULT_RETRY.with_deadline(TIMEOUT)


class GCPBackend(BaseBackend):
    bucket_credentials = settings.GCP_BUCKET_CREDENTIALS
    default_bucket_name = settings.GCP_BUCKET_NAME

    def __init__(
        self,
        project_id: str | None = None,
        bucket_name: str = "",
    ) -> None:
        self.project_id = project_id or self.bucket_credentials.get("project_id")
        self.bucket_name = bucket_name or self.default_bucket_name

    def get_gcp_storage_client(self) -> Client:
        credentials = Credentials.from_service_account_info(self.bucket_credentials)
        return Client(credentials=credentials, project=self.project_id)

    def get_gcp_storage_client_bucket(self) -> Bucket:

        storage_client = self.get_gcp_storage_client()
        return storage_client.bucket(self.bucket_name)

    def store_public_object(self, folder: str, object_id: str, blob: bytes, content_type: str) -> None:
        storage_path = folder + "/" + object_id
        try:
            bucket = self.get_gcp_storage_client_bucket()
            gcp_cloud_blob = bucket.blob(storage_path)
            gcp_cloud_blob.upload_from_string(
                blob,
                content_type=content_type,
                timeout=TIMEOUT,
                retry=RETRY_STRATEGY,
            )
        except Exception as exc:
            logger.exception(
                "An error has occurred while trying to upload file on GCP bucket",
                extra={
                    "exc": exc,
                    "project_id": self.project_id,
                    "bucket_name": self.bucket_name,
                    "storage_path": storage_path,
                },
            )
            raise exc

    def delete_public_object(self, folder: str, object_id: str) -> None:
        storage_path = folder + "/" + object_id
        try:
            bucket = self.get_gcp_storage_client_bucket()
            gcp_cloud_blob = bucket.blob(storage_path)
            gcp_cloud_blob.delete(timeout=TIMEOUT, retry=RETRY_STRATEGY)
        except NotFound:
            logger.info("File not found on deletion on GCP bucket: %s", storage_path)
        except Exception as exc:
            logger.exception(
                "An error has occurred while trying to delete file on GCP bucket",
                extra={
                    "exc": exc,
                    "project_id": self.project_id,
                    "bucket_name": self.bucket_name,
                    "storage_path": storage_path,
                },
            )
            raise exc

    def list_files(self, folder: str, *, max_results: int = 1000) -> list[str]:
        try:
            storage_client = self.get_gcp_storage_client()
            blobs = storage_client.list_blobs(self.bucket_name, max_results=max_results, prefix=folder)
            return [blob.name for blob in blobs]
        except Exception as exc:
            logger.exception(
                "An error has occurred while trying to list files in GCP bucket",
                extra={
                    "exc": exc,
                    "project_id": self.project_id,
                    "bucket_name": self.bucket_name,
                    "prefix": folder,
                },
            )
            raise exc


class GCPAlternateBackend(GCPBackend):
    """A backend for GCP Storage that connects to an alternate bucket.

    It is used during the transition between 2 buckets (accessible
    with the same credentials), with the following steps:

    0. Use single "soon-to-be-old" GCP backend.

    1. Use both GCP and GCP_ALTERNATE backends. The former uses the
       "soon-to-be-old" bucket name, the latter uses the new.

    2. Switch bucket names (in GCP secrets) and stop using GCP_ALTERNATE.

    3. (optional) Delete this class and the `GCP_ALTERNATE_BUCKET_NAME`
       secret.
    """

    default_bucket_name = settings.GCP_ALTERNATE_BUCKET_NAME
