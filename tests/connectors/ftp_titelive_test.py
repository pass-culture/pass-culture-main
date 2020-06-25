from unittest.mock import patch, MagicMock

from pytest_mock import mocker

from connectors.ftp_titelive import get_zip_file_from_ftp


class GetZipFileFromFtpTest:
    @patch('connectors.ftp_titelive.connect_to_titelive_ftp')
    def test_should_not_return_error_when_trying_to_get_empty_file(self, connect_ftp_mock: mocker):
        # Given
        connect_ftp_mock.retrbinary = MagicMock()
        connect_ftp_mock.retrbinary.return_value = None
        zip_file_name = 'Resume200618.zip'
        folder_name = 'tests/files/'

        # When
        zip_file_result = get_zip_file_from_ftp(zip_file_name, folder_name)

        # Then
        assert zip_file_result is None

