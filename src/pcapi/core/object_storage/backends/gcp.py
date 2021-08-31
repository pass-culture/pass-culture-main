import logging

from google.cloud.storage import Client
from google.cloud.storage.bucket import Bucket
from google.oauth2.service_account import Credentials

from pcapi import settings


logger = logging.getLogger(__name__)

from .base import BaseBackend


class GCPBackend(BaseBackend):
    def get_gcp_storage_client_bucket(self) -> Bucket:
        credentials = Credentials.from_service_account_info(settings.GCP_BUCKET_CREDENTIALS)
        project_id = settings.GCP_BUCKET_CREDENTIALS.get("project_id")
        storage_client = Client(credentials=credentials, project=project_id)

        return storage_client.bucket(settings.GCP_BUCKET_NAME)

    def store_public_object(self, bucket: str, object_id: str, blob: bytes, content_type: str) -> None:
        storage_path = bucket + "/" + object_id
        try:
            bucket = self.get_gcp_storage_client_bucket()
            gcp_cloud_blob = bucket.blob(storage_path)
            gcp_cloud_blob.upload_from_string(blob)
        except Exception as exc:
            logger.exception("An error has occured while trying to upload file on GCP bucket: %s", exc)
            raise exc

    def delete_public_object(self, bucket: str, object_id: str) -> None:
        storage_path = bucket + "/" + object_id
        try:
            bucket = self.get_gcp_storage_client_bucket()
            gcp_cloud_blob = bucket.blob(storage_path)
            gcp_cloud_blob.delete()
        except Exception as exc:
            logger.exception("An error has occured while trying to delete file on GCP bucket: %s", exc)
            raise exc
