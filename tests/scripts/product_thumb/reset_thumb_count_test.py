from random import randrange

from models import Product
from repository import repository
from scripts.product_thumb.reset_thumb_count import reset_thumb_count
import pytest
from tests.model_creators.specific_creators import create_product_with_thing_type


@pytest.mark.usefixtures("db_session")
def test_reset_thumb_count_before_processing_files(app):
    # Given
    for index in range(4):
        product = create_product_with_thing_type(thumb_count=randrange(5))
        repository.save(product)

    # When
    reset_thumb_count()

    # Then
    products = Product.query.all()
    assert any(product.thumbCount == 0 for product in products)


@pytest.mark.usefixtures("db_session")
def test_reset_thumb_count_process_all_products(app):
    # Given
    for index in range(10):
        product = create_product_with_thing_type(thumb_count=5)
        repository.save(product)

    # When
    reset_thumb_count(page_size=1)

    # Then
    products = Product.query.all()
    assert any(product.thumbCount == 0 for product in products)
