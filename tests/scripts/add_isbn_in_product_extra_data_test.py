from models import PcObject
from repository.provider_queries import get_provider_by_local_class
from scripts.add_isbn_in_product_extra_data import add_isbn_in_product_extra_data
from tests.conftest import clean_database
from tests.test_utils import create_product_with_thing_type


class AddIsbnInProductExtraDataTest:
    @clean_database
    def test_does_not_update_extra_data_when_isbn_is_already_present(self, app):
        # Given
        provider = get_provider_by_local_class('TiteLiveThings')
        json_data = {
            'author': 'author name',
            'isbn': 'isbn existant',
        }
        product = create_product_with_thing_type(id_at_providers='12345678',
                                                 last_provider_id=provider.id,
                                                 extra_data=json_data)

        PcObject.save(product)

        # When
        add_isbn_in_product_extra_data()

        # Then
        assert product.extraData == json_data

    @clean_database
    def test_update_extra_data_when_isbn_is_missing_and_product_was_updated_by_a_provider(self, app):
        # Given
        provider = get_provider_by_local_class('TiteLiveThings')
        json_data1 = {
            'author': 'author name',
            'isbn': 'isbn existant',
        }
        json_data2 = {
            'author': 'author name',
        }
        product1 = create_product_with_thing_type(id_at_providers='87654321',
                                                  last_provider_id=provider.id,
                                                  extra_data=json_data1)
        product2 = create_product_with_thing_type(id_at_providers='12345678',
                                                  last_provider_id=provider.id,
                                                  extra_data=json_data2)
        PcObject.save(product1, product2)
        expected_extra_data = {
            'author': 'author name',
            'isbn': '12345678'
        }

        # When
        add_isbn_in_product_extra_data()

        # Then
        assert product2.extraData == expected_extra_data
