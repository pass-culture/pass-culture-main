import pytest
from sqlalchemy import not_

from pcapi.core.offers.factories import ProductFactory
from pcapi.model_creators.specific_creators import create_product_with_thing_subcategory
from pcapi.models import Product
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize


@pytest.mark.usefixtures("db_session")
def when_product_has_one_thumb(app):
    # Given
    product = create_product_with_thing_subcategory(thumb_count=1)
    repository.save(product)
    product_id = humanize(product.id)

    # When
    thumb_url = product.thumbUrl

    # Then
    assert thumb_url == f"http://localhost/storage/thumbs/products/{product_id}"


@pytest.mark.usefixtures("db_session")
def when_product_has_no_thumb(app):
    # Given
    product = create_product_with_thing_subcategory(thumb_count=0)
    repository.save(product)

    # When
    thumb_url = product.thumbUrl

    # Then
    assert thumb_url is None


class ProductCanBeSynchronizedTest:
    @pytest.mark.usefixtures("db_session")
    def test_can_be_synchronized_product_cgu_compatible_and_sync_compatible(self):
        product = ProductFactory(isGcuCompatible=True, isSynchronizationCompatible=True)

        assert product.can_be_synchronized
        assert Product.query.filter(Product.can_be_synchronized).one() == product
        assert Product.query.filter(not_(Product.can_be_synchronized)).count() == 0

    @pytest.mark.usefixtures("db_session")
    def test_can_be_synchronized_product_cgu_compatible_and_not_sync_compatible(self):
        product = ProductFactory(isGcuCompatible=True, isSynchronizationCompatible=False)

        assert not product.can_be_synchronized
        assert Product.query.filter(Product.can_be_synchronized).count() == 0
        assert Product.query.filter(not_(Product.can_be_synchronized)).one() == product

    @pytest.mark.usefixtures("db_session")
    def test_can_be_synchronized_product_not_cgu_compatible_and_not_sync_compatible(self):
        product = ProductFactory(isGcuCompatible=False, isSynchronizationCompatible=False)

        assert not product.can_be_synchronized
        assert Product.query.filter(Product.can_be_synchronized).count() == 0
        assert Product.query.filter(not_(Product.can_be_synchronized)).one() == product

    @pytest.mark.usefixtures("db_session")
    def test_can_be_synchronized_product_not_cgu_compatible_and_sync_compatible(self):
        product = ProductFactory(isGcuCompatible=False, isSynchronizationCompatible=True)

        assert not product.can_be_synchronized
        assert Product.query.filter(Product.can_be_synchronized).count() == 0
        assert Product.query.filter(not_(Product.can_be_synchronized)).one() == product
