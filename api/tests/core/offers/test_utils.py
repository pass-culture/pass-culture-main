from pcapi import settings
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.utils import offer_webapp_link
from pcapi.core.testing import override_features
from pcapi.utils.human_ids import humanize
from pcapi.utils.urls import generate_firebase_dynamic_link


class OffersUtilsTest:
    @override_features(WEBAPP_V2_ENABLED=False)
    def test_offer_webapp_link_when_webapp_V2_not_enabled(self):
        offer = offers_factories.OffererFactory()
        link = offer_webapp_link(offer)
        assert link == f"{settings.WEBAPP_URL}/offre/details/{humanize(offer.id)}"

    @override_features(WEBAPP_V2_ENABLED=True)
    def test_offer_webapp_link_when_webapp_V2_enabled(self):
        offer = offers_factories.OffererFactory()
        link = offer_webapp_link(offer)
        assert link == generate_firebase_dynamic_link(path=f"offre/{offer.id}", params=None)
