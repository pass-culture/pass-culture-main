import logging
import os
from pathlib import Path
from pathlib import PurePath
from typing import Optional


logger = logging.getLogger(__name__)

from .base import BaseBackend


STORAGE_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / ".." / ".." / "static" / "object_store_data"


class LocalBackend(BaseBackend):
    def local_dir(self, bucket: str, object_id: str) -> Path:
        if "/" in object_id:
            return STORAGE_DIR / bucket / PurePath(object_id).parent
        return STORAGE_DIR / bucket

    def local_path(self, bucket: str, object_id: str) -> Path:
        return self.local_dir(bucket, object_id) / PurePath(object_id).name

    def store_public_object(self, bucket: str, object_id: str, blob: bytes, content_type: str) -> None:
        try:
            os.makedirs(self.local_dir(bucket, object_id), exist_ok=True)
            file_local_path = self.local_path(bucket, object_id)
            with open(str(file_local_path) + ".type", "w") as new_type_file:
                new_type_file.write(content_type)

            with open(file_local_path, "wb") as new_file:
                new_file.write(blob)

        except Exception as exc:
            logger.exception("An error has occured while trying to upload file on local file storage: %s", exc)
            raise exc

    def delete_public_object(self, bucket: str, object_id: str) -> None:
        file_local_path = self.local_path(bucket, object_id)
        try:
            os.remove(file_local_path)
            os.remove(str(file_local_path) + ".type")
        except OSError as exc:
            logger.exception("An error has occured while trying to delete file on local file storage: %s", exc)
            raise exc

    def get_container(
        self,
        container_name: Optional[str] = None,
        marker: str = "",
        end_marker: str = "",
        full_listing: bool = True,
    ) -> tuple:
        """
        This is modeled after OVH's get_container(), and quite similar to google.cloud.storage.Client.list_blobs
        and it will be mainly used to test the delete_unused_mediations_and_assets script
        """
        try:
            bucket_local_path = container_name or STORAGE_DIR
            bucket_local_path = str(bucket_local_path) + "/"
            asset_names = []

            # first, we build a list of asset_names
            for root, _subdirs, files in os.walk(bucket_local_path):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    asset_name = str(file_path).replace(str(bucket_local_path), "")
                    # don't add hidden system files
                    if "/." in asset_name or asset_name.startswith("."):
                        break
                    # don't add names lower than marker or higher than end_marker
                    if asset_name < marker or (end_marker and asset_name > end_marker):
                        break
                    asset_names.append(asset_name)

            # then we sort the list of asset_names and create a list of dict from it
            asset_names.sort()
            assets = [{"name": asset} for asset in asset_names]

            if not full_listing:
                # only keep the first 10_000 elements
                assets = assets[:10_000]

            # this is the only header we would use locally
            headers = {"x-container-object-count": len(assets)}

            return headers, assets

        except Exception as exc:
            logger.exception("An error has occured while trying to get container info on local file storage: %s", exc)
            raise exc
