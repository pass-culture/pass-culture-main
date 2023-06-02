import pytest

from pcapi.core.offers.factories import ProductFactory
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.scripts.bulk_update_is_synchronization_compatible_product_via_eans import (
    bulk_update_is_synchronization_compatible_via_eans,
)


@pytest.mark.usefixtures("db_session")
def test_should_mark_synchronized_offers_and_products_as_not_synchronization_compatible_via_ean():
    product_1 = ProductFactory(id=1, extraData={"isbn": "5555555555555", "ean": "5555555555555"})
    product_2 = ProductFactory(id=2, extraData={"isbn": "6666666666666", "ean": "6666666666666"})
    product_3 = ProductFactory(id=3, extraData={"isbn": "2222222222222", "ean": "2222222222222"})
    product_4 = ProductFactory(id=4, extraData={"isbn": "7777777777777", "ean": "7777777777777"})

    eans_list = ["5555555555555", "6666666666666", "8888888888888", "7777777777777"]

    with assert_no_duplicated_queries():
        bulk_update_is_synchronization_compatible_via_eans(eans_list, is_synchronization_compatible=False, batch_size=4)

    assert not product_1.isSynchronizationCompatible
    assert not product_2.isSynchronizationCompatible
    assert product_3.isSynchronizationCompatible
    assert not product_4.isSynchronizationCompatible


@pytest.mark.usefixtures("db_session")
def test_should_mark_products_as_synchronization_compatible_via_isbn():
    product_1 = ProductFactory(
        id=1, extraData={"isbn": "5555555555555", "ean": "5555555555555"}, isSynchronizationCompatible=False
    )
    product_2 = ProductFactory(
        id=2, extraData={"isbn": "6666666666666", "ean": "6666666666666"}, isSynchronizationCompatible=False
    )
    product_3 = ProductFactory(
        id=3, extraData={"isbn": "2222222222222", "ean": "2222222222222"}, isSynchronizationCompatible=False
    )
    product_4 = ProductFactory(
        id=4, extraData={"isbn": "7777777777777", "ean": "7777777777777"}, isSynchronizationCompatible=True
    )

    eans_list = ["5555555555555", "8888888888888", "2222222222222"]

    bulk_update_is_synchronization_compatible_via_eans(eans_list, is_synchronization_compatible=True, batch_size=3)

    assert product_1.isSynchronizationCompatible
    assert not product_2.isSynchronizationCompatible
    assert product_3.isSynchronizationCompatible
    assert product_4.isSynchronizationCompatible
