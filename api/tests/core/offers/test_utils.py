import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.utils import offer_webapp_link
from pcapi.utils.urls import generate_firebase_dynamic_link


class OffersUtilsTest:
    def test_offer_webapp_link(self):
        offer = offers_factories.OffererFactory()
        link = offer_webapp_link(offer)
        assert link == generate_firebase_dynamic_link(path=f"offre/{offer.id}", params=None)
