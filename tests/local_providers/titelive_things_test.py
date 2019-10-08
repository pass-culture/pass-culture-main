from datetime import datetime
from unittest.mock import patch

from local_providers import TiteLiveThings
from models import Product, BookFormat
from models.pc_object import PcObject
from repository.provider_queries import get_provider_by_local_class
from tests.conftest import clean_database
from tests.test_utils import create_offerer, create_venue, provider_test, create_product_with_thing_type


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
        assert product.extraData.get('isbn') == '2895026319'

    @clean_database
    @patch('local_providers.titelive_things.get_files_to_process_from_titelive_ftp')
    @patch('local_providers.titelive_things.get_lines_from_thing_file')
    def test_does_not_create_product_if_product_is_a_school_book(self,
                                                                 get_lines_from_thing_file,
                                                                 get_files_to_process_from_titelive_ftp,
                                                                 app):
        # mock
        files_list = list()
        files_list.append('Quotidien30.tit')

        get_files_to_process_from_titelive_ftp.return_value = files_list

        data_line = "9782895026310" \
                    "~2895026319" \
                    "~livre scolaire" \
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
                    "~Littérature scolaire" \
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
                    "~1" \
                    "~" \
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

        product = create_product_with_thing_type(id_at_providers='9782895026310',
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
