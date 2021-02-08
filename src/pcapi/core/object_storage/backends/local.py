import os
from pathlib import Path
from pathlib import PurePath

from pcapi.utils.logger import logger

from .base import BaseBackend


STORAGE_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / ".." / ".." / "static" / "object_store_data"


class LocalBackend(BaseBackend):
    def local_dir(self, bucket, object_id):
        if "/" in object_id:
            idFolders = PurePath(object_id).parent
        else:
            idFolders = ""
        return STORAGE_DIR / bucket / idFolders

    def local_path(self, bucket, object_id):
        return self.local_dir(bucket, object_id) / PurePath(object_id).name

    def store_public_object(
        self, bucket: str, object_id: str, blob: bytes, content_type: str, symlink_path: str = None
    ) -> None:
        try:
            os.makedirs(self.local_dir(bucket, object_id), exist_ok=True)
            file_local_path = self.local_path(bucket, object_id)
            new_type_file = open(str(file_local_path) + ".type", "w")
            new_type_file.write(content_type)

            if symlink_path and not os.path.isfile(file_local_path) and not os.path.islink(file_local_path):
                os.symlink(symlink_path, file_local_path)
                return

            new_file = open(file_local_path, "wb")
            new_file.write(blob)

        except Exception as exc:
            logger.exception("An error has occured while trying to upload file on local file storage: %s", exc)
            raise exc

    def delete_public_object(self, bucket: str, object_id: str):
        file_local_path = self.local_path(bucket, object_id)
        try:
            os.remove(file_local_path)
            os.remove(str(file_local_path) + ".type")
        except OSError as exc:
            logger.exception("An error has occured while trying to delete file on local file storage: %s", exc)
            raise exc
