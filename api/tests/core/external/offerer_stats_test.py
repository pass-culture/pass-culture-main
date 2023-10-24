from unittest.mock import patch

import pytest

from pcapi.connectors.big_query.queries.offerer_stats import DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE
from pcapi.connectors.big_query.queries.offerer_stats import TOP_3_MOST_CONSULTED_OFFERS_LAST_30_DAYS_TABLE
from pcapi.core.offerers import api
from pcapi.core.offerers.factories import OffererFactory
from pcapi.core.offerers.factories import OffererStatsFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offerers.models import OffererStats
from pcapi.core.offers.factories import OfferFactory


pytestmark = pytest.mark.usefixtures("db_session")


class OffererStatsTest:
    @patch("pcapi.connectors.big_query.TestingBackend.run_query")
    def test_update_offerer_stats_data(self, mock_run_query_with_params):
        offerer = OffererFactory()
        venue = VenueFactory(managingOfferer=offerer)
        offer1 = OfferFactory(venue=venue)
        offer2 = OfferFactory(venue=venue)
        offer3 = OfferFactory(venue=venue)

        OffererStatsFactory(
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

        OffererStatsFactory(
            offererId=offerer.id,
            syncDate="2023-10-14",
            table=TOP_3_MOST_CONSULTED_OFFERS_LAST_30_DAYS_TABLE,
            jsonData={
                "top_offers": [
                    {"numberOfViews": 7, "offerId": offer1.id},
                    {"numberOfViews": 6, "offerId": offer2.id},
                    {"numberOfViews": 4, "offerId": offer3.id},
                ]
            },
        )

        mock_run_query_with_params.side_effect = [
            iter(
                [
                    {"eventDate": "2023-10-16", "numberOfViews": 15},
                    {"eventDate": "2023-10-15", "numberOfViews": 10},
                ]
            ),
            iter(
                [
                    {"offerId": offer1.id, "numberOfViews": 12},
                    {"offerId": offer2.id, "numberOfViews": 10},
                    {"offerId": offer3.id, "numberOfViews": 8},
                ]
            ),
        ]

        api.get_offerer_stats_data(offerer.id)

        # Check that the stats have been updated

        offerer_global_stats = OffererStats.query.filter(
            OffererStats.offererId == offerer.id,
            OffererStats.table == DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE,
        ).one()
        assert offerer_global_stats.jsonData["daily_views"] == [
            {"eventDate": "2023-10-16", "numberOfViews": 15},
            {"eventDate": "2023-10-15", "numberOfViews": 10},
        ]

        offerer_top_offers = OffererStats.query.filter(
            OffererStats.offererId == offerer.id,
            OffererStats.table == TOP_3_MOST_CONSULTED_OFFERS_LAST_30_DAYS_TABLE,
        ).one()
        assert offerer_top_offers.jsonData["top_offers"] == [
            {"offerId": offer1.id, "numberOfViews": 12},
            {"offerId": offer2.id, "numberOfViews": 10},
            {"offerId": offer3.id, "numberOfViews": 8},
        ]

    @patch("pcapi.connectors.big_query.TestingBackend.run_query")
    def test_create_offerer_stats_data(self, mock_run_query_with_params):
        offerer = OffererFactory()
        venue = VenueFactory(managingOfferer=offerer)
        offer1 = OfferFactory(venue=venue)
        offer2 = OfferFactory(venue=venue)
        offer3 = OfferFactory(venue=venue)

        mock_run_query_with_params.side_effect = [
            iter(
                [
                    {"eventDate": "2023-10-16", "numberOfViews": 15},
                    {"eventDate": "2023-10-15", "numberOfViews": 10},
                ]
            ),
            iter(
                [
                    {"offerId": offer1.id, "numberOfViews": 12},
                    {"offerId": offer2.id, "numberOfViews": 10},
                    {"offerId": offer3.id, "numberOfViews": 8},
                ]
            ),
        ]

        assert OffererStats.query.count() == 0

        api.get_offerer_stats_data(offerer.id)

        # Check that the stats have been created

        offerer_global_stats = OffererStats.query.filter(
            OffererStats.offererId == offerer.id,
            OffererStats.table == DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE,
        ).one()
        assert offerer_global_stats.jsonData["daily_views"] == [
            {"eventDate": "2023-10-16", "numberOfViews": 15},
            {"eventDate": "2023-10-15", "numberOfViews": 10},
        ]

        offerer_top_offers = OffererStats.query.filter(
            OffererStats.offererId == offerer.id,
            OffererStats.table == TOP_3_MOST_CONSULTED_OFFERS_LAST_30_DAYS_TABLE,
        ).one()
        assert offerer_top_offers.jsonData["top_offers"] == [
            {"offerId": offer1.id, "numberOfViews": 12},
            {"offerId": offer2.id, "numberOfViews": 10},
            {"offerId": offer3.id, "numberOfViews": 8},
        ]
