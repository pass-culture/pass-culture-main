from datetime import datetime
from unittest.mock import patch

import pytest

from models import Product, PcObject, ThingType, VenueProvider, ApiErrors
from tests.conftest import clean_database
from tests.local_providers.provider_test_utils import TestLocalProvider, TestLocalProviderWithApiErrors, \
    TestLocalProviderNoCreation
from tests.test_utils import create_product_with_thing_type, create_venue, create_offerer, create_providable_info, \
    create_provider


class LocalProviderTest:
    class UpdateObjectsTest:
        @patch('tests.local_providers.provider_test_utils.TestLocalProvider.__next__')
        @clean_database
        def test_iterator_is_called_until_exhausted(self, dummy_function, app):
            # Given
            provider_test = create_provider('TestLocalProvider')
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

        @patch('tests.local_providers.provider_test_utils.TestLocalProvider.__next__')
        @clean_database
        def test_local_provider_create_new_object_when_no_object_in_database(self,
                                                                             next_function,
                                                                             app):
            # Given
            provider_test = create_provider('TestLocalProvider')
            PcObject.save(provider_test)

            providable_info = create_providable_info()

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

        @patch('tests.local_providers.provider_test_utils.TestLocalProvider.__next__')
        @clean_database
        def test_local_provider_update_existing_object(self,
                                                       next_function,
                                                       app):
            # Given
            provider_test = create_provider('TestLocalProvider')
            PcObject.save(provider_test)

            providable_info = create_providable_info(date_modified=datetime(2018, 1, 1))

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

        @patch('tests.local_providers.provider_test_utils.TestLocalProvider.__next__')
        @clean_database
        def test_local_provider_does_not_update_existing_object_when_date_is_older_than_last_modified_date(self,
                                                                                                           next_function,
                                                                                                           app):
            # Given
            provider_test = create_provider('TestLocalProvider')
            PcObject.save(provider_test)

            providable_info = create_providable_info(date_modified=datetime(2018, 1, 1))

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

        @patch('tests.local_providers.provider_test_utils.TestLocalProvider.__next__')
        @clean_database
        def test_local_provider_does_not_update_objects_when_venue_provider_is_not_active(self,
                                                                                          next_function,
                                                                                          app):
            # Given
            provider_test = create_provider('TestLocalProvider')
            PcObject.save(provider_test)

            providable_info = create_providable_info(date_modified=datetime(2018, 1, 1))

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

        @patch('tests.local_providers.provider_test_utils.TestLocalProvider.__next__')
        @clean_database
        def test_local_provider_does_not_update_objects_when_provider_is_not_active(self,
                                                                                    next_function,
                                                                                    app):
            # Given
            provider_test = create_provider('TestLocalProvider', is_active=False)
            PcObject.save(provider_test)

            providable_info = create_providable_info(date_modified=datetime(2018, 1, 1))

            next_function.side_effect = [
                [providable_info]
            ]

            provider = TestLocalProvider()

            # When
            provider.updateObjects()

            # Then
            assert Product.query.count() == 0

        @patch('tests.local_providers.provider_test_utils.TestLocalProviderNoCreation.__next__')
        @clean_database
        def test_local_provider_do_not_create_new_object_when_can_create_is_false(self,
                                                                                  next_function,
                                                                                  app):
            # Given
            provider_test = create_provider('TestLocalProviderNoCreation')
            PcObject.save(provider_test)

            providable_info = create_providable_info()

            next_function.side_effect = [
                [providable_info]
            ]

            provider = TestLocalProviderNoCreation()

            # When
            provider.updateObjects()

            # Then
            assert Product.query.count() == 0

        @patch('tests.local_providers.provider_test_utils.TestLocalProvider.__next__')
        @clean_database
        def test_local_provider_create_only_one_object_when_limit_is_one(self,
                                                                         next_function,
                                                                         app):
            # Given
            provider_test = create_provider('TestLocalProvider')
            PcObject.save(provider_test)

            providable_info1 = create_providable_info()

            providable_info2 = create_providable_info(id_at_providers='2')

            next_function.side_effect = [
                [providable_info1],
                [providable_info2]
            ]

            provider = TestLocalProvider()

            # When
            provider.updateObjects(limit=1)

            # Then
            new_product = Product.query.one()
            assert new_product.name == 'New Product'
            assert new_product.type == str(ThingType.LIVRE_EDITION)

    class CreateObjectTest:
        @clean_database
        def test_returns_object_with_expected_attributes(self, app):
            # Given
            provider_test = create_provider('TestLocalProvider')
            PcObject.save(provider_test)

            providable_info = create_providable_info()

            provider = TestLocalProvider()

            # When
            product = provider.create_object(providable_info)

            # Then
            assert product.name == 'New Product'
            assert product.type == str(ThingType.LIVRE_EDITION)

        @clean_database
        def test_raise_api_errors_exception_when_object_has_model_errors(self, app):
            # Given
            provider_test = create_provider('TestLocalProviderWithApiErrors')
            PcObject.save(provider_test)

            providable_info = create_providable_info()

            provider = TestLocalProviderWithApiErrors()

            # When
            with pytest.raises(ApiErrors) as api_errors:
                provider.create_object(providable_info)

            # Then
            assert api_errors.value.errors[
                       'url'] == ['Une offre de type Jeux (support physique) ne peut pas être numérique']
            assert Product.query.count() == 0

    class HandleUpdateTest:
        @clean_database
        def test_returns_object_with_expected_attributes(self, app):
            # Given
            provider_test = create_provider('TestLocalProvider')
            PcObject.save(provider_test)

            providable_info = create_providable_info()

            provider = TestLocalProvider()

            existing_product = create_product_with_thing_type(thing_name='Old product name',
                                                              thing_type=ThingType.INSTRUMENT,
                                                              id_at_providers=providable_info.id_at_providers,
                                                              last_provider_id=provider_test.id,
                                                              date_modified_at_last_provider=datetime(2000, 1, 1))

            # When
            provider.handle_update(existing_product, providable_info)

            # Then
            assert existing_product.name == 'New Product'
            assert existing_product.type == str(ThingType.LIVRE_EDITION)

        @clean_database
        def test_raise_api_errors_exception_when_object_has_model_errors(self, app):
            # Given
            provider_test = create_provider('TestLocalProviderWithApiErrors')
            PcObject.save(provider_test)

            providable_info = create_providable_info()

            provider = TestLocalProviderWithApiErrors()

            existing_product = create_product_with_thing_type(thing_name='Old product name',
                                                              thing_type=ThingType.INSTRUMENT,
                                                              id_at_providers=providable_info.id_at_providers,
                                                              last_provider_id=provider_test.id,
                                                              date_modified_at_last_provider=datetime(2000, 1, 1))

            # When
            with pytest.raises(ApiErrors) as api_errors:
                provider.handle_update(existing_product, providable_info)

            # Then
            assert api_errors.value.errors[
                       'url'] == ['Une offre de type Jeux (support physique) ne peut pas être numérique']
