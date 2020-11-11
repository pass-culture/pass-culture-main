import re
from unittest.mock import patch

import pytest

from pcapi.local_providers import TiteLiveThingDescriptions
from pcapi.repository import repository
from pcapi.repository.provider_queries import get_provider_by_local_class


class TiteLiveThingDescriptionsTest:
    class InitTest:
        @patch(
            "pcapi.local_providers.titelive_thing_descriptions.titelive_thing_descriptions.get_files_to_process_from_titelive_ftp"
        )
        @pytest.mark.usefixtures("db_session")
        def test_should_call_titelive_ftp_to_get_files_list(self, mock_get_files_to_process_from_titelive, app):
            # Given
            titelive_description_provider = get_provider_by_local_class("TiteLiveThingDescriptions")
            mock_get_files_to_process_from_titelive.return_value = ["Resume191012.zip", "Resume201012.zip"]
            repository.save(titelive_description_provider)

            # When
            titelive_description_provider = TiteLiveThingDescriptions()

            # Then
            mock_get_files_to_process_from_titelive.assert_called_once_with(
                "ResumesLivres", re.compile(r"Resume(\d{6}).zip")
            )
            titelive_description_provider.zips = ["Resume191012.zip", "Resume201012.zip"]

    class NextTest:
        @patch(
            "pcapi.local_providers.titelive_thing_descriptions.titelive_thing_descriptions.get_files_to_process_from_titelive_ftp"
        )
        @patch("pcapi.local_providers.titelive_thing_descriptions.titelive_thing_descriptions.get_zip_file_from_ftp")
        @patch("pcapi.local_providers.titelive_thing_descriptions.titelive_thing_descriptions.get_date_from_filename")
        @pytest.mark.usefixtures("db_session")
        def test_should_iterate_over_2_zip_files(
            self, mock_get_date_from_filename, mock_get_zip_file_from_ftp, mock_get_files_to_process_from_titelive
        ):
            # Given
            titelive_description_provider = get_provider_by_local_class("TiteLiveThingDescriptions")
            mock_get_files_to_process_from_titelive.return_value = ["Resume191012.zip", "Resume191013.zip"]
            mock_get_zip_file_from_ftp.side_effect = [
                MockZipFile(filename="Resume191012.zip"),
                MockZipFile(filename="Resume191013.zip"),
            ]
            mock_get_date_from_filename.side_effect = {"191012", "191013"}

            repository.save(titelive_description_provider)
            titelive_description_provider = TiteLiveThingDescriptions()

            # When
            with pytest.raises(StopIteration):
                next(titelive_description_provider)

            # Then
            mock_get_files_to_process_from_titelive.assert_called_once_with(
                "ResumesLivres", re.compile(r"Resume(\d{6}).zip")
            )
            assert mock_get_zip_file_from_ftp.call_count == 2
            assert mock_get_date_from_filename.call_count == 3


class MockZipFile:
    def __init__(self, filename: str):
        self.filename = filename
        self.filelist = [self]

    def __next__(self):
        return self.filename

    def infolist(self):
        return self.filelist
