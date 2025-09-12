import pytest

from pcapi.core.chronicles import factories
from pcapi.core.products import factories as products_factories
from pcapi.models import db


@pytest.mark.usefixtures("db_session")
def test_increment_product_count():
    product = products_factories.ProductFactory()
    factories.ChronicleFactory.create(products=[product])

    assert product.chroniclesCount == 1


@pytest.mark.usefixtures("db_session")
def test_decrement_product_count():
    product = products_factories.ProductFactory()

    chronicle = factories.ChronicleFactory.create(products=[product])
    assert product.chroniclesCount == 1

    db.session.delete(chronicle)
    db.session.refresh(product)

    assert product.chroniclesCount == 0
