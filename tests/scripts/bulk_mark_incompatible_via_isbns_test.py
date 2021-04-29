import pytest

from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.factories import ProductFactory
from pcapi.core.testing import override_features
from pcapi.models import Offer
from pcapi.models import Product
from pcapi.repository import repository
from pcapi.scripts.bulk_mark_incompatible_via_isbns import bulk_mark_incompatible_via_isbns


class BulkMarkIncompatibleViaIsbnsTest:
    @pytest.mark.usefixtures("db_session")
    @override_features(SYNCHRONIZE_ALGOLIA=False)
    def test_should_mark_offers_and_products_as_incompatible_via_isbn(self):
        # Given
        product = ProductFactory(id=1, extraData={"isbn": "ABCDEFG"})
        product_1 = ProductFactory(id=2, extraData={"isbn": "HIJKLMN"})
        product_2 = ProductFactory(id=3, extraData={"isbn": "VWXYZ"})
        offer = OfferFactory(id=1, product=product)
        offer_1 = OfferFactory(id=2, product=product_1)
        offer_2 = OfferFactory(id=3, product=product_2)
        repository.save(offer, offer_1, offer_2)

        isbns_list = ["ABCDEFG", "HIJKLMN", "OPQRSTU"]

        # When
        bulk_mark_incompatible_via_isbns(isbns_list, 2)

        # Then
        products = Product.query.order_by(Product.id).all()
        offers = Offer.query.order_by(Offer.id).all()
        assert not products[0].isGcuCompatible
        assert not products[1].isGcuCompatible
        assert products[2].isGcuCompatible
        assert not offers[0].isActive
        assert not offers[1].isActive
        assert offers[2].isActive
