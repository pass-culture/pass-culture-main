from itertools import chain
import logging
import os
import pathlib

from pcapi import settings

from .. import FileNotFound
from .base import BaseBackend


logger = logging.getLogger(__name__)


class LocalBackend(BaseBackend):

    def __init__(
        self,
        project_id: str | None = None,
        bucket_name: str = "",
    ) -> None:
        self.project_id = project_id
        self.bucket_name = bucket_name

    def local_dir(self, folder: str, object_id: str) -> pathlib.Path:
        folder_path = settings.LOCAL_STORAGE_DIR / self.bucket_name / folder
        if "/" in object_id:
            return folder_path / pathlib.PurePath(object_id).parent
        return folder_path

    def local_path(self, folder: str, object_id: str) -> pathlib.Path:
        return self.local_dir(folder, object_id) / pathlib.PurePath(object_id).name

    def store_public_object(self, folder: str, object_id: str, blob: bytes, content_type: str) -> None:
        try:
            os.makedirs(self.local_dir(folder, object_id), exist_ok=True)
            file_local_path = self.local_path(folder, object_id)
            with open(str(file_local_path) + ".type", "w", encoding="ascii") as new_type_file:
                new_type_file.write(content_type)

            with open(file_local_path, "wb") as new_file:
                new_file.write(blob)

        except Exception as exc:
            logger.exception("An error has occurred while trying to upload file on local file storage: %s", exc)
            raise exc

    def get_public_object(self, folder: str, object_id: str) -> bytes:
        file_local_path = self.local_path(folder, object_id)
        try:
            with open(file_local_path, "rb") as fp:
                return fp.read()
        except FileNotFoundError:
            raise FileNotFound()
        except OSError as exc:
            logger.exception("An error has occurred while trying to retrieve file on local file storage: %s", exc)
            raise exc

    def delete_public_object(self, folder: str, object_id: str) -> None:
        file_local_path = self.local_path(folder, object_id)
        try:
            os.remove(file_local_path)
            os.remove(str(file_local_path) + ".type")
        except FileNotFoundError:
            # replicate gpc backend behavior on file not found
            logger.info("File not found on deletion on local storage: %s", file_local_path)
        except OSError as exc:
            logger.exception("An error has occurred while trying to delete file on local file storage: %s", exc)
            raise exc

    def list_files(self, folder: str, *, max_results: int = 1000) -> list[str]:
        results = []
        local_dir_len = len(str(self.local_dir("", ""))) + 1
        for root, dirs, files in os.walk(self.local_dir(folder, "")):
            for item in chain(dirs, files):
                results.append(f"{root}/{item}"[local_dir_len:])
                if len(results) >= max_results:
                    return results
        return results
