import pytest
import time_machine

from pcapi.connectors.big_query.queries.offerer_stats import DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE
from pcapi.connectors.big_query.queries.offerer_stats import TOP_3_MOST_CONSULTED_OFFERS_LAST_30_DAYS_TABLE
from pcapi.core.offerers import api
from pcapi.core.offerers.factories import OffererFactory
from pcapi.core.offerers.factories import OffererStatsFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offerers.models import OffererStats
from pcapi.core.offers.factories import OfferFactory
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


class OffererStatsTest:
    @time_machine.travel("2023-10-25")
    def test_update_offerer_stats_data(self):
        offerer = OffererFactory()
        venue = VenueFactory(managingOfferer=offerer)
        offer1 = OfferFactory(venue=venue)
        offer2 = OfferFactory(venue=venue)
        offer3 = OfferFactory(venue=venue)

        daily_views = OffererStatsFactory(
            offererId=offerer.id,
            syncDate="2023-10-14",
            table=DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE,
            jsonData={
                "daily_views": [
                    {"numberOfViews": 10, "eventDate": "2023-10-14"},
                    {"numberOfViews": 7, "eventDate": "2023-10-13"},
                ]
            },
        )

        top_offers = OffererStatsFactory(
            offererId=offerer.id,
            syncDate="2023-10-14",
            table=TOP_3_MOST_CONSULTED_OFFERS_LAST_30_DAYS_TABLE,
            jsonData={
                "total_views": 50,
                "top_offers": [
                    {"numberOfViews": 7, "offerId": offer1.id},
                    {"numberOfViews": 6, "offerId": offer2.id},
                    {"numberOfViews": 4, "offerId": offer3.id},
                ],
            },
        )

        result = api.get_offerer_stats_data(offerer.id)

        assert daily_views in result
        assert top_offers in result

    @time_machine.travel("2023-10-25")
    def test_create_offerer_stats_data(self):
        offerer = OffererFactory()

        assert db.session.query(OffererStats).count() == 0

        result = api.get_offerer_stats_data(offerer.id)

        assert result == []
