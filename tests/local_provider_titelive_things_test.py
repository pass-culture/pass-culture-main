""" local providers test """
from pathlib import Path
from unittest.mock import patch

import os
import pytest

from local_providers import TiteLiveThings
from local_providers.titelive_things import THINGS_FOLDER_NAME_TITELIVE
from models.pc_object import PcObject
from models.provider import Provider
from models.venue_provider import VenueProvider
from tests.conftest import clean_database
from utils.test_utils import create_offerer, create_venue, \
    provider_test_whithout_mock


@pytest.mark.standalone
class TiteliveThingsTest:

    @clean_database
    @patch('local_providers.titelive_things.get_ordered_thing_files_from_titelive_ftp')
    @patch('local_providers.titelive_things.get_lines_from_thing_file')
    def test_titelive_things_create_1_thing(self,
                                            get_lines_from_thing_file,
                                            get_ordered_thing_files_from_titelive_ftp,
                                            app):
        # mock
        files_list = list()
        files_list.append('Quotidien30.tit')
        files_list.append('Quotidien31.tit')

        get_ordered_thing_files_from_titelive_ftp.return_value = files_list

        data_line = "9782895026310" \
                    "~2895026319" \
                    "~nouvelles du Chili" \
                    "~" \
                    "~0203" \
                    "~1" \
                    "~" \
                    "~" \
                    "~" \
                    "~18,99" \
                    "~LES EDITIONS DE L'INSTANT MEME" \
                    "~EPAGINE" \
                    "~11/05/2011" \
                    "~LE" \
                    "~2" \
                    "~0" \
                    "~0,0" \
                    "~0,0" \
                    "~0,0" \
                    "~0" \
                    "~0" \
                    "~0" \
                    "~0" \
                    "~Collectif" \
                    "~15/01/2013" \
                    "~02/03/2018" \
                    "~5,50" \
                    "~Littérature Hispano-Portugaise" \
                    "~" \
                    "~" \
                    "~" \
                    "~" \
                    "~" \
                    "~1" \
                    "~3012420280013" \
                    "~" \
                    "~" \
                    "~" \
                    "~" \
                    "~" \
                    "~0" \
                    "~" \
                    "~369" \
                    "~860" \
                    "~3694440" \
                    "~"
        get_lines_from_thing_file.return_value = iter([data_line])

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

        provider_test_whithout_mock(app,
                                    TiteLiveThings,
                                    venue_provider,
                                    checkedObjects=1,
                                    createdObjects=1,
                                    updatedObjects=0,
                                    erroredObjects=0,
                                    checkedThumbs=0,
                                    createdThumbs=0,
                                    updatedThumbs=0,
                                    erroredThumbs=0,
                                    Thing=1
                                    )

    @clean_database
    @patch('local_providers.titelive_things.get_ordered_thing_files_from_titelive_ftp')
    @patch('local_providers.titelive_things.get_lines_from_thing_file')
    def test_titelive_things_with_sandboxes_data(self,
                                                 get_lines_from_thing_file,
                                                 get_ordered_thing_files_from_titelive_ftp,
                                                 app):
        # mock
        files = self.get_ordered_thing_files_from_sandbox_files()
        get_ordered_thing_files_from_titelive_ftp.return_value = files

        files_content = []
        for file in files:
            content = self.get_lines_from_thing_file_sandboxes(file)
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

    def get_ordered_thing_files_from_sandbox_files(self):
        data_root_path = Path(os.path.dirname(os.path.realpath(__file__))) \
                         / '..' / 'sandboxes' / 'providers' / 'titelive_works'

        data_thing_paths = data_root_path / THINGS_FOLDER_NAME_TITELIVE
        all_thing_files = sorted(data_thing_paths.glob('Quotidien*.tit'))
        if not os.path.isdir(data_root_path):
            raise ValueError('File not found : ' + str(data_root_path)
                             + '\nDid you run "pc ftp_mirrors" ?')
        return all_thing_files

    def get_lines_from_thing_file_sandboxes(self, file):
        with open(file, 'r', encoding='iso-8859-1') as f:
            data_lines = iter(f.readlines())
        return data_lines
