from pcapi.core.offers.factories import OfferFactory, ProductFactory
from pcapi.core.offers.models import Offer, Product
from pcapi.scripts.catch_up_orphan_cine_offers import catch_up_orphan_cine_offers
import pytest


@pytest.mark.usefixtures("db_session")
def test_all_orphans_visa_if_product_has_no_allocine_id():
    OfferFactory(extraData={"visa": "1"})
    should_not_be_updated_offer_name = OfferFactory(extraData={"visa": "2"}).name
    is_orphan_offer_name = OfferFactory(extraData={"visa": "4"}).name
    ProductFactory(name="P1", description="Desc1", durationMinutes=111, extraData={"allocineId": 1, "visa": "1"})
    ProductFactory(name="P2", description="Desc2", durationMinutes=222, extraData={"visa": "2"})
    ProductFactory(name="P3", description="Desc3", durationMinutes=333, extraData={"allocineId": 3, "visa": "3"})

    catch_up_orphan_cine_offers(dry_run=False)

    offers = Offer.query.order_by(Offer.id).all()
    products = Product.query.order_by(Product.id).all()

    assert offers[0].name == "P1"
    assert offers[0].description == "Desc1"
    assert offers[0].durationMinutes == 111
    assert offers[0].product == products[0]
    assert offers[0].extraData == products[0].extraData

    assert offers[1].name == should_not_be_updated_offer_name
    assert offers[2].name == is_orphan_offer_name
