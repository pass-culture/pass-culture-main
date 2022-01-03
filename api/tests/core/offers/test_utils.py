from pcapi import settings
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.utils import offer_webapp_link


class OffersUtilsTest:
    def test_offer_webapp_link(self):
        offer = offers_factories.OffererFactory()
        link = offer_webapp_link(offer)
        assert link == f"{settings.WEBAPP_V2_URL}/offre/{offer.id}"
