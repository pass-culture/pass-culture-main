import os
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

from sqlalchemy import func

from local_providers import TiteLiveThings, TiteLiveThingThumbs, TiteLiveThingDescriptions
from local_providers.titelive_thing_descriptions import DESCRIPTION_FOLDER_NAME_TITELIVE
from local_providers.titelive_thing_thumbs import THUMB_FOLDER_NAME_TITELIVE
from local_providers.titelive_things import THINGS_FOLDER_NAME_TITELIVE
from models import Product
from models.db import db
from models.pc_object import PcObject
from tests.conftest import clean_database
from tests.test_utils import create_offerer, create_venue, \
    provider_test
from utils.logger import logger


class TiteliveTest:

    @clean_database
    @patch('local_providers.titelive_things.get_files_to_process_from_titelive_ftp')
    @patch('local_providers.titelive_things.get_lines_from_thing_file')
    @patch('local_providers.titelive_thing_thumbs.get_files_to_process_from_titelive_ftp')
    @patch('local_providers.titelive_thing_thumbs.get_zip_file_from_ftp')
    @patch('local_providers.titelive_thing_descriptions.get_files_to_process_from_titelive_ftp')
    @patch('local_providers.titelive_thing_descriptions.get_zip_file_from_ftp')
    def test_titelive_complete_integration(self,
                                           get_description_zip_file_from_ftp,
                                           get_ordered_descriptions_zip_from_titelive_ftp,
                                           get_thumbs_zip_file_from_ftp,
                                           get_ordered_thumbs_zip_files,
                                           get_lines_from_thing_file,
                                           get_files_to_process_from_titelive_ftp,
                                           app):
        # mock TiteliveThings
        files = get_ordered_thing_files_from_sandbox_files()
        get_files_to_process_from_titelive_ftp.return_value = files

        zip_files = []
        for file in files:
            zip_file = get_lines_from_thing_file_sandboxes(file)
            zip_files.append(zip_file)

        get_lines_from_thing_file.side_effect = zip_files

        # given
        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
        PcObject.save(venue)

        # Import things
        provider_test(app,
                      TiteLiveThings,
                      None,
                      checkedObjects=422,
                      createdObjects=339,
                      updatedObjects=16,
                      erroredObjects=0,
                      checkedThumbs=0,
                      createdThumbs=0,
                      updatedThumbs=0,
                      erroredThumbs=0,
                      Product=339
                      )

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
                      checkedObjects=62,
                      createdObjects=0,
                      updatedObjects=0,
                      erroredObjects=0,
                      checkedThumbs=62,
                      createdThumbs=107,
                      updatedThumbs=0,
                      erroredThumbs=0,
                      Product=0
                      )

        assert db.session.query(func.sum(Product.thumbCount)).scalar() == 92

        # mock TiteliveThingDescription
        files = get_ordered_zip_description_files_from_sandbox_files()
        get_ordered_descriptions_zip_from_titelive_ftp.return_value = files

        logger.info(files)
        zip_files = []
        for file in files:
            logger.info(file)
            zip_file = get_zip_file_from_sandbox(file)
            zip_files.append(zip_file)
        get_description_zip_file_from_ftp.side_effect = zip_files

        # Import description for existing things
        provider_test(app,
                      TiteLiveThingDescriptions,
                      None,
                      checkedObjects=6,
                      createdObjects=0,
                      updatedObjects=6,
                      erroredObjects=0,
                      checkedThumbs=0,
                      createdThumbs=0,
                      updatedThumbs=0,
                      erroredThumbs=0,
                      Product=0
                      )


def get_ordered_thing_files_from_sandbox_files():
    data_root_path = Path(os.path.dirname(os.path.realpath(__file__))) \
                     / '..' / '..' / 'sandboxes' / 'providers' / 'titelive_works'

    data_thing_paths = data_root_path / THINGS_FOLDER_NAME_TITELIVE
    all_thing_files = sorted(data_thing_paths.glob('Quotidien*.tit'))
    return all_thing_files


def get_lines_from_thing_file_sandboxes(file):
    with open(file, 'r', encoding='iso-8859-1') as f:
        data_lines = iter(f.readlines())
    return data_lines


def get_ordered_zip_thumbs_files_from_sandbox_files():
    data_root_path = Path(os.path.dirname(os.path.realpath(__file__))) \
                     / '..' / '..' / 'sandboxes' / 'providers' / 'titelive_works'
    data_thumbs_path = data_root_path / THUMB_FOLDER_NAME_TITELIVE
    all_zips = list(sorted(data_thumbs_path.glob('livres_tl*.zip')))
    return all_zips


def get_zip_file_from_sandbox(file):
    return ZipFile(file)


def get_ordered_zip_description_files_from_sandbox_files():
    data_root_path = Path(os.path.dirname(os.path.realpath(__file__))) \
                     / '..' / '..' / 'sandboxes' / 'providers' / 'titelive_works'
    data_thumbs_path = data_root_path / DESCRIPTION_FOLDER_NAME_TITELIVE
    all_zips = list(sorted(data_thumbs_path.glob('Resume*.zip')))
    return all_zips
