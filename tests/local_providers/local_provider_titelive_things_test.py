""" local providers test """
from datetime import datetime
from unittest.mock import patch

from local_providers import TiteLiveThings
from models import Product, BookFormat, ThingType
from models.pc_object import PcObject
from models.provider import Provider
from repository.provider_queries import get_provider_by_local_class
from tests.conftest import clean_database
from tests.local_providers.local_provider_titelive_test import get_ordered_thing_files_from_sandbox_files, \
    get_lines_from_thing_file_sandboxes
from tests.test_utils import create_offerer, create_venue, provider_test, create_product_with_Thing_type


class TiteliveThingsTest:

    @clean_database
    @patch('local_providers.titelive_things.get_files_to_process_from_titelive_ftp')
    @patch('local_providers.titelive_things.get_lines_from_thing_file')
    def test_create_1_thing_from_one_data_line_in_one_file(self,
                                                           get_lines_from_thing_file,
                                                           get_files_to_process_from_titelive_ftp,
                                                           app):
        # mock
        files_list = list()
        files_list.append('Quotidien30.tit')

        get_files_to_process_from_titelive_ftp.return_value = files_list

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
                    "~BL" \
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
        PcObject.save(venue)

        provider_test(app,
                      TiteLiveThings,
                      None,
                      checkedObjects=1,
                      createdObjects=1,
                      updatedObjects=0,
                      erroredObjects=0,
                      checkedThumbs=0,
                      createdThumbs=0,
                      updatedThumbs=0,
                      erroredThumbs=0,
                      Product=1
                      )

        product = Product.query.one()
        assert product.extraData.get('bookFormat') == BookFormat.BEAUX_LIVRES.value
        assert product.type == 'ThingType.LIVRE_EDITION'

    @clean_database
    @patch('local_providers.titelive_things.get_files_to_process_from_titelive_ftp')
    @patch('local_providers.titelive_things.get_lines_from_thing_file')
    def test_update_1_thing_from_one_data_line_in_one_file(self,
                                                           get_lines_from_thing_file,
                                                           get_files_to_process_from_titelive_ftp,
                                                           app):
        # mock
        files_list = list()
        files_list.append('Quotidien30.tit')

        get_files_to_process_from_titelive_ftp.return_value = files_list

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
                    "~BL" \
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
        titelive_things_provider = get_provider_by_local_class('TiteLiveThings')

        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')

        product = create_product_with_Thing_type(id_at_providers='9782895026310',
                                                 thing_name='Toto à la playa',
                                                 date_modified_at_last_provider=datetime(2001, 1, 1),
                                                 last_provider_id=titelive_things_provider.id)
        PcObject.save(venue, product)

        provider_test(app,
                      TiteLiveThings,
                      None,
                      checkedObjects=1,
                      createdObjects=0,
                      updatedObjects=1,
                      erroredObjects=0,
                      checkedThumbs=0,
                      createdThumbs=0,
                      updatedThumbs=0,
                      erroredThumbs=0,
                      )
        updated_product = Product.query.first()
        assert updated_product.name == 'nouvelles du Chili'
        assert updated_product.extraData.get('bookFormat') == BookFormat.BEAUX_LIVRES.value

    @clean_database
    @patch('local_providers.titelive_things.get_files_to_process_from_titelive_ftp')
    @patch('local_providers.titelive_things.get_lines_from_thing_file')
    def test_create_multiple_things_with_sandboxes_data(self,
                                                        get_lines_from_thing_file,
                                                        get_files_to_process_from_titelive_ftp,
                                                        app):
        # mock
        files = get_ordered_thing_files_from_sandbox_files()
        get_files_to_process_from_titelive_ftp.return_value = files

        files_content = []
        for file in files:
            content = get_lines_from_thing_file_sandboxes(file)
            files_content.append(content)

        get_lines_from_thing_file.side_effect = files_content

        # given
        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
        PcObject.save(venue)

        provider_test(app,
                      TiteLiveThings,
                      None,
                      checkedObjects=422,
                      createdObjects=340,
                      updatedObjects=16,
                      erroredObjects=0,
                      checkedThumbs=0,
                      createdThumbs=0,
                      updatedThumbs=0,
                      erroredThumbs=0,
                      Product=340
                      )

    @clean_database
    @patch('local_providers.titelive_things.get_files_to_process_from_titelive_ftp')
    def test_does_not_create_thing_if_no_files_found(self,
                                                     get_files_to_process_from_titelive_ftp,
                                                     app):
        # mock
        files_list = list()
        get_files_to_process_from_titelive_ftp.return_value = files_list

        # given
        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
        PcObject.save(venue)

        provider_test(app,
                      TiteLiveThings,
                      None,
                      checkedObjects=0,
                      createdObjects=0,
                      updatedObjects=0,
                      erroredObjects=0,
                      checkedThumbs=0,
                      createdThumbs=0,
                      updatedThumbs=0,
                      erroredThumbs=0,
                      Product=0
                      )

    @clean_database
    @patch('local_providers.titelive_things.get_files_to_process_from_titelive_ftp')
    @patch('local_providers.titelive_things.get_lines_from_thing_file')
    def test_does_not_create_thing_if_too_few_elements_in_data_line(self,
                                                                    get_lines_from_thing_file,
                                                                    get_files_to_process_from_titelive_ftp,
                                                                    app):
        # mock
        files_list = list()
        files_list.append('Quotidien30.tit')

        get_files_to_process_from_titelive_ftp.return_value = files_list

        data_line = "9782895026310"

        get_lines_from_thing_file.return_value = iter([data_line])

        # given

        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
        PcObject.save(venue)

        provider_test(app,
                      TiteLiveThings,
                      None,
                      checkedObjects=1,
                      createdObjects=0,
                      updatedObjects=0,
                      erroredObjects=0,
                      checkedThumbs=0,
                      createdThumbs=0,
                      updatedThumbs=0,
                      erroredThumbs=0,
                      Product=0
                      )

    @clean_database
    @patch('local_providers.titelive_things.get_files_to_process_from_titelive_ftp')
    @patch('local_providers.titelive_things.get_lines_from_thing_file')
    def test_does_not_create_thing_if_too_many_elements_in_data_line(self,
                                                                     get_lines_from_thing_file,
                                                                     get_files_to_process_from_titelive_ftp,
                                                                     app):
        # mock
        files_list = list()
        files_list.append('Quotidien30.tit')

        get_files_to_process_from_titelive_ftp.return_value = files_list

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
                    "~" \
                    "~Few Data" \
                    "~Some Test Data" \
                    "~Test Data" \
                    "~Other Test Data"
        get_lines_from_thing_file.return_value = iter([data_line])

        # given

        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
        PcObject.save(venue)

        provider_test(app,
                      TiteLiveThings,
                      None,
                      checkedObjects=1,
                      createdObjects=0,
                      updatedObjects=0,
                      erroredObjects=0,
                      checkedThumbs=0,
                      createdThumbs=0,
                      updatedThumbs=0,
                      erroredThumbs=0,
                      Product=0
                      )
