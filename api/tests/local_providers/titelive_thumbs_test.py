from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

import pytest

import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Product
from pcapi.local_providers import TiteLiveThingThumbs
from pcapi.repository import repository
import pcapi.sandboxes
from pcapi.utils.human_ids import humanize


class TiteliveThingThumbsTest:

    @patch("pcapi.local_providers.titelive_thing_thumbs.titelive_thing_thumbs.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_thing_thumbs.titelive_thing_thumbs.get_zip_file_from_ftp")
    @patch("pcapi.core.object_storage.store_public_object")
    def test_handle_only_relevant_thumb_files(
        self, mock_store_public_object, get_thumbs_zip_file_from_ftp, get_ordered_thumbs_zip_files, app
    ):
        product_with_new_thumbs = offers_factories.ProductFactory(idAtProviders="9782957799015")
        assert product_with_new_thumbs.thumbCount == 0
        _product_without_new_thumbs = offers_factories.ProductFactory(idAtProviders="9782016200000")
        zip_thumb_file = get_zip_with_1_relevant_thumb_file()
        get_ordered_thumbs_zip_files.return_value = [zip_thumb_file]
        get_thumbs_zip_file_from_ftp.side_effect = [get_zip_file_from_sandbox(zip_thumb_file)]
        # Import thumb for existing things
        provider_object = TiteLiveThingThumbs()
        provider_object.provider.isActive = True
        repository.save(provider_object.provider)

        assert Product.query.count() == 2

        provider_object.updateObjects()

        assert Product.query.count() == 2  # same count as before calling `updateObjects()`
        assert provider_object.checkedObjects == 1
        assert provider_object.createdObjects == 0
        assert provider_object.updatedObjects == 1
        assert provider_object.erroredObjects == 0
        assert provider_object.checkedThumbs == 1
        assert provider_object.createdThumbs == 1
        assert provider_object.updatedThumbs == 0
        assert provider_object.erroredThumbs == 0
        assert product_with_new_thumbs.thumbCount == 1
        mock_store_public_object.assert_called_once()
        assert mock_store_public_object.call_args.kwargs["folder"] == "thumbs"
        assert (
            mock_store_public_object.call_args.kwargs["object_id"] == f"products/{humanize(product_with_new_thumbs.id)}"
        )
        assert mock_store_public_object.call_args.kwargs["content_type"] == "image/jpeg"
        # no assert on the blob since it is very slow to compare the content of files


def get_zip_with_1_relevant_thumb_file():
    """
    The zip file contains
    9780847858903_1_75.jpg
    9780847858903_1_v.jpg
    9782957799015_1_75.jpg <- This is the relevant file for our test
    9782957799015_1_v.jpg
    9782957799015_4_75.jpg
    """
    return get_zip_thumbs_file_from_named_sandbox_file("test_livres_tl20221128.zip")


def get_zip_thumbs_file_from_named_sandbox_file(file_name):
    data_root_path = Path(pcapi.sandboxes.__path__[0]) / "providers" / "titelive_mocks"
    return data_root_path / file_name


def get_zip_file_from_sandbox(file):
    return ZipFile(file)
