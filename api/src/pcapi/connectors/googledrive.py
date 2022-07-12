"""A wrapper around the Google Drive API.

Usage:

    from pcapi.connectors import googledrive

    # Use the "client email" and private key of a Google API service account.
    backend = googledrive.get_backend()
    backend.create_file("parent-folder-id", "new_file.txt", "/tmp/new_file.txt")

Unless you customize the `GOOGLE_BACKEND` environment variable, a
proper backend is chosen depending on the environment (see
`_default_google_drive_backend` in `pcapi.settings`):

- on testing, staging, prod, etc.: a real backend that really uses the
  Google Drive API;

- on dev environment and in tests: a testing, dummy backend that does
  nothing (i.e. it does not send HTTP requests to the Google Drive
  API).
"""

from io import BytesIO
import pathlib

import googleapiclient.discovery
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload

from pcapi import settings
from pcapi.utils.module_loading import import_string


def get_backend() -> "BaseBackend":
    backend_class = import_string(settings.GOOGLE_DRIVE_BACKEND)
    return backend_class()


class BaseBackend:
    def get_folder(self, parent_folder_id: str, name: str) -> str | None:
        """Return folder id if it exists, None otherwise."""
        raise NotImplementedError()

    def get_or_create_folder(self, parent_folder_id: str, name: str) -> str:
        """Create a new folder (or do nothing if it already exists) and return
        its id.
        """
        raise NotImplementedError()

    def create_file(self, parent_folder_id: str, name: str, local_path: pathlib.Path) -> str:
        """Create a new file and return its id."""
        raise NotImplementedError()

    def download_file(self, file_id: str, content_type: str | None = None) -> BytesIO:
        """Download a file and return its content"""
        raise NotImplementedError()


class TestingBackend(BaseBackend):
    def get_folder(self, parent_folder_id: str, name: str) -> str | None:
        """Return folder id if it exists, None otherwise."""
        return parent_folder_id + name

    def get_or_create_folder(self, parent_folder_id: str, name: str) -> str:
        """Create a new folder (or do nothing if it already exists) and return
        its id.
        """
        return parent_folder_id + name

    def create_file(self, parent_folder_id: str, name: str, local_path: pathlib.Path) -> str:
        """Create a new file and return its id."""
        if not local_path.exists():
            raise ValueError("The given local path should exist.")
        return parent_folder_id + name

    def download_file(self, file_id: str, content_type: str | None = None) -> BytesIO:
        """Download a file and return its content"""
        return BytesIO()


class GoogleDriveBackend(BaseBackend):
    @property
    def service(self) -> googleapiclient.discovery.Resource:
        # No need to provide credentials. Authentication is done
        # through a Kubernetes "workload identity".
        return googleapiclient.discovery.build("drive", "v3")

    def get_folder(self, parent_folder_id: str, name: str) -> str | None:
        """Return folder id if it exists, None otherwise."""
        quoted_name = name.replace("'", "\\'")
        request = self.service.files().list(
            q=(
                "mimeType = 'application/vnd.google-apps.folder' "
                f"and '{parent_folder_id}' in parents "
                f"and name = '{quoted_name}'"
            ),
            fields="files (id)",
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
        )
        response = request.execute()
        if not response["files"]:
            return None
        return response["files"][0]["id"]

    def get_or_create_folder(self, parent_folder_id: str, name: str) -> str:
        """Create a new folder (or do nothing if it already exists) and return
        its id.
        """
        existing_folder_id = self.get_folder(parent_folder_id, name)
        if existing_folder_id:
            return existing_folder_id
        request = self.service.files().create(
            body={
                "parents": [parent_folder_id],
                "name": name,
                "mimeType": "application/vnd.google-apps.folder",
            },
            fields="id",  # yes, it's a string, not a list
            supportsAllDrives=True,
        )
        response = request.execute()
        return response["id"]

    def create_file(self, parent_folder_id: str, name: str, local_path: pathlib.Path) -> str:
        """Create a new file and return its id."""
        request = self.service.files().create(
            body={
                "parents": [parent_folder_id],
                "name": name,
            },
            media_body=MediaFileUpload(filename=str(local_path)),
            fields="id",  # yes, it's a string, not a list
            supportsAllDrives=True,
        )
        response = request.execute()
        return response["id"]

    def download_file(self, file_id: str, content_type: str | None = None) -> BytesIO:
        """Download a file and return its content"""
        request = self.service.files().export_media(fileId=file_id, mimeType=content_type)
        bytes_io = BytesIO()
        downloader = MediaIoBaseDownload(bytes_io, request)
        done = False
        while done is False:
            _, done = downloader.next_chunk()
        bytes_io.seek(0)
        return bytes_io
