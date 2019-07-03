""" local providers test """
from pathlib import Path
from unittest.mock import patch

import os
from zipfile import ZipFile

from datetime import datetime

from local_providers import TiteLiveThingThumbs
from local_providers.titelive_thing_thumbs import THUMB_FOLDER_NAME_TITELIVE, extract_thumb_index, \
    get_thumb_date_at_thumb_index
from models import PcObject
from tests.conftest import clean_database
from tests.test_utils import provider_test, create_product_with_Thing_type


class TiteliveThingThumbsTest:

    def test_extract_thumb_index_return_0_for_filename_with_1_75(self):
        # Given
        filename = "9780847858903_1_75.jpg"

        # When
        thumb_index = extract_thumb_index(filename)

        # Then
        assert thumb_index == 0

    def test_extract_thumb_index_return_3_for_filename_with_4(self):
        # Given
        filename = "9780847858903_4_75.jpg"

        # When
        thumb_index = extract_thumb_index(filename)

        # Then
        assert thumb_index == 3

    def test_get_thumb_date_at_thumb_index_return_only_thumb_date_if_first_thumb(self):
        # Given
        thumb_index = 1
        thumb_date = datetime.utcnow()

        # When
        list_thumb_dates = get_thumb_date_at_thumb_index(thumb_index, thumb_date)

        # Then
        assert list_thumb_dates == [None, thumb_date]

    def test_get_thumb_date_at_thumb_index_return_thumb_date_at_3_position(self):
        # Given
        thumb_index = 4
        thumb_date = datetime.utcnow()

        # When
        list_thumb_dates = get_thumb_date_at_thumb_index(thumb_index, thumb_date)

        # Then
        assert list_thumb_dates == [None, None, None, None, thumb_date]

    @clean_database
    @patch('local_providers.titelive_thing_thumbs.get_files_to_process_from_titelive_ftp')
    @patch('local_providers.titelive_thing_thumbs.get_zip_file_from_ftp')
    def test_compute_firsrt_thumb_dominant_color_even_if_not_first_file(self,
                                                                        get_thumbs_zip_file_from_ftp,
                                                                        get_ordered_thumbs_zip_files,
                                                                        app):
        # given
        product1 = create_product_with_Thing_type(id_at_providers='9780847858903', thumb_count=0)
        product2 = create_product_with_Thing_type(id_at_providers='9782016261903', thumb_count=0)
        PcObject.save(product1, product2)

        # mock TiteliveThingThumb
        files = get_ordered_zip_thumbs_files_from_sandbox_files()
        get_ordered_thumbs_zip_files.return_value = files

        zip_files = []
        for file in files:
            zip_file = get_zip_file_from_sandbox(file)
            zip_files.append(zip_file)
        get_thumbs_zip_file_from_ftp.side_effect = zip_files

        # Import thumbs for existing things
        provider_test(app,
                      TiteLiveThingThumbs,
                      None,
                      checkedObjects=2,
                      createdObjects=0,
                      updatedObjects=0,
                      erroredObjects=0,
                      checkedThumbs=2,
                      createdThumbs=2,
                      updatedThumbs=0,
                      erroredThumbs=0,
                      Product=0
                      )


def get_ordered_zip_thumbs_files_from_sandbox_files():
    data_root_path = Path(os.path.dirname(os.path.realpath(__file__))) \
                     / '..' / '..' / 'sandboxes' / 'providers' / 'titelive_works'
    data_thumbs_path = data_root_path / THUMB_FOLDER_NAME_TITELIVE
    all_zips = list(sorted(data_thumbs_path.glob('test_livres_tl*.zip')))
    return all_zips


def get_zip_file_from_sandbox(file):
    return ZipFile(file)
