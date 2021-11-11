""" local providers test """

from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

import pytest

from pcapi.local_providers import TiteLiveThingThumbs
from pcapi.local_providers.titelive_thing_thumbs.titelive_thing_thumbs import extract_thumb_index
from pcapi.model_creators.provider_creators import provider_test
from pcapi.model_creators.specific_creators import create_product_with_thing_subcategory
from pcapi.models import Product
from pcapi.repository import repository
import pcapi.sandboxes


class TiteliveThingThumbsTest:
    class ExtractThumbIndexTest:
        def test_return_0_for_filename_with_1_75(self):
            # Given
            filename = "9780847858903_1_75.jpg"

            # When
            thumb_index = extract_thumb_index(filename)

            # Then
            assert thumb_index == 1

        def test_return_4_for_filename_with_4(self):
            # Given
            filename = "9780847858903_4_75.jpg"

            # When
            thumb_index = extract_thumb_index(filename)

            # Then
            assert thumb_index == 4

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_thing_thumbs.titelive_thing_thumbs.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_thing_thumbs.titelive_thing_thumbs.get_zip_file_from_ftp")
    def test_compute_first_thumb_dominant_color_even_if_not_first_file(
        self, get_thumbs_zip_file_from_ftp, get_ordered_thumbs_zip_files, app
    ):
        # given
        product1 = create_product_with_thing_subcategory(id_at_providers="9780847858903", thumb_count=0)
        product2 = create_product_with_thing_subcategory(id_at_providers="9782016261903", thumb_count=0)
        repository.save(product1, product2)
        zip_thumb_file = get_zip_with_2_usable_thumb_files()
        get_ordered_thumbs_zip_files.return_value = [zip_thumb_file]
        get_thumbs_zip_file_from_ftp.side_effect = [get_zip_file_from_sandbox(zip_thumb_file)]

        # Import thumbs for existing things
        provider_test(
            app,
            TiteLiveThingThumbs,
            None,
            checkedObjects=2,
            createdObjects=0,
            updatedObjects=2,
            erroredObjects=0,
            checkedThumbs=2,
            createdThumbs=5,
            updatedThumbs=0,
            erroredThumbs=0,
            Product=0,
        )

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_thing_thumbs.titelive_thing_thumbs.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_thing_thumbs.titelive_thing_thumbs.get_zip_file_from_ftp")
    def test_updates_thumb_count_for_product_when_new_thumbs_added(
        self, get_thumbs_zip_file_from_ftp, get_ordered_thumbs_zip_files, app
    ):
        # Given
        product1 = create_product_with_thing_subcategory(id_at_providers="9780847858903", thumb_count=0)
        repository.save(product1)
        zip_thumb_file = get_zip_with_1_usable_thumb_file()
        get_ordered_thumbs_zip_files.return_value = [zip_thumb_file]
        get_thumbs_zip_file_from_ftp.side_effect = [get_zip_file_from_sandbox(zip_thumb_file)]

        provider_object = TiteLiveThingThumbs()
        provider_object.provider.isActive = True
        repository.save(provider_object.provider)

        # When
        provider_object.updateObjects()

        # Then
        new_product = Product.query.one()
        assert new_product.name == "Test Book"
        assert new_product.thumbCount == 1


def get_zip_with_2_usable_thumb_files():
    return get_zip_thumbs_file_from_named_sandbox_file("test_livres_tl20190505.zip")


def get_zip_with_1_usable_thumb_file():
    return get_zip_thumbs_file_from_named_sandbox_file("test_livres_tl20191104.zip")


def get_zip_thumbs_file_from_named_sandbox_file(file_name):
    data_root_path = Path(pcapi.sandboxes.__path__[0]) / "providers" / "titelive_mocks"
    return data_root_path / file_name


def get_zip_file_from_sandbox(file):
    return ZipFile(file)  # pylint: disable=consider-using-with
