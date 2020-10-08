import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError

from pcapi.models import Product
from pcapi.models.db import db
from pcapi.repository import repository
from pcapi.scripts.performance_toolkit import get_pc_object_by_id_in_database, bulk_update_pc_objects, bulk_insert_pc_objects
from tests.conftest import clean_database
from pcapi.model_creators.specific_creators import create_product_with_thing_type


class GetPcObjectByIdInDatabaseTest:
    @clean_database
    def test_should_return_pc_object_if_match(self, app):
        # Given
        product = create_product_with_thing_type()
        repository.save(product)

        # When
        existing_product = get_pc_object_by_id_in_database(product.id, Product)

        # Then
        assert existing_product == product

    @clean_database
    def test_should_return_None_if_not_match(self, app):
        # Given
        product = create_product_with_thing_type()
        repository.save(product)

        # When
        existing_product = get_pc_object_by_id_in_database(45, Product)

        # Then
        assert existing_product is None


class BulkUpdatePcObjectsTest:
    @classmethod
    def teardown_method(cls):
        # Clean remaining pc objects from session
        db.session.expunge_all()

    @clean_database
    def test_should_update_pc_object_list_in_database(self, app):
        # Given
        product = create_product_with_thing_type()
        repository.save(product)
        existing_product = get_pc_object_by_id_in_database(product.id, Product)
        existing_product.thumbCount = 5

        # When
        bulk_update_pc_objects([existing_product], Product)

        # Then
        modified_product = Product.query.one()
        assert modified_product.thumbCount == 5

    @clean_database
    def test_should_raise_error_when_pc_object_does_not_exist(self, app):
        # Given
        product_to_update = create_product_with_thing_type()
        product_to_update.thumbCount = 5

        # When / Then
        with pytest.raises(StaleDataError):
            bulk_update_pc_objects([product_to_update], Product)


class BulkInsertPcObjectsTest:
    @classmethod
    def teardown_method(cls):
        # Clean remaining pc objects from session
        db.session.expunge_all()

    @clean_database
    def test_should_insert_pc_object_list_in_database(self, app):
        # Given
        product = create_product_with_thing_type(thumb_count=5)

        # When
        bulk_insert_pc_objects([product], Product)

        # Then
        modified_product = Product.query.one()
        assert modified_product.thumbCount == 5

    @clean_database
    def test_should_raise_error_when_pc_object_already_exists(self, app):
        # Given
        product = create_product_with_thing_type()
        repository.save(product)

        # When / Then
        with pytest.raises(IntegrityError):
            bulk_insert_pc_objects([product], Product)
