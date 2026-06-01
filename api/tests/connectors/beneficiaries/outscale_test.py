import logging
import pathlib
from unittest.mock import patch

from botocore.exceptions import ClientError

from pcapi import settings
from pcapi.connectors.beneficiaries import outscale

import tests


IMAGES_DIR = pathlib.Path(tests.__path__[0]) / "files"


class UploadFileTest:
    def test_upload_file_not_found(self, caplog) -> None:
        unexisting_file_name = "unexisting_file.png"
        expected_log_message = f"No such file or directory: '{unexisting_file_name}'"

        with caplog.at_level(logging.INFO):
            result = outscale.upload_file(
                user_id="unkown_user", file_path=unexisting_file_name, file_name=unexisting_file_name
            )

        assert result is False
        assert len(caplog.records) >= 1
        record = caplog.records[0]
        assert expected_log_message in record.message

    @patch("botocore.session.Session.create_client")
    def test_upload_file_succesfully(self, mocked_storage_client, caplog) -> None:
        file_name = "carte_identite_front.png"
        file_path = f"{IMAGES_DIR}/{file_name}"
        expected_log_message = "Outscale upload started"
        user_id = "some-user-id"

        with caplog.at_level(logging.INFO):
            outscale.upload_file(user_id, file_path, file_name)

        assert mocked_storage_client.return_value.upload_file.call_count == 1
        assert len(caplog.records) >= 1
        record = caplog.records[0]
        assert expected_log_message in record.message
        assert record.extra["file_name"] == file_name


class ReadFileTest:
    @patch("boto3.s3.inject.download_fileobj")
    def test_download_file_successfully(self, mock_download_fileobj):
        content = outscale.read_file("123", "file.png", access_key="test", secret_key="secret")

        assert content == b""  # mock does not write anything in buffer

        mock_download_fileobj.assert_called_once()
        assert mock_download_fileobj.call_args[0] == (settings.OUTSCALE_SECNUM_BUCKET_NAME, "123/file.png")

    @patch(
        "boto3.s3.inject.download_fileobj",
        side_effect=ClientError({"Error": {"Code": "403", "Message": "Forbidden"}}, "test"),
    )
    def test_download_file_access_denied(self, mock_download_fileobj):
        content = outscale.read_file("123", "file.png", access_key="test", secret_key="secret")

        assert content is None

        mock_download_fileobj.assert_called_once()
        assert mock_download_fileobj.call_args[0] == (settings.OUTSCALE_SECNUM_BUCKET_NAME, "123/file.png")
