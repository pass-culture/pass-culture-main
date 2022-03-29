import logging

from google.cloud.exceptions import NotFound
from google.cloud.storage import Client
from google.cloud.storage.bucket import Bucket
from google.oauth2.service_account import Credentials

from pcapi import settings


logger = logging.getLogger(__name__)

from .base import BaseBackend


class GCPBackend(BaseBackend):
    def __init__(
        self,
        project_id: str = settings.GCP_BUCKET_CREDENTIALS.get("project_id"),
        bucket_name: str = settings.GCP_BUCKET_NAME,
    ) -> None:
        self.project_id = project_id
        self.bucket_name = bucket_name

    def get_gcp_storage_client_bucket(self) -> Bucket:
        credentials = Credentials.from_service_account_info(settings.GCP_BUCKET_CREDENTIALS)
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
