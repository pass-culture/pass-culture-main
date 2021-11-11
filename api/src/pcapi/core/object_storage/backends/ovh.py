import logging
from typing import Optional

import swiftclient
from swiftclient.client import Connection

from pcapi import settings


logger = logging.getLogger(__name__)

from .base import BaseBackend


class OVHBackend(BaseBackend):
    def swift_con(self) -> Connection:
        return swiftclient.Connection(
            user=settings.SWIFT_USER,
            key=settings.SWIFT_KEY,
            authurl=settings.SWIFT_AUTH_URL,
            os_options={"region_name": settings.SWIFT_REGION_NAME},
            tenant_name=settings.SWIFT_TENANT_NAME,
            auth_version="3",
        )

    def store_public_object(self, bucket: str, object_id: str, blob: bytes, content_type: str) -> None:
        container_name = settings.SWIFT_BUCKET_NAME
        try:
            storage_path = bucket + "/" + object_id
            self.swift_con().put_object(container_name, storage_path, contents=blob, content_type=content_type)
        except Exception as exc:
            logger.exception("An error has occured while trying to upload file on OVH bucket: %s", exc)
            raise exc

    def delete_public_object(self, bucket: str, object_id: str) -> None:
        container_name = settings.SWIFT_BUCKET_NAME
        try:
            storage_path = bucket + "/" + object_id
            self.swift_con().delete_object(container_name, storage_path)
        except Exception as exc:
            logger.exception("An error has occured while trying to delete file on OVH bucket: %s", exc)
            raise exc

    def get_container(
        self,
        container_name: Optional[str] = settings.SWIFT_BUCKET_NAME,
        marker: str = None,
        end_marker: str = None,
        full_listing: bool = True,
    ) -> tuple:
        try:
            response = self.swift_con().get_container(
                container=container_name,
                marker=marker,
                end_marker=end_marker,
                full_listing=full_listing,
            )
            return response
        except Exception as exc:
            logger.exception("An error has occured while trying to get container on OVH bucket: %s", exc)
            raise exc
