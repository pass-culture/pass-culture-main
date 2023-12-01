from unittest.mock import patch

import freezegun
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
    @freezegun.freeze_time("2023-10-25")
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
                "total_views": 50,
                "top_offers": [
                    {"numberOfViews": 7, "offerId": offer1.id},
                    {"numberOfViews": 6, "offerId": offer2.id},
                    {"numberOfViews": 4, "offerId": offer3.id},
                ],
            },
        )

        mock_run_query_with_params.side_effect = [
            iter(
                [
                    {"eventDate": "2023-10-18", "numberOfViews": 15},
                    {"eventDate": "2023-10-15", "numberOfViews": 10},
                    {"eventDate": "2023-10-14", "numberOfViews": 3},
                    {"eventDate": "2023-10-10", "numberOfViews": 2},
                ]
            ),
            iter(
                [
                    {"offerId": offer1.id, "numberOfViews": 12},
                    {"offerId": offer2.id, "numberOfViews": 10},
                    {"offerId": offer3.id, "numberOfViews": 8},
                ]
            ),
            iter(
                [
                    {"totalViews": 30},
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
            {"eventDate": "2023-10-10", "numberOfViews": 2},
            {"eventDate": "2023-10-11", "numberOfViews": 2},
            {"eventDate": "2023-10-12", "numberOfViews": 2},
            {"eventDate": "2023-10-13", "numberOfViews": 2},
            {"eventDate": "2023-10-14", "numberOfViews": 3},
            {"eventDate": "2023-10-15", "numberOfViews": 10},
            {"eventDate": "2023-10-16", "numberOfViews": 10},
            {"eventDate": "2023-10-17", "numberOfViews": 10},
            {"eventDate": "2023-10-18", "numberOfViews": 15},
            {"eventDate": "2023-10-19", "numberOfViews": 15},
            {"eventDate": "2023-10-20", "numberOfViews": 15},
            {"eventDate": "2023-10-21", "numberOfViews": 15},
            {"eventDate": "2023-10-22", "numberOfViews": 15},
            {"eventDate": "2023-10-23", "numberOfViews": 15},
            {"eventDate": "2023-10-24", "numberOfViews": 15},
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
        assert offerer_top_offers.jsonData["total_views_last_30_days"] == 30

    @freezegun.freeze_time("2023-10-25")
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
                    {"eventDate": "2023-10-10", "numberOfViews": 10},
                    {"eventDate": "2023-10-05", "numberOfViews": 5},
                ]
            ),
            iter(
                [
                    {"offerId": offer1.id, "numberOfViews": 12},
                    {"offerId": offer2.id, "numberOfViews": 10},
                    {"offerId": offer3.id, "numberOfViews": 8},
                ]
            ),
            iter(
                [
                    {"totalViews": 30},
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
            {"eventDate": "2023-10-05", "numberOfViews": 5},
            {"eventDate": "2023-10-06", "numberOfViews": 5},
            {"eventDate": "2023-10-07", "numberOfViews": 5},
            {"eventDate": "2023-10-08", "numberOfViews": 5},
            {"eventDate": "2023-10-09", "numberOfViews": 5},
            {"eventDate": "2023-10-10", "numberOfViews": 10},
            {"eventDate": "2023-10-11", "numberOfViews": 10},
            {"eventDate": "2023-10-12", "numberOfViews": 10},
            {"eventDate": "2023-10-13", "numberOfViews": 10},
            {"eventDate": "2023-10-14", "numberOfViews": 10},
            {"eventDate": "2023-10-15", "numberOfViews": 10},
            {"eventDate": "2023-10-16", "numberOfViews": 15},
            {"eventDate": "2023-10-17", "numberOfViews": 15},
            {"eventDate": "2023-10-18", "numberOfViews": 15},
            {"eventDate": "2023-10-19", "numberOfViews": 15},
            {"eventDate": "2023-10-20", "numberOfViews": 15},
            {"eventDate": "2023-10-21", "numberOfViews": 15},
            {"eventDate": "2023-10-22", "numberOfViews": 15},
            {"eventDate": "2023-10-23", "numberOfViews": 15},
            {"eventDate": "2023-10-24", "numberOfViews": 15},
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
        assert offerer_top_offers.jsonData["total_views_last_30_days"] == 30
