from random import randrange

from models import Product, PcObject
from scripts.product_thumb.reset_thumb_count import reset_thumb_count
from tests.conftest import clean_database
from tests.test_utils import create_product_with_thing_type


@clean_database
def test_reset_thumb_count_before_processing_files(app):
    # Given
    for index in range(4):
        product = create_product_with_thing_type(thumb_count=randrange(5))
        PcObject.save(product)

    # When
    reset_thumb_count()

    # Then
    products = Product.query.all()
    assert any(product.thumbCount == 0 for product in products)
