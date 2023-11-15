import datetime
import io
import re
from unittest.mock import patch

import pytest

from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.local_providers import TiteLiveThingDescriptions
from pcapi.repository import repository


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
        def test_should_update_product_and_offers_description(
            self, mock_get_date_from_filename, mock_get_zip_file_from_ftp, mock_get_files_to_process_from_titelive
        ):
            # Given
            titelive_description_provider = get_provider_by_local_class("TiteLiveThingDescriptions")
            product = offers_factories.ProductFactory(
                description="old description",
                idAtProviders="9782809455069",
                lastProviderId=titelive_description_provider.id,
            )
            offers_factories.OfferFactory(product=product, description="other description")

            tomorrow = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).strftime("%y%m%d")

            mock_get_files_to_process_from_titelive.return_value = [f"Resume{tomorrow}.zip"]
            mock_zip_file = MockZipFile(
                filename=f"Resume{tomorrow}.zip", filelist=[MockFile("9782809455069_p.txt", "A passionate description")]
            )
            mock_get_zip_file_from_ftp.side_effect = [
                mock_zip_file,
            ]
            mock_get_date_from_filename.side_effect = {tomorrow}
            repository.save(titelive_description_provider)

            # When
            titelive_description_provider = TiteLiveThingDescriptions()
            titelive_description_provider.updateObjects()
            titelive_description_provider.postTreatment()

            # Then
            product = offers_models.Product.query.one()
            assert product.description == "A passionate description"

            offer = offers_models.Offer.query.one()
            assert offer.description == "A passionate description"

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
    def __init__(self, filename: str, filelist: list = None):
        self.filename = filename
        self.filelist = filelist if filelist else [self]

    def __next__(self):
        return self.filename

    def infolist(self):
        return self.filelist

    def open(self, file):
        return io.BytesIO(file.description.encode("iso-8859-1"))


class MockFile:
    def __init__(self, filename: str, description: str):
        self._filename = filename
        self._description = description

    @property
    def filename(self):
        return self._filename

    @property
    def description(self):
        return self._description
