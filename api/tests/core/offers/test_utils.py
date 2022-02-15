import pytest

from pcapi import settings
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.utils import offer_app_link


class OffersUtilsTest:
    @pytest.mark.usefixtures("db_session")
    def test_offer_app_link(self):
        offer = offers_factories.OffererFactory()
        link = offer_app_link(offer)
        assert link == f"{settings.WEBAPP_V2_URL}/offre/{offer.id}"
