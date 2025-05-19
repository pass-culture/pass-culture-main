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

- on dev environment to debug connection to Google APIs: a way to configure
  a temporary service account in GOOGLE_DRIVE_SERVICE_ACCOUNT_INFO.
"""

import json
import pathlib
import typing
from io import BytesIO

import googleapiclient.discovery
from google.oauth2 import service_account
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

    def create_file(
        self,
        parent_folder_id: str,
        name: str,
        local_path: pathlib.Path,
        response_field: typing.Literal["id", "webContentLink"] = "id",
    ) -> str:
        """Create a new file and return its id by default.
        Return file download link if response_field = 'webContentLink'."""
        raise NotImplementedError()

    def download_file(self, file_id: str, content_type: str | None = None) -> BytesIO:
        """Download a file and return its content"""
        raise NotImplementedError()

    def search_file(self, parent_folder_id: str, name: str) -> str | None:
        """Search for an existing file and return its id, if it exists."""
        raise NotImplementedError()

    def create_spreadsheet(self, parent_folder_id: str, name: str) -> str:
        """Create a new spreadsheet and return its id."""
        raise NotImplementedError()

    def append_to_spreadsheet(self, spreadsheet_id: str, lines: list[list[typing.Any]]) -> int:
        """Append new lines in a spreadsheet"""
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

    def create_file(
        self, parent_folder_id: str, name: str, local_path: pathlib.Path, response_field: str = "id"
    ) -> str:
        """Create a new file and return its id by default.
        Return file download link if response_field = 'webContentLink'.
        """
        if not local_path.exists():
            raise ValueError("The given local path should exist.")
        return parent_folder_id + name

    def download_file(self, file_id: str, content_type: str | None = None) -> BytesIO:
        """Download a file and return its content"""
        return BytesIO()

    def search_file(self, parent_folder_id: str, name: str) -> str | None:
        """Search for an existing file and return its id, if it exists."""
        return parent_folder_id + name

    def create_spreadsheet(self, parent_folder_id: str, name: str) -> str:
        """Create a new spreadsheet and return its id."""
        return parent_folder_id + name

    def append_to_spreadsheet(self, spreadsheet_id: str, rows: list[list[typing.Any]]) -> int:
        """Append new rows in a spreadsheet"""
        return len(rows)


class GoogleDriveBackend(BaseBackend):
    @property
    def credentials(self) -> service_account.Credentials | None:
        # No need to provide credentials. Authentication is done
        # through a Kubernetes "workload identity".
        return None

    @property
    def service(self) -> googleapiclient.discovery.Resource:
        return googleapiclient.discovery.build("drive", "v3", credentials=self.credentials)

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

    def create_file(
        self, parent_folder_id: str, name: str, local_path: pathlib.Path, response_field: str = "id"
    ) -> str:
        """Create a new file and return its id by default.
        Return file download link if response_field = 'webContentLink'."""
        request = self.service.files().create(
            body={
                "parents": [parent_folder_id],
                "name": name,
            },
            media_body=MediaFileUpload(filename=str(local_path)),
            fields="id,webContentLink",  # yes, it's a string, not a list
            supportsAllDrives=True,
        )
        response = request.execute()
        return response.get(response_field, "")

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

    def search_file(self, parent_folder_id: str, name: str) -> str | None:
        """
        Search for an existing file and return its id, if it exists.
        Documentation: https://developers.google.com/drive/api/reference/rest/v3/files/list?hl=fr
        """
        request = self.service.files().list(
            q=f"name='{name}' and '{parent_folder_id}' in parents and trashed = false",
            spaces="drive",
            fields="files(id)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        )
        response = request.execute()
        if not response["files"]:
            return None
        if len(response["files"]) > 1:
            raise ValueError("More than one file found")
        return response["files"][0]["id"]

    def create_spreadsheet(self, parent_folder_id: str, name: str) -> str:
        """Create a new spreadsheet and return its id."""
        # Use files.create because spreadsheet.create does not allow to create spreadsheet in a specific folder
        # See: https://developers.google.com/sheets/api/guides/create?hl=fr
        request = self.service.files().create(
            body={"parents": [parent_folder_id], "name": name, "mimeType": "application/vnd.google-apps.spreadsheet"},
            fields="id",  # yes, it's a string, not a list
            supportsAllDrives=True,
        )
        response = request.execute()
        return response["id"]

    @property
    def sheets_service(self) -> googleapiclient.discovery.Resource:
        # No need to provide credentials. Authentication is done
        # through a Kubernetes "workload identity".
        return googleapiclient.discovery.build("sheets", "v4", credentials=self.credentials)

    def append_to_spreadsheet(self, spreadsheet_id: str, rows: list[list[typing.Any]]) -> int:
        """
        Append new rows in a spreadsheet
        Documentation: https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/append?hl=fr
        """
        request = (
            self.sheets_service.spreadsheets()
            .values()
            .append(
                spreadsheetId=spreadsheet_id,
                range="1:1",
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body={"values": rows},
            )
        )
        response = request.execute()
        return response["updates"]["updatedRows"]


class DevGoogleDriveBackend(GoogleDriveBackend):
    """
    For development and debug: use a personal service account.
    Create from here: https://console.cloud.google.com/iam-admin/serviceaccounts
    GOOGLE_DRIVE_SERVICE_ACCOUNT_INFO must be set with a valid service account key (json), which has write permission
    to the folder and/or files used in API calls.
    """

    SCOPES = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]

    @property
    def credentials(self) -> service_account.Credentials | None:
        assert settings.GOOGLE_DRIVE_SERVICE_ACCOUNT_INFO  # helps mypy
        service_account_info = json.loads(settings.GOOGLE_DRIVE_SERVICE_ACCOUNT_INFO)
        return service_account.Credentials.from_service_account_info(service_account_info, scopes=self.SCOPES)
