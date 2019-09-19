from datetime import datetime
from unittest.mock import patch

from local_providers.local_provider import LocalProvider
from local_providers.providable_info import ProvidableInfo
from models import Product, Provider, PcObject, ThingType, VenueProvider
from tests.conftest import clean_database
from tests.test_utils import create_product_with_thing_type, create_venue, create_offerer


class TestLocalProvider(LocalProvider):
    help = ""
    identifierDescription = "Code LocalProvider"
    identifierRegexp = "*"
    name = "LocalProvider Test"
    object_type = Product
    canCreate = True

    def __init__(self, venue_provider: VenueProvider = None):
        super().__init__(venue_provider)
        self.venue_provider = venue_provider

    def updateObject(self, obj):
        obj.name = 'New Product'
        obj.type = str(ThingType.LIVRE_EDITION)

    def __next__(self):
        pass


class LocalProviderTest:
    @patch('tests.local_providers.local_provider_test.TestLocalProvider.__next__')
    @clean_database
    def test_iterator_is_called_until_exhausted(self, dummy_function, app):
        # Given
        provider_test = Provider()
        provider_test.localClass = 'TestLocalProvider'
        provider_test.isActive = True
        provider_test.name = 'My Test Provider'
        PcObject.save(provider_test)

        dummy_function.side_effect = [
            None,
            None,
            None
        ]

        provider = TestLocalProvider()

        # When
        provider.updateObjects()

        # Then
        assert dummy_function.call_count == 4

    @patch('tests.local_providers.local_provider_test.TestLocalProvider.__next__')
    @clean_database
    def test_local_provider_create_new_object_when_no_object_in_database(self,
                                                                         next_function,
                                                                         app):
        # Given
        provider_test = Provider()
        provider_test.localClass = 'TestLocalProvider'
        provider_test.isActive = True
        provider_test.name = 'My Test Provider'
        PcObject.save(provider_test)

        providable_info = ProvidableInfo()
        providable_info.type = Product
        providable_info.id_at_providers = '1'
        providable_info.date_modified_at_provider = datetime.utcnow()

        next_function.side_effect = [
            [providable_info]
        ]

        provider = TestLocalProvider()

        # When
        provider.updateObjects()

        # Then
        new_product = Product.query.one()
        assert new_product.name == 'New Product'
        assert new_product.type == str(ThingType.LIVRE_EDITION)

    @patch('tests.local_providers.local_provider_test.TestLocalProvider.__next__')
    @clean_database
    def test_local_provider_update_existing_object(self,
                                                   next_function,
                                                   app):
        # Given
        provider_test = Provider()
        provider_test.localClass = 'TestLocalProvider'
        provider_test.isActive = True
        provider_test.name = 'My Test Provider'
        PcObject.save(provider_test)

        providable_info = ProvidableInfo()
        providable_info.type = Product
        providable_info.id_at_providers = '1'
        providable_info.date_modified_at_provider = datetime(2018, 1, 1)

        next_function.side_effect = [
            [providable_info]
        ]

        existing_product = create_product_with_thing_type(thing_name='Old product name',
                                                          thing_type=ThingType.INSTRUMENT,
                                                          id_at_providers=providable_info.id_at_providers,
                                                          last_provider_id=provider_test.id,
                                                          date_modified_at_last_provider=datetime(2000, 1, 1))
        PcObject.save(existing_product)

        provider = TestLocalProvider()

        # When
        provider.updateObjects()

        # Then
        new_product = Product.query.one()
        assert new_product.name == 'New Product'
        assert new_product.type == str(ThingType.LIVRE_EDITION)
        assert new_product.dateModifiedAtLastProvider == providable_info.date_modified_at_provider

    @patch('tests.local_providers.local_provider_test.TestLocalProvider.__next__')
    @clean_database
    def test_local_provider_does_not_update_existing_object_when_date_is_older_than_last_modified_date(self,
                                                                                                       next_function,
                                                                                                       app):
        # Given
        provider_test = Provider()
        provider_test.localClass = 'TestLocalProvider'
        provider_test.isActive = True
        provider_test.name = 'My Test Provider'
        PcObject.save(provider_test)

        providable_info = ProvidableInfo()
        providable_info.type = Product
        providable_info.id_at_providers = '1'
        providable_info.date_modified_at_provider = datetime(2018, 1, 1)

        next_function.side_effect = [
            [providable_info]
        ]

        existing_product = create_product_with_thing_type(thing_name='Old product name',
                                                          thing_type=ThingType.INSTRUMENT,
                                                          id_at_providers=providable_info.id_at_providers,
                                                          last_provider_id=provider_test.id,
                                                          date_modified_at_last_provider=datetime(2019, 1, 1))
        PcObject.save(existing_product)

        provider = TestLocalProvider()

        # When
        provider.updateObjects()

        # Then
        same_product = Product.query.one()
        assert same_product.name == 'Old product name'
        assert same_product.type == str(ThingType.INSTRUMENT)
        assert same_product.dateModifiedAtLastProvider == existing_product.dateModifiedAtLastProvider

    @patch('tests.local_providers.local_provider_test.TestLocalProvider.__next__')
    @clean_database
    def test_local_provider_does_not_update_objects_when_venue_provider_is_not_active(self,
                                                                                      next_function,
                                                                                      app):
        # Given
        provider_test = Provider()
        provider_test.localClass = 'TestLocalProvider'
        provider_test.isActive = True
        provider_test.name = 'My Test Provider'
        PcObject.save(provider_test)

        providable_info = ProvidableInfo()
        providable_info.type = Product
        providable_info.id_at_providers = '1'
        providable_info.date_modified_at_provider = datetime(2018, 1, 1)

        next_function.side_effect = [
            [providable_info]
        ]

        venue_provider = VenueProvider()
        venue_provider.provider = provider_test
        venue_provider.venue = create_venue(create_offerer())
        venue_provider.isActive = False
        PcObject.save(venue_provider)

        provider = TestLocalProvider(venue_provider)

        # When
        provider.updateObjects()

        # Then
        assert Product.query.count() == 0

    @patch('tests.local_providers.local_provider_test.TestLocalProvider.__next__')
    @clean_database
    def test_local_provider_does_not_update_objects_when_provider_is_not_active(self,
                                                                                next_function,
                                                                                app):
        # Given
        provider_test = Provider()
        provider_test.localClass = 'TestLocalProvider'
        provider_test.isActive = False
        provider_test.name = 'My Test Provider'
        PcObject.save(provider_test)

        providable_info = ProvidableInfo()
        providable_info.type = Product
        providable_info.id_at_providers = '1'
        providable_info.date_modified_at_provider = datetime(2018, 1, 1)

        next_function.side_effect = [
            [providable_info]
        ]

        provider = TestLocalProvider()

        # When
        provider.updateObjects()

        # Then
        assert Product.query.count() == 0
