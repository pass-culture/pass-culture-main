from models import PcObject
from repository.provider_queries import get_provider_by_local_class
from scripts.add_isbn_in_product_extra_data import add_isbn_in_product_and_offer_extra_data, \
    _extract_isbn_from_offer_id_at_providers
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue
from tests.model_creators.specific_creators import create_product_with_thing_type, create_offer_with_thing_product


class AddIsbnInProductExtraDataTest:
    @clean_database
    def test_does_not_update_extra_data_when_isbn_is_already_present(self, app):
        # Given
        provider = get_provider_by_local_class('TiteLiveThings')
        extra_data = {
            'author': 'author name',
            'isbn': '1234567891234',
        }
        product = create_product_with_thing_type(id_at_providers='12345678',
                                                 last_provider_id=provider.id,
                                                 extra_data=extra_data)

        PcObject.save(product)

        # When
        add_isbn_in_product_and_offer_extra_data()

        # Then
        assert product.extraData == extra_data

    @clean_database
    def test_update_extra_data_when_isbn_is_missing_and_product_was_updated_by_a_provider(self, app):
        # Given
        provider = get_provider_by_local_class('TiteLiveThings')
        extra_data1 = {
            'author': 'author name',
            'isbn': '*',
        }
        extra_data2 = {
            'author': 'author name',
        }
        product1 = create_product_with_thing_type(id_at_providers='8765432176124',
                                                  last_provider_id=provider.id,
                                                  extra_data=extra_data1)
        product2 = create_product_with_thing_type(id_at_providers='1234567809865',
                                                  last_provider_id=provider.id,
                                                  extra_data=extra_data2)
        PcObject.save(product1, product2)
        expected_extra_data = {
            'author': 'author name',
            'isbn': '1234567809865'
        }

        # When
        add_isbn_in_product_and_offer_extra_data()

        # Then
        assert product2.extraData == expected_extra_data

    @clean_database
    def test_update_extra_data_on_product_and_offer_when_isbn_is_missing(self, app):
        # Given
        provider = get_provider_by_local_class('TiteLiveThings')
        extra_data1 = {
            'author': 'author name',
            'isbn': '*',
        }
        extra_data2 = {
            'author': 'author name',
        }
        offerer = create_offerer()
        venue = create_venue(offerer)
        product1 = create_product_with_thing_type(id_at_providers='8765432176124',
                                                  last_provider_id=provider.id,
                                                  extra_data=extra_data1)
        product2 = create_product_with_thing_type(id_at_providers='1234567809865',
                                                  last_provider_id=provider.id,
                                                  extra_data=extra_data2)
        offer1 = create_offer_with_thing_product(venue,
                                                 product=product1,
                                                 id_at_providers='8765432176124@12345678912345',
                                                 last_provider_id=provider.id)
        offer2 = create_offer_with_thing_product(venue,
                                                 product=product2,
                                                 id_at_providers='1234567809865@12345678912345',
                                                 last_provider_id=provider.id)

        PcObject.save(product1, product2, offer1, offer2)

        # When
        add_isbn_in_product_and_offer_extra_data()

        # Then
        assert product1.extraData == {
            'author': 'author name',
            'isbn': '8765432176124'
        }
        assert product2.extraData == {
            'author': 'author name',
            'isbn': '1234567809865'
        }
        assert offer1.extraData == {
            'author': 'author name',
            'isbn': '8765432176124'
        }
        assert offer2.extraData == {
            'author': 'author name',
            'isbn': '1234567809865'
        }


class ExtractIsbnFromOfferIdAtProvidersTest:
    def test_should_return_first_part_of_id_at_providers(self):
        # Given
        offer_id_at_providers = '1234567809865@12345678912345'

        # When
        isbn = _extract_isbn_from_offer_id_at_providers(offer_id_at_providers)

        # Then
        assert isbn == '1234567809865'
