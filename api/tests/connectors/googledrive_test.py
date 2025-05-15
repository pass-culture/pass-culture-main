import functools
import io
import json
import urllib.parse
from unittest import mock

import httplib2
import pytest

from pcapi.connectors import googledrive


def mock_response(mocked, response_data):
    """Mock a response for googleapiclient."""
    response = httplib2.Response(
        {
            "status": 200,
            "headers": {"content-type": "application/json"},
        }
    )
    mocked.return_value = response, response_data


def mock_credentials(test_func):
    """Mock credentials for googleapiclient.

    ``googleapiclient`` expects to find credentials somewhere (in an
    environment variable, in a file set up by Google Cloud SDK, etc.).
    It works on real environments because we use Kubernetes "workload
    identity", but it fails on CI (and on unconfigured developer's
    machines). Here we fake default credentials.
    """

    def fake_credentials(*args, **kwargs):
        return None, "project_id"

    @functools.wraps(test_func)
    def wrapped(*args, **kwargs):
        with mock.patch("google.auth.default", fake_credentials):
            return test_func(*args, **kwargs)

    return wrapped


@pytest.mark.settings(GOOGLE_DRIVE_BACKEND="pcapi.connectors.googledrive.GoogleDriveBackend")
@mock_credentials
@mock.patch("googleapiclient.http._retry_request")
def test_get_folder(mocked_request):
    mock_response(mocked_request, json.dumps({"files": [{"id": "folder-id"}]}))

    backend = googledrive.get_backend()
    folder_id = backend.get_folder("parent-folder-id", "name 'with' single quotes")

    assert folder_id == "folder-id"
    mocked_request.assert_called_once()
    url = mocked_request.call_args_list[0].args[5]
    url, query = url.split("?")
    assert url == "https://www.googleapis.com/drive/v3/files"
    query = urllib.parse.parse_qs(query)
    assert query == {
        "q": [
            # fmt: off
            "mimeType = 'application/vnd.google-apps.folder' "
            "and 'parent-folder-id' in parents "
            r"and name = 'name \'with\' single quotes'"
            # fmt: on
        ],
        "fields": ["files (id)"],
        "includeItemsFromAllDrives": ["true"],
        "supportsAllDrives": ["true"],
        "alt": ["json"],
    }


@pytest.mark.settings(GOOGLE_DRIVE_BACKEND="pcapi.connectors.googledrive.GoogleDriveBackend")
@mock_credentials
@mock.patch("googleapiclient.http._retry_request")
@mock.patch(
    "pcapi.connectors.googledrive.GoogleDriveBackend.get_folder",
    lambda self_, parent_folder_id, name: None,  # folder does not exist yet
)
def test_get_or_create_folder_new_folder(mocked_request):
    mock_response(mocked_request, json.dumps({"id": "folder-id"}))

    backend = googledrive.get_backend()
    folder_id = backend.get_or_create_folder("parent-folder-id", "name")

    assert folder_id == "folder-id"
    mocked_request.assert_called_once()
    url = mocked_request.call_args_list[0].args[5].split("?")[0]
    assert url == "https://www.googleapis.com/drive/v3/files"
    assert mocked_request.call_args_list[0].kwargs["method"] == "POST"
    body = json.loads(mocked_request.call_args_list[0].kwargs["body"])
    assert body == {
        "parents": ["parent-folder-id"],
        "name": "name",
        "mimeType": "application/vnd.google-apps.folder",
    }


@pytest.mark.settings(GOOGLE_DRIVE_BACKEND="pcapi.connectors.googledrive.GoogleDriveBackend")
@mock_credentials
@mock.patch(
    "pcapi.connectors.googledrive.GoogleDriveBackend.get_folder",
    lambda self_, parent_folder_id, name: "existing-id",  # folder already exists
)
def test_get_or_create_folder_existing_folder():
    backend = googledrive.get_backend()
    folder_id = backend.get_or_create_folder("parent-folder-id", "name")

    assert folder_id == "existing-id"


@pytest.mark.settings(GOOGLE_DRIVE_BACKEND="pcapi.connectors.googledrive.GoogleDriveBackend")
@mock_credentials
@mock.patch("googleapiclient.http._retry_request")
def test_create_file(mocked_request, tmpdir):
    mock_response(mocked_request, json.dumps({"id": "file-id"}))

    backend = googledrive.get_backend()
    path = tmpdir / "tmp.txt"
    path.write_text("dummy data", "utf-8")
    file_id = backend.create_file("parent-folder-id", "name", path)

    assert file_id == "file-id"
    mocked_request.assert_called_once()
    url = mocked_request.call_args_list[0].args[5].split("?")[0]
    assert url == "https://www.googleapis.com/upload/drive/v3/files"
    assert mocked_request.call_args_list[0].kwargs["method"] == "POST"
    # It's MIME-encoded, don't bother to decode, just take a peek.
    assert b"dummy data" in mocked_request.call_args_list[0].kwargs["body"]


@pytest.mark.settings(GOOGLE_DRIVE_BACKEND="pcapi.connectors.googledrive.GoogleDriveBackend")
@mock_credentials
@mock.patch("googleapiclient.http._retry_request")
def test_download_file(mocked_request):
    mocked_request.return_value = (
        httplib2.Response({"status": 200, "headers": {"content-type": "text/csv"}}),
        b"abc,def\nghi,jkl",
    )

    backend = googledrive.get_backend()
    content = backend.download_file("file-id", "text/csv")

    assert isinstance(content, io.BytesIO)
    assert content.getvalue() == b"abc,def\nghi,jkl"
    mocked_request.assert_called_once()
    url = mocked_request.call_args_list[0].args[5]
    url, query = url.split("?")
    assert url == "https://www.googleapis.com/drive/v3/files/file-id/export"
    assert query == "mimeType=text%2Fcsv&alt=media"


@pytest.mark.settings(GOOGLE_DRIVE_BACKEND="pcapi.connectors.googledrive.GoogleDriveBackend")
@mock_credentials
@mock.patch("googleapiclient.http._retry_request")
def test_search_file(mocked_request, tmpdir):
    mock_response(mocked_request, json.dumps({"files": [{"id": "file-id"}]}))

    backend = googledrive.get_backend()
    file_id = backend.search_file("parent-folder-id", "name")

    assert file_id == "file-id"
    mocked_request.assert_called_once()
    url = mocked_request.call_args_list[0].args[5]
    assert (
        url == "https://www.googleapis.com/drive/v3/files"
        "?q=name%3D%27name%27+and+%27parent-folder-id%27+in+parents+and+trashed+%3D+false&spaces=drive&fields=files%28id%29&supportsAllDrives=true&includeItemsFromAllDrives=true&alt=json"
    )
    assert mocked_request.call_args_list[0].kwargs["method"] == "GET"
    assert mocked_request.call_args_list[0].kwargs["body"] is None


@pytest.mark.settings(GOOGLE_DRIVE_BACKEND="pcapi.connectors.googledrive.GoogleDriveBackend")
@mock_credentials
@mock.patch("googleapiclient.http._retry_request")
def test_create_spreadsheet(mocked_request, tmpdir):
    mock_response(mocked_request, json.dumps({"id": "file-id"}))

    backend = googledrive.get_backend()
    file_id = backend.create_spreadsheet("parent-folder-id", "name")

    assert file_id == "file-id"
    mocked_request.assert_called_once()
    url = mocked_request.call_args_list[0].args[5].split("?")[0]
    assert url == "https://www.googleapis.com/drive/v3/files"
    assert mocked_request.call_args_list[0].kwargs["method"] == "POST"
    assert (
        mocked_request.call_args_list[0].kwargs["body"]
        == '{"parents": ["parent-folder-id"], "name": "name", "mimeType": "application/vnd.google-apps.spreadsheet"}'
    )


@pytest.mark.settings(GOOGLE_DRIVE_BACKEND="pcapi.connectors.googledrive.GoogleDriveBackend")
@mock_credentials
@mock.patch("googleapiclient.http._retry_request")
def test_append_to_spreadsheet(mocked_request, tmpdir):
    mock_response(
        mocked_request,
        json.dumps(
            {
                "spreadsheetId": "file-id",
                "tableRange": "'Feuille 1'!A1:D8",
                "updates": {
                    "spreadsheetId": "file-id",
                    "updatedRange": "'Feuille 1'!A9:D10",
                    "updatedRows": 2,
                    "updatedColumns": 4,
                    "updatedCells": 8,
                },
            }
        ),
    )

    backend = googledrive.get_backend()
    added_rows = backend.append_to_spreadsheet("file-id", [["One", "Two", "3", 4], ["Five", "Six", "7", 8.0]])

    assert added_rows == 2
    mocked_request.assert_called_once()
    url = mocked_request.call_args_list[0].args[5].split("?")[0]
    assert url == "https://sheets.googleapis.com/v4/spreadsheets/file-id/values/1%3A1:append"
    assert mocked_request.call_args_list[0].kwargs["method"] == "POST"
    assert (
        mocked_request.call_args_list[0].kwargs["body"]
        == '{"values": [["One", "Two", "3", 4], ["Five", "Six", "7", 8.0]]}'
    )
