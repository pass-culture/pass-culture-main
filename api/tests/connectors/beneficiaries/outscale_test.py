import logging
import pathlib
from unittest.mock import patch

from pcapi.connectors.beneficiaries import outscale

import tests


IMAGES_DIR = pathlib.Path(tests.__path__[0]) / "files"


class UploadFileTest:
    def test_upload_file_not_found(self, caplog) -> None:
        # Given
        unexisting_file_name = "unexisting_file.png"
        expected_log_message = f"No such file or directory: '{unexisting_file_name}'"

        # When
        with caplog.at_level(logging.INFO):
            result = outscale.upload_file(
                user_id="unkown_user", file_path=unexisting_file_name, file_name=unexisting_file_name
            )

        # Then
        assert result is False
        assert len(caplog.records) >= 1
        record = caplog.records[0]
        assert expected_log_message in record.message

    @patch("pcapi.connectors.beneficiaries.outscale.boto3.client")
    def test_upload_file_succesfully(self, mock_s3_client, caplog) -> None:
        # Given
        file_name = "carte_identite_front.png"
        file_path = f"{IMAGES_DIR}/{file_name}"
        expected_log_message = "Outscale upload started"
        user_id = "some-user-id"

        # When
        with caplog.at_level(logging.INFO):
            outscale.upload_file(user_id, file_path, file_name)

        # Then
        assert mock_s3_client.return_value.upload_file.call_count == 1
        assert len(caplog.records) >= 1
        record = caplog.records[0]
        assert expected_log_message in record.message
        assert record.extra["file_name"] == file_name
