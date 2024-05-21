from contextlib import suppress

import pytest

import pcapi.core.categories.subcategories_v2 as subcategories
from pcapi.core.offers.factories import ProductFactory
from pcapi.core.offers.models import Product
from pcapi.scripts.integration.add_eans import fill_missing_eans
from pcapi.scripts.integration.eans_data import EANS
from pcapi.scripts.integration.eans_data import EAN_CAT


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(name="cds")
def cds_fixture():
    eans = list(EANS[EAN_CAT.CDS])[:2]
    return [
        ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id, extraData={"ean": eans[0]}),
        ProductFactory(subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id, extraData={"ean": eans[1]}),
    ]


@pytest.fixture(name="ebooks")
def ebooks_fixture():
    eans = list(EANS[EAN_CAT.EBOOKS])[:2]
    return [
        ProductFactory(subcategoryId=subcategories.LIVRE_NUMERIQUE.id, extraData={"ean": eans[0]}),
        ProductFactory(subcategoryId=subcategories.LIVRE_NUMERIQUE.id, extraData={"ean": eans[1]}),
    ]


class FillMissingEANsTest:
    def test_with_no_products_at_all(self):
        fill_missing_eans()

        assert_products_count()
        assert_eans()

    def test_some_eans_already_exists(self, cds, ebooks):
        fill_missing_eans()

        assert_products_count()
        assert_eans()

    def test_some_eans_exists_next_to_unrelated_products(self, cds, ebooks):
        subcategory_id = subcategories.SUPPORT_PHYSIQUE_FILM.id
        products = [
            ProductFactory(subcategoryId=subcategory_id, extraData={"ean": "001122334455"}),
            ProductFactory(subcategoryId=subcategory_id, extraData={"ean": "667788990011"}),
        ]

        fill_missing_eans()

        assert_products_count(products)
        assert_eans(products)

    def test_some_eans_exists_next_to_unrelated_products_without_eans(self, cds, ebooks):
        products = [
            # first, create with none value, then remove whole extraData
            # otherwise, the factory would create some random extraData
            ProductFactory(subcategoryId=subcategories.LOCATION_INSTRUMENT.id, extraData={"ean": None}),
            ProductFactory(subcategoryId=subcategories.LOCATION_INSTRUMENT.id, extraData={"ean": None}),
        ]

        for product in products:
            product.extraData = None

        fill_missing_eans()

        assert_products_count(products)
        assert_eans()


def assert_products_count(extra_expected=None):
    extra_expected = extra_expected or []

    found_products = Product.query.all()
    assert len(found_products) == sum(len(eans) for eans in EANS.values()) + len(extra_expected)


def assert_eans(extra_expected=None):
    if extra_expected is not None:
        extra_expected = {p.extraData["ean"] for p in extra_expected}
    else:
        extra_expected = set()

    found_products = Product.query.all()
    found_eans = set()

    for product in found_products:
        with suppress(TypeError, KeyError):
            found_eans.add(product.extraData["ean"])

    assert found_eans == {ean for eans in EANS.values() for ean in eans} | extra_expected
