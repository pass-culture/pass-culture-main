import logging

from google.cloud.exceptions import NotFound
from google.cloud.storage import Client
from google.cloud.storage.bucket import Bucket
from google.oauth2.service_account import Credentials

from pcapi import settings


logger = logging.getLogger(__name__)

from .base import BaseBackend


class GCPBackend(BaseBackend):
    bucket_credentials = settings.GCP_BUCKET_CREDENTIALS
    default_bucket_name = settings.GCP_BUCKET_NAME

    def __init__(
        self,
        project_id: str | None = None,
        bucket_name: str | None = None,
    ) -> None:
        self.project_id = project_id or self.bucket_credentials.get("project_id")
        self.bucket_name = bucket_name or self.default_bucket_name

    def get_gcp_storage_client_bucket(self) -> Bucket:
        credentials = Credentials.from_service_account_info(self.bucket_credentials)
        storage_client = Client(credentials=credentials, project=self.project_id)
        return storage_client.bucket(self.bucket_name)

    def store_public_object(self, folder: str, object_id: str, blob: bytes, content_type: str) -> None:
        storage_path = folder + "/" + object_id
        try:
            bucket = self.get_gcp_storage_client_bucket()
            gcp_cloud_blob = bucket.blob(storage_path)
            gcp_cloud_blob.upload_from_string(blob, content_type=content_type)
        except Exception as exc:
            logger.exception("An error has occured while trying to upload file on GCP bucket: %s", exc)
            raise exc

    def delete_public_object(self, folder: str, object_id: str) -> None:
        storage_path = folder + "/" + object_id
        try:
            bucket = self.get_gcp_storage_client_bucket()
            gcp_cloud_blob = bucket.blob(storage_path)
            gcp_cloud_blob.delete()
        except NotFound:
            logger.info("File not found on deletion on GCP bucket: %s", storage_path)
        except Exception as exc:
            logger.exception("An error has occured while trying to delete file on GCP bucket: %s", exc)
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
