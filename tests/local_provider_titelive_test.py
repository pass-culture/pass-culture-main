""" local providers titelive test """
from pathlib import Path
from unittest.mock import patch

import os
import pytest

from local_providers import TiteLiveThings, TiteLiveThingThumbs, TiteLiveThingDescriptions
from local_providers.titelive_things import THINGS_FOLDER_NAME_TITELIVE
from models import Thing
from models.db import db
from sqlalchemy import func
from models.pc_object import PcObject
from models.provider import Provider
from models.venue_provider import VenueProvider
from tests.conftest import clean_database
from utils.test_utils import create_offerer, create_venue, \
    provider_test_whithout_mock, provider_test


@pytest.mark.standalone
class TiteliveTest:

    @clean_database
    @patch('local_providers.titelive_things.get_ordered_thing_files_from_titelive_ftp')
    @patch('local_providers.titelive_things.get_lines_from_thing_file')
    def test_titelive_complete_integration(self,
                                           get_lines_from_thing_file,
                                           get_ordered_thing_files_from_titelive_ftp,
                                           app):
        # mock
        files = get_ordered_thing_files_from_sandbox_files()
        get_ordered_thing_files_from_titelive_ftp.return_value = files

        files_content = []
        for file in files:
            content = get_lines_from_thing_file_sandboxes(file)
            files_content.append(content)

        get_lines_from_thing_file.side_effect = files_content

        # given
        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
        PcObject.check_and_save(venue)

        titelive_things_provider = Provider.getByClassName('TiteLiveThings')
        venue_provider = VenueProvider()
        venue_provider.venue = venue
        venue_provider.provider = titelive_things_provider
        venue_provider.isActive = True
        venue_provider.venueIdAtOfferProvider = '77567146400110'
        PcObject.check_and_save(venue_provider)

        # Import things
        provider_test_whithout_mock(app,
                                    TiteLiveThings,
                                    venue_provider,
                                    checkedObjects=422,
                                    createdObjects=355,
                                    updatedObjects=13,
                                    erroredObjects=0,
                                    checkedThumbs=0,
                                    createdThumbs=0,
                                    updatedThumbs=0,
                                    erroredThumbs=0,
                                    Thing=355
                                    )

        # Import thumbs for existing things
        provider_test(app,
                      TiteLiveThingThumbs,
                      None,
                      checkedObjects=106,
                      createdObjects=0,
                      updatedObjects=0,
                      erroredObjects=0,
                      checkedThumbs=166,
                      createdThumbs=92,
                      updatedThumbs=0,
                      erroredThumbs=0,
                      Thing=0
                      )

        assert db.session.query(func.sum(Thing.thumbCount)).scalar() == 92

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
                      Thing=0
                      )


def get_ordered_thing_files_from_sandbox_files():
    data_root_path = Path(os.path.dirname(os.path.realpath(__file__))) \
                     / '..' / 'sandboxes' / 'providers' / 'titelive_works'

    data_thing_paths = data_root_path / THINGS_FOLDER_NAME_TITELIVE
    all_thing_files = sorted(data_thing_paths.glob('Quotidien*.tit'))
    return all_thing_files


def get_lines_from_thing_file_sandboxes(file):
    with open(file, 'r', encoding='iso-8859-1') as f:
        data_lines = iter(f.readlines())
    return data_lines
