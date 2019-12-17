from datetime import datetime
from unittest.mock import patch

from local_providers import TiteLiveThings
from models import Product, BookFormat, LocalProviderEvent
from models.local_provider_event import LocalProviderEventType
from models.pc_object import PcObject
from repository.provider_queries import get_provider_by_local_class
from tests.conftest import clean_database
from tests.test_utils import create_offerer, create_venue, create_product_with_thing_type, \
    activate_provider, create_offer_with_thing_product, create_stock, create_booking, create_user


class TiteliveThingsTest:
    @clean_database
    @patch('local_providers.titelive_things.get_files_to_process_from_titelive_ftp')
    @patch('local_providers.titelive_things.get_lines_from_thing_file')
    def test_create_1_thing_from_one_data_line_in_one_file(self,
                                                           get_lines_from_thing_file,
                                                           get_files_to_process_from_titelive_ftp,
                                                           app):
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

        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
        titelive_provider = activate_provider('TiteLiveThings')
        PcObject.save(venue, titelive_provider)

        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        product = Product.query.one()
        assert product.extraData.get('bookFormat') == BookFormat.BEAUX_LIVRES.value
        assert product.type == 'ThingType.LIVRE_EDITION'
        assert product.extraData.get('isbn') == '2895026319'

    @clean_database
    @patch('local_providers.titelive_things.get_files_to_process_from_titelive_ftp')
    @patch('local_providers.titelive_things.get_lines_from_thing_file')
    def test_does_not_create_product_when_product_is_a_school_book(self,
                                                                   get_lines_from_thing_file,
                                                                   get_files_to_process_from_titelive_ftp,
                                                                   app):
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

        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
        titelive_provider = activate_provider('TiteLiveThings')
        PcObject.save(venue, titelive_provider)

        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        assert Product.query.count() == 0

    @clean_database
    @patch('local_providers.titelive_things.get_files_to_process_from_titelive_ftp')
    @patch('local_providers.titelive_things.get_lines_from_thing_file')
    def test_update_1_thing_from_one_data_line_in_one_file(self,
                                                           get_lines_from_thing_file,
                                                           get_files_to_process_from_titelive_ftp,
                                                           app):
        # Given
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

        titelive_things_provider = get_provider_by_local_class('TiteLiveThings')

        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')

        product = create_product_with_thing_type(id_at_providers='9782895026310',
                                                 thing_name='Toto à la playa',
                                                 date_modified_at_last_provider=datetime(2001, 1, 1),
                                                 last_provider_id=titelive_things_provider.id)
        titelive_provider = activate_provider('TiteLiveThings')
        PcObject.save(venue, product, titelive_provider)

        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        updated_product = Product.query.first()
        assert updated_product.name == 'nouvelles du Chili'
        assert updated_product.extraData.get('bookFormat') == BookFormat.BEAUX_LIVRES.value

    @clean_database
    @patch('local_providers.titelive_things.get_files_to_process_from_titelive_ftp')
    def test_does_not_create_thing_when_no_files_found(self,
                                                       get_files_to_process_from_titelive_ftp,
                                                       app):
        # Given
        files_list = list()
        get_files_to_process_from_titelive_ftp.return_value = files_list

        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
        titelive_provider = activate_provider('TiteLiveThings')
        PcObject.save(venue, titelive_provider)

        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        assert Product.query.count() == 0

    @clean_database
    @patch('local_providers.titelive_things.get_files_to_process_from_titelive_ftp')
    @patch('local_providers.titelive_things.get_lines_from_thing_file')
    def test_does_not_create_thing_when_missing_columns_in_data_line(self,
                                                                     get_lines_from_thing_file,
                                                                     get_files_to_process_from_titelive_ftp,
                                                                     app):
        # Given
        files_list = list()
        files_list.append('Quotidien30.tit')

        get_files_to_process_from_titelive_ftp.return_value = files_list

        data_line = "9782895026310"

        get_lines_from_thing_file.return_value = iter([data_line])

        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
        titelive_provider = activate_provider('TiteLiveThings')
        PcObject.save(venue, titelive_provider)

        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        assert Product.query.count() == 0

    @clean_database
    @patch('local_providers.titelive_things.get_files_to_process_from_titelive_ftp')
    @patch('local_providers.titelive_things.get_lines_from_thing_file')
    def test_does_not_create_thing_when_too_many_columns_in_data_line(self,
                                                                      get_lines_from_thing_file,
                                                                      get_files_to_process_from_titelive_ftp,
                                                                      app):
        # Given
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

        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
        titelive_provider = activate_provider('TiteLiveThings')
        PcObject.save(venue, titelive_provider)

        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        assert Product.query.count() == 0

    @clean_database
    @patch('local_providers.titelive_things.get_files_to_process_from_titelive_ftp')
    @patch('local_providers.titelive_things.get_lines_from_thing_file')
    def test_should_not_create_product_when_school_related_product(self,
                                                                   get_lines_from_thing_file,
                                                                   get_files_to_process_from_titelive_ftp,
                                                                   app):
        # Given
        files_list = list()
        files_list.append('Quotidien30.tit')

        get_files_to_process_from_titelive_ftp.return_value = files_list

        data_line = "9782895026310" \
                    "~2895026319" \
                    "~livre scolaire" \
                    "~" \
                    "~2704" \
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
                    "~" \
                    "~" \
                    "~" \
                    "~369" \
                    "~860" \
                    "~3694440" \
                    "~"
        get_lines_from_thing_file.return_value = iter([data_line])

        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
        titelive_provider = activate_provider('TiteLiveThings')
        PcObject.save(venue, titelive_provider)

        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        assert Product.query.count() == 0

    @clean_database
    @patch('local_providers.titelive_things.get_files_to_process_from_titelive_ftp')
    @patch('local_providers.titelive_things.get_lines_from_thing_file')
    def test_should_delete_product_when_reference_changes_to_school_related_product(self,
                                                                                    get_lines_from_thing_file,
                                                                                    get_files_to_process_from_titelive_ftp,
                                                                                    app):
        # Given
        files_list = list()
        files_list.append('Quotidien30.tit')

        get_files_to_process_from_titelive_ftp.return_value = files_list

        data_line = "9782895026310" \
                    "~2895026319" \
                    "~livre scolaire" \
                    "~" \
                    "~2704" \
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
                    "~" \
                    "~" \
                    "~" \
                    "~369" \
                    "~860" \
                    "~3694440" \
                    "~"

        get_lines_from_thing_file.return_value = iter([data_line])

        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
        titelive_provider = activate_provider('TiteLiveThings')
        PcObject.save(venue, titelive_provider)
        product = create_product_with_thing_type(id_at_providers='9782895026310',
                                                 thing_name='Toto à la playa',
                                                 date_modified_at_last_provider=datetime(2001, 1, 1),
                                                 last_provider_id=titelive_provider.id)
        PcObject.save(product)

        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        assert Product.query.count() == 0

    @clean_database
    @patch('local_providers.titelive_things.get_files_to_process_from_titelive_ftp')
    @patch('local_providers.titelive_things.get_lines_from_thing_file')
    def test_should_delete_product_when_non_valid_product_type(self,
                                                               get_lines_from_thing_file,
                                                               get_files_to_process_from_titelive_ftp,
                                                               app):
        # Given
        files_list = list()
        files_list.append('Quotidien30.tit')

        get_files_to_process_from_titelive_ftp.return_value = files_list

        data_line = "9782895026310" \
                    "~2895026319" \
                    "~jeux de société" \
                    "~" \
                    "~1234" \
                    "~1" \
                    "~" \
                    "~" \
                    "~" \
                    "~18,99" \
                    "~LES EDITIONS DE L'INSTANT MEME" \
                    "~EPAGINE" \
                    "~11/05/2011" \
                    "~O" \
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
                    "~" \
                    "~" \
                    "~" \
                    "~369" \
                    "~860" \
                    "~3694440" \
                    "~"

        get_lines_from_thing_file.return_value = iter([data_line])

        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
        titelive_provider = activate_provider('TiteLiveThings')
        PcObject.save(venue, titelive_provider)
        product = create_product_with_thing_type(id_at_providers='9782895026310',
                                                 thing_name='Toto à la playa',
                                                 date_modified_at_last_provider=datetime(2001, 1, 1),
                                                 last_provider_id=titelive_provider.id)
        PcObject.save(product)

        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        assert Product.query.count() == 0

    @clean_database
    @patch('local_providers.titelive_things.get_files_to_process_from_titelive_ftp')
    @patch('local_providers.titelive_things.get_lines_from_thing_file')
    def test_should_log_error_when_trying_to_delete_product_with_associated_bookings(self,
                                                                                     get_lines_from_thing_file,
                                                                                     get_files_to_process_from_titelive_ftp,
                                                                                     app):
        # Given
        files_list = list()
        files_list.append('Quotidien30.tit')

        get_files_to_process_from_titelive_ftp.return_value = files_list

        data_line = "9782895026310" \
                    "~2895026319" \
                    "~jeux de société" \
                    "~" \
                    "~1234" \
                    "~1" \
                    "~" \
                    "~" \
                    "~" \
                    "~18,99" \
                    "~LES EDITIONS DE L'INSTANT MEME" \
                    "~EPAGINE" \
                    "~11/05/2011" \
                    "~O" \
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
                    "~" \
                    "~" \
                    "~" \
                    "~369" \
                    "~860" \
                    "~3694440" \
                    "~"

        get_lines_from_thing_file.return_value = iter([data_line])

        user = create_user()
        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
        titelive_provider = activate_provider('TiteLiveThings')
        PcObject.save(venue, titelive_provider)
        product = create_product_with_thing_type(id_at_providers='9782895026310',
                                                 thing_name='Toto à la playa',
                                                 date_modified_at_last_provider=datetime(2001, 1, 1),
                                                 last_provider_id=titelive_provider.id)
        offer = create_offer_with_thing_product(venue, product=product)
        stock = create_stock(offer=offer, price=0)
        booking = create_booking(user=user, stock=stock)
        PcObject.save(product, offer, stock, booking)

        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        assert Product.query.count() == 1
        provider_log_error = LocalProviderEvent.query \
            .filter_by(type=LocalProviderEventType.SyncError) \
            .one()
        assert provider_log_error.payload == 'Error deleting product with ISBN: 9782895026310'

    @clean_database
    @patch('local_providers.titelive_things.get_files_to_process_from_titelive_ftp')
    @patch('local_providers.titelive_things.get_lines_from_thing_file')
    def test_should_fill_isbn_info_with_ean13_if_isbn_not_known(self,
                                                                get_lines_from_thing_file,
                                                                get_files_to_process_from_titelive_ftp,
                                                                app):
        files_list = list()
        files_list.append('Quotidien30.tit')

        get_files_to_process_from_titelive_ftp.return_value = files_list

        data_line = "9782895026310" \
                    "~" \
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

        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
        titelive_provider = activate_provider('TiteLiveThings')
        PcObject.save(venue, titelive_provider)

        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        product = Product.query.one()
        assert product.extraData.get('isbn') == '9782895026310'
